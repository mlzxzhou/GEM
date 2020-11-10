# -*- coding: utf-8 -*-
"""
key编码

Created by ZhangZhen on 16/9/9.
Copyright © 2016年 didi. All rights reserved.
"""

import string

import utils
from dgtypes import DGrid

#单列
@utils.Singleton
class KeyCoder(object):
    def __init__(self):
        pass

    #解格子ID
    def Encode(self, hexIndex):
        return 'OL{0}F{1}i{2}j{3}'.format(hexIndex.layer, hexIndex.face, hexIndex.i, hexIndex.j)

    #批量解格子
    def Encodes(self, hexIndexes):
        s = []
        for hexIndex in hexIndexes:
            s.append(self.Encode(hexIndex))
        return s

    #转格子字符串, 转成功返回格子对象，转失败返回false
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

    #批量将字符串转成对象
    def Decodes(self, hexKeys):
        dgs = []
        for hexKey in hexKeys:
            dgs.append(self.Decode(hexKey))
        return dgs
