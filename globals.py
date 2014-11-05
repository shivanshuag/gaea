import os

def init():
    global ROOT
    global REPOINFO
    ROOT = os.getcwd()

def changeCWD(strng):
	global ROOT
	ROOT = str(strng)

