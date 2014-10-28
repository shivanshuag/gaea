import globals
import os
import shutil
import repo
from datetime import datetime

def snap(message):
    if not repo.diff():
        raise Exception("No changes have been done since the last snap was taken")
    snapId = globals.REPOINFO['latestId'] + 1
    head = globals.REPOINFO['HEAD']
    globals.REPOINFO['latestId'] = snapId
    globals.REPOINFO['HEAD'] = head+1
    globals.REPOINFO[snapId] = {'parent': head, 'message': message, 'time': str(datetime.now()), 'author': '' }
    if head > 0:
        globals.REPOINFO[head]['child'] = snapId
    snapDir = os.path.join(globals.ROOT,'.gaea','snaps',str(snapId))
    if not os.path.exists(snapDir):
        os.makedirs(snapDir)
    files = [f for f in os.listdir(globals.ROOT) if os.path.isfile(os.path.join(globals.ROOT,f))]
    dirs = [f for f in os.listdir(globals.ROOT) if os.path.isdir(os.path.join(globals.ROOT,f)) and f!='.gaea']
    for directory in dirs:
        shutil.copytree(os.path.join(globals.ROOT, directory), os.path.join(snapDir,directory))
    for f in files:
        shutil.copy2(os.path.join(globals.ROOT,f), os.path.join(snapDir, f))

    repo.dump(globals.REPOINFO)

def restore(snapId):
    if int(snapId) not in globals.REPOINFO.keys():
        raise Exception("there is no snapshot by the id "+str(snapId))
    if repo.diff():
        raise Exception("You have some unsaved changes in the repository. Please take their snapshot before restoring to another snapshot otherwise you may loose them")
    globals.REPOINFO['HEAD'] = int(snapId)
    snapDir = os.path.join(globals.ROOT, '.gaea', 'snaps', snapId)
    print snapDir
    #delete all files
    files = [f for f in os.listdir(globals.ROOT) if os.path.isfile(os.path.join(globals.ROOT,f))]
    dirs = [f for f in os.listdir(globals.ROOT) if os.path.isdir(os.path.join(globals.ROOT,f)) and f!='.gaea']
    for directory in dirs:
        shutil.rmtree(os.path.join(globals.ROOT,directory))
    for f in files:
        os.remove(os.path.join(globals.ROOT, f))
    #copy the files back from snapshot directory
    files = [f for f in os.listdir(snapDir) if os.path.isfile(os.path.join(snapDir,f))]
    dirs = [f for f in os.listdir(snapDir) if os.path.isdir(os.path.join(snapDir,f)) and f!='.gaea']
    for directory in dirs:
        shutil.copytree(os.path.join(snapDir, directory), os.path.join(globals.ROOT, directory))
    for f in files:
        shutil.copy2(os.path.join(snapDir,f), os.path.join(globals.ROOT, f))
    repo.dump(globals.REPOINFO)
