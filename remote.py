from paramiko import *
import paramiko
import getpass
from scp import SCPClient
from bzrlib.merge3 import Merge3

import os
import globals
import commit
import repo
import shutil
import yaml

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

def findCommonAncestor(remoteInfo, localInfo):
    lenRemote = findLength(remoteInfo)
    lenLocal = findLength(globals.REPOINFO)
    #print "remote lenght is"+str(lenRemote)
    #print "local length is"+str(lenLocal)
    if lenLocal > lenRemote:
        startRemote = remoteInfo['HEAD']
        startLocal = goToN(localInfo, lenLocal-lenRemote)
    elif lenRemote > lenLocal:
        startLocal = localInfo['HEAD']
        startRemote = goToN(remoteInfo, lenRemote-lenLocal)
    else:
        startLocal = localInfo['HEAD']
        startRemote = remoteInfo['HEAD']
    #print 'Start local '+startLocal
    #print 'Start Remote '+startRemote
    while 1:
        if startLocal == '0' or startRemote == '0':
            raise Exception('''History of the remote branch doesnt match the History of local branch.
            Unable to find a common ancestor''')
        if startLocal == startRemote:
            return startLocal
        startLocal = localInfo[startLocal]['parent']
        startRemote = remoteInfo[startRemote]['parent']

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

def pull(address):
    if(commit.diff()):
        raise Exception('You have unsaved changes. Take their snapshot before pulling otherwise you may loose them.')
    pullPath = os.path.join(globals.ROOT, '.gaea', 'pull', address.encode("hex"))
    if not os.path.exists(pullPath):
        os.makedirs(pullPath)
    os.chdir(pullPath)
    #TODO add print to give feedback to the user about what is being done
    clone(address)
    merge(pullPath, address)

def mergeLines(filePathBase, filePathNew, filePathLatest, copyPath, f, new=False):
    baseLines = repo.readFile(filePathBase)
    newLines = repo.readFile(filePathNew)
    latestLines = repo.readFile(filePathLatest)

    mg = Merge3(baseLines, newLines, latestLines)
    merg = mg.merge_lines(name_a=filePathNew,name_b=filePathLatest,name_base=filePathBase, reprocess=True)
    merged = '\n'.join(merg)
    #print merged
    if merged:
        if '<<<<<<<' in merged:
            print 'Merge conflict in file '+ os.path.join(copyPath,f)
        else:
            print 'Merged without conflict '+ os.path.join(copyPath,f)
        if not os.path.exists(copyPath):
            os.makedirs(copyPath)
        f = open(os.path.join(copyPath, f), 'w')
        f.write(merged)
        f.close()
    elif new:
        print 'Deleting file after merge '+ os.path.join(copyPath,f)


def merge(pullPath, address):
    remoteYaml = os.path.join(pullPath, os.listdir(pullPath)[0], '.gaea', 'gaea.yml');
    if os.path.exists(remoteYaml):
        f = open(remoteYaml)
        remoteInfo = yaml.safe_load(f)
        f.close()
    else:
        raise Exception(address+' is not a Gaea Repository')
    #check if merge is required
    if remoteInfo['HEAD'] == globals.REPOINFO['HEAD']:
        print "Remote HEAD is same as local. No merge required"
        return
    #find first common ancestor between remote and local
    ancestorId = findCommonAncestor(remoteInfo, globals.REPOINFO)
    #print "Common ancestor id is " + ancestorId
    basePath = os.path.join(globals.ROOT, '.gaea', 'snaps', ancestorId)
    newPath = os.path.join(globals.ROOT, '.gaea', 'snaps', globals.REPOINFO['HEAD'])
    latestPath = os.path.join(pullPath, os.listdir(pullPath)[0], '.gaea', 'snaps', remoteInfo['HEAD'])

    #delete all the current files in the repo
    files = commit.getFiles(globals.ROOT)
    dirs = commit.getDirs(globals.ROOT)
    for directory in dirs:
        shutil.rmtree(os.path.join(globals.ROOT,directory))
    for f in files:
        os.remove(os.path.join(globals.ROOT, f))
    filesDone = []
    #merge all the files present in base
    for root, subFolders, files in os.walk(basePath):
        if '.gaea' in subFolders:
            subFolders.remove('.gaea')
        copyPath = os.path.join(globals.ROOT, os.path.relpath(root, basePath))
        #print "copyPath is "+copyPath
        for f in files:
            filesDone.append(os.path.join(os.path.relpath(root, basePath),f))
            filePathBase = os.path.join(root, f)
            filePathNew = os.path.join(newPath, os.path.relpath(root, basePath), f)
            filePathLatest = os.path.join(latestPath, os.path.relpath(root, basePath), f)
            mergeLines(filePathBase, filePathNew, filePathLatest, copyPath, f)

    #merge files only in new
    for root, subFolders, files in os.walk(newPath):
        if '.gaea' in subFolders:
            subFolders.remove('.gaea')
        copyPath = os.path.join(globals.ROOT, os.path.relpath(root, newPath))
        if not os.path.exists(copyPath):
            os.makedirs(copyPath)
        for f in files:
            if os.path.join(os.path.relpath(root, newPath), f) not in filesDone:
                filesDone.append(os.path.join(os.path.relpath(root, newPath),f))
                filePathBase = os.path.join(basePath, os.path.relpath(root, newPath), f)
                filePathNew = os.path.join(root, f)
                filePathLatest = os.path.join(latestPath, os.path.relpath(root, newPath), f)
                mergeLines(filePathBase, filePathNew, filePathLatest, copyPath, f, new=True)

    #merge files only in latest
    for root, subFolders, files in os.walk(latestPath):
        if '.gaea' in subFolders:
            subFolders.remove('.gaea')
        copyPath = os.path.join(globals.ROOT, os.path.relpath(root, latestPath))
        if not os.path.exists(copyPath):
            os.makedirs(copyPath)
        for f in files:
            if os.path.join(os.path.relpath(root, latestPath), f) not in filesDone:
                filesDone.append(os.path.join(os.path.relpath(root, latestPath),f))
                filePathBase = os.path.join(basePath, os.path.relpath(root, newPath), f)
                filePathNew = os.path.join(newPath, os.path.relpath(root,newPath), f)
                filePathLatest = os.path.join(root, f)
                mergeLines(filePathBase, filePathNew, filePathLatest, copyPath, f)
