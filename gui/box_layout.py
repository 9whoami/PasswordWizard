# -*- coding: cp1251 -*-
__author__ = 'whoami'

from PyQt4 import QtGui, QtCore
from functools import partial


class BoxLayout(QtGui.QWidget):
    """
    Creating a set of widgets for information about the account
    acount: tuple information about the account (tuple)
    slots: a set of slots of the field (dict)
    tbl: tabel name (str)
    """
    def __init__(self, account, slots, tbl, parent=None):
        super(BoxLayout, self).__init__(parent)

        self.flag = False
        self.tbl = tbl
        self.id = account[0]
        widgets = self.create_widgets(account, slots)

        hbox = QtGui.QHBoxLayout()
        for widget in widgets:
            hbox.addWidget(widget)

        self.setLayout(hbox)

    def create_widgets(self, account, slots):
        menu = QtGui.QMenu()
        for slot in slots:
            menu.addAction(QtGui.QAction(slot["name"],
                                         self,
                                         triggered=partial(
                                             slot["method"],
                                             self
                                         )
                                         )
                           )

        self.service = QtGui.QLineEdit(account[1])
        self.service.setPlaceholderText("Service name")
        self.service.setMaxLength(50)

        self.login = QtGui.QLineEdit(account[2])
        self.login.setPlaceholderText("Login")
        self.login.setMaxLength(100)

        self.passwd = QtGui.QLineEdit(account[3])
        self.passwd.setPlaceholderText("Password")
        self.passwd.setEchoMode(QtGui.QLineEdit.Password)

        self.forgot = QtGui.QLineEdit(account[4])
        self.forgot.setMaxLength(500)
        self.forgot.setPlaceholderText("Other")

        self.get = QtGui.QPushButton("Actions")
        self.get.setMenu(menu)

        return [self.service, self.login, self.passwd, self.forgot, self.get]

