import yaml
import os
import globals
import difflib
import commit

def readFile(path):
    output = []
    if os.path.isfile(path):
        f1 = open(path, 'r')
        output = f1.readlines()
        f1.close()
    return output

def LoadRepo():
    yamlFile = globals.ROOT+'/.gaea/gaea.yml'
    if os.path.exists(yamlFile):
        #print 'load repo : '+yamlFile+'path exists'
        f = open(yamlFile)
        dataMap = yaml.safe_load(f)
        f.close()
        globals.REPOINFO = dataMap
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
        dataMap = {'HEAD':'0', 'latestId':'0', 'author': '', 'email': '', 'remote':{} }
        dump(dataMap)
        print "new repo created"


def diff(id1=None,id2=None):
    head = globals.REPOINFO['HEAD']
    if head != '0':
        if id1 == None:
            dir1 = os.path.join(globals.ROOT,'.gaea', 'snaps', head)
        else:
            id1 = commit.getFullSnapId(id1)
            dir1 = os.path.join(globals.ROOT, '.gaea', 'snaps', id1)
        if id2 == None:
            dir2 = globals.ROOT
        else:
            id2 = commit.getFullSnapId(id2)
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
                f1 = readFile(filePath1)
                f2 = readFile(filePath2)
                unifiedDiff = difflib.unified_diff(f1, f2, fromfile=filePath1, tofile=filePath2)
                difference = difference + ''.join(unifiedDiff)
        for root, subFolders, files in os.walk(dir1):
            if '.gaea' in subFolders:
                subFolders.remove('.gaea')
            for f in files:
                if os.path.join(os.path.relpath(root, dir1), f) not in filesDone:
                    filePath1 = os.path.join(root, f)
                    filePath2 = os.path.join(dir2, os.path.relpath(root, dir1), f)
                    f1 = readFile(filePath1)
                    f2 = readFile(filePath2)
                    unifiedDiff = difflib.unified_diff(f1, f2, fromfile=filePath1, tofile=filePath2)
                    difference = difference + ''.join(unifiedDiff)


    else:
         difference = 'No snapshot has been taken so far'
    return difference


def log():
    parent = globals.REPOINFO['latestId']
    log = ''
    while parent in globals.REPOINFO.keys():
        log = log + str(parent) + ':\tMessage - ' + globals.REPOINFO[parent]['message'] + '\n\tAuthor - '+globals.REPOINFO[parent]['author']+'\n\tTime-'+globals.REPOINFO[parent]['time']+'\n\n'
        parent = globals.REPOINFO[parent]['parent']
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
