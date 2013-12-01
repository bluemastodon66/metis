# -*- coding: utf-8 -*-
'''
Cache Object For Application
@author: Alvin

Example:
  d =  pyCacahe.WebOptions
  d["xx"] = 12345
  print d["xx"]

'''

class CacheObject(dict):
    def __init__(self):
        dict.__init__(self)
    def __getitem__(self, item):
        if item in self:
            return dict.__getitem__(self, item)
        return ""

"""
Add more objects if it needs
"""
WebOptions = CacheObject()
