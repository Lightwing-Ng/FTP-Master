#!/usr/bin/env python
# _*_ coding:utf-8 _*_
'''
 * @author: Lightwing Ng
 * email: rodney_ng@iCloud.com
 * created on Mar 15, 2018, 3:28 AM
 * Software: PyCharm
 * Project Name: FTP2-master
'''

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

USER_HOME = '%s/home' % BASE_DIR
LOG_DIR = '%s/log' % BASE_DIR
LOG_LEVEL = 'DEBUG'

ACCOUNT_FILE = '%s/conf/accounts.cfg' % BASE_DIR

HOST = '0.0.0.0'
PORT = 25100
