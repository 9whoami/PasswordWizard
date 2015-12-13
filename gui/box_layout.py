# -*- coding: cp1251 -*-
__author__ = 'whoami'

import time
from PyQt4 import QtGui, QtCore
from functools import partial
from threading import Thread


class BoxLayout(QtGui.QWidget):
    """
    Creating a set of widgets for information about the account
    acount: tuple information about the account (tuple)
    slots: a set of slots of the field (dict)
    tbl: tabel name (str)
    """

    def __init__(self, account, slots, tbl, icon, parent=None):
        super(BoxLayout, self).__init__(parent)

        self.flag = False
        self.tbl = tbl
        self.id = account[0]
        self.widgets = []
        self.actions = []

        self.create_widgets(account, slots, icon)
        self.set_hint()
        if isinstance(self.id, str):
            self.passwd.setEchoMode(QtGui.QLineEdit.Normal)
        hbox = QtGui.QHBoxLayout()
        for widget in self.widgets:
            if isinstance(self.id, str):
                widget.setProperty("addNewAccount", True)
            hbox.addWidget(widget)

        self.setLayout(hbox)

        if isinstance(self.id, str):
            t = Thread(target=self.th)
            t.setDaemon(True)
            t.start()

    def th(self):
        start = time.clock()
        while True:
            end = time.clock() - start
            if end > 1:
                for widget in self.widgets:
                    widget.setProperty("addNewAccount", False)
                break
        return

    def create_widgets(self, account, slots, icon):
        menu = QtGui.QMenu()

        for i, slot in enumerate(slots):
            self.actions.append(
                QtGui.QAction(slot["icon"], slot["name"], self,
                              triggered=partial(slot["method"], self))
            )
            menu.addAction(self.actions[i])

        if len(account) > 5:
            self.email = QtGui.QLabel(account[5])
            self.widgets.append(self.email)

        self.service = QtGui.QLineEdit(account[1])
        self.service.setPlaceholderText("Service name")
        self.service.setMaxLength(50)
        self.service.setProperty("mandatoryField", True)
        self.widgets.append(self.service)

        self.login = QtGui.QLineEdit(account[2])
        self.login.setPlaceholderText("Login")
        self.login.setMaxLength(100)
        self.widgets.append(self.login)

        self.passwd = QtGui.QLineEdit(account[3])
        self.passwd.setPlaceholderText("Password")
        self.passwd.setEchoMode(QtGui.QLineEdit.Password)
        self.widgets.append(self.passwd)

        self.forgot = QtGui.QLineEdit(account[4])
        self.forgot.setMaxLength(500)
        self.forgot.setPlaceholderText("Other")
        self.widgets.append(self.forgot)

        self.get = QtGui.QPushButton(icon, "Actions")
        self.get.setMenu(menu)
        self.widgets.append(self.get)

    def set_hint(self):
        self.service.setToolTip(self.service.text())
        self.login.setToolTip(self.login.text())
        self.forgot.setToolTip(self.forgot.text())
