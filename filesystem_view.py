from oss_client.oss_api import *
from ftp_file import *

class fs_view:
    host = 'oss.aliyuncs.com'
    access_id = 'c35SzGhvT6ovyOej'
    access_key = 'poExTElXz9fzLsTO4kzL8FKmh2d42k'
    
    def __init__(self):
        self.oss = OssAPI(self.host, self.access_id, self.access_key)
        
    def isBucket(self, path):
        phyPath = self.stripLastDelimiter(path)
        index = phyPath.rfind('/')
        if index == 0 and not self.isRoot(path):
            return True
        return False
    
    def isRoot(self, path):
        return path == '/'

    def stripLastDelimiter(self, path):
        if path.endswith('/'):
            path = path[:-1]
        return path

    def getOSSBucketName(self, path):
        if self.isRoot(path):
            return "/"
        phyPath = self.stripLastDelimiter(path)
        index = phyPath.find('/', 1)
        if index <= 0:
            return phyPath[1:]
        else:
            return phyPath[1:index]
        
    def getFileName(self, path):
        if self.isBucket(path):
            return ""
        if path == '/':
            return '/'
        bucket = self.getOSSBucketName(path)
        return path[len(bucket)+2:]
    
    def getParentPhysicalName(self, path):
        if path == '/':
            return '/'

        parentPath = self.stripLastDelimiter(path)

        index = parentPath.rfind('/')
        if index != -1:
            parentPath = parentPath[:index]

        return parentPath

    def normalizeSeparateChar(self, path):
        normalizedPathName = path.replace('\\', '/')
        return normalizedPathName
    
    def getPhysicalName(self, rootDir, curDir, fileName):
        normalizedRootDir = self.normalizeSeparateChar(rootDir)
        if normalizedRootDir[-1] != '/':
            normalizedRootDir += '/'
        normalizedFileName = self.normalizeSeparateChar(fileName)
        normalizedCurDir = curDir
        if normalizedFileName[0] != '/':
            if normalizedCurDir == None:
                normalizedCurDir = '/'
            if normalizedCurDir == '':
                normalizedCurDir = '/'
            normalizedCurDir = self.normalizeSeparateChar(normalizedCurDir)
            if normalizedCurDir[0] != '/':
                normalizedCurDir = '/' + normalizedCurDir
            if normalizedCurDir[-1] != '/':
                normalizedCurDir = normalizedCurDir + '/'
            resArg = normalizedRootDir + normalizedCurDir[1:]
        else:
            resArg = normalizedRootDir

        resArg = self.stripLastDelimiter(resArg)

        st = normalizedFileName.split('/')
        for tok in st:
            if tok == '':
                continue
            if tok == '.':
                continue
            if tok == '..':
                if resArg.startswith(normalizedRootDir):
                    slashIndex = resArg.rfind('/')
                    if slashIndex != -1:
                        resArg = resArg[0:slashIndex]
                continue
            if tok == '~':
                resArg = normalizedRootDir[:-1]
                continue

            resArg = resArg + '/' + tok

        if len(resArg) + 1 == len(normalizedRootDir):
            resArg = resArg + '/'

        return resArg
    
    def open_read(self, path):
        path = self.normalizeSeparateChar(path)
        return ftp_file(self.getOSSBucketName(path), self.getFileName(path), self.oss).open_read()
    
    def open_write(self, path):
        path = self.normalizeSeparateChar(path)
        return ftp_file(self.getOSSBucketName(path), self.getFileName(path), self.oss)
    
    def mkdir(self, path):
        path = self.normalizeSeparateChar(path)
        ftp_file(self.getOSSBucketName(path), self.getFileName(path), self.oss).mkdir()
        
    
    def listdir(self, path):
        path = self.normalizeSeparateChar(path)
        return ftp_file(self.getOSSBucketName(path), self.getFileName(path), self.oss).listdir()
    
    def rmdir(self, path):
        path = self.normalizeSeparateChar(path)
        ftp_file(self.getOSSBucketName(path), self.getFileName(path), self.oss).rmdir()
    
    def remove(self, path):
        path = self.normalizeSeparateChar(path)
        ftp_file(self.getOSSBucketName(path), self.getFileName(path), self.oss).remove()
    
    def rename(self, path1, path2):
        pass
    
    def getsize(self, path):
        path = self.normalizeSeparateChar(path)
        return ftp_file(self.getOSSBucketName(path), self.getFileName(path), self.oss).getsize()
    
    def getmodify(self, path):
        path = self.normalizeSeparateChar(path)
        return ftp_file(self.getOSSBucketName(path), self.getFileName(path), self.oss).getmodify()
    
    def isfile(self, path):
        path = self.normalizeSeparateChar(path)
        return ftp_file(self.getOSSBucketName(path), self.getFileName(path), self.oss).isfile()
    
    def isdir(self, path):
        path = self.normalizeSeparateChar(path)
        return ftp_file(self.getOSSBucketName(path), self.getFileName(path), self.oss).isdir()
    
fsview = fs_view()