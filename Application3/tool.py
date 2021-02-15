#coding=utf-8
import math
from math import asin, sin, cos
import time
import sys
import os
import os.path
import errno
import logging
from multiprocessing import Pool
import cPickle as pickle


ROOTDIR = os.path.abspath(os.path.dirname(__file__)) + '/../../'
sys.path.append(os.path.join(ROOTDIR, 'thirdparty/sdslib/Python/'))
from dgckernel.dgcalculator import Calculator
from dgckernel.dgtypes import GeoCoord

sys.path.append(os.path.join(ROOTDIR, 'thirdparty/multiprocessing-logging/'))
from multiprocessing_logging import install_mp_handler

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_ch = logging.StreamHandler()
logger_ch.setLevel(logging.DEBUG)
logger_ch.setFormatter(logging.Formatter(
    '%(asctime)s[%(levelname)s][%(filename)s:%(lineno)s:%(funcName)s]||%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'))
logger.addHandler(logger_ch)
install_mp_handler()


BASETIME = 946656000  # date -d '2000-01-01 00:00:00' +%s
# Non-workday
NONWORKDAY=[
    20161203, 20161204, 20161210, 20161211, 20161217, 20161218, 20161224, 20161225, 20161231,
    20170101, 20170102, 20170107, 20170108, 20170114, 20170115, 20170121, 20170122, 20170127, 20170128, 20170129, 20170130, 20170131,
    20170201, 20170202, 20170205, 20170211, 20170212, 20170218, 20170219, 20170225, 20170226,
    20170304, 20170305, 20170311, 20170312, 20170318, 20170319, 20170325, 20170326,

    20170603, 20170604, 20170610, 20170611, 20170617, 20170618, 20170624, 20170625,
    20170701, 20170702, 20170708, 20170709, 20170715, 20170716, 20170722, 20170723, 20170729, 20170730,
    20170805, 20170806, 20170812, 20170813, 20170819, 20170820, 20170826, 20170827,
    20170902, 20170903, 20170909, 20170910, 20170916, 20170917, 20170923, 20170924, 20170930,
    ]

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def safe_open_w(path, _):
    ''' Open "path" for writing, creating any parent directories as needed.
    '''
    mkdir_p(os.path.dirname(path))
    return open(path, 'w')

'''
Calc straight line distance in meters.
'''
def cal_distance(lng1, lat1, lng2, lat2):
    PI = 3.14159265
    EARTH_RADIUS = 6378137
    RAD = (PI/180.0)

    radLat1 = lat1 * RAD
    radLat2 = lat2 * RAD
    a = radLat1 - radLat2
    b = (lng1 - lng2) * RAD
    s = 2 * asin((sin(a / 2)**2 + cos(radLat1) * cos(radLat2) * (sin(b / 2)**2))**0.5)
    s = s * EARTH_RADIUS
    return s


def cal_distance_tuple(argv):
    return cal_distance(*argv)


def op_cal_distance(olng_olat, dlng_dlat, distance_limit):
    '''
    return [(oid, did, dist), ...] [(1,8,2342), (3,2,1233),...]
    '''
    out_dist_list = []

    lng_delta = 0.1
    lat_delta = 0.1
    lng_gap = 0.025
    lat_gap = 0.025
    lng_lat_key_map = {}
    for did, (dlng, dlat) in enumerate(dlng_dlat):
        key = (int(dlng / lng_delta), int(dlat / lat_delta))
        lng_lat_key_map.setdefault(key, []).append(did)
    for oid, (olng, olat) in enumerate(olng_olat):
        mm_key = (int(olng / lng_delta), int(olat / lat_delta))
        ll_key = (int((olng-lng_gap) / lng_delta), int((olat-lat_gap) / lat_delta))
        lu_key = (int((olng-lng_gap) / lng_delta), int((olat+lat_gap) / lat_delta))
        ul_key = (int((olng+lng_gap) / lng_delta), int((olat-lat_gap) / lat_delta))
        uu_key = (int((olng+lng_gap) / lng_delta), int((olat+lat_gap) / lat_delta))
        for okey in set((mm_key, ll_key, lu_key, ul_key, uu_key)):
            dlist = lng_lat_key_map.get(okey, None)
            if dlist is None: continue
            for did in dlist:
                (dlng, dlat) = dlng_dlat[did]
                dist = cal_distance(olng, olat, dlng, dlat)
                if dist >= distance_limit: continue
                out_dist_list.append((oid, did, dist))
    return out_dist_list


def op_cal_distance_old(olng_olat, dlng_dlat, distance_limit, obase_idx=0, dbase_idx=0):
    '''
    return [(oid, did, dist), ...] [(1,8,2342), (3,2,1233),...]
    '''
    out_dist_list = []
    for oid, o in enumerate(olng_olat):
        for did, d in enumerate(dlng_dlat):
            dist = cal_distance(o[0], o[1], d[0], d[1])
            if dist >= distance_limit: continue
            out_dist_list.append((oid+obase_idx, did+dbase_idx, dist))

    return out_dist_list


def mp_cal_distance(olng_olat, dlng_dlat, distance_limit):
    '''
    return [(1,8,2342), (3,2,1233),...]
    '''
    olen = len(olng_olat)
    dlen = len(dlng_dlat)
    if olen == 0 or dlen == 0: return []
    od_list = [None] * (olen * dlen)
    for oid, o in enumerate(olng_olat):
        for did, d in enumerate(dlng_dlat):
            od_list[oid*dlen + did] = (o[0], o[1], d[0], d[1])

    process_core = 30
    pool = Pool(processes=process_core)
    chunksize = (len(od_list) + process_core - 1) / process_core
    full_dist_list = pool.map(cal_distance_tuple, od_list, chunksize)
    pool.close()
    pool.join()

    out_dist_list = [(i / dlen, i % dlen, dist)
                     for i, dist in enumerate(full_dist_list)
                     if dist < distance_limit]

    return out_dist_list

def tid_to_timestamp(date, tid):
    # independent of system time
    date_seconds_diff = (time.mktime(time.strptime(str(date), '%Y%m%d'))
                         - time.mktime(time.strptime('20000101', '%Y%m%d')))
    ret = BASETIME + date_seconds_diff + 4*3600 + tid*600
    return int(ret)

def timestamp_to_tid(timestamp):
    t = timestamp - BASETIME
    # 04:00->0, 04:10->1, ...
    return ((t - 4*3600) % (24*3600))/600

def str2value(s):
    try:
        r = int(s)
    except ValueError:
        try:
            r = float(s)
        except ValueError:
            r = s
            if 'True' == r:
                r = True
            if 'False' == r:
                r = False
    return r

def cal_grid(lng, lat):
    cal = Calculator()
    cal.SetLayer(13)
    return cal.HexCellKey(GeoCoord(lat, lng))

def cal_grid_loc(g):
    cal = Calculator()
    cal.SetLayer(13)
    _, c = cal.HexCellVertexesAndCenter(g)
    return c.lng, c.lat


def vfunc_trans_pkl_to_txt(inputfname, outputfname=None):
    with open(inputfname, 'r') as f:
        vfunc_dict = pickle.load(f)
    vfunc_len = vfunc_dict['vfunc_len']
    vfunc = vfunc_dict['vfunc']
    grids = vfunc_dict['grids']
    grid_n = len(grids)
    if outputfname is None: outputfname = inputfname.replace('.pkl', '.txt')
    with open(outputfname, 'w') as f:
        for idx, grid in enumerate(grids):
            for tidx in range(144):
                for tt in range(6):
                    line = ([grid, str(tidx), str(tt)] +
                            ['%0.1f'%e for e in vfunc_len[tidx][tt*grid_n+idx]] +
                            ['%0.4f'%e for e in vfunc[tidx][tt*grid_n+idx]])
                    line = ' '.join(line) + '\n'
                    f.write(line)

def op_cal_distance_test():
    test_len = 2000
    with open('../../data/sim_data/sim_get_order_20171016_20171105_area5') as f:
        '''
        area    begin_time  end_time    flng    flat    tlng    tlat    gmv answer
        40  1508083219  1508083879  117.654658  39.699772   117.6798    39.67047    12.8    0
        '''
        lng_lat = []
        f.readline()
        for i, line in enumerate(f):
            if i > test_len + 10: break
            r = line.strip().split('\t')
            r = [str2value(e) for e in r]
            lng_lat.append((r[3], r[4]))
    print 'load done'
    olng_olat = list(lng_lat[:test_len])
    dlng_dlat = list(lng_lat[2:2+test_len])

    time_b = time.time()
    output = op_cal_distance(olng_olat, dlng_dlat, distance_limit=2000)
    print time.time() - time_b
    print len(output)

    time_b = time.time()
    output = op_cal_distance_old(olng_olat, dlng_dlat, distance_limit=2000)
    print time.time() - time_b
    print len(output)


def dist_grid():
    lat1, lng1, lat2, lng2 = 39.964724,116.322056, 39.964724,116.322056
    for eps in range(1, 20):
        eps *= 0.02
        lat_dist = cal_distance(lng1, lat1, lng2, lat2 + eps)
        lng_dist = cal_distance(lng1, lat1, lng2 + eps, lat2)
        dist = cal_distance(lng1, lat1, lng2 + eps, lat2 + eps)
        print 'eps=%f||lat_dist=%d||lng_dist=%d||dist=%d||rate=%f||dist_per_lat=%f||dist_per_lnt=%f' % (
            eps, lat_dist, lng_dist, dist, lat_dist*1.0/lng_dist, lat_dist/eps, lng_dist/eps
        )


if __name__ == '__main__':
    test()
