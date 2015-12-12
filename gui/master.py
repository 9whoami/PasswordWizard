# -*- coding: cp1251 -*-
__author__ = 'whoami'

import sys
from PyQt4 import QtGui, QtCore
from functools import partial
from string import digits, ascii_letters
from random import choice
from mysql.connector import Error
from key_gen import rsa_decode, rsa_encode
from .box_layout import BoxLayout


class MainWnd(QtGui.QMainWindow):
    """
    The main program window
    db: instance of DataBase
    keys: a set of keys (dict)
    username: (str)
    """
    def __init__(self, db, keys, username, parent=None):
        super(MainWnd, self).__init__(parent)
        self.setWindowIcon(QtGui.QIcon("ico.png"))
        # set wnd StayOnTop
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        self.widgets = {}
        self.db = db
        self.keys = keys
        self.tbl = None
        self.passwd_length = 6  # starting length for password
        # set tables_name name for data base
        self.tables_name = ("emails", "accounts", "other_accounts",)

        # setup tray icon
        self.tray_icon = QtGui.QSystemTrayIcon(QtGui.QIcon("ico.png"))
        self.tray_icon.activated.connect(self.on_tray_event)
        self.tray_icon.show()

        # main widgets
        self.btn_add = QtGui.QPushButton('Add')
        self.btn_add.clicked.connect(self.form_add)

        # setup main menu for btn_show
        menu_btn_show = QtGui.QMenu()
        for table in self.tables_name:
            menu_btn_show.addAction(QtGui.QAction(table,
                                              self,
                                              triggered=partial(
                                                  self.show_accounts,
                                                  table
                                              )
                                              )
                                )

        self.btn_show = QtGui.QPushButton("Show")
        self.btn_show.setMenu(menu_btn_show)

        self.btn_genpasswd = QtGui.QPushButton("Gen password")
        self.btn_genpasswd.clicked.connect(self.generation_passwd)

        self.edit = QtGui.QLineEdit()
        # setup statusbar
        self.status_bar = QtGui.QStatusBar()
        # create label for email
        self.email_label = QtGui.QLabel()
        self.status_bar.addPermanentWidget(self.email_label)
        self.status_bar.addPermanentWidget(QtGui.QLabel(username))
        # create main menu for tray icon
        self.main_menu = QtGui.QMenu()
        # setup scroll layouts
        self.scroll_layout = QtGui.QFormLayout()

        self.scroll_widget = QtGui.QWidget()
        self.scroll_widget.setLayout(self.scroll_layout)

        self.scroll_area = QtGui.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)

        self.horizontal_box = QtGui.QHBoxLayout()
        self.horizontal_box.addWidget(self.btn_add)
        self.horizontal_box.addWidget(self.btn_show)
        self.horizontal_box.addWidget(self.btn_genpasswd)
        self.horizontal_box.addWidget(self.edit)

        self.main_layout = QtGui.QVBoxLayout()
        self.main_layout.addLayout(self.horizontal_box)
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.status_bar)

        self.central_widget = QtGui.QWidget()
        self.central_widget.setLayout(self.main_layout)

        self.setCentralWidget(self.central_widget)

        self.show_accounts(self.tables_name[0])
        self.show_msg("Welcome %s" % username, timeout=5000)
        self.show()

    def on_tray_event(self, reason):
        # tray event for double click
        if reason == 2:
            if self.isHidden():
                self.show()
            else:
                self.hide()

    def form_add(self):
        # show form for add account
        if self.tbl in self.tables_name[1] and not self.db.get_email_id():
            self.show_msg("First you need to choose email")
            return
        account = ("add", None, None, None, None,)
        slots = (dict(name="comit", method=self.box_commit),
                 dict(name="del", method=self.box_del))
        index = "add"
        try:
            print(self.widgets[index])
            self.show_msg("The form of addition is already displayed")
        except KeyError:
            self.widgets[index] = self.scroll_layout.addRow(
                BoxLayout(account, slots, self.tbl)
            )

    def show_accounts(self, tbl, box_layout=None):

        def create_slots(self):
            slots = [
                dict(name="get password", method=self.box_get_passwd),
                dict(name="update", method=self.box_update),
                dict(name="del", method=self.box_del)
            ]

            if self.tables_name[0] in self.tbl:
                slots.append(
                    dict(name="show accounts",
                         method=partial(
                             self.show_accounts,
                             self.tables_name[1])
                         )
                )
            return slots

        def clear_widgets(self):
            if self.widgets:
                keys = self.widgets.keys()
                for key in keys:
                    try:
                        self.widgets[key].deleteLater()
                    except KeyError as e:
                        print(e)
                self.widgets.clear()

        self.tbl = tbl

        # setup result for database
        if box_layout:
            if isinstance(box_layout, QtGui.QWidget):
                self.db.set_email_id(box_layout.id)
        else:
            self.db.set_email_id(None)
        self.email_label.setText(self.db.get_email_login())

        accounts = self.db.get_accounts(self.tbl)
        # clear scroll area
        clear_widgets(self)
        slots = create_slots(self)
        # create widgets for accounts
        for account in accounts:
            index = account[0]
            try:
                print(self.widgets[index])
            except KeyError:
                self.widgets[index] = BoxLayout(account, slots, self.tbl)
                self.scroll_layout.addRow(
                    self.widgets[index]
                )
        self.show_msg("Show in %s" % self.tbl)

    def box_get_passwd(self, box_layout):
        # showing or hide password
        account = self.db.get_account(box_layout.tbl, box_layout.id)
        passwd = rsa_decode(account[2], self.keys["private"])

        if not passwd:
            self.show_msg("Unable to retrieve your password")
            return

        box_layout.flag = not box_layout.flag

        if box_layout.flag:
            box_layout.passwd.setEchoMode(QtGui.QLineEdit.Normal)
            box_layout.passwd.setText(passwd)
        else:
            box_layout.passwd.setEchoMode(QtGui.QLineEdit.Password)
            box_layout.passwd.setText(account[2])

    def box_del(self, box_layout):

        def del_confirm(box_layout):
            # TODO MessageBox should be StayOnTop
            confirmation_ok = 1024

            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Question)
            msg.setText("Are you sure you want to delete %s"
                        % box_layout.login.text())
            msg.setWindowTitle("Confirm")
            msg.setStandardButtons(QtGui.QMessageBox.Ok |
                                   QtGui.QMessageBox.Cancel)
            return msg.exec_() == confirmation_ok

        def del_(box_layuot):
            box_layuot.deleteLater()
            try:
                del (self.widgets[box_layout.id])
            except KeyError:
                pass

        if isinstance(box_layout.id, int) and del_confirm(box_layout):
            self.db.del_account(box_layout.tbl, box_layout.id)
            self.show_msg("Account %s removed" % box_layout.login.text())
            del_(box_layout)
        elif del_confirm(box_layout):
            del_(box_layout)

    def box_update(self, box_layout):
        if not box_layout.flag:
            self.show_msg("First get your password")
            return

        passwd = box_layout.passwd.text()
        passwd = rsa_encode(passwd, self.keys["public"])
        if not passwd:
            self.show_msg("Failed to encrypt password")
            return

        result, msg = self.db.update_account(
            box_layout.tbl,
            box_layout.service.text(),
            box_layout.login.text(),
            passwd,
            box_layout.forgot.text(),
            box_layout.id
        )

        if result:
            box_layout.passwd.setEchoMode(QtGui.QLineEdit.Password)
            box_layout.passwd.setText(passwd)
            box_layout.flag = False
            self.show_msg("The data have been updated successfully")
        else:
            self.show_msg(msg)

    def box_commit(self, box_layout):
        passwd = box_layout.passwd.text()
        passwd = rsa_encode(passwd, self.keys["public"])

        if not passwd:
            self.show_msg("Failed to encrypt password")
            return

        # dict methods on add
        db_add = dict(emails=self.db.insert_email,
                      accounts=self.db.insert_account,
                      other_accounts=self.db.insert_other_account)

        db_add[box_layout.tbl]([
            box_layout.service.text(),
            box_layout.login.text(),
            passwd,
            box_layout.forgot.text(),
        ])

        del self.widgets["add"]
        box_layout.deleteLater()
        self.show_accounts(self.tbl, True)
        self.show_msg("Account added %s" % box_layout.login.text())

    def generation_passwd(self):
        length = self.edit.text()
        if length and length.isdigit():
            self.passwd_length = int(length)
        elif not self.passwd_length:
            self.edit.setText("the length password is not specified")
            return

        spec = '!@#$%&*?^'
        digits_ = digits
        all_symbols = spec + digits_ + ascii_letters

        count = 0
        res = []
        while count < self.passwd_length:
            res.append(choice(all_symbols))
            count += 1
        password = ''.join(res)
        self.edit.setText(password)

    def show_msg(self, msg, timeout=3000):
        self.status_bar.showMessage(str(msg), timeout)

    def create_menu_actions(self, menu=None):
        """������������� ������ ���� �� ����� �� ������ � ����"""
        if menu:
            keys = menu.keys()  # [����� �������]
            for key in keys:
                function = menu[key]
                action = self.main_menu.addAction(key)
                action.triggered.connect(function)

        quit_action = self.main_menu.addAction('Quit')
        quit_action.triggered.connect(QtGui.QApplication.quit)
        self.tray_icon.setContextMenu(self.main_menu)
        return True

    def closeEvent(self, event):
        QtGui.QApplication.exit()


def start(db, keys, login):
    app = QtGui.QApplication([])
    app.setStyle("Plastique")

    main_wnd = MainWnd(db, keys, login)

    main_wnd.create_menu_actions(
        dict(Show=main_wnd.show,
             Hide=main_wnd.hide)
    )

    app.exec_()
    del main_wnd
    del db
    sys.exit()
