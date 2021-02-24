# -*- coding: utf-8 -*-
"""
key encoding

Created by ZhangZhen on 16/9/13.
Copyright © 2016 didi. All rights reserved.
"""

import math
import sys
from .dgtypes import ObliqueCoord, FaceIndexCoord, DGrid
from .hexpicker import HexPicker
from .d3coordor import D3Coordor

class OctEarth(object):
    def __init__(self):
        self.n = None
        self.cellLength = None
        self.layer = None
        self.hexPicker = HexPicker()
        self.d3Coord = D3Coordor()

    def isNearest(self, ii, jj):
        a = ii + jj/2
        b = jj + ii/2
        if a <= 0.5 and b <= 0.5:
            return True
        return False

    def SetLayer(self, layer):
        self.layer = layer
        self.n = int(3 * pow(2.0, (float)(layer-1)))

    def FaceID(self, geoPos):
        lat = geoPos.lat
        lon = geoPos.lng
        if lon >= 0:
            if lon <= 90:
                index = 0
            else:
                index = 1
        else:
            if lon <= -90:
                index = 2
            else:
                index = 3
        if lat < 0:
            index = index + 4
        return index

    def FacePos(self, geoPos):
        if geoPos.lng >= 0:
            if geoPos.lng > 90:
                geoPos.lng = geoPos.lng - 90
        else:
            if geoPos.lng <= -90:
                geoPos.lng = geoPos.lng + 180
            else:
                geoPos.lng = geoPos.lng + 90
        if geoPos.lat < 0:
            geoPos.lat = -geoPos.lat
        return geoPos

    def ObliqueCoord(self, geoPos):
        orthPos = self.d3Coord.GeoToOrth(geoPos)
        s = orthPos.x + orthPos.y + orthPos.z
        k = (s - 1) / s
        j = orthPos.x * float(1 - k) * float(self.n)
        i = orthPos.z * float(1 - k) * float(self.n)
        return ObliqueCoord(i, j, k)

    def FaceCoord(self, geoPos):
        coord = self.ObliqueCoord(geoPos)
        return FaceIndexCoord(coord.i, coord.j)

    def NearestIndex(self, index):
        i = math.floor(index.i)
        j = math.floor(index.j)
        ii = index.i - i
        jj = index.j - j
        if self.isNearest(ii, jj):
            fi = i
            fj = j
        elif self.isNearest(1-ii, 1-jj):
            fi = i + 1
            fj = j + 1
        elif ii > jj:
            fi = i + 1
            fj = j
        else:
            fi = i
            fj = j + 1
        return FaceIndexCoord(fi, fj)

    def HexIndex(self, geoPos, reduceSameIndex):
        frameIndex = self.FaceID(geoPos)
        geoPos = self.FacePos(geoPos)
        index = self.FaceCoord(geoPos)
        nstIndex = self.NearestIndex(index)
        hexIndex = DGrid(self.layer, frameIndex, int(nstIndex.i), int(nstIndex.j))
        if reduceSameIndex:
            hexIndex = self.AdjustEdgeHexIndex(hexIndex)
        return hexIndex

    def AdjustEdgeHexIndex(self, hexIndex):
        #South to North
        if hexIndex.i+hexIndex.j == int(self.n):
            if hexIndex.face > 3:
                hexIndex.face = hexIndex.face - 4
        #West to East
        if hexIndex.i == 0:
            hexIndex = self.hexPicker.MirrorDGrid(hexIndex, True, 1)
        #Polar vertex
        if hexIndex.i == 0 and hexIndex.j == 0:
            if hexIndex.face < 4:
                hexIndex.face = 0
            else:
                hexIndex.face = 4
        return hexIndex

    def EffectiveEarthNeighborK(self, k):
        if k < 0:
            k = -k
        k = k % (4 * self.n)
        if k > 2*self.n:
            k = 4*self.n - k
        return k

    def UnfoldNeighbor(self, hexIndex, k):
        neighbor = []
        if k <= 0:
            return neighbor
        kk = int(k)
        ii = int(k)
        for jj in range(0, -kk-1, -1):
            neighbor.append(DGrid(hexIndex.layer, hexIndex.face, hexIndex.i+ii, hexIndex.j+jj))
        jj = -kk
        for ii in range(kk-1, -1, -1):
            neighbor.append(DGrid(hexIndex.layer, hexIndex.face, hexIndex.i+ii, hexIndex.j+jj))
        for ii in range(-1, 1-kk-1, -1):
            jj = -kk - ii
            neighbor.append(DGrid(hexIndex.layer, hexIndex.face, hexIndex.i+ii, hexIndex.j+jj))
        ii = -kk
        for jj in range(0, kk+1):
            neighbor.append(DGrid(hexIndex.layer, hexIndex.face, hexIndex.i+ii, hexIndex.j+jj))
        jj = kk
        for ii in range(1-kk, 1):
            neighbor.append(DGrid(hexIndex.layer, hexIndex.face, hexIndex.i+ii, hexIndex.j+jj))
        for ii in range(1, kk):
            jj = kk - ii
            neighbor.append(DGrid(hexIndex.layer, hexIndex.face, hexIndex.i+ii, hexIndex.j+jj))
        return neighbor

    def TopoFaceID(self, baseFace, topoFace, inverse):
        if baseFace == 0:
            topoInd = topoFace
        elif baseFace == 4:
            topoInd = self.hexPicker.FlipFaceId(topoFace)
        elif baseFace == 1:
            topoInd = self.hexPicker.RotateFaceInd(topoFace, inverse, 1)
        elif baseFace == 5:
            topoInd = self.hexPicker.FlipFaceId(topoFace)
            topoInd = self.hexPicker.RotateFaceInd(topoInd, inverse, 1)
        elif baseFace == 2:
            topoInd = self.hexPicker.RotateFaceInd(topoFace, True, 2)
        elif baseFace == 6:
            topoInd = self.hexPicker.FlipFaceId(topoFace)
            topoInd = self.hexPicker.RotateFaceInd(topoInd, True, 2)
        elif baseFace == 3:
            topoInd = self.hexPicker.RotateFaceInd(topoFace, not inverse, 1)
        elif baseFace == 7:
            topoInd = self.hexPicker.FlipFaceId(topoFace)
            topoInd = self.hexPicker.RotateFaceInd(topoInd, not inverse, 1)
        else:
            topoInd = -1
        return topoInd

    def FoldTopoFaceID(self, unfoldHexInde):
        i = unfoldHexInde.i
        j = unfoldHexInde.j
        n = int(self.n)
        if i >= 0 and i <= n and j >= 0 and j <= n:
            if i+j <= n:
                return 0
            else:
                return 4
        if i > 0 and i <= n and j < 0 and j >= -n:
            if i+j >= 0:
                return 3
            else:
                return 21
        if j > 0 and j <= n and i < 0 and i > -n:
            if i+j >= 0:
                return 1
            else:
                return 22
        if i <= 0 and i >= -n and j <= 0 and j >= -n and i+j >= -n:
            return 20
        if i > n and i <= 2*n and j <= 0 and j >= -n:
            if i+j < n:
                return 71
            else:
                return 70
        if i > n and i < 2*n and j > 0 and j < n and i+j <= 2*n:
            return 72
        if j > n and j <= 2*n and i <= 0 and i >= -n:
            if (i+j) < n:
                return 51
            else:
                return 50
        if j > n and j < 2*n and i > 0 and i < n and i+j <= 2*n:
            return 52
        return -1

    def FoldHexIndex(self, index):
        faceID = self.FoldTopoFaceID(index)
        fldIndex = DGrid(index.layer, index.face, index.i, index.j)
        n = int(self.n)
        if faceID == -1:
            fldIndex.face = faceID
            return fldIndex
        elif faceID == 0:
            pass
        elif faceID == 4:
            fldIndex.i = n - index.j
            fldIndex.j = n - index.i
        elif faceID == 1:
            fldIndex.i = index.i + index.j
            fldIndex.j = -index.i
        elif faceID == 50:
            fldIndex.i = 2*n - index.j
            fldIndex.j = -index.i
            faceID = 5
        elif faceID == 51:
            fldIndex.i = index.i + n
            fldIndex.j = n - index.i - index.j
            faceID = 5
        elif faceID == 52:
            fldIndex.i = 2*n - index.i - index.j
            fldIndex.j = index.j - n
            faceID = 5
        elif faceID == 3:
            fldIndex.i = -index.j
            fldIndex.j = index.i + index.j
        elif faceID == 70:
            fldIndex.i = -index.j
            fldIndex.j = 2*n - index.i
            faceID = 7
        elif faceID == 71:
            fldIndex.i = n - index.i - index.j
            fldIndex.j = index.j + n
            faceID = 7
        elif faceID == 72:
            fldIndex.i = index.i - n
            fldIndex.j = 2 * n - index.i - index.j
            faceID = 7
        elif faceID == 20:
            fldIndex.i = -index.i
            fldIndex.j = -index.j
            faceID = 2
        elif faceID == 21:
            fldIndex.i = -index.i - index.j
            fldIndex.j = index.i
            faceID = 2
        elif faceID == 22:
            fldIndex.i = index.j
            fldIndex.j = -index.i - index.j
            faceID = 2
        fldFaceInd = self.TopoFaceID(index.face, faceID, True)
        fldIndex.face = fldFaceInd
        return fldIndex

    def NeighborLayer(self, hexIndex, k):
        k = self.EffectiveEarthNeighborK(k)
        if k > self.n:
            hexIndex = self.hexPicker.SymmetryDGrid(hexIndex)
            symK = 2*self.n - k
            return self.NeighborLayer(hexIndex, symK)
        neighbor = []
        if k == 0:
            neighbor.append(DGrid(hexIndex.layer, hexIndex.face, hexIndex.i, hexIndex.j))
            return neighbor
        ufldNeighbor = self.UnfoldNeighbor(hexIndex, k)
        if hexIndex.i > int(k) and hexIndex.j > int(k) and (int(self.n-hexIndex.i-hexIndex.j)) > int(k):
            return ufldNeighbor
        for v in ufldNeighbor:
            fldIndex = self.FoldHexIndex(v)
            if fldIndex.face != -1:
                fldIndex = self.AdjustEdgeHexIndex(fldIndex)
                neighbor.append(fldIndex)
        return self.hexPicker.UniqueIndex(neighbor)

    def NearestNeighbor(self, hexIndex, k):
        newK = self.EffectiveEarthNeighborK(k)
        neighbor = []
        for i in range(newK+1):
            iNeighbor = self.NeighborLayer(hexIndex, i)
            for v in iNeighbor:
                neighbor.append(v)
        return self.hexPicker.UniqueIndex(neighbor)
