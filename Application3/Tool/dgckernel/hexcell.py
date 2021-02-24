# -*- coding: utf-8 -*-
"""
Hexagonal cell

Created by ZhangZhen on 16/9/12
Copyright © 2016 didi. All rights reserved.
"""

from dgtypes import VERTEX0DD, VERTEX1RD, VERTEX2RU, VERTEX3UU, VERTEX4LU, VERTEX5LD
from dgtypes import OrthCoord, FaceIndexCoord, GeoCoord
from d3coordor import D3Coordor

class HexCellGenerator(object):
    def __init__(self):
        self.vertex_offset = {}
        self.D3Coord = D3Coordor()
        self.topAxis = OrthCoord(0, 1, 0)
        self.ONETHIRD = 1.0 / 3
        self.vertex_offset[VERTEX0DD] = FaceIndexCoord(self.ONETHIRD, self.ONETHIRD)
        self.vertex_offset[VERTEX1RD] = FaceIndexCoord(-self.ONETHIRD, 2*self.ONETHIRD)
        self.vertex_offset[VERTEX2RU] = FaceIndexCoord(-2*self.ONETHIRD, self.ONETHIRD)
        self.vertex_offset[VERTEX3UU] = FaceIndexCoord(-self.ONETHIRD, -self.ONETHIRD)
        self.vertex_offset[VERTEX4LU] = FaceIndexCoord(self.ONETHIRD, -2*self.ONETHIRD)
        self.vertex_offset[VERTEX5LD] = FaceIndexCoord(2*self.ONETHIRD, -self.ONETHIRD)

    def getOrthPos(self, faceIndex):
        x = faceIndex.i*self.leftAxis.x + faceIndex.j*self.rightAxis.x + self.topAxis.x
        y = faceIndex.i*self.leftAxis.y + faceIndex.j*self.rightAxis.y + self.topAxis.y
        z = faceIndex.i*self.leftAxis.z + faceIndex.j*self.rightAxis.z + self.topAxis.z
        return OrthCoord(x, y, z)
    

    def getFaceIndex(self, hexGrid, vertex_key):
        i = float(hexGrid.i) + self.vertex_offset[vertex_key].i
        j = float(hexGrid.j) + self.vertex_offset[vertex_key].j
        return FaceIndexCoord(i, j)

    def vertexes_polar(self, hexGrid):
        vertexes = [0]*4
        faceID = int(hexGrid.face)
        if hexGrid.i == 0 and hexGrid.j == 0:
            index = self.getFaceIndex(hexGrid, VERTEX0DD)
            orthPos = self.getOrthPos(index)
            geoPos = self.D3Coord.OrthToGeo(orthPos)
            geoPos = self.Topology(geoPos, faceID)
            vertexes[0] = GeoCoord(geoPos.lat, geoPos.lng)
            geoPos = self.Mirror(geoPos, True, 1)
            vertexes[1] = GeoCoord(geoPos.lat, geoPos.lng)
            geoPos = self.Mirror(geoPos, True, 1)
            vertexes[2] = GeoCoord(geoPos.lat, geoPos.lng)
            geoPos = self.Mirror(geoPos, True, 1)
            vertexes[3] = GeoCoord(geoPos.lat, geoPos.lng)
        elif hexGrid.i != 0:
            index = self.getFaceIndex(hexGrid, VERTEX2RU)
            orthPos = self.getOrthPos(index)
            geoPos = self.D3Coord.OrthToGeo(orthPos)
            geoPos = self.Topology(geoPos, faceID)
            vertexes[0] = GeoCoord(geoPos.lat, geoPos.lng)
            geoPos = self.Mirror(geoPos, False, 1)
            vertexes[1] = GeoCoord(geoPos.lat, geoPos.lng)
            geoPos = self.Flip(geoPos)
            vertexes[2] = GeoCoord(geoPos.lat, geoPos.lng)
            geoPos = self.Mirror(geoPos, True, 1)
            vertexes[3] = GeoCoord(geoPos.lat, geoPos.lng)
        else:
            index = self.getFaceIndex(hexGrid, VERTEX4LU)
            orthPos = self.getOrthPos(index)
            geoPos = self.D3Coord.OrthToGeo(orthPos)
            geoPos = self.Topology(geoPos, faceID)
            vertexes[0] = GeoCoord(geoPos.lat, geoPos.lng)
            geoPos = self.Flip(geoPos)
            vertexes[1] = GeoCoord(geoPos.lat, geoPos.lng)
            geoPos = self.Mirror(geoPos, True, 1)
            vertexes[2] = GeoCoord(geoPos.lat, geoPos.lng)
            geoPos = self.Flip(geoPos)
            vertexes[3] = GeoCoord(geoPos.lat, geoPos.lng)
        return vertexes
    

    def vertexes_edge(self, hexGrid):
        vertexes = [0]*6
        faceID = int(hexGrid.face)
        if hexGrid.j == 0:
            index = self.getFaceIndex(hexGrid, VERTEX0DD)
            orthPos = self.getOrthPos(index)
            geoPos = self.D3Coord.OrthToGeo(orthPos)
            geoPos = self.Topology(geoPos, faceID)
            vertexes[0] = GeoCoord(geoPos.lat, geoPos.lng)
            geoPos = self.Mirror(geoPos, False, 1)
            vertexes[5] = GeoCoord(geoPos.lat, geoPos.lng)

            index = self.getFaceIndex(hexGrid, VERTEX1RD)
            orthPos = self.getOrthPos(index)
            geoPos = self.D3Coord.OrthToGeo(orthPos)
            geoPos = self.Topology(geoPos, faceID)
            vertexes[1] = GeoCoord(geoPos.lat, geoPos.lng)
            geoPos = self.Mirror(geoPos, False, 1)
            vertexes[4] = GeoCoord(geoPos.lat, geoPos.lng)

            index = self.getFaceIndex(hexGrid, VERTEX2RU)
            orthPos = self.getOrthPos(index)
            geoPos = self.D3Coord.OrthToGeo(orthPos)
            geoPos = self.Topology(geoPos, faceID)
            vertexes[2] = GeoCoord(geoPos.lat, geoPos.lng)
            geoPos = self.Mirror(geoPos, False, 1)
            vertexes[3] = GeoCoord(geoPos.lat, geoPos.lng)
        elif hexGrid.i == 0:
            index = self.getFaceIndex(hexGrid, VERTEX0DD)
            orthPos = self.getOrthPos(index)
            geoPos = self.D3Coord.OrthToGeo(orthPos)
            geoPos = self.Topology(geoPos, faceID)
            vertexes[5] = GeoCoord(geoPos.lat, geoPos.lng)
            geoPos = self.Mirror(geoPos, True, 1)
            vertexes[0] = GeoCoord(geoPos.lat, geoPos.lng)

            index = self.getFaceIndex(hexGrid, VERTEX5LD)
            orthPos = self.getOrthPos(index)
            geoPos = self.D3Coord.OrthToGeo(orthPos)
            geoPos = self.Topology(geoPos, faceID)
            vertexes[4] = GeoCoord(geoPos.lat, geoPos.lng)
            geoPos = self.Mirror(geoPos, True, 1)
            vertexes[1] = GeoCoord(geoPos.lat, geoPos.lng)

            index = self.getFaceIndex(hexGrid, VERTEX4LU)
            orthPos = self.getOrthPos(index)
            geoPos = self.D3Coord.OrthToGeo(orthPos)
            geoPos = self.Topology(geoPos, faceID)
            vertexes[3] = GeoCoord(geoPos.lat, geoPos.lng)
            geoPos = self.Mirror(geoPos, True, 1)
            vertexes[2] = GeoCoord(geoPos.lat, geoPos.lng)
        else:
            index = self.getFaceIndex(hexGrid, VERTEX2RU)
            orthPos = self.getOrthPos(index)
            geoPos = self.D3Coord.OrthToGeo(orthPos)
            geoPos = self.Topology(geoPos, faceID)
            vertexes[2] = GeoCoord(geoPos.lat, geoPos.lng)
            geoPos = self.Flip(geoPos)
            vertexes[1] = GeoCoord(geoPos.lat, geoPos.lng)

            index = self.getFaceIndex(hexGrid, VERTEX3UU)
            orthPos = self.getOrthPos(index)
            geoPos = self.D3Coord.OrthToGeo(orthPos)
            geoPos = self.Topology(geoPos, faceID)
            vertexes[3] = GeoCoord(geoPos.lat, geoPos.lng)
            geoPos = self.Flip(geoPos)
            vertexes[0] = GeoCoord(geoPos.lat, geoPos.lng)

            index = self.getFaceIndex(hexGrid, VERTEX4LU)
            orthPos = self.getOrthPos(index)
            geoPos = self.D3Coord.OrthToGeo(orthPos)
            geoPos = self.Topology(geoPos, faceID)
            vertexes[4] = GeoCoord(geoPos.lat, geoPos.lng)
            geoPos = self.Flip(geoPos)
            vertexes[5] = GeoCoord(geoPos.lat, geoPos.lng)
        return vertexes
    

    def vertexes_inner(self, hexGrid):
        vertexes =  []
        faceID = int(hexGrid.face)
        VERLIST = [VERTEX0DD, VERTEX1RD, VERTEX2RU, VERTEX3UU, VERTEX4LU, VERTEX5LD]
        for k in VERLIST:
            index = self.getFaceIndex(hexGrid, k)
            orthPos = self.getOrthPos(index)
            geoPos = self.D3Coord.OrthToGeo(orthPos)
            geoPos = self.Topology(geoPos, faceID)
            vertexes.append(geoPos)
        return vertexes
    

    def SetLayer(self, layer):
        self.layer = layer
        self.N = int(3 * pow(2.0, (float)(layer-1)))
        self.leftAxis = OrthCoord(0, -1.0/(float)(self.N), 1.0/(float)(self.N))
        self.rightAxis = OrthCoord(1.0/(float)(self.N), -1.0/(float)(self.N), 0)
    
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
    
    def ExchangeIJ(self, geoPos):
        if geoPos.lng >= 0:
            if geoPos.lng < 90:
                geoPos.lng = 90 - geoPos.lng
            else:
                geoPos.lng = 270 - geoPos.lng
        else:
            if geoPos.lng > -90:
                geoPos.lng = -90 - geoPos.lng
            else:
                geoPos.lng = -270 - geoPos.lng
        return geoPos
    

    def Flip(self, geoPos):
        geoPos.lat = -geoPos.lat
        return geoPos
    

    def Rotate(self, geoPos, westToEast, nTimes):
        if nTimes == 1:
            if westToEast:
                geoPos.lng = geoPos.lng + 90
                if geoPos.lng > 180:
                    geoPos.lng = geoPos.lng - 360
            else:
                geoPos.lng = geoPos.lng - 90
                if geoPos.lng < -180:
                    geoPos.lng = geoPos.lng + 360
        else:
            for i in range(nTimes):
                geoPos = self.Rotate(geoPos, westToEast, 1)
        return geoPos

    def Mirror(self, geoPos, westToEast, nTimes):
        geoPos = self.Rotate(geoPos, westToEast, nTimes)
        if nTimes%2 == 1:
            geoPos = self.ExchangeIJ(geoPos)
        return geoPos

    def Symmetry(self, geoPos):
        geoPos = self.Flip(geoPos)
        return self.Rotate(geoPos, True, 2)

    def Topology(self, geoPos, faceID):
        if faceID >= 4:
            faceID = faceID - 4
            geoPos = self.Flip(geoPos)
        return self.Rotate(geoPos, True, faceID)
    
    def HexCellVertexes(self, hexGrid):
        if (hexGrid.i == 0 and hexGrid.j == 0) or (hexGrid.i == self.N and hexGrid.j == 0) or (hexGrid.i == 0 and hexGrid.j == self.N):
            return self.vertexes_polar(hexGrid)
        elif (hexGrid.i == 0 or hexGrid.j == 0) or (hexGrid.i+hexGrid.j == self.N):
            return self.vertexes_edge(hexGrid)
        else:
            return self.vertexes_inner(hexGrid)

    def HexCellCenter(self, hexGrid):
        index = FaceIndexCoord(float(hexGrid.i), float(hexGrid.j))
        orthPos = self.getOrthPos(index)
        geoPos = self.D3Coord.OrthToGeo(orthPos)
        geoPos = self.Topology(geoPos, int(hexGrid.face))
        return geoPos
