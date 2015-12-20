# -*- coding: cp1251 -*-
__author__ = 'whoami'

import sys
from re import match
from threading import Thread
from PyQt4 import QtGui, QtCore
from os import path, getcwd
from key_gen import encode_md5, rsa_gen_key, rsa_load_key
from .message_box import message_box
from config_read import read_cfg


class RegWnd(QtGui.QWidget):
    def __init__(self, db, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.res = read_cfg("resources.ini", "welcome")
        self.icon_wnd = QtGui.QIcon(self.res["icon"])

        self.setWindowTitle(self.res["title"])
        self.setWindowIcon(self.icon_wnd)
        # self.setMaximumSize(250, 200)
        # self.setMinimumSize(250, 200)
        self.setFixedSize(250, 200)
        # self.connect(self, QtCore.SIGNAL("closeEvent()"), self, QtCore.SLOT(""))
        # self.connect(self, QtCore.SIGNAL("showEvent()"), self, QtCore.SLOT(""))

        self.label = QtGui.QLabel(self.res["msg_welcome"])
        self.label.setObjectName("welcome")
        self.label.setWordWrap(True)

        self.edit = QtGui.QLineEdit()
        self.edit.setPlaceholderText(self.res["edit_holder_text"])
        # self.edit.setMaxLength(20)

        self.btn_ok = QtGui.QPushButton(self.res["btn_ok"])

        self.btn_cancel = QtGui.QPushButton(self.res["btn_cancel"])

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
        self.set_animation()

    # def close(self):
        # self.emit(QtCore.SIGNAL("closeEvent()"))

    # def show(self):
        # self.emit(QtCore.SIGNAL("showEvent()"))

    def set_animation(self):
        self.animation = QtCore.QStateMachine()

        state_start = QtCore.QState()
        state_end = QtCore.QState()

        state_start.assignProperty(self.label, "geometry",
                                   QtCore.QRect(20, -29, 200, 200))
        state_end.assignProperty(self.label, "geometry",
                                 QtCore.QRect(21, -29, 200, 200))

        state_start.addTransition(self.btn_ok,
                                  QtCore.SIGNAL("clicked()"), state_end)
        state_end.addTransition(self.btn_ok,
                                QtCore.SIGNAL("clicked()"), state_start)

        label_anim = QtCore.QPropertyAnimation(self.label, "geometry")
        label_anim.setEasingCurve(QtCore.QEasingCurve.InOutElastic)
        label_anim.setDuration(700)

        self.animation.addState(state_start)
        self.animation.addState(state_end)
        self.animation.setInitialState(state_start)
        self.animation.addDefaultAnimation(label_anim)
        self.animation.start()

    def set_signals(self):
        self.btn_ok.clicked.connect(self.btn_ok_click)
        self.btn_cancel.clicked.connect(self.btn_cancel_click)
        self.connect(self.edit, QtCore.SIGNAL("returnPressed()"),
                     self.btn_ok.click)

    def sign_up(self, username):

        def confirm(login):
            return message_box(
                self.res["confirm_text"].format(login),
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                QtGui.QMessageBox.Question,
                self.res["confirm_title"],
                self.icon_wnd
            )

        pattern = r"[0-9A-Za-z]+"
        result = match(pattern, username)
        if not result or len(result.group()) != len(username):
            return False

        if self.db.check_user(username) and confirm(username):
            result = [None]
            t1 = Thread(target=self.get_keys, args=(result,))
            t1.start()
            self.label.setText(self.res["msg_gen_start"])
            # wait thread
            self.setEnabled(False)
            while t1.isAlive():
                self.app.processEvents()
            self.setEnabled(True)

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
                self.label.setText(self.res["msg_wrong_key"])
            else:
                self.close()
        else:
            if not self.sign_up(username):
                self.label.setText(self.res["msg_gen_end"])
            else:
                self.username = username
                self.close()

    def btn_cancel_click(self):
        self.close()


def register(db, style=None):
    app = QtGui.QApplication([])
    app.setStyle("Plastique")
    app.setStyleSheet(style)

    wnd = RegWnd(db, app)

    app.exec_()

    return wnd.pubkey, wnd.privkey, wnd.username