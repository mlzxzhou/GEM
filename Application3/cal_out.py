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


_T = 6  # 60 min
_TD = 60  # 10 min
_TN = int(24*3600/_TD)  # 144


with open('data/raw/area5/grids_to_id.pickle', 'rb') as f:
   grids_to_id = pickle.load(f)

grids_to_id_s = sorted(grids_to_id.items(), key=operator.itemgetter(1))
gridsKey=[]
for i in range(len(grids_to_id)):
    gridsKey.append(grids_to_id_s[i][0])

date_start = 20181112
a1 = []
b = []
c = []
d = []
e = []
data_dir = 'data/processed/area5/'
output_dir = 'data/output/area5/'
metric_dir = 'data/ab_test/area5/'
for i in range(14):
    date_on = date_start+i
    order = np.load(data_dir + 'area5_' + str(date_on) + '_order.npz')
    order_count_full = order['order_count_full']
    order_count_finish = order['order_count_finish']
    driver = np.load(data_dir + 'area5_' + str(date_on) + '_driver.npz')
    cur_driver_count = driver['cur_driver_count']
    cost_norm = driver['cost_norm']
    L1 = np.absolute(order_count_full - cur_driver_count)
    L2 = order_count_finish - cur_driver_count
    L2[L2 < 0] = 0
    a1.append(np.sum(L1 - L2, axis = 0))
    metric = np.load(output_dir + 'area5_' + str(date_on) + '_metric.npz')
    b.append(metric['metric'])
    c.append(np.sum(order_count_finish,axis=0)/np.sum(order_count_full,axis=0))
    d.append(np.sum(order_count_full, axis=0))
    e.append(np.sum(np.sum(cur_driver_count, axis=0)))
a_1 = np.asarray(a1).reshape(1440*14,1)
b_1 = np.asarray(b).reshape(1440*14,1)
c_1 = np.asarray(c).reshape(1440*14,1)
d_1 = np.asarray(d).reshape(1440*14,1)
e_1 = np.asarray(e).reshape(1440*14,1)
out = np.concatenate((a_1,b_1, c_1),axis=1)

np.save(metric_dir + 'out0_new.npy',out)

date_start = 20181203
a1 = []
b = []
c = []
for i in range(14):
    date_on = date_start + i
    order = np.load(data_dir + 'area5_' + str(date_on) + '_order.npz')
    order_count_full = order['order_count_full']
    order_count_finish = order['order_count_finish']
    driver = np.load(data_dir + 'area5_' + str(date_on) + '_driver.npz')
    cur_driver_count = driver['cur_driver_count']
    cost_norm = driver['cost_norm']
    L1 = np.absolute(order_count_full - cur_driver_count)
    L2 = order_count_finish - cur_driver_count
    L2[L2 < 0] = 0
    a1.append(np.sum(L1 - L2, axis=0))
    metric = np.load(output_dir + 'area5_' + str(date_on) + '_metric.npz')
    b.append(metric['metric'])
    c.append(np.sum(order_count_finish, axis=0) / np.sum(order_count_full, axis=0))
    d.append(np.sum(order_count_full, axis=0))
    e.append(np.sum(np.sum(cur_driver_count, axis=0)))
a_1 = np.asarray(a1).reshape(1440 * 14, 1)
b_1 = np.asarray(b).reshape(1440 * 14, 1)
c_1 = np.asarray(c).reshape(1440 * 14, 1)
d_1 = np.asarray(d).reshape(1440 * 14, 1)
e_1 = np.asarray(e).reshape(1440 * 14, 1)
out = np.concatenate((a_1, b_1, c_1), axis=1)

np.save(metric_dir + 'out1_new.npy',out)
