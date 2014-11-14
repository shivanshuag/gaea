import sys
from PyQt4 import QtCore, QtGui, uic
from random import *
import os

#import gaea
import globals
import repo
import commit
import remote
#import clint libraries
from clint.arguments import Args
from clint.textui import puts, colored, indent

gaeaDir = os.getcwd()
form_class = uic.loadUiType(os.path.join(gaeaDir, "git.ui"))[0]                 # Load the UI
projectDir = None

class InitPromptWindow(QtGui.QMainWindow):
    parent = None
    def __init__(self, parent):
        QtGui.QMainWindow.__init__(self)
        uic.loadUi(os.path.join(gaeaDir, 'initui.ui'),self)
        self.setWindowTitle("Init Prompt")
        self.resize(350,400)
        self.move(500, 500)
        self.but.clicked.connect(self.init)
        self.editPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.editRootPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.parent = parent 
    
    def init(self):
        print "button clicked"
        name = str(self.editName.text())
        print "name is ", name

        Password = str(self.editPassword.text())
        print "password is ", Password

        RootPassword = str(self.editRootPassword.text())
        print "password is ", RootPassword
        if (name.strip() and Password.strip() and RootPassword.strip()): 
            try:
                repo.init(RootPassword, name, Password)
                self.parent.load()
                self.close()
            except Exception, e:
                print "error"
                self.errorMessage(str(e))  
        else :
            if not name.strip():
                self.errorMessage("Name field cannot be empty")
            elif not Password.strip():
                self.errorMessage("Password field cannot be empty")
            elif not RootPassword.strip():
                self.errorMessage("RootPassword field cannot be empty")
            print "error"

    def errorMessage(self,str):
        print "error"
        msgBox = QtGui.QMessageBox() 
        msgBox.setWindowTitle("Error!")
        msgBox.setText(str)
        msgBox.exec_()    



class CommitPromptWindow(QtGui.QMainWindow):
    t = 0
    parent = None
    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self)
        uic.loadUi(os.path.join(gaeaDir, 'commitui.ui'),self)

        self.setWindowTitle("Commit Prompt")
        self.resize(350,200)
        self.move(500, 500)
        self.but.clicked.connect(self.commit)
    #    self.radioSoft.toggled.connect(self.softClick)
        self.parent = parent

    def commit(self):
        print "button clicked"
        message = str(self.editMessage.text())
        print "msg is ", message, " toggle is ", self.t
        try:       
        #if self.t == 0:
            commit.snap('soft', message)
        # elif self.t == 1:
        #     commit.snap('hard', message)
            self.parent.load()
            self.close()

        except Exception, e:
            print e
            print "error"
            msgBox = QtGui.QMessageBox() 
            msgBox.setWindowTitle("Error!")
            msgBox.setText(str(e))
            msgBox.exec_()    

    # def softClick(self):
    #     self.t = 1 - self.t
    #     print "toggle ", t
    #     # self.radioSoft.setChecked(True)
    #     # self.radioHard.setChecked(False)

    # def hardClick(self):
    #     self.t = 1 - self.t
    #     print "toggle ", self.t
    #     # self.radioSoft.setChecked(False)
    #     # self.radioHard.setChecked(True)



class CloneWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        uic.loadUi(os.path.join(gaeaDir, 'prompt_clone.ui'),self)
        self.setWindowTitle("Clone")
        self.resize(350,400)
        self.move(500, 500)
        self.but.clicked.connect(self.clone)
        self.editPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.editNewPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.editRootPassword.setEchoMode(QtGui.QLineEdit.Password)

    def clone(self):
        print "button clicked"
        IP = str(self.editIP.text())
        print "ip is ", IP
        Path = str(self.editPath.text())
        print "path is ", Path
        Name = str(self.editName.text())
        print "name is ", Name
        Password = str(self.editPassword.text())
        print "password is ", Password
        NewName = str(self.editNewName.text())
        print "name is ", NewName
        NewPassword = str(self.editNewPassword.text())
        print "name is ", NewPassword
        RootPassword = str(self.editRootPassword.text())
        print "name is ", RootPassword



        if (IP.strip() and Path.strip() and Name.strip() and Password.strip()): 
            try:
                remote.clone(IP, Path, Name, Password, False, RootPassword, NewName, NewPassword)
                self.close()
            except Exception, e:
                print "error"
                self.errorMessage(str(e))
        else:
            if not IP.strip():
                self.errorMessage("IP field cannot be empty")
            elif not Path.strip():
                self.errorMessage("Path field cannot be empty")
            elif not Name.strip():
                self.errorMessage("Name field cannot be empty")
            elif not Password.strip():
                self.errorMessage("Password field cannot be empty")
            print "error"
                
    def errorMessage(self,str):
        print "error"
        msgBox = QtGui.QMessageBox() 
        msgBox.setWindowTitle("Error!")
        msgBox.setText(str)
        msgBox.exec_()    



class PeerWindow(QtGui.QMainWindow):
    PeerSelected = []
    parent = None
    def __init__(self, parent):
        QtGui.QMainWindow.__init__(self)
        uic.loadUi(os.path.join(gaeaDir, 'peers.ui'),self)
        self.setWindowTitle("Peer Details")
        self.resize(350,600)
        self.move(500, 500)
        self.but_add.clicked.connect(self.add)
        self.but_delete.clicked.connect(self.delete)
        self.but_delete.setEnabled(False)
        self.but_pull.clicked.connect(self.pull)
        self.but_pull.setEnabled(False)
        self.but_pullAll.clicked.connect(self.pullAll)
        self.list_peers.clicked.connect(self.listClicked1)

        self.populatePeers()
        self.parent = parent

        
    def populatePeers(self):           #get PEER_INFO and populate it
        self.PeerSelected = []
        model = QtGui.QStandardItemModel()
        for key in globals.PEERINFO['peers'].keys():
            item = QtGui.QStandardItem(globals.PEERINFO['peers'][key]['username'] + '@'+key+':'+globals.PEERINFO['peers'][key]['path'])
            check = QtCore.Qt.Unchecked
            item.setCheckState(check)
            item.setCheckable(True)
            item.setEditable(False)
            model.appendRow(item)
        self.list_peers.setModel(model)

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
        self.myOtherWindow = AddPeerWindow(self)
        self.myOtherWindow.show()

    def delete(self):
        print "del button clicked"
        del_msg = "Are you sure you want to delete " + str(self.PeerSelected)[1:-1]
        reply = QtGui.QMessageBox.question(self, 'Message', del_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            print "delete", self.PeerSelected
            try:
                ip_del = globals.PEERINFO['peers'].keys()[self.PeerSelected[0]]
                remote.deletePeer(ip_del)
                self.populatePeers()
            except Exception, e:
                print e
                self.errorMessage(str(e))

    def pullAll(self):
        print "pull all button pressed"
    #    try:
        remote.pullAll()
        self.parent.load()
        # except Exception, e:
        #     print e 
        #     self.errorMessage(e)


    def pull(self):
        print "pull button pressed"
        pull_msg = "Are you sure you want to pull from " + str(self.PeerSelected)[1:-1]
        reply = QtGui.QMessageBox.question(self, 'Message', pull_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            print "pull from ", self.PeerSelected
            if len(self.PeerSelected) == 1:
                #try:
                ip = globals.PEERINFO['peers'].keys()[self.PeerSelected[0]]
                name = globals.PEERINFO['peers'][ip]['username']
                path = globals.PEERINFO['peers'][ip]['path']
                password = globals.PEERINFO['peers'][ip]['password']
                print ip, name, path, password
                remote.pull(ip, path, name, password)
                self.parent.load()
                # except Exception, e:
                #     print e
                #     self.errorMessage(str(e))

    def errorMessage(self,str):
        print "error"
        msgBox = QtGui.QMessageBox() 
        msgBox.setWindowTitle("Error!")
        msgBox.setText(str)
        msgBox.exec_()    



class AddPeerWindow(QtGui.QMainWindow):
    parent = None
    def __init__(self, parent):
        QtGui.QMainWindow.__init__(self)
        uic.loadUi(os.path.join(gaeaDir, 'prompt.ui'),self)
        self.setWindowTitle("Add Peer")
        self.resize(350,400)
        self.move(500, 500)
        self.but.clicked.connect(self.addPeer)
        self.editPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.parent = parent

    def addPeer(self):
        print "button clicked"
        IP = str(self.editIP.text())
        print "ip is ", IP
        Path = str(self.editPath.text())
        print "path is ", Path
        Name = str(self.editName.text())
        print "user name is ", Name
        Password = str(self.editPassword.text())
        print "password is ", Password
        if (IP.strip() and Path.strip() and Name.strip() and Password.strip()):
            try:
                remote.addPeer(IP, Path, Name, Password)
                self.parent.populatePeers()
                self.close()
            except Exception, e:
                print "error"
                self.errorMessage(str(e))
        else:
            if not IP.strip():
                self.errorMessage("IP field cannot be empty")
            elif not Path.strip():
                self.errorMessage("Path field cannot be empty")
            elif not Name.strip():
                self.errorMessage("Name field cannot be empty")
            elif not Password.strip():
                self.errorMessage("Password field cannot be empty")
            print "error"

    def errorMessage(self,str):
        print "error"
        msgBox = QtGui.QMessageBox() 
        msgBox.setWindowTitle("Error!")
        msgBox.setText(str)
        msgBox.exec_()    


class MyWindowClass(QtGui.QMainWindow, form_class):
    all_logs = []
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
        self.but_managePeers.clicked.connect(self.managePeers)
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


        # model = QtGui.QStandardItemModel()
        # for i in range(10):
        #     item = QtGui.QStandardItem('Item %s' % randint(1, 100))
        #     check = QtCore.Qt.Unchecked
        #     item.setCheckState(check)
        #     item.setCheckable(True)
        #     item.setEditable(False)
        #     model.appendRow(item)
        # self.list_commit.setModel(model)
        # self.list_commit.clicked.connect(self.listClicked)

        self.disableButtons()
        self.list_commit.clicked.connect(self.listClicked)


    #    QtCore.QObject.connect(self.list_commit,QtCore.SIGNAL("clicked(QModelIndex)"), self.list_commit, QtCore.SLOT("ItemClicked(QModelIndex)"))


        self.actionOpne_Project.setShortcut('Ctrl+O')
        self.actionOpne_Project.triggered.connect(self.openFile)

        self.actionExit.setShortcut('Alt+F4')
        self.actionExit.triggered.connect(self.exit)
        #print "cwd is " + globals.ROOT

        #############
        #functions to be called at when a repo is selected
        # diff, log

    
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
        global projectDir
#    	fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        fname = QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', '\home')
    	self.txt_path1.setText(fname)
        globals.changeCWD(fname)
        print "ROOT name changed to ", fname
        projectDir = fname
        print globals.ROOT
        os.chdir(globals.ROOT)
        self.disableButtons()
        self.load()

            # clone and init enable, else disableButtons


    def load(self):
        try:
            print "load called"
            self.diffList = []
            repo.LoadRepo()   ### already a repo
            self.enableButtons()
            self.log()
            self.diff()
            self.but_init.setEnabled(False)
            self.but_clone.setEnabled(False)

        except Exception, e:
            print e
            self.but_init.setEnabled(True)
            self.but_clone.setEnabled(True)


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
                self.errorMessage(str(e))

    def setEmail(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 'Enter your email address:')
        
        if ok:
            print "email is ", str(text)
            try:
                repo.LoadRepo()
                repo.setEmail(str(text))
            except Exception, e:
                print e
                self.errorMessage(str(e))
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

    def populateDiffInList(self,difference):
        print difference
        model = QtGui.QStandardItemModel()
        for line in iter(difference.splitlines()):
            item = QtGui.QStandardItem(line)
            if len(line) > 0:
                if line[0]=='+' and (len(line) <2 or line[1] != '+'):
                    brush = QtGui.QBrush(QtGui.QColor(0, 255, 0)) #Green

                elif line[0]=='-' and (len(line) <2 or line[1] != '-'):
                    brush = QtGui.QBrush(QtGui.QColor(255, 0, 0)) #Red

                else:
                    brush = QtGui.QBrush(QtGui.QColor(0,0,0)) #black

            brush.setStyle(QtCore.Qt.SolidPattern)
            item.setForeground(brush)
            item.setEditable(False)
            model.appendRow(item)
       
        self.list_diff.setModel(model)

    def diff(self):
        print "diff called"
        print "diff list is ", self.diffList
        difference = ''
        if(len(self.diffList) == 1):
            print "diff of current state and ", self.diffList[0]
            difference = repo.diff(id1= self.all_logs[self.diffList[0]][0])
            self.populateDiffInList(difference)
        elif(len(self.diffList) == 2):
            print "diff between ", self.diffList[0], " and ", self.diffList[1]
            difference = repo.diff(id1= self.all_logs[self.diffList[0]][0], id2 = self.all_logs[self.diffList[1]][0])
            self.populateDiffInList(difference)
        elif(len(self.diffList) == 0):
            print "diff from last commit"
            difference = repo.diff()
            self.populateDiffInList(difference)

            # diff = repo.diff()
            # 

        else:
            print "error"
            self.errorMessage("You have selected more than two commits for diff.")
            # msgBox = QtGui.QMessageBox() 
            # msgBox.setWindowTitle("Error!")
            # msgBox.setText("You have selected more than two commits for diff.")
            # msgBox.exec_()

    def populateTable(self, qtable):
        array = [["mohit", "kumar", "garg", "cse"], ["gaurav", "gautam", "-", "phy"]]
        print "populateTable called"

        for row in range(2):
            qtable.insertRow(row)
            for column in range(4):
                qtable.setItem(row, column, QtGui.QTableWidgetItem(QtCore.QString("%1").arg(array[row][column])))

    def snap(self):
        print "commit button pressed"

        try:
            self.myOtherWindow = CommitPromptWindow(self)
            self.myOtherWindow.show()
            print "commit function called"

        except Exception, e:
            print e
            self.errorMessage(str(e))

    # this function has been shifted to another window
    # def pull(self):   
    #     print "pull button pressed"

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
                try:
                    commit.delete(self.all_logs[self.diffList[0]][0])
                    print "delete done", self.all_logs[self.diffList[0]][0]
                    self.load()
                except Exception, e:
                    print e
                    self.errorMessage(str(e))        

                # try:
                #     repo.LoadRepo()
                #     commit.delete( convert self.diffList[0] to commit id)
                # except Exception,e:
                #     print e


    # This function has been shifted to another window
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
            self.errorMessage(str(e))
        self.edit_diff.setText("diff of two commits comes here")  

    def init(self):
        try:
            self.myOtherWindow = InitPromptWindow(self)
            self.myOtherWindow.show()
            self.load()
        #    repo.init()
            print "init function called"

        except Exception, e:
            print e
            self.errorMessage(str(e))
        

    def log(self):
        print "log button pressed"
        try:
            repo.LoadRepo()
            print "log starts"
            self.all_logs = repo.log()
            model = QtGui.QStandardItemModel()
            for i in self.all_logs:
                item = QtGui.QStandardItem( i[0] +' ' +i[1] + ' '+ i[2] + ' '+ i[3])
                if i[0] == globals.REPOINFO['HEAD']:
                    brush = QtGui.QBrush(QtGui.QColor(0,255,0)) #green
                    brush.setStyle(QtCore.Qt.SolidPattern)
                    item.setForeground(brush)
                check = QtCore.Qt.Unchecked
                item.setCheckState(check)
                item.setCheckable(True)
                item.setEditable(False)
                model.appendRow(item)
            self.list_commit.setModel(model)
        except Exception, e:
            print e
            self.errorMessage(str(e))

    def clone(self):
        print "clone button pressed"
        try:
            self.myOtherWindow = CloneWindow()
            self.myOtherWindow.show()
        except Exception, e:
            print e 
            self.errorMessage(str(e))
        

    def managePeers(self):
        print "peer button pressed"
        try:
            self.myOtherWindow = PeerWindow(self)
            self.myOtherWindow.show()
        except Exception, e:
            print e 
            self.errorMessage(str(e))

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
            try:
                commit.restore(self.all_logs[self.diffList[0]][0])
                self.load()
            except Exception,e:
                print e
                self.errorMessage(str(e))

    def enableButtons(self):
        self.but_name.setEnabled(True)
        self.but_email.setEnabled(True)
        self.but_restore.setEnabled(True)
        self.but_delete.setEnabled(True)
        self.but_commit.setEnabled(True)
        self.but_diff.setEnabled(True)
        self.but_managePeers.setEnabled(True)



    def disableButtons(self):
        self.but_name.setEnabled(False)
        self.but_email.setEnabled(False)
        self.but_init.setEnabled(False)
        self.but_restore.setEnabled(False)
        self.but_delete.setEnabled(False)
        self.but_commit.setEnabled(False)
        self.but_diff.setEnabled(False)
        self.but_clone.setEnabled(False)
        self.but_managePeers.setEnabled(False)


    def errorMessage(self,str):
        print "error"
        msgBox = QtGui.QMessageBox() 
        msgBox.setWindowTitle("Error!")
        msgBox.setText(str)
        msgBox.exec_()
        globals.ROOT = projectDir

app = QtGui.QApplication(sys.argv)
myWindow = MyWindowClass(None)
myWindow.show()
app.exec_()
