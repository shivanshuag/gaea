#!/usr/bin/python

import sys
import os

#import all the commands
import repo
import commit
import remote
import globals

#import clint libraries
from clint.arguments import Args
from clint.textui import puts, colored, indent

args = Args()
globals.init()
if len(args.all) == 1:
    if args.all[0] == 'init':
        try:
            repo.init()
        except Exception, e:
            print e
    elif args.all[0] == 'diff':
        try:
            repo.LoadRepo()
            diff = repo.diff()
            for line in iter(diff.splitlines()):
                if line[0]=='+' and line[1]!='+':
                    puts(colored.green(line))
                elif line[0]=='-' and line[2]!='-':
                    puts(colored.red(line))
                else:
                    puts(colored.white(line, False, True))
        except Exception, e:
            print e
    elif args.all[0] == 'log':
        try:
            repo.LoadRepo()
            print repo.log()
        except Exception, e:
            print e
    else:
        puts(colored.red("Incorrect Usage"))
elif len(args.all) == 2:
    if args.all[0] == 'restore':
        try:
            repo.LoadRepo()
            commit.restore(args.all[1])
        except Exception,e:
            print e
    elif args.all[0] == 'clone':
        try:
            remote.clone(args.all[1])
        except Exception,e:
            print e
    elif args.all[0] == 'pull':
        try:
            repo.LoadRepo()
            remote.pull(args.all[1])
        except Exception,e:
            print e
    elif args.all[0] == 'delete':
        try:
            repo.LoadRepo()
            commit.delete(args.all[1])
        except Exception,e:
            print e
    else:
        puts(colored.red("Incorrect Usage"))
elif len(args.all) == 3:
    if args.all[0] == 'snap':
        try:
            repo.LoadRepo()
            commit.snap(args.all[1], args.all[2])
        except Exception, e:
            print e
    elif args.all[0] == 'set':
        if args.all[1] == 'author':
            try:
                repo.LoadRepo()
                repo.setAuthor(args.all[2])
            except Exception,e:
                print e
    elif args.all[1] == 'email':
        try:
            repo.LoadRepo()
            repo.setEmail(args.all[2])
        except Exception, e:
            print e
elif len(args.all) == 4:
    if args.all[0] == 'set':
        if args.all[1] == 'remote':
            try:
                repo.LoadRepo()
                repo.setRemote(args.all[2], args.all[3])
            except Exception, e:
                print e
        else:
            puts(colored.red("Incorrect Usage"))
    else:
        puts(colored.red("Incorrect Usage"))

else:
    puts(colored.red("Incorrect Usage"))
    exit(0)
