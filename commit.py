import globals
import os
import shutil
import repo
import helpers
from datetime import datetime
from hashlib import md5
from random import randint

def snap(snapType, message):

    #give error if no changes have been made
    diff = repo.diff()
    if not diff:
        raise Exception("No changes have been done since the last snap was taken")

    #check for commit type
    if snapType != 'soft' and snapType != 'hard':
        raise Exception("Commit type can only be hard or soft")

    #calculate commit ID which is hash of the diff
    snapId = md5(diff).hexdigest()

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
    files = helpers.getFiles(globals.ROOT)
    dirs = helpers.getDirs(globals.ROOT)
    for directory in dirs:
        shutil.copytree(os.path.join(globals.ROOT, directory), os.path.join(snapDir,directory))
    for f in files:
        shutil.copy2(os.path.join(globals.ROOT,f), os.path.join(snapDir, f))

    helpers.dump(globals.REPOINFO)


def restore(snapId):
    snapId = helpers.getFullSnapId(snapId)
    #give error if there are some unsaved changes present
    if repo.diff():
        raise Exception('''You have some unsaved changes in the repository.
        Please take their snapshot before restoring to another snapshot otherwise you may loose them''')

    globals.REPOINFO['HEAD'] = snapId
    snapDir = os.path.join(globals.ROOT, '.gaea', 'snaps', snapId)

    #delete all files/folders from ROOT
    files = helpers.getFiles(globals.ROOT)
    dirs = helpers.getDirs(globals.ROOT)
    for directory in dirs:
        shutil.rmtree(os.path.join(globals.ROOT,directory))
    for f in files:
        os.remove(os.path.join(globals.ROOT, f))

    #copy the files back from snapshot directory to the ROOT directory
    files = helpers.getFiles(snapDir)
    dirs = helpers.getDirs(snapDir)
    for directory in dirs:
        shutil.copytree(os.path.join(snapDir, directory), os.path.join(globals.ROOT, directory))
    for f in files:
        shutil.copy2(os.path.join(snapDir,f), os.path.join(globals.ROOT, f))
    helpers.dump(globals.REPOINFO)


def delete(snapId):
    snapId = helpers.getFullSnapId(snapId)

    head = globals.REPOINFO['HEAD']
    latest = globals.REPOINFO['latestId']
    parent = globals.REPOINFO[snapId]['parent']
    if 'child' in globals.REPOINFO[snapId].keys():
        child = globals.REPOINFO[snapId]['child']
        if parent != '0':
            globals.REPOINFO[parent]['child'] = globals.REPOINFO[snapId]['child']
        globals.REPOINFO[child]['parent'] = parent
    else:
        if parent != '0':
            del globals.REPOINFO[parent]['child']
    del globals.REPOINFO[snapId]
    snapDir = os.path.join(globals.ROOT, '.gaea', 'snaps', snapId)
    shutil.rmtree(snapDir)
    helpers.dump(globals.REPOINFO)
