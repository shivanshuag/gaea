import yaml
import os
import globals
import difflib

def LoadRepo():
    yamlFile = globals.ROOT+'/.gaea/gaea.yml'
    if os.path.exists(yamlFile):
        print 'load repo : '+yamlFile+'path exists'
        f = open(yamlFile)
        dataMap = yaml.safe_load(f)
        f.close()
        if(dataMap['HEAD'] >= 0 and dataMap['latestId'] >= 0):
            globals.REPOINFO = dataMap
        else:
            raise Exception('Not a Gaea Repository')
    else:
        raise Exception('Not a Gaea Repository')

def init():
    try:
        LoadRepo()
        print 'Already a repository'
        exit(0)
    except Exception, e:
        if not os.path.exists(globals.ROOT+'/.gaea'):
            os.makedirs(globals.ROOT+'/.gaea')
        if not os.path.exists(globals.ROOT+'/.gaea/snaps'):
            os.makedirs(globals.ROOT+'/.gaea/snaps')
        dataMap = {'HEAD':0, 'latestId':0, 'author': '', 'email': '', 'remote':{} }
        dump(dataMap)
        print "new repo created"


def diff():
     head = globals.REPOINFO['HEAD']
     if head > 0:
         headDir = os.path.join(globals.ROOT,'.gaea', 'snaps', str(head))
         difference = ''
         for root, subFolders, files in os.walk(globals.ROOT):
            if '.gaea' in subFolders:
                subFolders.remove('.gaea')
            for f in files:
                filePath = os.path.join(root, f)
                headFilePath = os.path.join(headDir, os.path.relpath(root, globals.ROOT), f)
                f1 = open(filePath, 'r')
                f2 = open(headFilePath, 'r')
                unifiedDiff = difflib.unified_diff(f2.readlines(), f1.readlines(), fromfile=headFilePath, tofile=filePath)
                difference = difference + ''.join(unifiedDiff)
                f1.close()
                f2.close()
     else:
         difference = 'No snapshot has been taken so far'
     return difference


def log():
    parent = globals.REPOINFO['latestId']
    log = ''
    while parent in globals.REPOINFO.keys():
        log = log + str(parent) + ':\t' + globals.REPOINFO[parent]['message'] + '\n\n\n'
        parent = globals.REPOINFO[int(parent)]['parent']
    return log

def setAuthor(author):
    globals.REPOINFO['author'] = author
    dump(globals.REPOINFO)

def setEmail(email):
    globals.REPOINFO['email'] = email
    dump(globals.REPOINFO)

def setRemote(name, address):
    globals.REPOINFO['remote'].update({name: address})
    dump(globals.REPOINFO)

def dump(data):
    yamlFile = globals.ROOT+'/.gaea/gaea.yml'
    f = open(yamlFile, 'w')
    yaml.dump(data, f, default_flow_style=False)
    f.close()
