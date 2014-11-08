import os
import socket
import yaml
import globals

def dump(data):
    yamlFile = os.path.join(globals.ROOT, '.gaea', 'gaea.yml')
    f = open(yamlFile, 'w')
    yaml.dump(data, f, default_flow_style=False)
    f.close()

def dumpPeerDirec(data):
    direc = os.path.join(globals.ROOT, '.gaea', 'peers')
    fil = os.path.join(direc, 'peers.yml')
    if not os.path.exists(direc):
        os.makedirs(direc)
    f = open(fil, 'w')
    yaml.dump(data, f, default_flow_style=False)
    f.close()

def mergePeers():
    direc = os.path.join(globals.ROOT, '.gaea', 'peers')
    files = getFiles(direc)
    peers = {}
    for fil in files:
        if fil == 'peers.yml':
            continue
        filePath = os.path.join(direc,fil)
        f = open(filePath)
        dic = yaml.safe_load(f)
        f.close()
        peers.update(dic)
        os.remove(filePath)
    return peers

def readFile(path):
    output = []
    if os.path.isfile(path):
        f1 = open(path, 'r')
        output = f1.readlines()
        f1.close()
    return output

#lists all the files inside a folder
def getFiles(root):
    return [f for f in os.listdir(root) if os.path.isfile(os.path.join(root,f))]

#lists all the directories inside a folder excpet '.gaea' directory
def getDirs(root):
    return [f for f in os.listdir(root) if os.path.isdir(os.path.join(root,f)) and f!='.gaea']

#find the full id of the snapshot by matching substring of all the keys
def getFullSnapId(snapId):
    if len(snapId) < 6:
        raise Exception("Provide at least 6 characters of id")
    found = False
    keys = globals.REPOINFO.keys()
    keys.remove("HEAD")
    keys.remove("latestId")
    keys.remove("author")
    keys.remove("email")
    keys.remove("remote")
    for key in keys:
        if snapId in key:
            snapId = key
            found = True
            break
    if not found:
        raise Exception("There is no snapshot by the id "+snapId)
    return snapId

def findLength(repoInfo):
    node = repoInfo[repoInfo['HEAD']]
    length = 1
    while node['parent'] != '0':
        node = repoInfo[node['parent']]
        length+=1
    return length

def goToN(repoInfo, n):
    output = repoInfo['HEAD']
    for i in range(0,n):
        output = repoInfo[output]['parent']
    return output

def getIp():
    try:
        host = socket.gethostname()
        ip = socket.gethostbyname(host)
    except:
        ip = raw_input("Give you hostname or IP address:")
    return ip
