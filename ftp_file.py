from oss_client.oss_api import *
from oss_client.oss_util import *
from pyftpdlib._compat import PY3, u, unicode, property
import time
import pdb

class ftp_file:
    size_cache = {}
    dir_cache = {}
    expire_time = 10
    
    def __init__(self, bucket, object, oss):
        self.bucket = self.stripFirstDelimiter(bucket)
        self.object = self.stripFirstDelimiter(object)
        self.oss = oss
        self.buf = ''
        self.buflimit = 10 * 1024 * 1024
        self.closed = False
        self.name = bucket + '/' + object
    
    def stripFirstDelimiter(self, path):
        while path.startswith('/'):
            path = path[1:]
        return path
    
    def get_upload_id(self):
        try:
            return self.upload_id
        except:
            resp = self.oss.init_multi_upload(self.bucket, self.object)
            if resp.status == 200:
                body = resp.read()
                h = GetInitUploadIdXml(body)
                self.upload_id = h.upload_id
                self.partNum = 0
                return self.upload_id
        return None
    
    def send_buf(self):
        upload_id = self.get_upload_id()
        assert upload_id != None
        if self.buf == '':
            return
        self.partNum += 1
        retry = 3
        while retry > 0:
            retry -= 1
            resp = self.oss.upload_part_from_string(self.bucket, self.object, self.buf, upload_id, self.partNum)
            if resp.status / 100 == 2:
                self.buf = ''
                break
        
    def write(self, data):
        while len(data) + len(self.buf) > self.buflimit:
            _len = self.buflimit - len(self.buf)
            self.buf = self.buf + data[:_len]
            data = data[_len:]
            self.send_buf()
        self.buf += data
        
    def close(self):
        assert self.closed == False
        try:
            self.upload_id
        except:
            retry = 3
            while retry > 0:
                retry -= 1
                resp = self.oss.put_object_from_string(self.bucket, self.object, self.buf)
                if resp.status / 100 == 2:
                    return
            return
        
        self.send_buf()
        upload_id = self.get_upload_id()
        part_msg_xml = get_part_xml(self.oss, self.bucket, self.object, upload_id)
        retry = 3
        while retry > 0:
            retry -= 1
            resp = self.oss.complete_upload(self.bucket, self.object, upload_id, part_msg_xml)
            if resp.status / 100 == 2:
                break
        self.closed = True
        
    def listdir(self):
        try:
            return self.contents
        except:
            pass
        object = self.object
        if object != '' and not object.endswith('/'):
            object = object + '/'
        self.object_list, self.dir_list = self.oss.list_objects(self.bucket, object, '/')
        self.contents = []
        for entry in self.object_list:
            toAdd = entry[0][len(object):]
            self.contents.append((toAdd, entry[1], entry[2]))
            self.cache_set(self.size_cache, (self.bucket, entry[0]), entry[1])
        for entry in self.dir_list:
            toAdd = entry[len(object):]
            self.contents.append((toAdd, -1, 0))
        
        return self.contents
        
    def isfile(self):
        value = self.cache_get(self.dir_cache, (self.bucket, self.object))
        if value != None:
            return not value
        self.listdir()
        value = (len(self.contents) == 0)
        self.cache_set(self.dir_cache, (self.bucket, self.object), not value)
        return value
    
    def isdir(self):
        value = self.cache_get(self.dir_cache, (self.bucket, self.object))
        if value != None:
            return value
        value = not self.isfile()
        self.cache_set(self.dir_cache, (self.bucket, self.object), value)
        return value
    
    def cache_get(self, cache, key):
        if cache.has_key(key):
            if cache[key][1] + self.expire_time < time.time():
                return None
            return cache[key][0]
        return None
    
    def cache_set(self, cache, key, value):
        cache[key] = (value, time.time())
        
    def getsize(self):
        value = self.cache_get(self.size_cache, (self.bucket, self.object))
        if value != None:
            return value
        resp = self.oss.head_object(self.bucket, self.object)
        content_len = 0
        if (resp.status / 100) == 2:
            header_map = convert_header2map(resp.getheaders())
            content_len = safe_get_element("content-length", header_map)
            self.cache_set(self.size_cache, (self.bucket, self.object), content_len)
        return content_len
    
    def open_read(self):
        resp = self.oss.get_object(self.bucket, self.object)
        resp.name = self.bucket + '/' + self.object
        return resp
     
    def mkdir(self):
        bucket = self.bucket
        object = self.object
        if not object.endswith('/'):
            object = object + '/'
        content_type = "text/HTML"
        resp = self.oss.put_object_from_string(bucket, object, 'Dir')
        
    def rmdir(self):
        bucket = self.bucket
        object = self.object
        if not object.endswith('/'):
            object = object + '/'
        self.oss.delete_object(bucket, object)
        
    def remove(self):
        bucket = self.bucket
        object = self.object
        self.oss.delete_object(bucket, object)
        