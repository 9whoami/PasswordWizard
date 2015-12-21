#!/usr/bin/env python
# -*- coding: cp1251 -*-

import sys
from PyQt4 import QtGui, QtCore

class MainWindow(QtGui.QMainWindow):

     def __init__(self):
         QtGui.QMainWindow.__init__(self)

         self.resize(QtCore.QSize(QtCore.QRect(0,0,800,600).size()).expandedTo(self.minimumSizeHint()))

         self.setMinimumSize(QtCore.QSize(200,200))

         self.menubar = QtGui.QMenuBar(self)
         self.setMenuBar(self.menubar)

         self.menuFile = QtGui.QMenu(self.menubar)
         self.menuFile.setTitle("&File")

         self.actionExit = QtGui.QAction(self)
         self.actionExit.setText("E&xit")
         self.connect(self.actionExit,
                  QtCore.SIGNAL("activated()"),
                  self.close)
         self.menuFile.addAction(self.actionExit)
         self.menubar.addAction(self.menuFile.menuAction())

         p = QtGui.QPalette()
         brush = QtGui.QBrush(QtCore.Qt.white,QtGui.QPixmap('./img/51406(1).jpg'))
         p.setBrush(QtGui.QPalette.Active,QtGui.QPalette.Window,brush)
         p.setBrush(QtGui.QPalette.Inactive,QtGui.QPalette.Window,brush)
         p.setBrush(QtGui.QPalette.Disabled,QtGui.QPalette.Window,brush)
         self.setPalette(p)

         self.show()

def main(args):
     app = QtGui.QApplication(args)
     mainWindow = MainWindow()
     sys.exit(app.exec_())

if __name__ == '__main__':
     main(sys.argv)