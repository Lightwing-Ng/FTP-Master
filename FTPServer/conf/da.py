#!/usr/bin/env python
# _*_ coding:utf-8 _*_
'''
 * @author: Lightwing Ng
 * email: rodney_ng@iCloud.com
 * created on Mar 15, 2018, 3:28 AM
 * Software: PyCharm
 * Project Name: FTP2-master
'''

import configparser

config = configparser.ConfigParser()
config.read('accounts.cfg')

config['alex']['username'] = 'liang'
print(config['alex']['username'])
