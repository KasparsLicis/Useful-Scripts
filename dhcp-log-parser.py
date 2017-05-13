#usually only smb module is missing, we can install it by pip install pysmb
import os
import shutil
import socket
from smb.SMBConnection import SMBConnection
import sys

##Variable section
USER_ID="user_name"
PASSWORD="user_password"
DOMAIN_NAME="server_domain_name"
CLIENT_MACHINE_NAME = "localpcname"
DHCP_SHARE_NAME="DHCP_logs"
TMP_FOLDER="/tmp/dhcp_tmp"
FIN_FOLDER="/root/Desktop/DHCP_33"
servers = ['server1','server2', 'server3', 'server4']
files=['DhcpSrvLog-Fri.log','DhcpSrvLog-Mon.log', 'DhcpSrvLog-Sat.log','DhcpSrvLog-Sun.log','DhcpSrvLog-Thu.log','DhcpSrvLog-Tue.log','DhcpSrvLog-Wed.log']

def errorHandlerAndExit(error):
    print error
    sys.exc_info()[0]
    sys.exit(0)

def createFolderStructure(folder):
    try:
	    shutil.rmtree(folder)
	except:
	    print 'Folder does not exist, skipping ..'+folder
    try:
        os.makedirs(folder)
    except:
        errorHandlerAndExit('Error: Cannot create folder. Exiting:'+folder)

def connectAndDownloadLogs(x):
    try:
        server_ip = socket.gethostbyname(x)
        conn = SMBConnection(USER_ID, PASSWORD, CLIENT_MACHINE_NAME, x, domain=DOMAIN_NAME, use_ntlm_v2=True,
                             is_direct_tcp=True)
        conn.connect(server_ip, 445)
        shares = conn.listShares()
    except:
        errorHandlerAndExit('Error: Cannot connect to server. Check network and credentials. Exiting')

    for share in shares:
        try:
            if share.name == DHCP_SHARE_NAME:
                sharedfiles = conn.listPath(share.name, '/')
                for sharedfile in sharedfiles:
                    if sharedfile.filename in files:
                        file_obj = open(os.path.join(TMP_FOLDER, sharedfile.filename), 'w')
                        conn.retrieveFile(share.name, sharedfile.filename, file_obj)
                        file_obj.close()
        except:
            errorHandlerAndExit('Error: Downloading error. Exiting')
    conn.close()

def parseLogsAndSaveResult():
    f = open(os.path.join(FIN_FOLDER, 'result.txt'), 'a+')
##can crash if not all week logs are awailable in folder
    for d in files:
        for line in open(os.path.join(TMP_FOLDER, d), 'r'):
            if ('DNS Update Request' in line):
                fields = line.split(',')
                f.write(fields[1] + ',' + fields[2] + ',' + fields[4] + ',' + fields[5] + '\n')
    f.close()

def main():
    createFolderStructure(FIN_FOLDER)
    for x in servers:
        createFolderStructure(TMP_FOLDER)
        connectAndDownloadLogs(x)
        parseLogsAndSaveResult()

if __name__ == "__main__":
    main()
