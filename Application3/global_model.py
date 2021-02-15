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
sys.path.insert(0,'../dgckernel')
from dgckernel.octearth import OctEarth
from dgckernel.keycoder import KeyCoder
from dgckernel.hexcell import HexCellGenerator
from dgckernel.dgcalculator import Calculator

date=DATE

_T = 6  # 60 min
_TD = 60  # 10 min
_TN = int(24 * 3600 / _TD)  # 144


with open('../data/raw/area5/grids_to_id.pickle', 'rb') as f:
   grids_to_id = pickle.load(f)

grids_to_id_s = sorted(grids_to_id.items(), key=operator.itemgetter(1))
gridsKey = []
for i in range(len(grids_to_id)):
    gridsKey.append(grids_to_id_s[i][0])

data_dir = '../data/processed/area5/'
order = np.load(data_dir + 'area5_{}_order.npz'.format(date))
order_count_full = order['order_count_full']
order_count_finish = order['order_count_finish']
driver = np.load(data_dir + 'area5_{}_driver.npz'.format(date))
cur_driver_count = driver['cur_driver_count']
cost_norm = driver['cost_norm']

_N = len(grids_to_id)


def global_transport(o_t, d_t, gridsKey, grids_to_id, k, w):
    indice_count = np.zeros((_N,),dtype=int)
    for j in range(_N):
        hex_cal = Calculator()
        hex_cal.SetLayer(12)
        key = gridsKey[j]
        indices = [j]
        for i in range(k):
            bhex_ids = hex_cal.HexCellBoudary(key,i+1)
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
            bhex_ids = hex_cal.HexCellBoudary(key,i+1)
            inter = set(gridsKey).intersection(bhex_ids)
            indices_add = [grids_to_id[x] for x in inter]
            if len(indices_add) > 0:
                indices = indices + indices_add
        A_1[j,np.sum(indice_count[:j]):np.sum(indice_count[:(j+1)])] = 1
        for p in range(int(indice_count[j])):
            cost[:, np.sum(indice_count[:j])+p] = w * cost_norm[j,indices[p]]
            O_1[j, np.sum(indice_count[:j])+p] = w * cost_norm[j,indices[p]]
    
    A_2 = np.zeros((_N, np.sum(indice_count)))
    O_2 = np.zeros((_N, np.sum(indice_count)))
    for j in range(_N):
        hex_cal = Calculator()
        hex_cal.SetLayer(12)
        key = gridsKey[j]
        indices = [j]
        for i in range(k):
            bhex_ids = hex_cal.HexCellBoudary(key, i+1)
            inter = set(gridsKey).intersection(bhex_ids)
            indices_add = [grids_to_id[x] for x in inter]
            if len(indices_add) > 0:
               indices = indices + indices_add
        
        for p in indices:
            key = gridsKey[p]
            indices_1 = [p]
            for i in range(k):
                bhex_ids = hex_cal.HexCellBoudary(key, i+1)
                inter = set(gridsKey).intersection(bhex_ids)
                indices_add = [grids_to_id[x] for x in inter]
                if len(indices_add) > 0:
                   indices_1 = indices_1 + indices_add
            index = indices_1.index(j)
            A_2[j, np.sum(indice_count[:p])+index] = 1
            O_2[j, np.sum(indice_count[:p])+index] = w * cost_norm[j,p]

    obj = cvx.Minimize(C.T*S + cost * gamma)

    constr = [A_2 * gamma + S >= o_t.reshape(-1, 1), A_2 * gamma - S <= o_t.reshape(-1, 1), 0 <= gamma, 0 <= S, A_1 * gamma == d_t.reshape(-1, 1)]
    prob = cvx.Problem(obj, constr)
    d = prob.solve(solver=cvx.GLPK)
    return d


metric = np.zeros((_TN, ))
for j in range(_TN):
    metric[j] = global_transport(order_count_full[:,j], cur_driver_count[:, j], gridsKey, grids_to_id, 1, 0.4)
    print(j)

np.savez('../data/output/area5/area5_{}_metric.npz'.format(date), metric=metric)
