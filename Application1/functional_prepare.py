from __future__ import division
import os
import sys
import cvxpy as cvx
import numpy as np
import scipy.sparse as sp
import timeit
from multiprocessing import Pool
import pandas as pd
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
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
from typing import Any

_T = 6  # 60 min
_TD = 10 * 60  # 10 min
_TN = 144  # 144

################################
### Load data and processing ###
################################

index = [9, 171, 13, 299, 8, 262, 65]

### Wasserstein Distance ###
def wd_coherence_dual(o_t,d_t,cost_norm):
    O_t = np.sum(o_t)
    D_t = np.sum(d_t)
    index = (o_t > 0) | (d_t > 0)
    b_1 = o_t[index] / O_t
    b_2 = d_t[index] / D_t
    b = np.concatenate((b_1, b_2))
    var_num = np.sum(index)
    y = cvx.Variable(var_num * 2, 1)
    obj = cvx.Maximize(b.T * y)
    
    A_1 = np.zeros((var_num, var_num * var_num))
    for p in range(var_num):
        A_1[p, (var_num * p):(var_num * (p + 1))] = np.ones((1, var_num))
    A_2 = np.zeros((var_num, var_num * var_num))
    for p in range(var_num):
        for q in range(var_num):
            A_2[p, (q * var_num + p)] = 1
    A = np.concatenate((A_1, A_2))
    C = cost_norm[index, :][:, index].reshape((var_num * var_num, 1))
    constr = [A.T * y <= C]
    prob = cvx.Problem(obj, constr)
    d = prob.solve(solver=cvx.SCS)
    return d


####### Predict answer rate ########

### 10 min metric ###
response = np.zeros(4464, )
metric = np.zeros((4464, 4))

for i in range(10):
    # Load order, driver data #
    basetime = 20180421 + i
    data_dir = 'data/processed/area5/'

    # Load order data #
    order_dir = data_dir + 'area5_' + str(basetime) + '_order.npz'
    order_count = np.load(order_dir)
    order_count_full = order_count['order_count_full']
    order_count_finish = order_count['order_count_finish']

    # Load driver data #
    driver_dir = data_dir + 'area5_' + str(basetime) + '_driver.npz'
    driver_count = np.load(driver_dir)
    cur_driver_count = driver_count['cur_driver_count']
    cost_norm = driver_count['cost_norm']

    # Load metric data #
    metric_dir = 'data/output/area5/area5_' + str(basetime) + '_metric.npz'
    metric_data = np.load(metric_dir)
    ratio = metric_data['ratio'].T
    global_metric = metric_data['global_metric']


    metric_w_dir = 'data/output/area5/area5_' + str(basetime) + '_metric_1.npz'
    metric_w_data = np.load(metric_w_dir)
    global_metric_w = metric_w_data['global_metric_w']

    for j in range(144):
        order = order_count_full[:, (10 * j):(10 * j + 10)]
        order_finish = order_count_finish[:, (10 * j):(10 * j + 10)]
        driver = cur_driver_count[:, (10 * j):(10 * j + 10)]
        ratio1 = ratio[(10 * j):(10 * j + 10), :].T
        global_metric_1 = global_metric[(10 * j):(10 * j + 10)].T
        global_metric_w_1 = global_metric_w[(10 * j):(10 * j + 10)].T

        response[i * 144 + j] = np.sum(order_finish) / np.sum(order)
        
        ### Hellinger Distance ###
        order_norm = np.sqrt(order / np.sum(order))
        driver_norm = np.sqrt(driver / np.sum(driver))
        metric[i * 144 + j, 0] = np.sqrt(np.sum((order_norm - driver_norm) ** 2)) / np.sqrt(2)
        
        ### L2 Distance ###
        metric[i * 144 + j, 1] = np.log(np.sqrt(np.sum((order - driver) ** 2)) / np.sqrt(2))
        
        ### Wasserstein Distance ###
        metric[i * 144 + j, 2] = np.sum(np.sum(order, axis=0) * global_metric_w_1) / np.sum(order)

        ### GLobal Ratio ###
        metric[i * 144 + j, 3] = np.sum(ratio1 * order) / np.sum(order)


for i in range(21):
    # Load order, driver data #
    basetime = 20180501 + i
    data_dir = 'data/processed/area5/'

    # Load order data #
    order_dir = data_dir + 'area5_' + str(basetime) + '_order.npz'
    order_count = np.load(order_dir)
    order_count_full = order_count['order_count_full']
    order_count_finish = order_count['order_count_finish']

    # Load driver data #
    driver_dir = data_dir + 'area5_' + str(basetime) + '_driver.npz'
    driver_count = np.load(driver_dir)
    cur_driver_count = driver_count['cur_driver_count']
    cost_norm = driver_count['cost_norm']

    # Load metric data #
    metric_dir = 'data/output/area5/area5_' + str(basetime) + '_metric.npz'
    metric_data = np.load(metric_dir)
    ratio = metric_data['ratio'].T
    global_metric = metric_data['global_metric']

    metric_w_dir = 'data/output/area5/area5_' + str(basetime) + '_metric1.npz'
    metric_w_data = np.load(metric_w_dir)
    global_metric_w = metric_w_data['global_metric_w']

    for j in range(144):
        order = order_count_full[:, (10 * j):(10 * j + 10)]
        order_finish = order_count_finish[:, (10 * j):(10 * j + 10)]
        driver = cur_driver_count[:, (10 * j):(10 * j + 10)]
        ratio1 = ratio[(10 * j):(10 * j + 10), :].T
        global_metric_1 = global_metric[(10 * j):(10 * j + 10)].T
        global_metric_w_1 = global_metric_w[(10 * j):(10 * j + 10)].T
        response[(i + 10) * 144 + j] = np.sum(order_finish) / np.sum(order)
        
        ### Hellinger Distance ###
        order_norm = np.sqrt(order / np.sum(order))
        driver_norm = np.sqrt(driver / np.sum(driver))
        metric[(i + 10) * 144 + j, 0] = np.sqrt(np.sum((order_norm - driver_norm) ** 2)) / np.sqrt(2)
        
        ### L2 Distance ###
        metric[(i + 10) * 144 + j, 1] = np.log(np.sqrt(np.sum((order - driver) ** 2)) / np.sqrt(2))
        
        ### Wasserstein Distance ###
        metric[(i + 10) * 144 + j, 2] = np.sum(np.sum(order, axis=0) * global_metric_w_1) / np.sum(order)

        ### GLobal Ratio ###
        metric[(i + 10) * 144 + j, 3] = np.sum(ratio1 * order) / np.sum(order)

np.save('data/prediction/area5/response_10.npy', response)
np.save('data/prediction/area5/metric_10.npy', metric)

#### Build y (t + 1) ####
y = response[864:]
x_1 = np.zeros((3600, 10, 4))
for i in range(3600):
    x_1[i, :, :] = metric[(854 + i):(864 + i), :]

x_2 = np.zeros((3600, 5, 4))
for i in range(3600):
    for j in range(5):
        x_2[i, (4 - j), :] = metric[(864 + i - 144 * (j + 1)), :]

data = np.column_stack([y, x_1[:, :, 1], x_2[:, :, 0], x_1[:, :, 1], x_2[:, :, 1], x_1[:, :, 2], x_2[:, :, 2], x_1[:, :, 3], x_2[:, :, 3]])

np.save('data/prediction/area5/t_1/data.npy', data)

#### Build y (t + 6) ####
y = response[864:]
x_1 = np.zeros((3600, 10, 4))
for i in range(3600):
    x_1[i, :, :] = metric[(849 + i):(859 + i), :]

x_2 = np.zeros((3600, 5, 4))
for i in range(3600):
    for j in range(5):
        x_2[i, (4 - j), :] = metric[(864 + i - 144 * (j + 1)), :]

data = np.column_stack([y, x_1[:, :, 1], x_2[:, :, 0], x_1[:, :, 1], x_2[:, :, 1], x_1[:, :, 2], x_2[:, :, 2], x_1[:, :, 3], x_2[:, :, 3]])
np.save('../data/prediction/area5/t_6/data.npy', data)




