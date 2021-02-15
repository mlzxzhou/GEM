# -*- coding: utf-8 -*-
"""
Grid calculation algorithm test case

Created by ZhangZhen on 16/9/14.
Copyright © 2016年 didi. All rights reserved.
"""

from dgcalculator import Calculator
from dgtypes import GeoCoord

if __name__ == "__main__":
    cal = Calculator()
    cal.SetLayer(13)
    #Get grid by coordinates
    print cal.HexCellKey(GeoCoord(0, -90))
    #print cal.HexCellNeighbor("OL13F2i12288j0", 1)
    #Get neighborhood
    print cal.HexCellNeighbor("OL13F1i10774j1514", 1)
    #Get boundary, which layer
    print cal.HexCellBoudary("OL13F3i211j12077", 10)
    #Get vertex and center point
    vs, c = cal.HexCellVertexesAndCenter("OL13F2i12288j0")
    for v in vs:
        print v.lat, v.lng
    print c.lat, c.lng
