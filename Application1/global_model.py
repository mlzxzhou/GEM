from __future__ import division
import os
import sys
import cvxpy as cvx
import numpy as np
import scipy.sparse as sp
import timeit
from multiprocessing import Pool
import pickle
import bisect
import time
import matplotlib.pyplot as plt
import argparse
import math
import operator
from tool import logger
from tool import ROOTDIR
from tool import BASETIME
from tool import NONWORKDAY
from tool import safe_open_w
from tool import cal_distance
from tool import tid_to_timestamp
from tool import str2value
from tool import cal_grid_loc
from tool import cal_grid
from dgckernel.octearth import OctEarth
from dgckernel.keycoder import KeyCoder
from dgckernel.hexcell import HexCellGenerator
from dgckernel.dgcalculator import Calculator

print(sys.path)
date = DATE
_T = 6  # 10 min
_TD = 60  # 1 min
_TN = int(24 * 3600 / _TD)  # 1440


with open('data/processed/area5/grids_to_id.pickle', 'rb') as f:
   grids_to_id = pickle.load(f)

grids_to_id_s = sorted(grids_to_id.items(), key=operator.itemgetter(1))
gridsKey = []
for i in range(len(grids_to_id)):
    gridsKey.append(grids_to_id_s[i][0])

data_dir = 'data/processed/area5/'
order_count = np.load(data_dir + 'area5_{}_order.npz'.format(date))
order_count_full = order_count['order_count_full']
driver_count = np.load(data_dir + 'area5_{}_driver.npz'.format(date))
cur_driver_count = driver_count['cur_driver_count']
cost_norm = driver_count['cost_norm']

_N = len(grids_to_id)


### GEM ###
def global_transport(o_t, d_t, gridsKey, grids_to_id, k, w):
    indice_count = np.zeros((_N,),dtype=int)
    for j in range(_N):
        hex_cal = Calculator()
        hex_cal.SetLayer(12)
        key = gridsKey[j]
        indices = [j]
        for i in range(k):
            bhex_ids = hex_cal.HexCellBoudary(key, i + 1)
            inter = set(gridsKey).intersection(bhex_ids)
            indices_add = [grids_to_id[x] for x in inter]
            if len(indices_add) > 0:
                indices = indices + indices_add
        indice_count[j] = len(indices)

    gamma = cvx.Variable((np.sum(indice_count), 1))
    S = cvx.Variable((_N, 1))
    C = np.ones((_N, 1))

    A_1 = np.zeros((_N, np.sum(indice_count)))
    O_1 = np.zeros((_N, np.sum(indice_count)))
    cost = np.zeros((1, np.sum(indice_count)))
    for j in range(_N):
        hex_cal = Calculator()
        hex_cal.SetLayer(12)
        key = gridsKey[j]
        indices = [j]
        for i in range(k):
            bhex_ids = hex_cal.HexCellBoudary(key, i + 1)
            inter = set(gridsKey).intersection(bhex_ids)
            indices_add = [grids_to_id[x] for x in inter]
            if len(indices_add) > 0:
                indices = indices + indices_add
        A_1[j, np.sum(indice_count[:j]):np.sum(indice_count[:(j + 1)])] = 1
        for p in range(int(indice_count[j])):
            cost[:, np.sum(indice_count[:j]) + p] = w * cost_norm[j, indices[p]]
            O_1[j, np.sum(indice_count[:j]) + p] = w * cost_norm[j, indices[p]]

    A_2 = np.zeros((_N, np.sum(indice_count)))
    O_2 = np.zeros((_N, np.sum(indice_count)))
    for j in range(_N):
        hex_cal = Calculator()
        hex_cal.SetLayer(12)
        key = gridsKey[j]
        indices = [j]
        for i in range(k):
            bhex_ids = hex_cal.HexCellBoudary(key, i + 1)
            inter = set(gridsKey).intersection(bhex_ids)
            indices_add = [grids_to_id[x] for x in inter]
            if len(indices_add) > 0:
               indices = indices + indices_add

        for p in indices:
            key = gridsKey[p]
            indices_1 = [p]
            for i in range(k):
                bhex_ids = hex_cal.HexCellBoudary(key, i + 1)
                inter = set(gridsKey).intersection(bhex_ids)
                indices_add = [grids_to_id[x] for x in inter]
                if len(indices_add) > 0:
                   indices_1 = indices_1 + indices_add
            index = indices_1.index(j)
            A_2[j, np.sum(indice_count[:p]) + index] = 1
            O_2[j, np.sum(indice_count[:p]) + index] = w * cost_norm[j, p]

    obj = cvx.Minimize(C.T * S + cost * gamma)

    constr = [A_2 * gamma + S >= o_t.reshape(-1, 1), A_2 * gamma - S <= o_t.reshape(-1, 1), 0 <= gamma, 0 <= S,
              A_1 * gamma == d_t.reshape(-1, 1)]
    prob = cvx.Problem(obj, constr)
    d = prob.solve(solver=cvx.GLPK)

    tmp = o_t.reshape(_N, 1)
    ratio = np.zeros((_N,))
    tild_d = np.dot(A_2, gamma.value) - np.dot(O_2, gamma.value)
    tild_d[tild_d < 0] = 0
    for i in range(_N):
        if (tmp[i, 0] == 0) & (tild_d[i, 0] == 0):
            ratio[i] = 1
        elif tild_d[i, 0] == 0:
            ratio[i] = tmp[i, 0] / (tild_d[i, 0] + 1)
        else:
            ratio[i] = tmp[i, 0] / tild_d[i, 0]

    return d, ratio


### Wasserstein Distance ###
def wd_coherence_dual(o_t, d_t, cost_norm):
    O_t = np.sum(o_t)
    D_t = np.sum(d_t)
    index = (o_t > 0) | (d_t > 0)
    b_1 = o_t[index] / O_t
    b_2 = d_t[index] / D_t
    b = np.concatenate((b_1,b_2))
    var_num = np.sum(index)
    y = cvx.Variable((var_num * 2, 1))
    obj = cvx.Maximize(b.T*y)

    A_1 = np.zeros((var_num, var_num * var_num))
    for p in range(var_num):
        A_1[p,(var_num * p): (var_num * (p+1))] = np.ones((1, var_num))
    A_2 = np.zeros((var_num, var_num * var_num))
    for p in range(var_num):
        for q in range(var_num):
            A_2[p,(q * var_num + p)] = 1
    A = np.concatenate((A_1, A_2))
    C = cost_norm[index, :][:, index].reshape((var_num * var_num, 1))
    constr = [A.T * y <= C]
    prob = cvx.Problem(obj, constr)
    d = prob.solve(solver=cvx.GLPK)
    return d


metric = np.zeros((_TN, ))
metric_1 = np.zeros((_TN, ))
ratio = np.zeros((_N, _TN))
for j in range(_TN):
    metric[j], ratio[:, j] = global_transport(order_count_full[:, j], cur_driver_count[:, j], gridsKey, grids_to_id, 1, 0.4)
    metric_1[j] = wd_coherence_dual(order_count_full[:, j], cur_driver_count[:, j], cost_norm)
    print(j)

np.savez('data/output/area5/area5_{}_metric.npz'.format(date), ratio=ratio, global_metric=metric)
np.savez('data/output/area5/area5_{}_metric_1.npz'.format(date), ratio=ratio, global_metric_w=metric_1)
