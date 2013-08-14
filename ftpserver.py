from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.filesystems import AbstractedFS
from filesystem_view import *
from FtpFs import *
from oss_client.oss_api import *

import os
from optparse import OptionParser

def main(user, password, port, bucket, access_id, access_key):
    fs_view.access_id = access_id
    fs_view.access_key = access_key
    fsview.oss = OssAPI(fs_view.host, fs_view.access_id, fs_view.access_key)
    
    authorizer = DummyAuthorizer()
    
    authorizer.add_user(user, password, bucket, perm = 'elradfmwM')
    authorizer.add_anonymous(bucket)
    
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.abstracted_fs = ftpFS
    #handler.abstracted_fs = AbstractedFS
    
    handler.banner = 'pyftpdlib based ftpd ready'
    
    address = ('127.0.0.1', port)
    server = FTPServer(address, handler)
    
    server.serve_forever()
    
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("", "--access_id", dest="access_id", help="")
    parser.add_option("", "--access_key", dest="access_key", help="")
    parser.add_option("", "--ftp_user_name", dest="ftp_user_name", help="")
    parser.add_option("", "--ftp_password", dest="ftp_password", help="")
    parser.add_option("", "--bucket", dest="bucket", help="")
    parser.add_option("", "--port", dest="port", help="")
    (options, args) = parser.parse_args()
    if options.ftp_user_name:
        user = options.ftp_user_name
    else:
        user = 'admin'
        
    if options.ftp_password:
        password = options.ftp_password
    else:
        password = '12345'
        
    if options.port:
        port = options.port
    else:
        port = 2121
        
    bucket = options.bucket
    if not bucket.startswith('/'):
        bucket = '/' + bucket
    if not bucket.endswith('/'):
        bucket = bucket + '/'
        
    main(user, password, port, bucket, options.access_id, options.access_key)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    