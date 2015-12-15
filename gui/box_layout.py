# -*- coding: cp1251 -*-
__author__ = 'whoami'

from time import clock
from PyQt4 import QtGui, QtCore
from functools import partial
from threading import Thread
from config_read import read_cfg


# class QWhatThis(QtGui.QWhatsThis):
#     def __init__(self, *args, **kwargs):
#         super().__init__(args, kwargs)

# class QAction(QtGui.QAction):
#
#     def event(self, QEvent):
#         print(QEvent.type())
#         if QEvent.type() == QtCore.QEvent.LeaveWhatsThisMode:
#             print("Ok")
#         return QtCore.QObject.event(self, QEvent)
#
#     def hover(self):
#         QtCore.QCoreApplication.sendEvent(self, QtCore.QEvent.LeaveWhatsThisMode)
#
#     def hovered(self, *args, **kwargs):
#         QtCore.QCoreApplication.sendEvent(self, QtCore.QEvent.LeaveWhatsThisMode)


class BoxLayout(QtGui.QWidget):
    """
    Creating a set of widgets for information about the account
    account, slots, icon
    """

    def __init__(self, tbl, *args):
        super(BoxLayout, self).__init__()

        self.ini = "resources.ini"
        # self.installEventFilter(self)

        self.flag = False
        self.tbl = tbl
        self.id = args[0][0]
        self.widgets = []
        self.actions = []

        self.create_widgets(*args)
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
        start = clock()
        while True:
            end = clock() - start
            if end > 1:
                for widget in self.widgets:
                    widget.setProperty("addNewAccount", False)
                break
        return

    def create_widgets(self, account, slots, icon):
        tool_tip = read_cfg(self.ini, "tool_tip")
        test = []
        menu = QtGui.QMenu()
        for i, slot in enumerate(slots):
            self.actions.append(
                QtGui.QAction(slot["icon"], slot["name"], self)
            )
            self.connect(self.actions[i], QtCore.SIGNAL('triggered()'),
                         partial(slot["method"], self))
            self.actions[i].setWhatsThis(tool_tip["show_pwd"])
            self.actions[i].setToolTip(tool_tip["show_pwd"])
            menu.addAction(self.actions[i])

        if len(account) > 5:
            self.email = QtGui.QLabel(account[5])
            self.email.setToolTip(account[5])
            self.email.setTextInteractionFlags(
                QtCore.Qt.TextSelectableByKeyboard |
                QtCore.Qt.TextSelectableByMouse)
            self.email.setObjectName("labelEmail")
            self.widgets.append(self.email)

        holder_text = read_cfg(self.ini, "holder_text")
        self.service = QtGui.QLineEdit(account[1])
        self.service.setPlaceholderText(holder_text["service"])
        self.service.setMaxLength(50)
        self.service.setProperty("mandatoryField", True)
        self.widgets.append(self.service)

        self.login = QtGui.QLineEdit(account[2])
        self.login.setPlaceholderText(holder_text["login"])
        self.login.setMaxLength(100)
        self.widgets.append(self.login)

        self.passwd = QtGui.QLineEdit(account[3])
        self.passwd.setObjectName("password")
        self.passwd.setPlaceholderText(holder_text["passwd"])
        self.passwd.setEchoMode(QtGui.QLineEdit.Password)
        self.passwd.setToolTip(tool_tip["passwd"])
        self.widgets.append(self.passwd)

        self.forgot = QtGui.QLineEdit(account[4])
        self.forgot.setMaxLength(500)
        self.forgot.setPlaceholderText(holder_text["forgot"])
        self.widgets.append(self.forgot)

        btn_name = read_cfg(self.ini, "btn_name")
        self.get = QtGui.QPushButton(icon, btn_name["actions"])
        self.get.setMenu(menu)
        self.get.setToolTip(tool_tip["action"])
        self.widgets.append(self.get)

    def set_hint(self):
        self.service.setToolTip(self.service.text())
        self.login.setToolTip(self.login.text())
        self.forgot.setToolTip(self.forgot.text())
