import sys
from PyQt4 import QtCore, QtGui, uic

#import gaea
import globals
import repo
import commit

#import clint libraries
from clint.arguments import Args
from clint.textui import puts, colored, indent

form_class = uic.loadUiType("list.ui")[0]                 # Load the UI
class MyWindowClass(QtGui.QMainWindow, form_class):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        model = QtGui.QStringListModel()
        model.setStringList(QtCore.QString("Item 1;Item 2;Item 3;Item 4").split(";"))    
    	self.listView.setModel(model)

app = QtGui.QApplication(sys.argv)
myWindow = MyWindowClass(None)
myWindow.show()
app.exec_()