# -*- coding: utf-8 -*-
'''
Some Useful Tool
@author: Alvin

'''
import re
import cgi
import math
import hashlib
import json
import urllib
def isAccountLegal(t):
    flag = False
    if re.match('^[a-zA-Z0-9_]{3,}$',t):
        flag = True
    return flag
def isHex(t):
    flag = False
    if re.match('^#?([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',t):
        flag = True
    return flag
def isSlug(t):
    flag = False
    if re.match('^[A-Za-z0-9-]+$',t):
        flag = True
    return flag
def isURL(t):
    flag = False
    if re.match('^(http|https)\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(:[a-zA-Z0-9]*)?/?([a-zA-Z0-9\-\._\?\,\'/\\\+&amp;%\$#\=~])*$',t):
        flag = True
    return flag
def isIP(t):
    flag = False
    if re.match('^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',t):
        flag = True
    return flag

def isLegalChar(t):
    flag = False
    if re.match('^[a-zA-Z0-9_\.@]+$',t):
        flag = True
    return flag
def isNumberAlphabetOnly(t):
    flag = False
    if re.match('^[a-zA-Z0-9]+$',t):
        flag = True
    return flag
def isEmail(t):
    flag = False
    if re.match('^([A-Za-z0-9_\.-]+)@([\da-zA-Z\.-]+)\.([A-Za-z\.]{2,6})$',t):
        flag = True
    return flag
def isHtmlTagLegal(t):
    flag = False
    if re.match('^<([a-z]+)([^<]+)*(?:>(.*)<\/\1>|\s+\/>)$',t):
        flag = True
    return flag
def isPermaLinkLegal(t):
    flag = False
    if re.match('^([a-zA-Z\-0-9\.:,_/]+)$',t):
        flag = True
    return flag
def html_escape(s):
    return cgi.escape(s)
def urlencode(s):
    return urllib.unquote(s)
def html_unescape(self, s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    # this has to be last:
    s = s.replace("&amp;", "&")
    return s
def html_purify(html):
    s = re.sub('</*(script|iframe|frame|frameset|html|body|title)[^>]*>','',html)
    return s
def reply_purify(html):
    s = re.sub('</*(script|iframe|frame|frameset|html|body|title|img)[^>]*>','',html)
    return s
def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)
def remove_extra_spaces(data):
    p = re.compile(r'\s+')
    return p.sub(' ', data)
def md5(s):
    return hashlib.md5(s).hexdigest()
def str2int(s):
    try:
        i = int(s)
        return i
    except ValueError:
        return 0
def jsonDecode(s):
    try:
        r=json.loads(s)
        return r
    except:
        return None
def generate_paging_data(**kwargs):
    start = int(kwargs.get('start',0))
    limit = int(kwargs.get('limit',10))
    total = int(kwargs.get('total',0))
    if total <=0:
        return []
    if start >= total:
        start= total-1
    pagers = []
    currentPage = int(math.floor(start/limit))
    TotalPages = int(math.ceil(float(total)/float(limit)))
    if TotalPages <= 1:
        return pagers
    prev=(currentPage - 1)*limit
    nxt=(currentPage+1)*limit
    # first one
    d=dict(
        disable=False,
        value=str(prev),
        text="«",
        current=False
    )
    if currentPage==0:
        d['disable']=True
    pagers.append(d)
    nums = 10
    if currentPage < 5:
        base = 0
    else:
        if currentPage > (TotalPages - 5):
            base = TotalPages - 10

        else:
            base = currentPage - 5

    if nums > TotalPages:
        nums = TotalPages
    for x in xrange(nums):
        page = x+base
        d=dict(
            disable=False,
            text=str(page+1),
            value=str(page*limit),
            current=False
        )
        if(page == currentPage):
            d['current']=True
        pagers.append(d)


    # last one
    d=dict(
        disable=False,
        value=str(nxt),
        text="»",
        current=False
    )
    if currentPage >= TotalPages-1:
        d['disable']=True
    pagers.append(d)
    return pagers




