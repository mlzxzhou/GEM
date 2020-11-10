# -*- coding: utf-8 -*-
"""
格子计算算法对外接口

Created by ZhangZhen on 16/9/14.
Copyright © 2016年 didi. All rights reserved.
"""
import sys
sys.path.insert(0,'')

from .octearth import OctEarth
from .keycoder import KeyCoder
from .hexcell import HexCellGenerator

class Calculator(object):
    def __init__(self):
        self.keyCoder = KeyCoder()
        self.octEarth = OctEarth()

    def SetLayer(self, layer):
        self.octEarth.SetLayer(layer)

    #通过坐标获取key
    def HexCellKey(self, geoPos):
        index = self.octEarth.HexIndex(geoPos, True)
        key = self.keyCoder.Encode(index)
        return key

    #获取第k层及以内的所有格子
    def HexCellNeighbor(self, hexKey, k):
        index = self.keyCoder.Decode(hexKey)
        neighbor = self.octEarth.NearestNeighbor(index, k)
        neighborkeys = self.keyCoder.Encodes(neighbor)
        return neighborkeys

    #获取第k层的格子列表
    def HexCellBoudary(self, hexKey, k):
        index = self.keyCoder.Decode(hexKey)
        boudary = self.octEarth.NeighborLayer(index, k)
        boudarykeys = self.keyCoder.Encodes(boudary)
        return boudarykeys

    #通过格子ID查顶点和中心点 最后一个是中心点
    #格子ID非法返回[], NULL
    def HexCellVertexesAndCenter(self, hexKey):
        dgrid = self.keyCoder.Decode(hexKey)
        if not dgrid:
            return [], None
        hcg = HexCellGenerator()
        hcg.SetLayer(dgrid.layer)
        vertexes = hcg.HexCellVertexes(dgrid)
        center = hcg.HexCellCenter(dgrid)
        return vertexes, center
