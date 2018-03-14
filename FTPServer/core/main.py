#!/usr/bin/env python
# _*_ coding:utf-8 _*_
'''
 * @author: Lightwing Ng
 * email: rodney_ng@iCloud.com
 * created on Mar 15, 2018, 3:33 AM
 * Software: PyCharm
 * Project Name: FTP2-master
'''

import optparse
from core.ftp_server import FTPHandler
import socketserver
from conf import settings


class ArvgHandler(object):
    def __init__(self):
        self.parser = optparse.OptionParser()
        (options, args) = self.parser.parse_args()
        self.verify_args(options, args)

    def verify_args(self, options, args):
        '''
        Check and call some other functions
        :param options:
        :param args:
        :return:
        '''
        if args:
            if hasattr(self, args[0]):
                print(args[0])
                func = getattr(self, args[0])
                func()
            else:
                exit('Usage: start/stop'.center(50, ' '))
        else:
            exit('Usage: start/stop'.center(50, ' '))

    def start(self):
        '''

        :return:
        '''
        print(('Starting FTP Server on %s: %s' % (settings.HOST, settings.PORT)).center(50, ' '))
        server = socketserver.ThreadingTCPServer((settings.HOST, settings.PORT), FTPHandler)
        server.serve_forever()
