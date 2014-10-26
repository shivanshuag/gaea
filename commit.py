import globals
import os
import shutil
import repo

def snap(message):
    snapId = globals.REPOINFO['latestId'] + 1
    head = globals.REPOINFO['HEAD']
    globals.REPOINFO['latestId'] = snapId
    globals.REPOINFO['HEAD'] = head+1
    globals.REPOINFO[snapId] = {'parent': head, 'message': message }
    if head > 0:
        globals.REPOINFO[head]['child'] = snapId

    snapDir = os.path.join(globals.ROOT,'.gaea','snaps',str(snapId))
    if not os.path.exists(snapDir):
        os.makedirs(snapDir)
    files = [f for f in os.listdir(globals.ROOT) if os.path.isfile(os.path.join(globals.ROOT,f))]
    dirs = [f for f in os.listdir(globals.ROOT) if os.path.isdir(os.path.join(globals.ROOT,f)) and f!='.gaea']
    print files
    print dirs
    for directory in dirs:
        shutil.copytree(os.path.join(globals.ROOT, directory), os.path.join(snapDir,directory))
    for f in files:
        shutil.copy2(os.path.join(globals.ROOT,f), os.path.join(snapDir, f))

    repo.dump(globals.REPOINFO)
