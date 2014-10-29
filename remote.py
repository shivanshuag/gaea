from paramiko import *
import paramiko
import getpass
from scp import SCPClient
import os

def clone(address):
    address = address.split(':')
    password = getpass.getpass('Password:')
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    addSplit = address[0].split('@')
    if(len(addSplit) == 2):
        ssh.connect(addSplit[1], username=addSplit[0], password=password)
    else:
        ssh.connect(addSplit[0])

    scp = SCPClient(ssh.get_transport())
    scp.get(address[1], recursive=True)

