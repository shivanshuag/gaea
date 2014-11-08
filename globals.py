import os

def init():
    global ROOT
    global REPOINFO
    global PEERINFO
    ROOT = os.getcwd()

def changeCWD(strng):
	global ROOT
	ROOT = str(strng)

