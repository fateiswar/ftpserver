#coding=utf-8
from pyftpdlib.filesystems import AbstractedFS
from filesystem_view import *
import sys
import time
import tempfile
import stat
import pdb

from pyftpdlib._compat import PY3, u, unicode, property

class ftpFS(AbstractedFS):
    timer = 0
    def __init__(self, root, cmd_channel):
        AbstractedFS.__init__(self, root, cmd_channel)
    
    @property
    def root(self):
        return self._root
    
    @property
    def cwd(self):
        return self._cwd
    
    @root.setter
    def root(self, path):
        assert isinstance(path, unicode), path
    
    @cwd.setter
    def cwd(self, path):
        assert isinstance(path, unicode), path
        print self.timer, 'cwd', path
        self.timer += 1
        self._cwd = path
    
    def open(self, filename, mode):
        assert isinstance(filename, unicode), filename
        print self.timer, 'cwd', filename, mode
        self.timer += 1
        #print self.cwd(), filename, mode
        if mode.startswith('r') or mode.startswith('R'):
            return fsview.open_read(filename)
        else:
            return fsview.open_write(filename)
    
    def chdir(self, path):
        assert isinstance(path, unicode), path
        #import pdb
        #pdb.set_trace()
        print self.timer, 'chdir', path
        self.timer += 1
        path = path.replace('\\', '/')
        if not path.startswith(self.root):
            path = u'/'
        else:
            path = path[len(self.root):]
        if path == "":
            path = u'/'
        if not path.startswith('/'):
            path = '/' + path
        self._cwd = path
    
    def mkdir(self, path):
        assert isinstance(path, unicode), path
        print self.timer, 'mkdir', path
        self.timer += 1
        fsview.mkdir(path)
        
    def listdir(self, path):
        assert isinstance(path, unicode), path
        #import pdb
        #pdb.set_trace()
        print self.timer, 'listdir', path
        self.timer += 1
        return fsview.listdir(path)
        
    def rmdir(self, path):
        assert isinstance(path, unicode), path
        print self.timer, 'rmdir', path
        self.timer += 1
        fsview.rmdir(path)
        
    def remove(self, path):
        assert isinstance(path, unicode), path
        print self.timer, 'remove', path
        self.timer += 1
        fsview.remove(path)
        
    def rename(self, src, dst):
        assert isinstance(src, unicode), src
        assert isinstance(dst, unicode), dst
        print self.timer, 'rename', src, dst
        self.timer += 1
        fsview.rename(src, dst)
        
    def chmod(self, path, mode):
        assert isinstance(path, unicode), path
        raise NotImplementedError
    
    def getsize(self, path):
        assert isinstance(path, unicode), path
        return fsview.getsize(path)
    
    def getmodify(self, path):
        assert isinstance(path, unicode), path
        return fsview.getmodify(path)
    
    def stat(self, path):
        return ""
    
    def isfile(self, path):
        assert isinstance(path, unicode), path
        return fsview.isfile(path)
    
    def isdir(self, path):
        assert isinstance(path, unicode), path
        #print path
        return fsview.isdir(path)
    
    def get_list_dir(self, path):
        assert isinstance(path, unicode), path
        if self.isdir(path):
            listing = self.listdir(path)
            try:
                listing.sort()
            except UnicodeDecodeError:
                pass
            return self.format_list(path, listing)
        else:
            basedir, filename = os.path.split(path)
            return self.format_list(basedir, [(filename, 0, 0)])
        
    def format_list(self, basedir, listing, ignore_err=True):
        assert isinstance(basedir, unicode), basedir
        if listing:
            assert isinstance(listing[0][0], unicode)
        if self.cmd_channel.use_gmt_times:
            timefunc = time.gmtime
        else:
            timefunc = time.localtime
        SIX_MONTHS = 180 * 24 * 60 * 60
        readlink = getattr(self, 'readlink', None)
        now = time.time()
        for (basename, size, modify) in listing:
            if basename == '':
                continue
            file = os.path.join(basedir, basename)
            perms = 'rwxrwxrwx'
            nlinks = 1
            size = 0
            uname = 'user'
            gname = 'user'
            mtime = timefunc(now)
            mtimestr = "1111111"
            
            islink = False
            line = "%s %3s %-8s %-8s %8s %s %s\r\n" % (perms, nlinks, uname, gname,
                                                       size, mtimestr, basename)
            yield line.encode('utf8', self.cmd_channel.unicode_errors)
    
    def format_mlsx(self, basedir, listing, perms, facts, ingore_err=True):
        assert isinstance(basedir, unicode), basedir
        if listing:
            assert isinstance(listing[0][0], unicode)
        if self.cmd_channel.use_gmt_times:
            timefunc = time.gmtime
        else:
            timefunc = time.localtime
        permdir = ''.join([x for x in perms if x not in 'arw'])
        permfile = ''.join([x for x in perms if x not in 'celmp'])
        if ('w' in perms) or ('a' in perms) or ('f' in perms):
            permdir += 'c'
        if 'd' in perms:
            permdir += 'p'
        show_type = 'type' in facts
        show_perm = 'perm' in facts
        show_size = 'size' in facts
        show_modify = 'modify' in facts
        show_create = 'create' in facts
        show_mode = 'unix.mode' in facts
        show_uid = 'unix.uid' in facts
        show_gid = 'unix.gid' in facts
        show_unique = 'unique' in facts
        for (basename, size, modify) in listing:
            if basename == '':
                continue
            retfacts = dict()
            file = os.path.join(basedir, basename)
            isdir = self.isdir(file)
            if isdir:
                if show_type:
                    if basename == '.':
                        retfacts['type'] = 'cdir'
                    elif basename == '..':
                        retfacts['type'] = 'pdir'
                    else:
                        retfacts['type'] = 'dir'
                if show_perm:
                    retfacts['perm'] = permdir
            else:
                if show_type:
                    retfacts['type'] = 'file'
                if show_perm:
                    retfacts['perm'] = permfile
            if show_size and not isdir:
                #retfacts['size'] = self.getsize(file)
                retfacts['size'] = size
            # last modification time
            if not isdir:
                retfacts['modify'] = modify[:4] + modify[5:7] + modify[8:10] + modify[11:13] + modify[14:16] + modify[17:19]
            factstring = "".join(["%s=%s;" % (x, retfacts[x]) \
                                  for x in sorted(retfacts.keys())])
            line = "%s %s\r\n" % (factstring, basename)
            yield line.encode('utf8', self.cmd_channel.unicode_errors) 
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    