import sys
from PyQt4 import QtCore, QtGui, uic
from random import *

#import gaea
import globals
import repo
import commit

#import clint libraries
from clint.arguments import Args
from clint.textui import puts, colored, indent

form_class = uic.loadUiType("git.ui")[0]                 # Load the UI

class InitPromptWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        uic.loadUi('initui.ui',self)
        self.setWindowTitle("Init Prompt")
        self.resize(350,400)
        self.move(500, 500)
        self.but.clicked.connect(self.init)
        self.editPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.editRootPassword.setEchoMode(QtGui.QLineEdit.Password)

    def init(self):
        print "button clicked"
        name = self.editName.text()
        print "name is ", name

        Password = self.editPassword.text()
        print "password is ", Password

        RootPassword = self.editRootPassword.text()
        print "password is ", RootPassword

class CommitPromptWindow(QtGui.QMainWindow):
    t = 0
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        uic.loadUi('commitui.ui',self)
        self.setWindowTitle("Commit Prompt")
        self.resize(350,200)
        self.move(500, 500)
        self.but.clicked.connect(self.commit)
        self.radioSoft.setChecked(True)
        self.radioHard.setChecked(False)
    #    self.radioSoft.toggled.connect(self.softClick)
        self.radioHard.toggled.connect(self.hardClick)
    
    def commit(self):
        print "button clicked"
        message = self.editMessage.text()
        print "msg is ", message, " toggle is ", self.t

    def softClick(self):
        self.t = 1 - self.t
        print "toggle ", t
        # self.radioSoft.setChecked(True)
        # self.radioHard.setChecked(False)

    def hardClick(self):
        self.t = 1 - self.t
        print "toggle ", self.t
        # self.radioSoft.setChecked(False)
        # self.radioHard.setChecked(True)



class CloneWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        uic.loadUi('prompt.ui',self)
        self.setWindowTitle("Clone")
        self.resize(350,400)
        self.move(500, 500)
        self.but.clicked.connect(self.clone)
        self.editPassword.setEchoMode(QtGui.QLineEdit.Password)

    def clone(self):
        print "button clicked"
        IP = self.editIP.text()
        print "ip is ", IP
        Path = self.editPath.text()
        print "path is ", Path
        Password = self.editPassword.text()
        print "password is ", Password

class PeerWindow(QtGui.QMainWindow):
    PeerSelected = []
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        uic.loadUi('peers.ui',self)
        self.setWindowTitle("Peer Details")
        self.resize(350,600)
        self.move(500, 500)
        self.but_add.clicked.connect(self.add)
        self.but_delete.clicked.connect(self.delete)
        self.but_delete.setEnabled(False)
        self.but_pull.clicked.connect(self.pull)
        self.but_pull.setEnabled(False)
        self.but_pullAll.clicked.connect(self.pullAll)
        model = QtGui.QStandardItemModel()
        for i in range(10):
            item = QtGui.QStandardItem('Item %s' % randint(1, 100))
            check = QtCore.Qt.Unchecked
            item.setCheckState(check)
            item.setCheckable(True)
            item.setEditable(False)
            model.appendRow(item)
        self.list_peers.setModel(model)
        self.list_peers.clicked.connect(self.listClicked1)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def listClicked1(self, index):
        print 'called ' 
        print index.row() 
        print index.data().toString()
        
        if index.row() in self.PeerSelected:
            self.PeerSelected.remove(index.row())
            index.model().item(index.row()).setCheckState(QtCore.Qt.Unchecked)
            print "removed "
            print self.PeerSelected

        elif index.row() not in self.PeerSelected:
            self.PeerSelected.append(index.row())
            index.model().item(index.row()).setCheckState(QtCore.Qt.Checked)
            print "appended "
            print self.PeerSelected

        if(len(self.PeerSelected) == 0):
            self.but_delete.setEnabled(False)
            self.but_pull.setEnabled(False)
        else:
            self.but_delete.setEnabled(True)
            self.but_pull.setEnabled(True)

    def add(self):
        print "add button clicked"
        self.myOtherWindow = AddPeerWindow()
        self.myOtherWindow.show()

    def delete(self):
        print "del button clicked"
        del_msg = "Are you sure you want to delete " + str(self.PeerSelected)[1:-1]
        reply = QtGui.QMessageBox.question(self, 'Message', del_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            print "delete", self.PeerSelected

    def pullAll(self):
        print "pull all button pressed"

    def pull(self):
        print "pull button pressed"
        pull_msg = "Are you sure you want to pull from " + str(self.PeerSelected)[1:-1]
        reply = QtGui.QMessageBox.question(self, 'Message', pull_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            print "pull from ", self.PeerSelected

class AddPeerWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        uic.loadUi('prompt.ui',self)
        self.setWindowTitle("Add Peer")
        self.resize(350,400)
        self.move(500, 500)
        self.but.clicked.connect(self.addPeer)
        self.editPassword.setEchoMode(QtGui.QLineEdit.Password)


    def addPeer(self):
        print "button clicked"
        IP = self.editIP.text()
        print "ip is ", IP
        Path = self.editPath.text()
        print "path is ", Path
        Password = self.editPassword.text()
        print "password is ", Password



class MyWindowClass(QtGui.QMainWindow, form_class):
    diffList = []
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.but_openFile.clicked.connect(self.openFile)
        self.but_name.clicked.connect(self.setName)
        self.but_email.clicked.connect(self.setEmail)
        self.but_diff.clicked.connect(self.diff)
    #    self.but_remote.clicked.connect(self.setRemote)

    #    self.but_push.clicked.connect(self.push)
    #    self.but_pullAll.clicked.connect(self.pullAll)
    #    self.but_pull.clicked.connect(self.pull)
        self.but_commit.clicked.connect(self.snap)
        self.but_init.clicked.connect(self.init)
    #    self.but_log.clicked.connect(self.log)
        self.but_restore.clicked.connect(self.restore)
        self.but_clone.clicked.connect(self.clone)
        self.but_addPeer.clicked.connect(self.addPeer)
        self.but_delete.clicked.connect(self.delete)
        self.diffList = []
        # qtable_history = self.table_history
        # qtable_history.setColumnCount(4)
        # listOfLables = ['Commit Id','Message', 'Author', 'Time']

        # header = qtable_history.horizontalHeader()
        # header.setResizeMode(QtGui.QHeaderView.Stretch)
                
        # qtable_history.setHorizontalHeaderLabels(listOfLables)
        # self.populateTable(qtable_history)

        # self.displayDiff()

        model = QtGui.QStandardItemModel()
        for i in range(10):
            item = QtGui.QStandardItem('Item %s' % randint(1, 100))

            # item.setForeground

            # b = QtGui.QBrush()


            # b.setColor(QtCore.Qt.red)
            # item.setBackground(b)
            if i%2 == 0 :
                brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
            else :
                brush = QtGui.QBrush(QtGui.QColor(0, 255, 0))

            brush.setStyle(QtCore.Qt.SolidPattern)
            item.setForeground(brush)

            check = QtCore.Qt.Unchecked
            item.setCheckState(check)
            item.setCheckable(True)
            item.setEditable(False)
            #item.setBackgroundColor(QtCore.Qt.blue)
            #Qt.QColor rowColor = QtCore.Qt.blue
#            item.setData(QtCore.Qt.blue, QtCore.Qt.ForegroundRole)
            model.appendRow(item)
#        model.setStringList(QtCore.QString("Item 1;Item 2;Item 3;Item 4").split(";"))    
        self.list_commit.setModel(model)
        self.list_commit.clicked.connect(self.listClicked)

    #    QtCore.QObject.connect(self.list_commit,QtCore.SIGNAL("clicked(QModelIndex)"), self.list_commit, QtCore.SLOT("ItemClicked(QModelIndex)"))

        self.actionNew_Project.setShortcut('Ctrl+N')
        self.actionNew_Project.triggered.connect(self.newProject)

        self.actionOpne_Project.setShortcut('Ctrl+O')
        self.actionOpne_Project.triggered.connect(self.openFile)

        self.actionExit.setShortcut('Alt+F4')
        self.actionExit.triggered.connect(self.exit)
        #print "cwd is " + globals.ROOT

    
    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def listClicked(self, index):
        print 'called ' 
        print index.row() 
        print index.data().toString()
        #index.setCheckState(True)

#        print self.list_commit.item(index.row())
        #print index.child(0, 0)
        if index.row() in self.diffList:
            self.diffList.remove(index.row())
            print "removed "
            print self.diffList
            index.model().item(index.row()).setCheckState(QtCore.Qt.Unchecked)

        elif index.row() not in self.diffList:
            self.diffList.append(index.row())
            index.model().item(index.row()).setCheckState(QtCore.Qt.Checked)
            print "appended "
            print self.diffList
        # itms = self.assetList.selectedIndexes()
        # for it in itms:
        #     print 'selected item index found at %s' % it.row()


    # @pyqtSlot("QModelIndex")
    # def ItemClicked(self,index):
    #     QMessageBox.information(None,"Hello!","You Clicked: \n"+index.data().toString())

    def openFile(self):
#    	fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        fname = QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', '\home')
    	self.txt_path1.setText(fname)
        globals.changeCWD(fname)
        print "ROOT name changed to ", fname
        print globals.ROOT

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
    # def setRemote(self):
    #     name, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 'Enter remote name:')
    #     if ok:
    #        # print "name is ", str(name)
    #         try:
    #             address, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 'Enter remote address:')
    #             if ok:
    #                 print "name is ", str(name), " address is ", str(address)

    #         except Exception, e:
    #             print e

    def diff(self):

        print "diff called"
        
        ## this is how to populate the list_diff
        # model = QtGui.QStandardItemModel()
        # for i in range(20):
        #     item = QtGui.QStandardItem('Item %s' % randint(1, 100))
        #     if i%2 == 0 :
        #         brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        #     else :
        #         brush = QtGui.QBrush(QtGui.QColor(0, 255, 0))

        #     brush.setStyle(QtCore.Qt.SolidPattern)
        #     item.setForeground(brush)
        #     item.setEditable(False)
        #     model.appendRow(item)
        # self.list_diff.setModel(model)




        print "diff list is ", self.diffList
        if(len(self.diffList) == 1):
            print "diff of current state and ", self.diffList[0]
        elif(len(self.diffList) == 2):
            print "diff between ", self.diffList[0], " and ", self.diffList[1]
        elif(len(self.diffList) == 0):
            print "diff from last commit"
        else:
            print "error"
            msgBox = QtGui.QMessageBox() 
            msgBox.setWindowTitle("Error!")
            msgBox.setText("You have selected more than two commits for diff.")
            msgBox.exec_()

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
        # text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 'Enter your name:')
        # if ok:
        #     print "message is ", str(text)
        #     try:
        #         repo.LoadRepo()
        #         commit.snap(str(text))
        #         print "commit successfull"
        #     except Exception, e:
        #         print e
        try:
            self.myOtherWindow = CommitPromptWindow()
            self.myOtherWindow.show()

        #    repo.init()
            print "commit function called"

        except Exception, e:
            print e



    def pull(self):
        print "pull button pressed"

    def delete(self):
        print "delete button pressed"
        if(len(self.diffList) == 0):
            print "select atleast one"
            msgBox = QtGui.QMessageBox() 
            msgBox.setWindowTitle("Error!")
            msgBox.setText("Please select the commit you want to delete.")
            msgBox.exec_()

        elif(len(self.diffList) > 1):
            print "select atleast one"
            msgBox = QtGui.QMessageBox() 
            msgBox.setWindowTitle("Error!")
            msgBox.setText("You have selected more than one commits. Please delete one by one.")
            msgBox.exec_()

        elif(len(self.diffList) == 1):
            del_msg = "Are you sure you want to delete " + str(self.diffList[0])
            reply = QtGui.QMessageBox.question(self, 'Message', del_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                print "del", self.diffList[0]



    # def pullAll(self):
    #     print "pull all button pressed"

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
        try:
            self.myOtherWindow = InitPromptWindow()
            self.myOtherWindow.show()

        #    repo.init()
            print "init function called"

        except Exception, e:
            print e
        

    def log(self):
        print "log button pressed"
        try:
            repo.LoadRepo()
            print "log starts"
            print repo.log()
        except Exception, e:
            print e

    def clone(self):
        print "clone button pressed"
        self.myOtherWindow = CloneWindow()
        self.myOtherWindow.show()

    def addPeer(self):
        print "peer button pressed"
        self.myOtherWindow = PeerWindow()
        self.myOtherWindow.show()

    def restore(self):
        if(len(self.diffList) == 0):
            print "select atleast one"
            msgBox = QtGui.QMessageBox() 
            msgBox.setWindowTitle("Error!")
            msgBox.setText("Please select the commit you want to restore.")
            msgBox.exec_()

        elif(len(self.diffList) > 1):
            print "select atleast one"
            msgBox = QtGui.QMessageBox() 
            msgBox.setWindowTitle("Error!")
            msgBox.setText("You have selected more than one commits.")
            msgBox.exec_()

        elif(len(self.diffList) == 1):
            restore_msg = "Are you sure you want to restore " + str(self.diffList[0])
            reply = QtGui.QMessageBox.question(self, 'Message', restore_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                print "restore", self.diffList[0]
        #        try:
        #         repo.LoadRepo()
        #         commit.restore(str(text))
        #     except Exception,e:
        #         print e

        ## old part, leave it commented
        # text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 'Enter commit id:')
        # if ok:
        #     print "commit id is ", str(text)
        #     try:
        #         repo.LoadRepo()
        #         commit.restore(str(text))
        #     except Exception,e:
        #         print e

    def enableButtons(self):
        self.but_name.setEnabled(True)
        self.but_email.setEnabled(True)
        #self.but_pullAll.setEnabled(True)
        #self.but_pull.setEnabled(True)
        self.but_commit.setEnabled(True)
        self.but_delete.setEnabled(True)
        self.but_clone.setEnabled(True)
        self.but_addPeer.setEnabled(True)
        self.but_restore.setEnabled(True)



    def disableButtons(self):
        self.but_name.setEnabled(False)
        self.but_email.setEnabled(False)
        #self.but_pullAll.setEnabled(False)
        #self.but_pull.setEnabled(False)
        self.but_commit.setEnabled(False)
        self.but_delete.setEnabled(False)
        self.but_clone.setEnabled(False)
        self.but_addPeer.setEnabled(False)
        self.but_restore.setEnabled(False)


app = QtGui.QApplication(sys.argv)
myWindow = MyWindowClass(None)
myWindow.show()
app.exec_()