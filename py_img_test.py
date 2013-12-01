import Image
import json
import os
import datetime
im = None
filename = "/home/sample.jpg"
main, ext = os.path.splitext(filename)
try:
    im = Image.open(filename)
except:
    print "error"
if im:
    print im.size
    width = 400
    ratio = float(width)/im.size[0]
    height = int(im.size[1]*ratio)
    nim = im.resize( (width, height), Image.BILINEAR )
    print nim.size
    print ext
    nim.save("thumb-"+main+ext)
o = {}
o['url'] = 'xxxx'
o['name'] = 'xxxx'
o['type'] = 'image'
o['size'] = 123
o['deleteUrl'] = 'xxxx'
o['deleteType'] = 'DELETE'
ret = {'files':[o]}
jsonStr = json.dumps(ret)
print jsonStr

dt = datetime.datetime.now().strftime("%Y-%m-%d")
print dt.strftime("%Y-%m-%d")