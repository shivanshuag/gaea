import globals
import os
import shutil
import repo
from datetime import datetime
from hashlib import md5
from random import randint



#lists all the files inside a folder
def getFiles(root):
    return [f for f in os.listdir(root) if os.path.isfile(os.path.join(root,f))]

#lists all the directories inside a folder excpet '.gaea' directory
def getDirs(root):
    return [f for f in os.listdir(root) if os.path.isdir(os.path.join(root,f)) and f!='.gaea']

#find the full id of the snapshot by matching substring of all the keys
def getFullSnapId(snapId):
    if len(snapId) < 6:
        raise Exception("Provide at least 6 characters of id")
    found = False
    keys = globals.REPOINFO.keys()
    keys.remove("HEAD")
    keys.remove("latestId")
    keys.remove("author")
    keys.remove("email")
    keys.remove("remote")
    for key in keys:
        if snapId in key:
            snapId = key
            found = True
            break
    if not found:
        raise Exception("There is no snapshot by the id "+snapId)
    return snapId


def snap(snapType, message):

    #give error if no changes have been made
    diff = repo.diff()
    if not diff:
        raise Exception("No changes have been done since the last snap was taken")

    #check for commit type
    if snapType != 'soft' and snapType != 'hard':
        raise Exception("Commit type can only be hard or soft")

    #calculate commit ID which is hash of the diff
    snapId = md5(diff).hexdigest() + str(randint(0,100000))

    head = globals.REPOINFO['HEAD']
    latestId = globals.REPOINFO['latestId']
    if head != latestId:
        raise Exception('''You are not at the latest sanpshot.
        Either go to latest snapshot or delete all the snapshots ahead of the current snapshot''')

    globals.REPOINFO['HEAD'] = snapId
    globals.REPOINFO['latestId'] = snapId
    globals.REPOINFO[snapId] = {'type':snapType, 'parent': head, 'message': message, 'time': str(datetime.now()), 'author': globals.REPOINFO['author'] }

    #set the new snapshot as the child of previous snapshot
    if head != '0':
        globals.REPOINFO[head]['child'] = snapId

    #copy all the files/folders to the snapshot directory
    snapDir = os.path.join(globals.ROOT,'.gaea','snaps',snapId)
    if not os.path.exists(snapDir):
        os.makedirs(snapDir)
    files = getFiles(globals.ROOT)
    dirs = getDirs(globals.ROOT)
    for directory in dirs:
        shutil.copytree(os.path.join(globals.ROOT, directory), os.path.join(snapDir,directory))
    for f in files:
        shutil.copy2(os.path.join(globals.ROOT,f), os.path.join(snapDir, f))

    repo.dump(globals.REPOINFO)

def restore(snapId):
    snapId = getFullSnapId(snapId)
    #give error if there are some unsaved changes present
    if repo.diff():
        raise Exception('''You have some unsaved changes in the repository.
        Please take their snapshot before restoring to another snapshot otherwise you may loose them''')

    globals.REPOINFO['HEAD'] = snapId
    snapDir = os.path.join(globals.ROOT, '.gaea', 'snaps', snapId)

    #delete all files/folders from ROOT
    files = getFiles(globals.ROOT)
    dirs = getDirs(globals.ROOT)
    for directory in dirs:
        shutil.rmtree(os.path.join(globals.ROOT,directory))
    for f in files:
        os.remove(os.path.join(globals.ROOT, f))

    #copy the files back from snapshot directory to the ROOT directory
    files = getFiles(snapDir)
    dirs = getDirs(snapDir)
    for directory in dirs:
        shutil.copytree(os.path.join(snapDir, directory), os.path.join(globals.ROOT, directory))
    for f in files:
        shutil.copy2(os.path.join(snapDir,f), os.path.join(globals.ROOT, f))
    repo.dump(globals.REPOINFO)


def delete(snapId):
    snapId = getFullSnapId(snapId)

    head = globals.REPOINFO['HEAD']
    latest = globals.REPOINFO['latestId']
    parent = globals.REPOINFO['parent']
    if 'child' in globals.REPOINFO[snapId].keys():
        child = globals.REPOINFO[snapId]['child']
        if parent != '0':
            globals.REPOINFO[parent]['child'] = globals.REPOINFO[snapId]['child']
        globals.REPOINFO[child]['parent'] = parent
    else:
        if parent != '0':
            del globals.REPOINFO[parent]['child']

    snapDir = os.path.join(globals.ROOT, '.gaea', 'snaps', snapId)
    shutil.rmtree(snapDir)
    repo.dump(globals.REPOINFO)
