# -*- coding: cp1251 -*-
__author__ = 'whoami'

import sys
import re
from threading import Thread
from PyQt4 import QtGui, QtCore
from os import path, getcwd
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
        # self.edit.setMaxLength(20)

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
        self.pubkey = None
        self.privkey = None
        self.pubkey_in_md5 = None
        self.username = None

        self.show()

    def set_signals(self):
        self.btn_ok.clicked.connect(self.btn_ok_click)
        self.btn_cancel.clicked.connect(self.btn_cancel_click)

    def sign_up(self, username):

        def confirm():
            confirmation_ok = 1024

            msg = QtGui.QMessageBox()
            msg.setWindowFlags(msg.windowFlags() |
                               QtCore.Qt.WindowStaysOnTopHint)
            msg.setIcon(QtGui.QMessageBox.Question)
            msg.setText("Are you sure you want to register new account")
            msg.setWindowTitle("Confirm registration")
            msg.setStandardButtons(QtGui.QMessageBox.Ok |
                                   QtGui.QMessageBox.Cancel)
            return msg.exec_() == confirmation_ok

        pattern = r"[0-9A-Za-z]+"
        result = re.match(pattern, username)
        if not result or len(result.group()) != len(username):
            return False

        # TODO get_key move to thread future
        if self.db.check_user(username) and confirm():
            result = [None]
            t1 = Thread(target=self.get_keys, args=(result,))
            t1.start()
            self.label.setText("RSA key generation...")
            while t1.isAlive():
                pass
            if result[0]:
                return self.db.insert_users(
                    [self.pubkey_in_md5, username]
                )
            else:
                return False
        else:
            return False

    def sign_in(self, dir):
        if self.get_keys(dir=dir):
            return self.db.sign_in(self.pubkey_in_md5)
        else:
            return None

    def get_keys(self, result=None, dir=None):
        self.pubkey = None
        self.privkey = None
        self.pubkey_in_md5 = None
        self.username = None

        if dir:
            self.pubkey, self.privkey = rsa_load_key(dir=dir)
        else:
            self.pubkey, self.privkey = rsa_gen_key()

        if self.pubkey and self.privkey:
            self.pubkey_in_md5 = encode_md5(self.pubkey.save_pkcs1())
            if result: result[0] = True
            return True
        else:
            if result: result[0] = False
            return False

    def btn_ok_click(self):
        username = self.edit.text()
        if not username:
            username = getcwd()
        if path.exists(username):
            self.username = self.sign_in(username)
            if not self.username:
                self.label.setText("Не удалось войти. "
                                   "Убедитесь что фалы ключей не повреждены")
            else:
                self.close()
        else:
            if not self.sign_up(username):
                self.label.setText("Не удалось зарегистрировать аккаунт. "
                                   "Либо логин указан не верно, "
                                   "либо уже занят...")
            else:
                self.username = username
                self.close()

    def btn_cancel_click(self):
        self.close()


def register(db, style=None):
    app = QtGui.QApplication([])
    app.setStyle("Plastique")

    wnd = RegWnd(db)

    app.exec_()

    return wnd.pubkey, wnd.privkey, wnd.username