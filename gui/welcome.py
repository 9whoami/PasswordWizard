# -*- coding: cp1251 -*-
__author__ = 'whoami'

import sys
import re
from PyQt4 import QtGui, QtCore
from os import path
from key_gen import encode_md5, rsa_gen_key, rsa_load_key


class RegWnd(QtGui.QWidget):
    def __init__(self, db, parent=None):
        super(RegWnd, self).__init__(parent)
        self.setWindowTitle("Registration")

        self.label = QtGui.QLabel("Type login or "
                                  "enter the path to the folder "
                                  "with the keys", self)

        self.edit = QtGui.QLineEdit()
        self.edit.setPlaceholderText("Login")
        self.edit.setMaxLength(20)

        self.btn_ok = QtGui.QPushButton("ok")

        self.btn_cancel = QtGui.QPushButton("cancel")

        self.box_label = QtGui.QHBoxLayout()
        self.box_label.addWidget(self.label)

        self.box_edit = QtGui.QHBoxLayout()
        self.box_edit.addWidget(self.edit)

        self.box_buttons = QtGui.QHBoxLayout()
        self.box_buttons.addWidget(self.btn_ok)
        self.box_buttons.addWidget(self.btn_cancel)

        self.vbox = QtGui.QVBoxLayout()
        self.vbox.addLayout(self.box_label)
        self.vbox.addLayout(self.box_edit)
        self.vbox.addLayout(self.box_buttons)

        self.setLayout(self.vbox)
        self.set_signals()

        self.db = db
        self.pubkey, self.privkey, self.pubkey_in_md5 = None

        self.show()

    def set_signals(self):
        self.btn_ok.clicked.connect(self.btn_ok_click)
        self.btn_cancel.clicked.connect(self.btn_cancel_click)

    def sign_up(self, username):

        def confirm():
            # TODO MessageBox should be StayOnTop
            confirmation_ok = 1024

            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Question)
            msg.setText("Are you sure you want to register new account")
            msg.setWindowTitle("Confirm registration")
            msg.setStandardButtons(QtGui.QMessageBox.Ok |
                                   QtGui.QMessageBox.Cancel)
            return msg.exec_() == confirmation_ok

        # TODO check username [0-9A-Za-z]{4,}
        if self.get_keys():
            # TODO confirm registration
            if self.db.check_user(username) and confirm():
                return self.db.insert_users(
                    [self.pubkey_in_md5, username]
                )
            else:
                return False

    def sign_in(self, dir):
        if self.get_keys(dir=dir):
            return self.db.sign_in(self.pubkey_in_md5)
        else:
            return None

    def get_keys(self, dir=None):
        self.pubkey, self.privkey, self.pubkey_in_md5 = None

        if dir:
            self.pubkey, self.privkey = rsa_load_key(dir=dir)
        else:
            self.pubkey, self.privkey = rsa_gen_key()
        self.pubkey_in_md5 = encode_md5(self.pubkey.save_pkcs1())

        if self.pubkey and self.privkey:
            return True
        else:
            return False

    def btn_ok_click(self):
        username = self.edit.text()
        if path.exists(username):
            self.sign_in(username)
        else:
            self.sign_up(username)

    def btn_cancel_click(self):
        self.close()


def register(db):
    app = QtGui.QApplication([])
    wnd = RegWnd(db)
    app.exec_()
    if wnd.pubkey and wnd.privkey:
        pass
