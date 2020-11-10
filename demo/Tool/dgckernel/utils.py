# -*- coding: utf-8 -*-
"""
工具箱

Created by ZhangZhen on 16/9/9.
Copyright © 2016年 didi. All rights reserved.
"""

#单列装饰器
def Singleton(cls, *args, **kw):
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton
