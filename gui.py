# -*- coding: cp1251 -*-
__author__ = 'whoami'

import sys
from PyQt4 import QtGui, QtCore
from collections import OrderedDict
from functools import partial
from string import digits, ascii_letters
from random import choice
from mysql.connector import Error
from key_gen import rsa_decode, rsa_encode, encode_md5, rsa_gen_key


class Main(QtGui.QMainWindow):
    def __init__(self, db, keys, login, tray_icon=None, parent=None):
        super(Main, self).__init__(parent)
        self.setWindowIcon(QtGui.QIcon("ico.png"))
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        self.widgets = {}
        self.db = db
        self.keys = keys
        self.passwd_length = 6
        self.tray_icon = tray_icon
        self.tray_icon.show()
        tables = ("emails", "accounts", "other_accounts",)

        # главная кнопка
        self.btn_add = QtGui.QPushButton('Add')
        self.btn_add.clicked.connect(self.add_account)

        self.btn_show = QtGui.QPushButton("Show")
        self.btn_genpasswd = QtGui.QPushButton("Gen password")
        self.edit = QtGui.QLineEdit()
        self.email_lable = QtGui.QLabel("None")

        self.status_bar = QtGui.QStatusBar()
        self.status_bar.addPermanentWidget(self.email_lable)
        self.status_bar.addPermanentWidget(QtGui.QLabel(login))
        # подключаем дейсвтие для добавления новой новой кнопки
        # при натажии на Кнопку добавления
        self.main_menu = QtGui.QMenu()

        menu_show = QtGui.QMenu()
        for table in tables:
            menu_show.addAction(QtGui.QAction(table,
                                              self,
                                              triggered=partial(
                                                  self.show_accounts,
                                                  table
                                              )
                                              )
                                )

        # self.btn_add.setMenu(menu_add)
        self.btn_show.setMenu(menu_show)
        self.btn_genpasswd.clicked.connect(self.__generation_passwd)
        # определяем содержимое области(виджета) прокрутки
        #  - а именно слой формата (QFormLayout) - два столбца
        self.scrollLayout = QtGui.QFormLayout()
        # добавляем  ране созданный слой прокрутки
        # на виджет прокрутки
        self.scrollWidget = QtGui.QWidget()  # cначала создаём сам виджет
        self.scrollWidget.setLayout(
            self.scrollLayout)  # добавляем на него слой
        # определяем область механизм прокрутки (QScrollArea)
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidgetResizable(True)  # разрешаем проктурку
        # добавляем на область виджет, с ранее добавленным на него слоем слоем
        self.scrollArea.setWidget(self.scrollWidget)
        # создаём главный вертикальный слой
        self.mainLayout = QtGui.QVBoxLayout()

        self.hbox = QtGui.QHBoxLayout()
        self.hbox.addWidget(self.btn_add)
        self.hbox.addWidget(self.btn_show)
        self.hbox.addWidget(self.btn_genpasswd)
        self.hbox.addWidget(self.edit)

        # добавляем элементы на главный слой
        self.mainLayout.addLayout(self.hbox)  # добавляем основную кнопку
        self.mainLayout.addWidget(
            self.scrollArea)  # добавляем область прокрутки
        self.mainLayout.addWidget(self.status_bar)

        # определяем "центральный виджет"
        self.centralWidget = QtGui.QWidget()
        self.centralWidget.setLayout(self.mainLayout)

        # устанавливаем "центральный виджет"
        self.setCentralWidget(self.centralWidget)

        self.show_accounts(tables[0])
        self.show_msg("Welcome %s" % login)

    def add_account(self):
        if "accounts" == self.tbl and not self.db.get_email_id():
            self.show_msg("First you need to choose email")
            return
        # self.tbl = tbl
        account = ("add", None, None, None, None,)
        slots = (dict(name="comit", method=self.box_comit),
                 dict(name="del", method=self.box_del))
        index = "add"
        try:
            print(self.widgets[index])
            self.show_msg("The form of addition is already displayed")
        except KeyError:
            self.widgets[index] = self.scrollLayout.addRow(
                BoxLayout(account, slots, self.tbl)
            )
            # self.status_bar.showMessage("Аккаунт %s добавлен" % account[1], 2000)

    def show_accounts(self, tbl, box_layout=None):

        def create_slots(self):
            slots = [
                dict(name="get password", method=self.box_get_passwd),
                dict(name="update", method=self.box_update),
                dict(name="del", method=self.box_del)
            ]

            if "emails" in self.tbl:
                slots.append(
                    dict(name="show accounts",
                         method=partial(self.show_accounts,"accounts")
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

        if box_layout:
            if isinstance(box_layout, QtGui.QWidget):
                self.db.set_email_id(box_layout.id)
        else:
            self.db.set_email_id(None)
            self.db.all = True
        self.email_lable.setText(self.db.get_email_login())

        accounts = self.db.get_accounts(self.tbl)

        clear_widgets(self)
        slots = create_slots(self)

        for account in accounts:
            index = account[0]
            try:
                print(self.widgets[index])
            except KeyError:
                self.widgets[index] = BoxLayout(account, slots, self.tbl)
                self.scrollLayout.addRow(
                    self.widgets[index]
                )

        self.db.all = False
        self.show_msg("Show in %s" % self.tbl)

    def box_get_passwd(self, box_layout):
        if box_layout.flag:
            self.show_msg("Password already getting")
        account = self.db.get_account(box_layout.tbl, box_layout.id)
        passwd = rsa_decode(account[2], self.keys["private"])
        if not passwd:
            self.show_msg("Unable to retrieve your password")
            return
        box_layout.passwd.setEchoMode(QtGui.QLineEdit.Normal)
        box_layout.passwd.setText(passwd)
        box_layout.flag = True

    def box_del(self, box_layout):

        def del_confirm(text):
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Question)
            msg.setText(text)
            msg.setWindowTitle("Confirm")
            msg.setStandardButtons(QtGui.QMessageBox.Ok |
                                   QtGui.QMessageBox.Cancel)
            return msg.exec_() == 1024

        def del_(box_layuot):
            box_layout.deleteLater()
            try:
                del (self.widgets[box_layout.id])
            except KeyError:
                pass

        if isinstance(box_layout.id, int) and \
            del_confirm("Are you sure you want to delete %s"
                                   % box_layout.login.text()):

            self.db.del_account(box_layout.tbl, box_layout.id)
            self.show_msg("Account %s removed" % box_layout.login.text())
            del_(box_layout)
        elif not isinstance(box_layout.id, int):
            del_(box_layout)

    def box_update(self, box_layout):
        if box_layout.flag:
            passwd = box_layout.passwd.text()
            passwd = rsa_encode(passwd, self.keys["public"])
            if not passwd:
                self.show_msg("Failed to encrypt password")
                return
            query = "update %s " \
                    "set login = '%s', passwd = '%s', forgot = '%s' " \
                    "where id = %d;" % (box_layout.tbl,
                                        box_layout.login.text(),
                                        passwd,
                                        box_layout.forgot.text(),
                                        box_layout.id)
            try:
                self.db.cursor.execute(query)
                self.db.commit()
                box_layout.passwd.setEchoMode(QtGui.QLineEdit.Password)
                box_layout.passwd.setText(passwd)
                box_layout.flag = False
                self.show_msg("The data have been updated successfully")
            except Error as e:
                print(e)
                self.show_msg(e)
        else:
            self.show_msg("First get your password")

    def box_comit(self, box_layout):
        passwd = box_layout.passwd.text()
        passwd = rsa_encode(passwd, self.keys["public"])
        if not passwd:
            self.show_msg("Failed to encrypt password")
            return
        db_add = dict(emails=self.db.insert_email,
                      accounts=self.db.insert_account,
                      other_accounts=self.db.insert_other_account)  # словарь методов add
        db_add[box_layout.tbl]([
            box_layout.service.text(),
            box_layout.login.text(),
            passwd,
            box_layout.forgot.text(),
        ])
        del (self.widgets["add"])
        box_layout.deleteLater()
        self.show_accounts(self.tbl, 1)
        self.show_msg("Account added")

    def __generation_passwd(self):
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

    def show_msg(self, msg):
        self.status_bar.showMessage(str(msg), 3000)

    def create_menu_actions(self, menu=None):
        """Устанавливает пункты меню по клику на иконку в трее"""
        if menu:
            keys = menu.keys()  # [имена пунктов]
            for key in keys:
                function = menu[key]
                self.action = self.main_menu.addAction(key)
                self.action.triggered.connect(function)

        self.quit_action = self.main_menu.addAction('Quit')
        self.quit_action.triggered.connect(QtGui.QApplication.quit)
        self.tray_icon.setContextMenu(self.main_menu)
        return True

    def closeEvent(self, event):
        QtGui.QApplication.exit()

class BoxLayout(QtGui.QWidget):
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


def start(db, keys, login):
    app = QtGui.QApplication([])
    app.setStyle("Plastique")
    tray = QtGui.QSystemTrayIcon(
        QtGui.QIcon("ico.png")
    )
    myWidget = Main(db, keys, login, tray)

    myWidget.create_menu_actions(
        dict(Show=myWidget.show,
             Hide=myWidget.hide)
    )
    myWidget.show()
    app.exec_()
    print("Goodbye")
    del (db)
    sys.exit()


class RegWnd(QtGui.QWidget):
    def __init__(self, db, parent=None):
        super(RegWnd, self).__init__(parent)
        self.setWindowTitle("Registration")

        self.label = QtGui.QLabel("Type login", self)

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
        # self.resize(300, 150)
        self.db = db
        self.set_signals()

    def set_signals(self):
        self.btn_ok.clicked.connect(self.btn_ok_click)
        self.btn_cancel.clicked.connect(self.btn_cancel_click)

    def btn_ok_click(self):
        login = self.edit.text()
        if self.db.check_user(login):
            self.label.setText("Generating keys...")
            data = rsa_gen_key()
            if data:
                passwd = encode_md5(data)
                if self.db.insert_users([passwd, login]):
                    self.label.setText("Register is done.")
                else:
                    self.label.setText("Wrong login.")
        else:
            self.label.setText("Wrong login.")

    def btn_cancel_click(self):
        self.close()


def register(db):
    app = QtGui.QApplication([])
    wnd = RegWnd(db)
    wnd.show()
    app.exec_()
    del (db)
