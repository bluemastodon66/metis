from handlers.base import BaseHandler
from model.Media import Media
from handlers.module import loginRequired
from libs import pyUtility, pyEnum, pyCache
import random, string, os
import json
import datetime
import sys
import Image
class MediaAdminHandler(BaseHandler):
    @loginRequired (roles = [pyEnum.AccountRole.Manager])
    def get(self):
        type = self.get_request("ty","")
        s = self.get_int_request("s",0)
        k = self.get_request("k","")
        limit=30
        d = Media().searchByKeyword(k,s,limit)
        if d['total'] > limit:
            paginate = pyUtility.generate_paging_data(start=s,limit=limit,total=d['total'])
        else:
            paginate =None
        p={}
        p['title']='Media files'
        p['records']=d['data']
        p['total']=d['total']
        p['keyword']=k
        p['parameters']="k="+k
        p['paginate']=paginate
        if type =="ajax":
            self.render("topic/partial_media_list.html", **p)
        else:
            self.render("admin/admin_media.html", **p)
    @loginRequired (roles = [pyEnum.AccountRole.Manager])
    def post(self):
        upload_path = self.settings['upload_path']
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
        dtStr = datetime.datetime.now().strftime("%Y-%m-%d")
        upload_path+=dtStr+"/"
        upload_dir=self.settings['upload_dir']+dtStr+"/"
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
        file1 = self.request.files['files'][0]
        original_fname = file1['filename']
        upload_size = sys.getsizeof(file1['body'])
        extension = os.path.splitext(original_fname)[1]
        fname = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(10))
        final_filename= fname+extension
        print upload_path+final_filename
        output_file = open(upload_path+final_filename, 'w')
        try:
            output_file.write(file1['body'])
            output_file.close()
        except:
            self.write('error: write to file')
            return
        im = None
        try:
            im = Image.open(upload_path+final_filename)
        except:
            print "read img err"
            self.write('error: write to file (read img)')
            return
        # ---- thumb
        orgResolution = str(im.size[0])+"x"+str(im.size[1])
        maxWidth = int(pyCache.WebOptions['thumb_width'])
        maxHeight = int(pyCache.WebOptions['thumb_height'])
        ratio = float(maxWidth)/im.size[0]
        height = int(im.size[1]*ratio)
        if maxHeight > 0:
            if height > maxHeight:
                ratio = float(maxHeight)/im.size[1]
                height = maxHeight
                maxWidth = int(im.size[0]*ratio)
        nim = im.resize( (maxWidth, height), Image.BILINEAR )
        try:
            nim.save(upload_path+"thumb-"+final_filename)
        except:
            print "err to write"
            self.write("error: write to file (thumb img)")
            return


        m = Media()
        m.author_id = self.userID
        m.name = final_filename
        m.related_path = upload_dir
        m.upload_date = str(datetime.datetime.now())
        m.type ="image"
        m.size = upload_size
        m.resolution = orgResolution
        m.description = "new"
        newID = m.save()
        if newID <=0:
            # -------- remove files

            try:
                os.remove(upload_path+"/"+final_filename)
                os.remove(upload_path+"/"+"thumb-"+final_filename)
            except:
                pass
            self.write('error: write to db')
            return
        # Successs

        o = {}
        o['url'] = self.static_url(upload_dir+final_filename)
        o['name'] = final_filename
        o['type'] = 'image'
        o['size'] = upload_size
        o['deleteUrl'] = self.webroot_url("admin/media/delete/"+str(newID))
        o['deleteType'] = 'DELETE'
        ret = {'files':[o]}
        jsonStr = json.dumps(ret)
        self.write(jsonStr)
        # self.redirect(self.webroot_url("admin/media/"))


class MediaAdminDeleteHandler(BaseHandler):
    @loginRequired (roles = [pyEnum.AccountRole.Manager])
    def get(self, id):
        s = Media().getByID(id)
        if not s:
            self.redirect(self.webroot_url("admin/media/"))
            return
        if not self.isManager():
            if s.author_id != self.userID:
                self.redirect(self.webroot_url("admin/media/"))
                return
        upload_path = self.settings['static_path']
        file_path = upload_path+ "/"+s.related_path + s.name
        thumb_path = upload_path+ "/"+s.related_path + "thumb-"+s.name
        if os.path.isfile(thumb_path):
            try:
                os.remove(thumb_path)
            except:
                self.redirect(self.webroot_url("admin/media/"))
                return
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except:
                self.redirect(self.webroot_url("admin/media/"))
                return
        ids = []
        ids.append(id)
        print id
        Media().delByIDs(ids)
        self.redirect(self.webroot_url("admin/media/"))

class MediaAdminEditHandler(BaseHandler):
    @loginRequired (roles = [pyEnum.AccountRole.Manager])
    def get(self, id):
        r = Media().getByID(id)
        p={}
        p['title']='Media Edit'
        p['data']=r
        self.render("admin/admin_media_edit.html", **p)
    @loginRequired (roles = [pyEnum.AccountRole.Manager])
    def post(self, id):
        description = self.get_request("description","")
        r = Media().getByID(id, False)
        if r:
            r.description = description
            r.update()
        self.redirect(self.webroot_url("admin/media/edit/"+str(id)))
