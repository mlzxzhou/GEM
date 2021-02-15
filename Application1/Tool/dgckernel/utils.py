# -*- coding: utf-8 -*-
"""
tools

Created by ZhangZhen on 16/9/9.
Copyright © 2016 didi. All rights reserved.
"""

#Single column decorator
def Singleton(cls, *args, **kw):
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton
