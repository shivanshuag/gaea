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
            return dataMap
        else:
            raise Exception('Not a Gaea Repository')
    else:
        raise Exception('Not a Gaea Repository')

def init():
    try:
        repo = LoadRepo()
        print 'Already a repository'
        exit(0)
    except Exception, e:
        if not os.path.exists(globals.ROOT+'/.gaea'):
            os.makedirs(globals.ROOT+'/.gaea')
        yamlFile = globals.ROOT+'/.gaea/gaea.yml'
        f = open(yamlFile, 'w')
        dataMap = {'HEAD':0, 'latestId':0 }
        yaml.dump(dataMap, f, default_flow_style=False)
        f.close()
