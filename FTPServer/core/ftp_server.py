#!/usr/bin/env python
# _*_ coding:utf-8 _*_
'''
 * @author: Lightwing Ng
 * email: rodney_ng@iCloud.com
 * created on Mar 15, 2018, 3:33 AM
 * Software: PyCharm
 * Project Name: FTP2-master
'''

import socketserver, configparser, os, subprocess, hashlib, re, json
from conf import settings

STATUS_CODE = {
    200: "Task finished",  # 任务完成

    # 错误格式
    250: "Invalid cmd format, e.g: {'action':'get','filename':'test.py','size':344}",
    251: "Invalid cmd ",  # 无效命令
    252: "Invalid auth data",  # 无效认证数据
    253: "Wrong username or password",  # 用户名密码错误
    254: "Passed authentication",  # 通过认证
    255: "Filename doesn't provided",  # 文件名未提供
    256: "File doesn't exist on server",  # 服务器上不存在文件
    257: "ready to send file",  # 准备发送文件
    288: "你可以发文件了",
    258: "md5 verification",  # MD5验证
    259: "path doesn't exist on server",  # 路径不存在于服务器上
    260: "path changed",  # 路径改变
    261: "Not a directory",
    262: "Permission denied",
    263: "Print working directory error",
    264: "Ready to send data",
    265: "Put: overwrite",
    266: "Ready to receive file",
    267: "The file is consistent",
    268: "The file is not consistent",
    270: "Remove file error",
    271: "It is not a file",
    272: "Filename doesn't provided",
    273: "Create directory error",
    275: "File or directory exists",
    276: "Remove directory error",
    277: "Directory not exists",
    300: "Direectroy is yes",
}


class FTPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        '''

        :return:
        '''
        while True:
            self.data = self.request.recv(1024).strip()
            print(self.client_address[0])
            print(self.data)
            if not self.data:
                print('Client closed...'.center(50, ' '))
                break
            data = json.loads(self.data.decode())

            if data.get('action') is not None:
                if hasattr(self, '_%s' % data.get('action')):
                    func = getattr(self, '_%s' % data.get('action'))
                    func(data)
                else:
                    print('Invalid Command.'.center(50, ' '))
                    self.send_response(251)
            else:
                print('Invalid Command Format.'.center(50, ' '))
                self.send_response(250)

    def send_response(self, status_code, data=None):
        '''
        Send response code back to client ends
        :param status_code:
        :param data:
        :return:
        '''
        response = {
            'status_code': status_code,
            'status_msg': STATUS_CODE[status_code],
        }
        if data:
            response.update({'data': data})
        self.request.send(json.dumps(response).encode())

    def _auth(self, *args, **kwargs):
        '''
        Auth the username and passwords
        :param args:
        :param kwargs:
        :return:
        '''
        data = args[0]
        if data.get('username') is None or data.get('password') is None:
            self.send_response(252)

        user = self.authenticate(data.get('username'), data.get('password'))

        if user is None:
            self.send_response(253)
        else:
            print(('%s Passed Authentication' % user).center(50, ' '))
            self.user = user
            self.user['username'] = data.get('username')

        # The directory of user
        self.home_dir = '%s/home/%s' % (settings.BASE_DIR, data.get('username'))
        self.current_dir = self.home_dir
        self.send_response(254)

    def authenticate(self, username, password):
        '''
        Verify the user's data
        :param username:
        :param password:
        :return: user's data
        '''
        config = configparser.ConfigParser()
        config.read(settings.ACCOUNT_FILE)

        if username in config.sections():
            _password = config[username]['Password']
            if _password == password:
                print('%s has Pass Authentication...' % username)
                config[username]['Username'] = username
                return config[username]

    def _listdir(self, *args, **kwargs):
        '''
        Return file list on current dir
        :param args:
        :param kwargs:
        :return:
        '''
        res = self.run_cmd('ls -lsh %s' % self.current_dir)
        self.send_response(200, data=res)

    def run_cmd(self, cmd):
        '''
        Output as shell's format
        :param cmd:
        :return:
        '''
        cmd_res = subprocess.getstatusoutput(cmd)
        return cmd_res

    def _change_dir(self, *args, **kwargs):
        '''
        Change the directory
        :param args:
        :param kwargs:
        :return:
        '''
        if args[0]:
            dest_path = '%s/%s' % (self.current_dir, args[0]['path'])
        else:
            dest_path = self.home_dir
        real_path = os.path.realpath(dest_path)
        print('The real path is: %s.' % real_path)

        if real_path.startswith(self.home_dir):
            if os.path.isdir(real_path):
                self.current_dir = real_path
                current_relative_dir = self.get_relative_path(self.current_dir)
                self.send_response(260, {'current_path': current_relative_dir})
            else:
                self.send_response(259)
        else:
            print('Has no permission to the access of: ', real_path)
            current_relative_dir = self.get_relative_path(self.current_dir)
            self.send_response(260, {'current_path': current_relative_dir})

    def get_relative_path(self, abs_path):
        '''
        return the relative path of the current user
        :param abs_path:
        :return:
        '''
        relative_path = re.sub('^%s' % settings.BASE_DIR, '', abs_path)
        return relative_path

    def _pwd(self, *args, **kwargs):
        '''
        Display the current path
        :param args:
        :param kwargs:
        :return:
        '''
        current_relative_dir = self.get_relative_path(self.current_dir)
        self.send_response(200, data=current_relative_dir)

    def _put(self, *args, **kwargs):
        '''
        The client ends upload some files
        :param args:
        :param kwargs:
        :return:
        '''
        data = args[0]
        file_abs_path = '{}/{}'.format(self.home_dir, data.get('filename'))
        self.send_response(288)
        file_size = json.loads(self.request.recv(1024).decode())

        if file_size:
            self.request.send(b'1')
            received_size = 0
            file_obj = open(file_abs_path, 'wb')

            if data.get('md5'):
                md5_obj = hashlib.md5()

                while received_size < file_size['file_size']:
                    data = self.request.recv(4096)
                    received_size += len(data)
                    file_obj.write(data)
                    md5_obj.update(data)
                else:
                    print('File Received'.center(50, ' '))
                    file_obj.close()
                    self.request.send(b'1')  # 解决粘包
                    md5_val = md5_obj.hexdigest()
                    md5_from_client = json.loads(self.request.recv(1024).decode())

                    if md5_from_client['md5'] == md5_val:
                        self.send_response(267)
                    else:
                        self.send_response(268)
            else:
                while received_size < file_size['file_size']:
                    data = self.request.recv(4096)
                    received_size += len(data)
                    file_obj.write(data)

    def _put2(self, *args, **kwargs):
        '''

        :param args:
        :param kwargs:
        :return:
        '''
        data = args[0]
        client_recv = json.loads(self.request.recv(1024).decode())
        print('Ready to send files.'.center(50, ' '))

        if client_recv('filename') is None:
            self.send_response(255)
            exit('Error'.center(50, ' '))

        file_size = client_recv('filesize')

        if file_size is None:
            self.send_response(255)
            exit('Error'.center(50, ' '))
        self.send_response(288)
        print('Sending Files is now available.'.center(50, ' '))
        file_abs_path = '%s/%s' % (self.current_dir, data.get('filename'))
        print('File Absolute Path: ', file_abs_path)

        if os.path.isfile(file_abs_path):
            f = open(file_abs_path, 'wb')
        else:
            f = open(file_abs_path, "wb")

        received_size = 0
        cmd_res = b''

        while received_size < file_size:
            data = self.request.recv(1024)
            received_size += len(data)
            cmd_res += data
        else:
            f.close()
            print('File receiving is done'.center(50, ' '))
            f.write(cmd_res)

    def _get(self, *args, **kwargs):
        '''
        Load data from the server to local base
        :param args:
        :param kwargs:
        :return:
        '''
        data = args[0]
        if data.get('filename') is None:
            self.send_response(255)
        file_abs_path = '%s/%s' % (self.current_dir, data.get('filename'))
        print('File Absolute Path: ', file_abs_path)

        if os.path.isfile(file_abs_path):
            file_obj = open(file_abs_path, 'rb')
            file_size = os.path.getsize(file_abs_path)
            self.send_response(257, data={'file_size': file_size})
            self.request.recv(1)

            if data.get('md5'):
                md5_obj = hashlib.md5()
                for line in file_obj:
                    self.request.send(line)
                    md5_obj.update(line)
                else:
                    file_obj.close()
                    md5_val = md5_obj.hexdigest()
                    self.send_response(258, {'md5': md5_val})
                    print('File sending is done'.center(50, ' '))
            else:
                for line in file_obj:
                    self.request.send(line)
                else:
                    file_obj.close()
                    print('File sending is done'.center(50, ' '))
        else:
            self.send_response(256)

    def _mkdir(self, *args, **kwargs):
        '''
        make some new directories
        :param args:
        :param kwargs:
        :return:
        '''
        data = args[0]
        Folder_user = data.get('filename')
        choice = '%s/%s' % (self.current_dir, Folder_user)
        if os.path.isfile(choice):
            self.send_response(277)
        else:
            res = self.run_cmd('mkdir -p %s' % choice)
            self.send_response(300, data=res)

    def _touch(self, *args, **kwargs):
        '''
        create a new file
        :param args:
        :param kwargs:
        :return:
        '''
        data = args[0]
        user_file = data.get('filename')
        choice = '%s/%s' % (self.current_dir, user_file)

        if os.path.isfile(choice):
            self.send_response(266)
        else:
            res = self.run_cmd('touch %s' % choice)
            self.send_response(300, data=res)

    def _rm(self, *args, **kwargs):
        '''

        :param args:
        :param kwargs:
        :return:
        '''
        data = args[0]
        user_file = data.get('filename')
        choice = '%s/%s' % (self.current_dir, user_file)
        print("User Path: ", choice)


if __name__ == '__main__':
    HOST, PORT = 'localhost', 9500
