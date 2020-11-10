# -*- coding: utf-8 -*-
"""
格子计算算法测试用例

Created by ZhangZhen on 16/9/14.
Copyright © 2016年 didi. All rights reserved.
"""

from dgcalculator import Calculator
from dgtypes import GeoCoord

if __name__ == "__main__":
    cal = Calculator()
    cal.SetLayer(13)
    #通过坐标获取格子
    print cal.HexCellKey(GeoCoord(0, -90))
    #print cal.HexCellNeighbor("OL13F2i12288j0", 1)
    #获取邻域
    print cal.HexCellNeighbor("OL13F1i10774j1514", 1)
    #获取边界，第几层
    print cal.HexCellBoudary("OL13F3i211j12077", 10)
    #获取顶点及中心点
    vs, c = cal.HexCellVertexesAndCenter("OL13F2i12288j0")
    for v in vs:
        print v.lat, v.lng
    print c.lat, c.lng
