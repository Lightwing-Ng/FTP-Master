#!/usr/bin/env python
# _*_ coding:utf-8 _*_
'''
 * @author: Lightwing Ng
 * email: rodney_ng@iCloud.com
 * created on Mar 15, 2018, 1:09 AM
 * Software: PyCharm
 * Project Name: FTP2-master
'''

import socket, os, json, optparse, getpass, hashlib, sys

# Status Code
STATUS_CODE = {
    # 错误格式
    250: "Invalid cmd format, e.g: {'action':'get','filename':'test.py','size':344}",
    251: "Invalid Commands ",  # 错误命令
    252: "Invalid Auth Data",  # 验证失败
    253: "Wrong Username or Password",  # 用户名或者密码错误
    254: "Passed Authentication",  # 验证错误
}


class FTPClient(object):
    def __init__(self):
        self.user = None  # temporary user
        parser = optparse.OptionParser()  # Create an instance

        # Add options
        parser.add_option('-s', '--server', dest='server', help='ftp server ip_addr')
        parser.add_option('-P', '--port', type='int', dest='port', help='ftp server port')
        parser.add_option('-u', '--username', dest='username', help='username')
        parser.add_option('-p', '--password', dest='password', help='password')

        self.options, self.args = parser.parse_args()

        # check if available
        self.verify_args(self.options, self.args)

        # create a connection
        self.make_connection()

    def make_connection(self):
        '''
        Create a connection
        :return:
        '''
        self.sock = socket.socket()
        self.sock.connect((self.options.server, self.options.port))  # (addr, port)

    def verify_args(self, options, args):
        '''
        Check its legality
        :param option:
        :param args:
        :return:
        '''
        if options.username is not None and options.password is not None:
            pass
        elif options.username is None and options.password is None:
            pass
        else:
            # options.username is None or options.password is None:
            exit('Error: username and password must be provided together...')

        if options.server and options.port:
            if options.port > 0 and options.port < 65535:
                return True
            else:
                exit('Error: host port must in the range of 0 - 65535.')
        else:
            exit('Error:must supply ftp server address, use -h to check all available arguments.')

    def authenticate(self):
        '''
        User authentication
        :return:
        '''
        if self.options.username:
            print(self.options.username, self.options.password)
            return self.get_auth_result(self.options.username, self.options.password)
        else:
            # if the accs and passwords does not consists in paras
            retry_count = 0
            while retry_count < 3:
                username = input('username: ').strip()
                password = input('password: ').strip()
                if self.get_auth_result(username, password):
                    return True
                retry_count += 1

    def get_auth_result(self, user, password):
        data = {
            'action': 'auth',
            'username': user,
            'password': password
        }
        self.sock.send(json.dumps(data).encode())
        response = self.get_response()

        if response.get('status_code') == 254:
            print('Passed Authentication!'.center(50, ' '))
            self.user = user
            return True
        else:
            print(response.get('status_msg'))

    def get_response(self):
        '''
        Get the return value from the server
        :return:
        '''
        data = self.sock.recv(1024)  # 1024 bytes each time
        data = json.loads(data.decode())
        return data

    def interactive(self):
        '''
        communicate with the server
        :return: authenticate successfully, True
        else, None
        '''
        if self.authenticate():
            print('Start to interactive:'.center(50, ' '))
            self.terminal_display = '[%s]$:' % self.user

            while True:
                choice = input(self.terminal_display).strip()
                if len(choice) == 0:
                    continue
                elif choice == 'q' or choice == 'exit':
                    exit('Good Bye'.center(50, ' '))

                cmd_list = choice.split()
                print(cmd_list)

                # Judge if hte commands in self, class method
                if hasattr(self, '_%s' % cmd_list[0]):
                    func = getattr(self, '_%s' % cmd_list[0])
                    func(cmd_list)
                else:
                    print("Invalid cmd, type 'help' to check available commands.".center(50, ' '))

    def __md5_required(self, cmd_list):
        '''
        Check if the command needs MD5 verification
        :param cmd_list:
        :return:
        '''
        if '--md5' in cmd_list:
            return True
        else:
            return None

    def _help(self, *args, **kwargs):
        '''
        Show help options
        :param args:
        :param kwargs:
        :return:
        '''
        supported_actions = '''
        get filename    # get file from FTP server
        put filename    # upload file to FTP server
        ls              # list files in current dir on FTP server
        pwd             # check current path on server
        cd path         # change directory , same usage as linux cd command
        touch           # touch file 
        rm              # rm file  rm director
        mkdir           # mkdir direcotr
        '''
        print(supported_actions)
        pass

    def show_progress(self, total):
        '''
        Display progress bar
        :param total:
        :return:
        '''
        received_size = 0
        current_percent = 0
        while received_size < total:
            if int((received_size / total) * 100) > current_percent:
                print('▇', end='', flush=True)
                current_percent = int((received_size / total) * 100)
                new_size = yield
                received_size += new_size

    def _cd(self, *args, **kwargs):
        '''
        Get the path
        :param args:
        :param kwargs:
        :return:
        '''
        if len(args[0]) > 1:
            path = args[0][1]
        else:
            path = ''
        data = {
            'action': 'change_dir',
            'path': path
        }

        self.sock.send(json.dumps(data).encode())
        response = self.get_response()

        if response.get('status_code') == 260:
            self.terminal_display = '%s:' % response.get('data').get('current_path')

    def _pwd(self, *args, **kwargs):
        '''
        Show the current path
        :param args:
        :param kwargs:
        :return:
        '''
        data = {'action': 'pwd'}
        self.sock.send(json.dumps(data).encode())
        response = self.get_response()
        has_err = False

        if response.get('status_code') == 200:
            data = response.get('data')
            if data:
                print(data)
            else:
                has_err = True
        else:
            has_err = True

        if has_err:
            print('Error: unexpected fault.'.center(50, ' '))

    def _ls(self, *args, **kwargs):
        '''
        list all the files as below
        :param args:
        :param kwargs:
        :return:
        '''
        data = {'action': 'listdir'}
        self.sock.send(json.dumps(data).encode())
        response = self.get_response()
        has_err = False

        if response.get('status_code') == 200:
            data = response.get('data')
            if data:
                print(data[1])
            else:
                has_err = True
        else:
            has_err = True

        if has_err:
            print('Error: unexpected fault.'.center(50, ' '))

    def get_abs_path(self, *args, **kwargs):
        '''
        Obtain the absolute path
        :param args:
        :param kwargs:
        :return: the absolute path
        '''
        abs_path = os.getcwd()
        return abs_path

    def _put(self, cmd_list):
        '''
        for clients upload files
        :param cmd_list:
        :return:
        '''
        if len(cmd_list) == 1:
            print('No filename follows.'.center(50, ' '))
            return

        # Get the current absolute path
        abs_path = self.get_abs_path()
        if cmd_list[1].startswith('/'):
            file_abs_path = cmd_list[1]
        else:
            file_abs_path = '{}/{}'.format(abs_path, cmd_list[1])
        print('File abs path: ', file_abs_path)

        # When file does not exist
        if not os.path.isfile(file_abs_path):
            print(STATUS_CODE[260])
            return

        # Extract the file's name
        base_filename = cmd_list[1].split('/')[-1]

        # send the protocal to the server
        data_header = {
            'action': 'put',
            'filename': base_filename
        }

        # check if needs MD5 verification
        if self.__md5_required(cmd_list):
            data_header['ma5'] = True
        self.sock.send(json.dumps(data_header).encode())
        response = self.get_response()

        # when the status code is 288, sending files is ready
        if response['status_code'] == 288:
            print('Ready to Send Files'.center(50, ' '))
            file_obj = open(file_abs_path, 'rb')
            file_size = os.path.getsize(file_abs_path)
            self.sock.send(json.dumps({'file_size': file_size}).encode())
            self.sock.recv(1)

            if data_header.get('md5'):
                md5_obj = hashlib.md5()
                for line in file_obj:
                    self.sock.send(line)
                    md5_obj.update(line)
                else:
                    file_obj.close()
                    self.sock.recv(1)
                    print(STATUS_CODE[258])

                    md5_val = md5_obj.hexdigest()
                    self.sock.send(json.dumps({'md5': md5_val}).encode())
                    md5_response = self.get_response()

                    if md5_response['status_code'] == 267:
                        print('[%s] %s!' % (base_filename, STATUS_CODE[267]))
                    else:
                        print('[%s] %s!' % (base_filename, STATUS_CODE[268]))
                    print('File Sending is done.'.center(50, ' '))
            else:  # No need to verify MD5
                for line in file_obj:  # send to the server directly
                    self.sock.send(line)
                else:
                    file_obj.close()
                    print('File Sending is done.'.center(50, ' '))

        else:  # Error occurs
            print(STATUS_CODE[256])

    def _put2(self, cmd_list):
        '''

        :param cmd_list:
        :return:
        '''
        print('put--', cmd_list)
        if len(cmd_list) == 1:
            print('Please type the correct file name:'.center(50, ' '))
            return

        filename = cmd_list[-1]
        print(filename)

        if os.path.isfile(filename):
            file_size = os.path.getsize(filename)
            data_header = {
                'action': 'put',
                'filename': filename,
                'filesize': file_size,
            }

            print('File Sending is ready.'.center(50, ' '))
            self.sock.send(json.dumps(data_header).encode())
            response = self.get_response()

            print(response)
            if response['status_code'] == 288:
                print('aa')
                received_size = 0
                received_data = b''
                print(file_size)

                while received_size < file_size:
                    f = open(filename, 'rb')
                    for line in f:
                        self.sock.send(line)
                        received_size += len(line)
                        received_data += line
                    else:
                        print('OK')
                        f.close()
        else:
            print('Invalid Options!'.center(50, ' '))

    def _get(self, cmd_list):
        '''
        Download file from the server
        :param cmd_list:
        :return:
        '''
        print('get--', cmd_list)
        if len(cmd_list) == 1:
            print('No Filename Follows...'.center(50, ' '))
            return
        data_header = {
            'action': 'get',
            'filename': cmd_list[1]
        }

        if self.__md5_required(cmd_list):
            data_header['md5'] = True
        self.sock.send(json.dumps(data_header).encode())
        response = self.get_response()
        print(response)

        if response['status_code'] == 257:  # get ready to receive
            self.sock.send(b'1')  # send a confirmation to server
            base_filename = cmd_list[1].split('/')[-1]
            received_size = 0
            file_obj = open(base_filename, "wb")

            if response['data']['file_size'] == 0:
                file_obj.close()
                return

            if self.__md5_required(cmd_list):
                md5_obj = hashlib.md5()
                progress = self.show_progress(response['data']['file_size'])  # generator
                progress.__next__()

                while received_size < response['data']['file_size']:
                    data = self.sock.recv(4096)
                    received_size += len(data)
                    try:
                        progress.send(len(data))
                    except StopIteration as e:
                        print('End with %s, 100%')

                    file_obj.write(data)
                    md5_obj.update(data)
                else:
                    print('File Receiving is Done'.center(50, ' '))
                    file_obj.close()
                    md5_val = md5_obj.hexdigest()
                    md5_from_server = self.get_response()
                    if md5_from_server['status_code'] == 258:
                        if md5_from_server['md5'] == md5_val:
                            print(('%s MD5 Verification is done.' % base_filename).center(50, ' '))

            else:
                progress = self.show_progress(response['data']['file_size'])
                progress.__next__()

                while received_size < response['data']['file_size']:
                    data = self.sock.recv(4096)
                    received_size += len(data)
                    file_obj.write(data)

                    try:
                        progress.send(len(data))
                    except StopIteration as e:
                        print('100%')

                else:
                    print('File Receiving is Done'.center(50, ' '))
                    file_obj.close()

    def _mkdir(self, cmd_list):
        '''
        Make a new directory
        :param cmd_list:
        :return:
        '''
        print('-mkdir', cmd_list)
        if len(cmd_list) == 1:
            print('No filename follows.'.center(50, ' '))
            return
        data_header = {
            'action': 'mkdir',
            'filename': cmd_list[1]
        }
        self.sock.send(json.dumps(data_header).encode())
        response = self.get_response()

        if response['status_code'] == 300:
            print('OK'.center(50, ' '))
        else:
            print('Failed'.center(50, ' '))

    def _touch(self, cmd_list):
        '''
        Create a new file
        :param cmd_list:
        :return:
        '''
        print('-- touch', cmd_list)
        if len(cmd_list) == 1:
            print('No filename follows.'.center(50, ' '))
            return
        data_header = {
            'action': 'touch',
            'filename': cmd_list[1]
        }
        self.sock.send(json.dumps(data_header).encode())
        response = self.get_response()

        if response['status_code'] == 300:
            print('OK')
        else:
            print('Failed')

    def _rm(self, cmd_list):
        '''
        Remove a file or directory
        :param cmd_list:
        :return:
        '''
        print('-- touch', cmd_list)
        if len(cmd_list) == 1:
            print('No filename follows.'.center(50, ' '))
            return
        data_header = {
            'action': 'rm',
            'filename': cmd_list[1],
        }
        self.sock.send(json.dumps(data_header).encode())
        response = self.get_response()
        if response['status_code'] == 300:
            print('OK')
        else:
            print('Failed')


if __name__ == '__main__':
    ftp = FTPClient()
    ftp.interactive()
