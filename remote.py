from paramiko import *
import paramiko
import getpass
from scp import SCPClient
from bzrlib.merge3 import Merge3

import sys
import os
import globals
import commit
import repo
import helpers
import shutil
import yaml
from subprocess import Popen, PIPE


def findCommonAncestor(remoteInfo, localInfo):
    lenRemote = helpers.findLength(remoteInfo)
    lenLocal = helpers.findLength(globals.REPOINFO)
    #print "remote lenght is"+str(lenRemote)
    #print "local length is"+str(lenLocal)
    if lenLocal > lenRemote:
        startRemote = remoteInfo['HEAD']
        startLocal = helpers.goToN(localInfo, lenLocal-lenRemote)
    elif lenRemote > lenLocal:
        startLocal = localInfo['HEAD']
        startRemote = helpers.goToN(remoteInfo, lenRemote-lenLocal)
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

def clone(ip, path, username, password, pull=False, rootPassword=None, newUsername=None, newPassword=None):
    print username
    print password
    print ip
    print path
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    ssh.connect(ip, username=username, password=password)
    scp = SCPClient(ssh.get_transport())
    scp.get(path, recursive=True)
    #after cloning, change the peerinfo file of the user
    oldroot = globals.ROOT
    globals.ROOT = os.path.join(globals.ROOT,os.path.basename(os.path.normpath(path)))
    print globals.ROOT
    sys.stdout.flush()
    #check if this is a gaea repo
    if not os.path.exists(os.path.join(globals.ROOT, '.gaea', 'snaps')) or not os.path.exists(os.path.join(globals.ROOT, '.gaea', 'peers')):
        globals.ROOT = oldroot
        raise Exception("cloned path "+username+"@"+ip+":"+path+" is not a gaea repository")
    f = open(os.path.join(globals.ROOT, '.gaea', 'peers', 'peers.yml'))
    clonedPeers = yaml.safe_load(f)
    f.close()
    clonedPeers['peers'].update(helpers.mergePeers())
    if not pull:
        myMap = repo.initPeerDirec(rootPassword, newUsername, newPassword, clonedPeers)
        print myMap
        #push my peerrinfo the remote user
        f = open(myMap['ip'], 'w')
        os.chmod(myMap['ip'], 0666)
        myPeerInfo = {myMap['ip']:{'username':myMap['username'], 'password':myMap['password'], 'path':myMap['path']}}
        yaml.dump(myPeerInfo, f, default_flow_style=False)
        f.close()
        scp.put(myMap['ip'], os.path.join(path, '.gaea', 'peers'))
        #change the permissions of pushed file
        ssh.exec_command('chmod 777 '+os.path.join(path, '.gaea', 'peers', myMap['ip']))
        os.remove(myMap['ip'])
    else:
        globals.PEERINFO['peers'].update(clonedPeers['peers'])
    ssh.close()



def pullAll():
    peerInfo = globals.PEERINFO['peers']
    abort = False
    print peerInfo.keys()
    for index,ip in enumerate(peerInfo.keys()):
        if 'pull' in globals.REPOINFO.keys():
            if index <= globals.REPOINFO['pull']:
                print "continuing " + str(index)
                continue

        #try:
        globals.REPOINFO['pull'] = index
        helpers.dump(globals.REPOINFO)
        pull(ip, peerInfo[ip]['path'], peerInfo[ip]['username'], peerInfo[ip]['password'])
        # except Exception,e:
        #     print e
        #     abort = True;
        #     break;
    if not abort:
        print "deleting"
        del globals.REPOINFO['pull']
        helpers.dump(globals.REPOINFO)
    pass

def pull(ip, path, username, password):
    if(repo.diff()):
        raise Exception('You have unsaved changes. Take their snapshot before pulling otherwise you may loose them.')
    pullPath = os.path.join(globals.ROOT, '.gaea', 'pull', (ip+":"+path).encode("hex"))
    if not os.path.exists(pullPath):
        os.makedirs(pullPath)
    os.chdir(pullPath)
    #TODO add print to give feedback to the user about what is being done
    print 'Pulling '+username+'@'+ip+':'+path
    #change the ROOT for clone to work
    previousRoot = globals.ROOT
    globals.ROOT = pullPath
    clone(ip, path, username, password, pull=True)
    globals.ROOT = previousRoot
    os.chdir(globals.ROOT)
    #dump the updated peerinfo back to repo
    helpers.dumpPeerDirec(globals.PEERINFO)
    conflicts, conflictCount = merge(pullPath, (ip+":"+path))
    if conflictCount > 0:
        s =  "Total "+str(conflictCount)+" conflicts in merge\nFix them and take a snapshot before running pull again"
        print s
        raise Exception("Merge Conflict in "+username+'@'+ip+':'+path + "\nFix them and take a snapshot before running pull again" + conflicts)
    else:
        if repo.diff():
            commit.snap('hard', "Merged HEAD from "+ (ip+":"+path))
    shutil.rmtree(pullPath)

def mergeLines(filePathBase, filePathNew, filePathLatest, copyPath, f, new=False):
    conflict = False
    conflicts = ''
    baseLines = helpers.readFile(filePathBase)
    newLines = helpers.readFile(filePathNew)
    latestLines = helpers.readFile(filePathLatest)

    mg = Merge3(baseLines, newLines, latestLines)
    merg = mg.merge_lines(name_a=filePathNew,name_b=filePathLatest,name_base=filePathBase, reprocess=True)
    merged = '\n'.join(merg)
    #print merged
    if merged:
        if '<<<<<<<' in merged:
            s = 'Merge conflict in file '+ os.path.join(copyPath,f)
            print s
            conflicts = conflicts + '\n' + s
            conflict = True
        else:
            print 'Merged without conflict '+ os.path.join(copyPath,f)
        if not os.path.exists(copyPath):
            os.makedirs(copyPath)
        f = open(os.path.join(copyPath, f), 'w')
        f.write(merged)
        f.close()
    elif new:
        print 'Deleting file after merge '+ os.path.join(copyPath,f)
    return conflicts, conflict


def merge(pullPath, address):
    conflictCount = 0
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
    files = helpers.getFiles(globals.ROOT)
    dirs = helpers.getDirs(globals.ROOT)
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
            if mergeLines(filePathBase, filePathNew, filePathLatest, copyPath, f):
                conflictCount += 1

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
                if mergeLines(filePathBase, filePathNew, filePathLatest, copyPath, f, new=True):
                    conflictCount += 1

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
                if mergeLines(filePathBase, filePathNew, filePathLatest, copyPath, f):
                    conflictCount += 1
    return conflictCount

def addPeer(ip, path, username, password):
    globals.PEERINFO['peers'].update({ip:{'path':path, 'username':username, 'password':password}})
    helpers.dumpPeerDirec(globals.PEERINFO)

def deletePeer(ip):
    del globals.PEERINFO['peers'][ip]
    helpers.dumpPeerDirec(globals.PEERINFO)

def syncPeer(ip, path, username, password):
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    ssh.connect(ip, username=username, password=password)
    scp = SCPClient(ssh.get_transport())
    scp.get(path, recursive=True)
    #after cloning, change the peerinfo file of the user
    globals.ROOT = os.path.join(globals.ROOT,os.path.basename(os.path.normpath(path)))
    #check if this is a gaea repo
    if not os.path.exists(os.path.join(globals.ROOT, '.gaea', 'snaps')) or not os.path.exists(os.path.join(globals.ROOT, '.gaea', 'peers')):
        raise Exception("cloned path "+username+"@"+ip+":"+path+" is not a gaea repository")
    f = open(os.path.join(globals.ROOT, '.gaea', 'peers', 'peers.yml'))
    clonedPeers = yaml.safe_load(f)
    f.close()
    clonedPeers['peers'].update(helpers.mergePeers())
    globals.PEERINFO['peers'].update(clonedPeers['peers'])
    helpers.dumpPeerDirec(globals.PEERINFO)
    shutil.rmtree(os.path.basename(os.path.normpath(path)))

