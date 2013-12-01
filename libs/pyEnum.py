# -*- coding: utf-8 -*-
'''
Simple Enum
@author: Alvin
'''


class AccountRole:
    Admin = 'admin'
    Manager = 'manager'
    Normal = 'normal'
    List = [Admin, Manager, Normal]


def AccountStatus():
    ms = dict()
    ms["0"]="未認證"
    ms["1"]="認證帳號"
    ms["2"]="鎖住帳號"
    return ms
def GetAccountStatusID(s):
    key = str(s)
    ms = AccountStatus()
    if key in ms:
        return s
    return 0
def GetAccountRole(key):
    ret = AccountRole.Normal
    for r in AccountRole.List:
        if key == r:
            ret = r
            break
    return ret

def GetAccountStatus(s):
    ke = str(s)
    ms = AccountStatus()
    ret = ms["0"]
    if ms.has_key(ke):
        ret = ms[ke]
    return ret

