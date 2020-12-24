# -*- coding: utf-8 -*-

"""
Data structure used in grid calculation algorithm

Created by ZhangZhen on 16/9/9.
Copyright © 2016 didi. All rights reserved.
"""

RADIUS = 6371004
MPI = 3.141592653589793238462643383279502884197169399
HalfPI = MPI / 2
RAD2DEG = 180 / MPI
DEG2RAD = MPI / 180
POLARLAT = 89.999999

VERTEX0DD = "Vertex0DD"
VERTEX1RD = "Vertex1RD"
VERTEX2RU = "Vertex2RU"
VERTEX3UU = "Vertex3UU"
VERTEX4LU = "Vertex4LU"
VERTEX5LD = "Vertex5LD"

class DGrid(object):
    def __init__(self, layer, face, i, j):
        self.layer = layer
        self.face = face
        self.i = i
        self.j = j

    #Generate grid ID
    def DGridStr(self):
        return 'OL{0}F{1}i{2}j{3}'.format(self.layer, self.face, self.i, self.j)

class GeoCoord(object):
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng

    def GeoCoordStr(self):
        return 'GeoCoord_{0}_lat{1}_lng'.format(self.lat, self.lng)

class OrthCoord(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def OrthCoordStr(self):
        return 'OrthCoord_{0}_x{1}_y{2}_z'.format(self.x, self.y, self.z)

class SphereCoord(object):
    def __init__(self, r, p, a):
        self.radial = r
        self.polar = p
        self.azim = a

    def SphereCoordStr(self):
        return 'SphereCoord_{0}_radial{1}_polar{2}_azim'.format(self.radial, self.polar, self.azim)

class ObliqueCoord(object):
    def __init__(self, i, j, k):
        self.i = i
        self.j = j
        self.k = k

    def ObliqueCoordStr(self):
        return 'ObliqCoord_{0}_i{1}_j{2}_k'.format(self.i, self.j, self.k)

class FaceIndexCoord(object):
    def __init__(self, i, j):
        self.i = i
        self.j = j

    def FaceIndexCoordStr(self):
        return 'FaceIndexCoord_{0}_i{1}_j'.format(self.i, self.j)
