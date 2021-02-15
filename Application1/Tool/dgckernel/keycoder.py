# -*- coding: utf-8 -*-
"""
key encoding

Created by ZhangZhen on 16/9/9.
Copyright © 2016 didi. All rights reserved.
"""

import string

import utils
from dgtypes import DGrid

#single column
@utils.Singleton
class KeyCoder(object):
    def __init__(self):
        pass

    #Get grid ID
    def Encode(self, hexIndex):
        return 'OL{0}F{1}i{2}j{3}'.format(hexIndex.layer, hexIndex.face, hexIndex.i, hexIndex.j)

    #Get grid ID in batch
    def Encodes(self, hexIndexes):
        s = []
        for hexIndex in hexIndexes:
            s.append(self.Encode(hexIndex))
        return s

    #Turn the grid string, return the grid object if successful, return false if it fails
    def Decode(self, hexKey):
        lpos = hexKey.find("L")
        if lpos == -1:
            return False
        fpos = hexKey.find("F")
        if fpos == -1:
            return False
        ipos = hexKey.find("i")
        if ipos == -1:
            return False
        jpos = hexKey.find("j")
        if jpos == -1:
            return False
        size = len(hexKey)
        lind = int(hexKey[lpos+1 : fpos])
        find = int(hexKey[fpos+1 : ipos])
        iind = int(hexKey[ipos+1 : jpos])
        jind = int(hexKey[jpos+1 : size])
        return DGrid(lind, find, iind, jind)

    #Batch convert strings into objects
    def Decodes(self, hexKeys):
        dgs = []
        for hexKey in hexKeys:
            dgs.append(self.Decode(hexKey))
        return dgs
