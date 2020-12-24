# -*- coding: utf-8 -*-
"""
External interface of Grid calculation algorithm

Created by ZhangZhen on 16/9/14.
Copyright © 2016 didi. All rights reserved.
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

    #Get key by coordinates
    def HexCellKey(self, geoPos):
        index = self.octEarth.HexIndex(geoPos, True)
        key = self.keyCoder.Encode(index)
        return key

    #Get all the grids in and below the kth layer
    def HexCellNeighbor(self, hexKey, k):
        index = self.keyCoder.Decode(hexKey)
        neighbor = self.octEarth.NearestNeighbor(index, k)
        neighborkeys = self.keyCoder.Encodes(neighbor)
        return neighborkeys

    #Get the grid list of the kth layer
    def HexCellBoudary(self, hexKey, k):
        index = self.keyCoder.Decode(hexKey)
        boudary = self.octEarth.NeighborLayer(index, k)
        boudarykeys = self.keyCoder.Encodes(boudary)
        return boudarykeys

    #Check vertices and center points by grid ID. The last one is the center point
    #Illegal return of grid ID [], NULL
    def HexCellVertexesAndCenter(self, hexKey):
        dgrid = self.keyCoder.Decode(hexKey)
        if not dgrid:
            return [], None
        hcg = HexCellGenerator()
        hcg.SetLayer(dgrid.layer)
        vertexes = hcg.HexCellVertexes(dgrid)
        center = hcg.HexCellCenter(dgrid)
        return vertexes, center
