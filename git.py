import sys
from PyQt4 import QtCore, QtGui, uic

import gaea
import globals
import repo
import commit

#import clint libraries
from clint.arguments import Args
from clint.textui import puts, colored, indent

form_class = uic.loadUiType("git.ui")[0]                 # Load the UI

class MyWindowClass(QtGui.QMainWindow, form_class):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.but_openFile.clicked.connect(self.openFile)
        self.but_name.clicked.connect(self.setName)
        self.but_email.clicked.connect(self.setEmail)
        self.but_push.clicked.connect(self.push)
        self.but_pull.clicked.connect(self.pull)
        self.but_commit.clicked.connect(self.snap)
        self.but_init.clicked.connect(self.init)
        self.but_log.clicked.connect(self.log)
        self.but_restore.clicked.connect(self.restore)


        qtable_history = self.table_history
        qtable_history.setColumnCount(4)
        listOfLables = ['first', 'middle', 'last', 'department']

        header = qtable_history.horizontalHeader()
        header.setResizeMode(QtGui.QHeaderView.Stretch)
                
        qtable_history.setHorizontalHeaderLabels(listOfLables)
        self.populateTable(qtable_history)

        self.displayDiff()

        self.actionNew_Project.setShortcut('Ctrl+N')
        self.actionNew_Project.triggered.connect(self.newProject)

        self.actionOpne_Project.setShortcut('Ctrl+O')
        self.actionOpne_Project.triggered.connect(self.openFile)

        self.actionExit.setShortcut('Alt+F4')
        self.actionExit.triggered.connect(self.exit)
        print "cwd is " + globals.ROOT

    def openFile(self):
#    	fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        fname = QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', '\home')
    	self.txt_path1.setText(fname)
        globals.changeCWD(fname)
        print "ROOT name changed to ", fname

    def newProject(self):
    	self.txt_path1.setText("new project")

    def exit(self):
        quit_msg = "Are you sure you want to exit the program?"
        reply = QtGui.QMessageBox.question(self, 'Message', 
                         quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            sys.exit(0)

    def setName(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 'Enter your name:')
        
        if ok:
            print "name is ", str(text)
            try:
                repo.LoadRepo()
                repo.setAuthor(str(text))
            except Exception,e:
                print e

    def setEmail(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 'Enter your email address:')
        
        if ok:
            print "email is ", str(text)
            try:
                repo.LoadRepo()
                repo.setEmail(str(text))
            except Exception, e:
                print e

    
    def populateTable(self, qtable):
        array = [["mohit", "kumar", "garg", "cse"], ["gaurav", "gautam", "-", "phy"]]
        print "populateTable called"

        for row in range(2):
            qtable.insertRow(row)
            for column in range(4):
                qtable.setItem(row, column, QtGui.QTableWidgetItem(QtCore.QString("%1").arg(array[row][column])))

    def snap(self):
        print "commit button pressed"
        # here put a check for changes... if no change has been made then don't allow commit
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 'Enter your name:')
        if ok:
            print "message is ", str(text)
            try:
                repo.LoadRepo()
                commit.snap(str(text))
                print "commit successfull"
            except Exception, e:
                print e

    def push(self):
        print "push button pressed"

    def pull(self):
        print "pull button pressed"

    def displayDiff(self):
        try:
            repo.LoadRepo()
            diff = repo.diff()
            for line in iter(diff.splitlines()):
                if line[0]=='+' and line[1]!='+':
                    puts(colored.red(line))
                elif line[0]=='-' and line[2]!='-':
                    puts(colored.green(line))
                else:
                    puts(colored.white(line, False, True))
        except Exception, e:
            print e
        self.edit_diff.setText("diff of two commits comes here")  

    def init(self): 
        repo.init()
        print "init function called"

    def log(self):
        print "log button pressed"
        try:
            repo.LoadRepo()
            print "log starts"
            print repo.log()
        except Exception, e:
            print e

    def restore(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 'Enter commit id:')
        if ok:
            print "commit id is ", str(text)
            try:
                repo.LoadRepo()
                commit.restore(str(text))
            except Exception,e:
                print e

app = QtGui.QApplication(sys.argv)
myWindow = MyWindowClass(None)
myWindow.show()
app.exec_()