#!/usr/bin/python

import sys
import os

#import all the commands
import repo
import commit
import globals

#import clint libraries
from clint.arguments import Args
from clint.textui import puts, colored, indent

args = Args()
globals.init()
print globals.ROOT
print args.all
if len(args.all) == 1:
    if args.all[0] == 'init':
        try:
            repo.init()
        except Exception, e:
            print 'exception'
            print e
if len(args.all) == 2:
    if args.all[0] == 'snap':
        try:
            repo.LoadRepo()
            commit.snap(args.all[1])
        except Exception, e:
            print e

