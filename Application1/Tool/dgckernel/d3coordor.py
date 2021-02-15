# -*- coding: utf-8 -*-
"""
Coordinate conversion

Created by ZhangZhen on 16/9/12.
Copyright © 2016 didi. All rights reserved.
"""

import math

import utils
from dgtypes import HalfPI, MPI, RAD2DEG, DEG2RAD
from dgtypes import SphereCoord, OrthCoord, GeoCoord

#single column
@utils.Singleton
class D3Coordor(object):
    def __init__(self):
        pass

    #input OrthCoord return float
    def dot(self, pos):
        return pos.x * pos.x + pos.y * pos.y + pos.z * pos.z

    #Convert Orthogonal, Sphere and Geographic Coordinate System one to one
    def OrthToSphere(self, pos):
        posDot = self.dot(pos)
        radial = math.sqrt(posDot)
        polar = math.acos(pos.y / radial)
        if pos.z == 0:
            if pos.x >= 0:
                azim = HalfPI
            else:
                azim = -HalfPI
        else:
            azim = math.atan(pos.x /pos.z)
            if pos.z < 0:
                if pos.x >= 0:
                    azim = MPI + azim
                else:
                    azim = MPI - azim
        return SphereCoord(radial, polar, azim)

    def SphereToOrth(self, pos):
        y = pos.radial * math.cos(pos.polar)
        z = pos.radial * math.sin(pos.polar) * math.cos(pos.azim)
        x = pos.radial * math.sin(pos.polar) * math.sin(pos.azim)
        x = float(int(x * 1000000000000000)) / 1000000000000000
        y = float(int(y * 1000000000000000)) / 1000000000000000
        z = float(int(z * 1000000000000000)) / 1000000000000000
        return OrthCoord(x, y, z)

    def SphereToGeo(self, pos):
        lat = 90 - pos.polar * RAD2DEG
        lng = pos.azim * RAD2DEG
        return GeoCoord(lat, lng)

    def GeoToSphere(self, pos):
        polar = (90 - pos.lat) * DEG2RAD
        azim = pos.lng * DEG2RAD
        return SphereCoord(1.0, polar, azim)

    def OrthToGeo(self, pos):
        sprPos = self.OrthToSphere(pos)
        return self.SphereToGeo(sprPos)

    def GeoToOrth(self, pos):
        sprPos = self.GeoToSphere(pos)
        return self.SphereToOrth(sprPos)
