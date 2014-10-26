import yaml
import os
import globals

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

def dump(data):
    yamlFile = globals.ROOT+'/.gaea/gaea.yml'
    f = open(yamlFile, 'w')
    yaml.dump(data, f, default_flow_style=False)
    f.close()
