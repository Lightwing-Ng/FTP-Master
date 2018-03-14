#!/usr/bin/env python
# _*_ coding:utf-8 _*_
'''
 * @author: Lightwing Ng
 * email: rodney_ng@iCloud.com
 * created on Mar 15, 2018, 3:26 AM
 * Software: PyCharm
 * Project Name: FTP2-master
'''

import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from core import main

if __name__ == '__main__':
    main.ArvgHandler()
