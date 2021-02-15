# -*- coding: utf-8 -*-
"""
Selector

Created by ZhangZhen on 16/9/13.
Copyright © 2016 didi. All rights reserved.
"""
import os
import sys

ROOTDIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0,ROOTDIR)

import dgtypes
import utils

KEYLEN=4

#Selector Single column
@utils.Singleton
class HexPicker(object):
    def __init__(self):
        self.keylen = KEYLEN

    def ExchangeIJ(self, dg):
        tmp = dg.i
        dg.i = dg.j
        dg.j = tmp
        return dg

    def FlipFaceId(self, faceID):
        if faceID > 3:
            faceID = faceID - 4
        elif faceID < 4:
            faceID = faceID + 4
        return faceID

    def FlipDGrid(self, dg):
        return self.FlipFaceId(dg.face)

    def RotateFaceInd(self, faceInd, westToEast, nTimes):
        if nTimes == 1:
            if westToEast:
                faceInd = faceInd + 1
                if faceInd == 4:
                    faceInd = 0
                
                if faceInd == 8:
                    faceInd = 4
            else:
                faceInd = faceInd - 1
                if faceInd == -1:
                    faceInd = 3
                elif faceInd == 3:
                    faceInd = 7
        else:
            for i in range(nTimes):
                faceInd = self.RotateFaceInd(faceInd, westToEast, 1)
        return faceInd

    def RotateDGrid(self, dg, westToEast, nTimes):
        faceInd = self.RotateFaceInd(dg.face, westToEast, nTimes)
        dg.face = faceInd
        return dg
    
    def MirrorFaceInd(self, faceInd, westToEast, nTimes):
        return self.RotateFaceInd(faceInd, westToEast, nTimes)

    def MirrorDGrid(self, dg, westToEast, nTimes):
        dg = self.RotateDGrid(dg, westToEast, nTimes)
        if nTimes%2 == 1:
            dg = self.ExchangeIJ(dg)
        return dg
    
    def SymmetryFaceInd(self, faceInd):
        faceInd = self.FlipFaceId(faceInd)
        return self.RotateFaceInd(faceInd, true, 2)
    
    def SymmetryDGrid(self, dg):
        return self.SymmetryFaceInd(dg.face)

    def UniqueIndex(self, indexes):
        #List to be generated
        newIndexes = []
        #Generate a collection
        s = {}
        for v in indexes:
            key = v.DGridStr()
            if not s.has_key(key):
                newIndexes.append(v)
                s[key] = True
        return newIndexes
