# FTP-Master
# File Structure

├── .idea
│   ├── FTP_master.iml
│   ├── inspectionProfiles
│   ├── misc.xml
│   ├── modules.xml
│   └── workspace.xml
├── FTPClient
│   ├── __init__.py
│   └── ftp_client.py
├── FTPServer
│   ├── __init__.py
│   ├── bin
│   │   ├── __init__.py
│   │   └── ftp_server.py
│   ├── conf
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-36.pyc
│   │   │   └── settings.cpython-36.pyc
│   │   ├── accounts.cfg
│   │   ├── da.py
│   │   └── settings.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-36.pyc
│   │   │   ├── ftp_server.cpython-36.pyc
│   │   │   └── main.cpython-36.pyc
│   │   ├── ftp_server.py
│   │   └── main.py
│   └── home
│       └── __init__.py
├── README.md
└── __init__.py

# This is a Python poject, basing socket and re packes

# Running:
	For Server, in terminal:
		$ cd ~/FTP_master/FTPServer/bin/
		$ python ftp_server.py start
	For Client, in terminal:
		$ cd ~/FTP_master/FTPClient
		$ python ftp_client.py -s 127.0.0.1 -P25100 -uLightwing -pabc123
	Remarks:
		defaul account and passwords: Lightwing, abc123

# Menu:
[Lightwing]$:help
['help']

        get filename    # get file from FTP server
        put filename    # upload file to FTP server
        ls              # list files in current dir on FTP server
        pwd             # check current path on server
        cd path         # change directory , same usage as linux cd command
        touch           # touch file 
        rm              # rm file  rm director
        mkdir           # mkdir direcotr