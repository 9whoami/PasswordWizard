# -*- coding: cp1251 -*-
__author__ = 'whoami'

from time import clock
from PyQt4 import QtGui, QtCore
from functools import partial
from string import digits, ascii_letters
from random import choice
from mysql.connector import Error
from threading import Thread, Lock
from key_gen import rsa_decode, rsa_encode
from .box_layout import BoxLayout
from .style import get_style_sheet
from .message_box import message_box
from config_read import read_cfg, write_cfg


class QWidget(QtGui.QWidget):
    def __init__(self, wnd):
        super().__init__()
        self.wnd = wnd

    def resizeEvent(self, QResizeEvent):
        super().resizeEvent(QResizeEvent)
        try:
            self.wnd.scroll_area.ensureWidgetVisible(self.wnd.widgets["add"])
        except KeyError:
            pass


class MainWnd(QtGui.QMainWindow):
    """
    The main program window
    db, keys, username, ver, app, parent=None
    """

    def __init__(self, *args, **kwargs):
        super().__init__()

        self.ini = "resources.ini"

        icons_path = read_cfg(self.ini, 'image')
        self.icons = {}
        for key, value in icons_path.items():
            self.icons[key] = QtGui.QIcon(value)
        self.msg = read_cfg(self.ini, "msg")

        self.db = args[0] if args else kwargs["db"]
        self.keys = args[1] if args else kwargs["keys"]
        self.username = args[2] if args else kwargs["username"]
        self.ver = "v." + args[3] if args else kwargs["version"]
        # self.app_style = args[4] if args else kwargs["app_style"]

        self.widgets = {}
        self.tbl = None
        self.last_widget = None
        self.passwd_length = 6  # starting length for password
        # set tables_name name for data base
        self.tables_name = read_cfg(self.ini, "table_db")

        self.create_widgets()
        self.set_signals()
        self.set_layouts()
        self.set_window()

        self.show_accounts(self.tables_name["emails"])
        self.tray_icon.show()
        self.show()

    def __del__(self):
        self.clear_widgets()
        del self.db

        for icon in self.icons:
            del icon

    # def mouseDoubleClickEvent(self, *args, **kwargs):
    #     self.emit(QtCore.SIGNAL('style()'))
    #     super().mouseDoubleClickEvent(*args, **kwargs)

    def show(self):
        super().show()
        self.show_msg(self.msg["msg_welcome"].format(self.username), timeout=5000)

    def closeEvent(self, *args, **kwargs):
        self.store_window()

    def set_window(self):
        wnd_params = read_cfg(self.ini, "window")
        self.setWindowIcon(self.icons["window"])
        self.setWindowTitle(wnd_params["name"])
        size = wnd_params["size"][1:-1].split(",")
        self.resize(int(size[1]), int(size[0]))
        self.setWindowFlags(self.windowFlags() |
                            QtCore.Qt.WindowStaysOnTopHint)

    def store_window(self):
        size = self.size()
        write_cfg(self.ini, "window", "size",
                  (size.height(), size.width(),))
        return

    def create_widgets(self):
        btn_caption = read_cfg(self.ini, "btn_name")
        tool_tip = read_cfg(self.ini, "tool_tip")
        self.tray_icon = QtGui.QSystemTrayIcon(self.icons["window"])
        self.main_menu = QtGui.QMenu()
        self.btn_add = QtGui.QPushButton(self.icons["add"], btn_caption["add"])
        self.btn_add.setToolTip(tool_tip["add"])

        self.btn_genpasswd = QtGui.QPushButton(self.icons["random"],
                                               btn_caption["gen"])
        self.btn_genpasswd.setObjectName("btnPwd")

        self.email_label = QtGui.QLabel()

        self.edit = QtGui.QLineEdit()
        self.edit.setObjectName("editPwd")
        self.edit.setToolTip(tool_tip["edit_pwd"])

        self.status_bar = QtGui.QStatusBar()
        self.status_bar.addPermanentWidget(self.email_label)
        self.status_bar.addPermanentWidget(
            QtGui.QLabel(self.username)
        )
        self.status_bar.addPermanentWidget(QtGui.QLabel(self.ver))

        # setup main menu for btn_show
        menu_btn_show = QtGui.QMenu()
        for key, table in self.tables_name.items():
            try:
                action = QtGui.QAction(self.icons[key], table, self,
                                       triggered=partial(self.show_accounts,
                                                         table))
                action.setToolTip(tool_tip[key])
                menu_btn_show.addAction(action)
            except KeyError:
                continue

        self.btn_show = QtGui.QPushButton(self.icons["down"],
                                          btn_caption["show"])
        self.btn_show.setToolTip(tool_tip["show"])
        self.btn_show.setMenu(menu_btn_show)

    def set_layouts(self):
        self.scroll_layout = QtGui.QFormLayout()
        self.scroll_layout.setAlignment(QtCore.Qt.AlignHCenter |
                                        QtCore.Qt.AlignTop)
        self.scroll_layout.setHorizontalSpacing(0)
        self.scroll_layout.setVerticalSpacing(0)

        # self.scroll_area = QtGui.QScrollArea()
        self.scroll_widget = QWidget(self)
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

    def set_signals(self):
        self.connect(self, QtCore.SIGNAL("style()"),
                     QtCore.SLOT("set_style()"))
        self.tray_icon.activated.connect(self.on_tray_event)
        self.btn_add.clicked.connect(self.form_add)
        self.btn_genpasswd.clicked.connect(self.generation_passwd)
        self.btn_genpasswd.click()

    def on_tray_event(self, reason):
        # tray event for double click
        if reason == 2:
            if self.isHidden():
                self.show()
            else:
                self.hide()

    def generation_passwd(self):
        length = self.edit.text()
        if length and length.isdigit():
            self.passwd_length = int(length)
        elif not self.passwd_length:
            self.edit.setText("the length password is not specified")
            return
        tool_tip = read_cfg(self.ini, "tool_tip")
        self.btn_genpasswd.setToolTip(
            tool_tip["gen_pwd"].format(self.passwd_length))
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

    def th(self):
        start_ = clock()
        while True:
            end = clock() - start_
            if end > 3:
                self.emit(QtCore.SIGNAL('style()'))
                break
        return

    def clear_widgets(self):
        if self.widgets:
            keys = self.widgets.keys()
            for key in keys:
                try:
                    self.box_connect(self.widgets[key], False)
                    self.widgets[key].deleteLater()
                except KeyError as e:
                    print(e)
            self.widgets.clear()

    def form_add(self):
        # show form for add account
        btn_caption = read_cfg(self.ini, "btn_name")

        if self.tbl in self.tables_name["accounts"] and \
                not self.db.get_email_id():
            self.show_msg("First you need to choose email")
            return
        account = ("add", None, None, None, None,)
        slots = (
            dict(name=btn_caption["commit"], method=self.box_commit,
                 icon=self.icons["commit"]),
            dict(name=btn_caption["del"], method=self.box_del,
                 icon=self.icons["del"])
        )
        index = "add"
        try:
            print(self.widgets[index])
            self.show_msg("The form of addition is already displayed")
        except KeyError:
            self.widgets[index] = BoxLayout(self.tbl,
                                            account,
                                            slots,
                                            self.icons["down"])
            self.box_connect(self.widgets[index])
            self.scroll_layout.addRow(self.widgets[index])
            t = Thread(target=self.th)
            t.setDaemon(True)
            t.start()

    def show_accounts(self, tbl, box_layout=None):

        def create_slots(main):
            btn_caption = read_cfg(self.ini, "btn_name")
            slots_ = [
                dict(name=btn_caption["show_pwd"], method=main.box_get_passwd,
                     icon=main.icons["locked"]),
                dict(name=btn_caption["update"], method=main.box_update,
                     icon=main.icons["update"]),
                dict(name=btn_caption["del"], method=main.box_del,
                     icon=main.icons["trash"])
            ]

            if main.tables_name["emails"] in main.tbl:
                slots_.append(
                    dict(name=btn_caption["show_accounts"],
                         method=partial(
                             main.show_accounts,
                             main.tables_name["accounts"]),
                         icon=main.icons["accounts_2"]
                         )
                )
            return slots_

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
        self.clear_widgets()
        slots = create_slots(self)
        # create widgets for accounts
        try:
            for account in accounts:
                index = account[0]
                try:
                    print(self.widgets[index])
                except KeyError:
                    self.widgets[index] = BoxLayout(self.tbl,
                                                    account,
                                                    slots,
                                                    self.icons["down"])
                    self.last_widget = self.widgets[index]
                    self.scroll_layout.addRow(self.widgets[index])
        except TypeError:
            pass
        self.show_msg(self.msg["msg_show_accounts"].format(self.tbl))

    def box_connect(self, box_layout, flag=True):
        if flag:
            self.connect(self.edit, QtCore.SIGNAL("textChanged(QString)"),
                         box_layout.passwd.setText)
        else:
            self.disconnect(self.edit, QtCore.SIGNAL("textChanged(QString)"),
                            box_layout.passwd.setText)

    def box_flag_change(self, *args):
        args[0].flag = not args[0].flag
        tool_tip = read_cfg(self.ini, "tool_tip")
        btn_name = read_cfg(self.ini, "btn_name")
        if args[0].flag:
            self.box_connect(args[0])
            args[0].actions[0].setIcon(self.icons["unlocked"])
            args[0].actions[0].setText(btn_name["hide_pwd"])
            args[0].actions[0].setToolTip(tool_tip["hide_pwd"])

            args[0].passwd.setEchoMode(QtGui.QLineEdit.Normal)
            args[0].passwd.setText(args[1])
        else:
            self.box_connect(args[0], False)
            args[0].actions[0].setIcon(self.icons["locked"])
            args[0].actions[0].setText(btn_name["show_pwd"])
            args[0].actions[0].setToolTip(tool_tip["show_pwd"])

            args[0].passwd.setEchoMode(QtGui.QLineEdit.Password)
            args[0].passwd.setText(args[2] if len(args) == 3 else args[1])

    def box_get_passwd(self, box_layout):
        # showing or hide password
        account = self.db.get_account(box_layout.tbl, box_layout.id)
        passwd = rsa_decode(account[2], self.keys["private"])

        if not passwd:
            self.show_msg("Unable to retrieve your password")
            return

        self.box_flag_change(box_layout, passwd, account[2])

    def box_del(self, box_layout):

        def del_confirm(cls, box):
            return message_box(
                cls.msg["confirm_del"].format(box.login.text()) \
                if box.tbl not in cls.tables_name["emails"] else \
                cls.msg["confirm_del_email"].format("\n", "\n", box.login.text()),
                QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                QtGui.QMessageBox.Warning,
                cls.msg["title_confirm_del"],
                cls.icons["window"],
                parent=self)

        def del_(box_layuot):
            box_layuot.deleteLater()
            try:
                del (self.widgets[box_layout.id])
                if box_layout.flag:
                    self.box_connect(box_layout, False)
            except KeyError:
                pass

        if isinstance(box_layout.id, int) and del_confirm(self, box_layout):
            self.db.del_account(box_layout.tbl, box_layout.id)
            self.show_msg(self.msg["msg_account_del"].format(box_layout.login.text()))
            del_(box_layout)
        elif isinstance(box_layout.id, str):
            del_(box_layout)

    def box_update(self, box_layout):
        if not box_layout.flag:
            self.show_msg(self.msg["msg_update_error_1"])
            return

        passwd = box_layout.passwd.text()
        if not passwd:
            self.show_msg(self.msg["msg_update_error_2"])
            return

        passwd = rsa_encode(passwd, self.keys["public"])
        if not passwd:
            self.show_msg(self.msg["msg_update_error_3"])
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
            self.box_flag_change(box_layout, passwd)
            self.box_connect(box_layout, False)
            box_layout.set_hint()
            self.show_msg(self.msg["msg_update_ok"])
        else:
            self.show_msg(self.msg["msg_update_error_4"])

    def box_commit(self, box_layout):
        passwd = box_layout.passwd.text()
        if not passwd:
            self.show_msg(self.msg["msg_password_empty"])
            return
        passwd = rsa_encode(passwd, self.keys["public"])

        if not passwd:
            self.show_msg(self.msg["msg_encrypt_error"])
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
        self.box_connect(box_layout, False)
        del self.widgets["add"]
        box_layout.deleteLater()
        self.show_accounts(self.tbl, True)
        self.show_msg(self.msg["msg_account_add"].format(box_layout.login.text()))

    def show_msg(self, msg, timeout=3000):
        self.status_bar.showMessage(str(msg), timeout)

    def create_menu_actions(self, menu=None):
        """Устанавливает пункты меню по клику на иконку в трее"""
        if menu:
            for key in menu.keys():
                function = menu[key]
                action = self.main_menu.addAction(self.icons[key],
                                                  key.capitalize())
                action.triggered.connect(function)

        quit_action = self.main_menu.addAction(self.icons['heart'], 'Quit')
        quit_action.triggered.connect(QtGui.QApplication.quit)
        self.tray_icon.setContextMenu(self.main_menu)
        return True

    # @QtCore.pyqtSlot()
    # def set_style(self):
    #     self.app_style["app"].setStyleSheet(get_style_sheet())
    #     return


def start(db, keys, login, ver, style=None):
    app = QtGui.QApplication([])
    app.setStyle("Plastique")
    app.setStyleSheet(style)

    main_wnd = MainWnd(db, keys, login, ver)
    main_wnd.create_menu_actions(
        dict(show=main_wnd.show,
             hide=main_wnd.hide, )
    )

    app.exec_()
    del main_wnd
    return
