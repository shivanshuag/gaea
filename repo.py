import yaml
import os
import globals
import difflib
import helpers
import getpass
import grp
import pwd
from subprocess import Popen, PIPE

def LoadRepo():
    yamlFile = os.path.join(globals.ROOT, '.gaea', 'gaea.yml')
    peerFile = os.path.join(globals.ROOT, '.gaea', 'peers', 'peers.yml')
    if os.path.exists(yamlFile) and os.path.exists(peerFile):
        #print 'load repo : '+yamlFile+'path exists'
        f = open(yamlFile)
        dataMap = yaml.safe_load(f)
        f.close()
        globals.REPOINFO = dataMap
        f = open(peerFile)
        globals.PEERINFO = yaml.safe_load(f)
        globals.PEERINFO['peers'].update(helpers.mergePeers())
        yaml.dump(globals.PEERINFO,f,default_flow_style=False)
        f.close()
    else:
        raise Exception('Not a Gaea Repository')

def init():
    try:
        LoadRepo()
        print 'Already a repository'
        exit(0)
    except Exception, e:
        if os.path.exists(os.path.join(globals.ROOT, '.gaea')):
            p = Popen(['rm', '-rf', os.path.join(globals.ROOT, '.gaea')])
            p.wait()
        os.makedirs(os.path.join(globals.ROOT, '.gaea', 'snaps'))
        os.makedirs(os.path.join(globals.ROOT, '.gaea', 'peers'))
        dataMap = {'HEAD':'0', 'latestId':'0', 'author': '', 'email': '', 'remote':{} }
        helpers.dump(dataMap)
        initPeerDirec()
        print "new repo created"

def initPeerDirec(clonedPeers=None):
    username = raw_input('Username:')
    password = getpass.getpass('Password:')
    peerMap = {'username':username, 'password':password, 'ip':helpers.getIp() ,'path':globals.ROOT, 'peers':{}}
    if(clonedPeers!=None):
        peerMap['peers'].update(clonedPeers['peers'])
        peerMap['peers'][clonedPeers['ip']]={'username':clonedPeers['username'], 'password':clonedPeers['password'], 'path':clonedPeers['path']}
    #rootPassword = getpass.getpass('Give your system password:')
    try:
        grp.getgrnam('gaea')
    except KeyError:
        p1 = Popen(['sudo', 'groupadd', 'gaea'], stdout=PIPE, stdin=PIPE)
        p1.wait()
    #p1.communicate(rootPassword+'\n')
    try:
        pwd.getpwnam(username)
        print 'User '+username+' already exists. No new user created'
    except KeyError:
        p2 = Popen(['sudo','useradd', '-G',  'gaea', '-p', password, username], stdout=PIPE)
        p2.wait()
    #p2.communicate(rootPassword+'\n')
    p3 = Popen(['sudo','chgrp', '-R',  'gaea', globals.ROOT], stdout=PIPE)
    p3.wait()
    #p3.communicate(rootPassword+'\n')
    p4 = Popen(['sudo','chmod', '-R', 'g+rw', globals.ROOT], stdout=PIPE)
    p4.wait()
    #p4.communicate(rootPassword+'\n')
    helpers.dumpPeerDirec(peerMap)
    return peerMap


def diff(id1=None,id2=None):
    head = globals.REPOINFO['HEAD']
    if head != '0':
        if id1 == None:
            dir1 = os.path.join(globals.ROOT,'.gaea', 'snaps', head)
        else:
            id1 = helpers.getFullSnapId(id1)
            dir1 = os.path.join(globals.ROOT, '.gaea', 'snaps', id1)
        if id2 == None:
            dir2 = globals.ROOT
        else:
            id2 = helpers.getFullSnapId(id2)
            dir2 = os.path.join(globals.ROOT, '.gaea', 'snaps', id2)
        difference = ''
        filesDone = []
        for root, subFolders, files in os.walk(dir2):
            if '.gaea' in subFolders:
                subFolders.remove('.gaea')
            for f in files:
                filesDone.append(os.path.join(os.path.relpath(root, dir2),f))
                filePath1 = os.path.join(dir1, os.path.relpath(root, dir2), f)
                filePath2 = os.path.join(root, f)
                f1 = helpers.readFile(filePath1)
                f2 = helpers.readFile(filePath2)
                unifiedDiff = difflib.unified_diff(f1, f2, fromfile=filePath1, tofile=filePath2)
                difference = difference + ''.join(unifiedDiff)
        for root, subFolders, files in os.walk(dir1):
            if '.gaea' in subFolders:
                subFolders.remove('.gaea')
            for f in files:
                if os.path.join(os.path.relpath(root, dir1), f) not in filesDone:
                    filePath1 = os.path.join(root, f)
                    filePath2 = os.path.join(dir2, os.path.relpath(root, dir1), f)
                    f1 = helpers.readFile(filePath1)
                    f2 = helpers.readFile(filePath2)
                    unifiedDiff = difflib.unified_diff(f1, f2, fromfile=filePath1, tofile=filePath2)
                    difference = difference + ''.join(unifiedDiff)


    else:
         difference = 'No snapshot has been taken so far'
    return difference


def log():
    parent = globals.REPOINFO['latestId']
    log = ''
    while parent in globals.REPOINFO.keys():
        log = log + str(parent) + ':\n\tMessage - ' + globals.REPOINFO[parent]['message'] + '\n\tAuthor - '+globals.REPOINFO[parent]['author']+'\n\tTime-'+globals.REPOINFO[parent]['time']+'\n\n'
        parent = globals.REPOINFO[parent]['parent']
    return log

def setAuthor(author):
    globals.REPOINFO['author'] = author
    helpers.dump(globals.REPOINFO)

def setEmail(email):
    globals.REPOINFO['email'] = email
    helpers.dump(globals.REPOINFO)

def setRemote(name, address):
    globals.REPOINFO['remote'].update({name: address})
    helpers.dump(globals.REPOINFO)

