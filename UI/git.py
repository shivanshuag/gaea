import sys
from PyQt4 import QtCore, QtGui, uic

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
        self.but_commit.clicked.connect(self.commit)


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

    def openFile(self):
#    	fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home')
        fname = QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', '\home')
    	self.txt_path1.setText(fname)

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

    def setEmail(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 'Enter your email address:')
        
        if ok:
            print "email is ", str(text)
    
    def populateTable(self, qtable):
        array = [["mohit", "kumar", "garg", "cse"], ["gaurav", "gautam", "-", "phy"]]
        print "populateTable called"

        for row in range(2):
            qtable.insertRow(row)
            for column in range(4):
                qtable.setItem(row, column, QtGui.QTableWidgetItem(QtCore.QString("%1").arg(array[row][column])))

    def commit(self):
        print "commit button pressed"

    def push(self):
        print "push button pressed"

    def pull(self):
        print "pull button pressed"

    def displayDiff(self):
        self.edit_diff.setText("diff of two commits comes here")    

app = QtGui.QApplication(sys.argv)
myWindow = MyWindowClass(None)
myWindow.show()
app.exec_()