import yaml
import os
import globals
import difflib

def LoadRepo():
    yamlFile = globals.ROOT+'/.gaea/gaea.yml'
    if os.path.exists(yamlFile):
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
        dataMap = {'HEAD':0, 'latestId':0 }
        dump(dataMap)

def diff():
     head = globals.REPOINFO['HEAD']
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
     return difference

def dump(data):
    yamlFile = globals.ROOT+'/.gaea/gaea.yml'
    f = open(yamlFile, 'w')
    yaml.dump(data, f, default_flow_style=False)
    f.close()
