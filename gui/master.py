# -*- coding: cp1251 -*-
__author__ = 'whoami'
__version__ = "2.6.4"

"""
������� ���� ���������.
"""

from time import sleep, clock
import threading
from itertools import chain
from PyQt4 import QtGui, QtCore
from functools import partial
from string import digits, ascii_letters
from random import choice
from mysql.connector import Error
from key_gen import rsa_decode, rsa_encode
from .box_layout import BoxLayout
from .get_style import get_style_sheet
from .message_box import message_box
from config_read import read_cfg, write_cfg


def thread(my_func):
    """
    ��������� ��� ������� ������� � ������
    :param my_func: functions
    :return: functions
    """

    def wrapper(*args, **kwargs):
        my_thread = threading.Thread(target=my_func, args=args, kwargs=kwargs)
        my_thread.start()

    return wrapper


@thread
def wait(args):
    """
    �������� ����������� �������� ���� ����������
    :param args: self, self.my_signal, tbl, box_layout, accounts
    :return:
    """
    try:
        timer = 4
        while args[0].scroll_layout.count():
            i = timer - int(clock())
            if i < 2:
                break
            args[0].app.processEvents()
        args[1].emit(args[2:])
    except Error:
        return


class QWidget(QtGui.QWidget):
    def __init__(self, wnd):
        """
        :arg wnd: self
        """
        super().__init__()
        self.wnd = wnd

    def resizeEvent(self, QResizeEvent):
        """
        ���� ������� ��������� ������� ��� ���������� ��������, �����
        ���������� ������ ���� � ������������ �������
        """
        try:
            self.wnd.scroll_area.ensureWidgetVisible(
                self.wnd.widgets["add"], 0, 0)
        except KeyError:
            pass
        return super().resizeEvent(QResizeEvent)


class MainWnd(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        """
        ������� ������ ����� ������ ������ ��� self � ���������� ����
        :param args: db, keys, username, ver, app
        :param kwargs:
        :return:
        """
        super().__init__()
        # read settings
        self.ini = "resources.ini"
        icons_path = read_cfg(self.ini, 'image')
        self.tables_name = read_cfg(self.ini, "table_db")
        self.msg = read_cfg(self.ini, "msg")
        # get passed parameters
        self.db = args[0] if args else kwargs["db"]
        self.keys = args[1] if args else kwargs["keys"]
        self.username = args[2] if args else kwargs["username"]
        self.ver = "v." + args[3] if args else kwargs["version"]
        self.app = args[4] if args else kwargs["app"]
        # setup default parameters
        self.widgets = {}
        self.tbl = None
        self.last_widget = None
        self.passwd_length = 6  # starting length for password

        # TODO ������� !
        buf = read_cfg(self.ini, "animation_color")
        keys = buf.keys()
        self.animation_color = {}
        for key in keys:
            if key in "css" or key in "increment":
                self.animation_color[key] = buf[key]
                continue
            i = buf[key].split(",")
            for j in range(len(i)):
                i[j] = int(i[j])
            self.animation_color[key] = i

        self.icons = {}
        for key, value in icons_path.items():
            self.icons[key] = QtGui.QIcon(value)

        self.create_widgets()
        self.set_signals()
        self.set_layouts()
        self.set_window()
        self.tray_icon.show()
        self.show()

    def __del__(self):
        del self.db
        for icon in self.icons:
            del icon

    def show(self):
        super().show()
        self.show_msg(self.msg["msg_welcome"].format(self.username),
                      timeout=5000)
        self.animation_object(self.btn_add, reverse=True)
        self.animation_object(self.btn_show, reverse=True)
        self.animation_object(self.btn_genpasswd, reverse=True)
        self.animation_object(self.edit, reverse=True)
        self.show_accounts((self.tables_name["emails"],))

    def closeEvent(self, *args, **kwargs):
        # save settings before closing
        self.store_window()

    def set_window(self):
        wnd_params = read_cfg(self.ini, "window")
        size = wnd_params["size"][1:-1].split(",")

        self.setWindowIcon(self.icons["window"])
        self.setWindowTitle(wnd_params["name"])
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

        self.tray_icon = QtGui.QSystemTrayIcon(self.icons["window"],
                                               parent=self)
        self.main_menu = QtGui.QMenu(parent=self)
        self.btn_add = QtGui.QPushButton(self.icons["add"], btn_caption["add"],
                                         parent=self)
        self.btn_add.setToolTip(tool_tip["add"])

        self.btn_genpasswd = QtGui.QPushButton(self.icons["random"],
                                               btn_caption["gen"], parent=self)
        self.btn_genpasswd.setObjectName("btnPwd")

        self.email_label = QtGui.QLabel(parent=self)

        self.edit = QtGui.QLineEdit(parent=self)
        self.edit.setObjectName("editPwd")
        self.edit.setToolTip(tool_tip["edit_pwd"])

        self.status_bar = QtGui.QStatusBar(parent=self)
        self.status_bar.addPermanentWidget(self.email_label)
        self.status_bar.addPermanentWidget(
            QtGui.QLabel(self.username, parent=self)
        )
        self.status_bar.addPermanentWidget(QtGui.QLabel(self.ver, parent=self))

        # setup main menu for btn_show
        menu_btn_show = QtGui.QMenu()
        for key, table in self.tables_name.items():
            try:
                action = QtGui.QAction(self.icons[key], table, self,
                                       triggered=partial(
                                           self.hide_show_accounts,
                                           table))
                action.setToolTip(tool_tip[key])
                menu_btn_show.addAction(action)
            except KeyError:
                continue

        self.btn_show = QtGui.QPushButton(self.icons["down"],
                                          btn_caption["show"], parent=self)
        self.btn_show.setToolTip(tool_tip["show"])
        self.btn_show.setMenu(menu_btn_show)
        values = chain(self.animation_color["hide"],
                       self.animation_color["hide"])
        qss = get_style_sheet(target=(self.animation_color["css"],))
        self.setStyleSheet(qss.format(*values))

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

    signal_1 = QtCore.pyqtSignal(list, name='my_signal')

    def set_signals(self):
        self.signal_1.connect(self.show_accounts, QtCore.Qt.QueuedConnection)
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

    def animation_object(self, obj, color=None, color_end=None,
                         font_color=None, font_end_color=None,
                         reverse=False):
        """
        ��������� �������� ��������� � ������������ ��������. ���������� �����
        0.3-0.4 c. ��� �������� ��������� ����� �������� �������� ������
        ������������ ��������. ��� ����� � rgb. ��������� �������� �������
        � resourse.ini
        :type obj: QtCore.QObject (������ ��������.
                                    ������ ������������ ����� setStyleSheet)
        :type color: list (��������� �������� ����� ��� ������� ���-��)
        :default: hide
        :type color_end: list (�������� �������� �����)
        :default: light
        :type font_color: list (��������� �������� ��� ������� ��������)
        :default: hide
        :type font_end_color: list (�������� ��������)
        :default: font
        :type reverse: bool (True - ��������� �������, False - ���������)
        """

        def switch(color, color_end, increment):
            """

            :type font: list
            :type font_end: list
            :type increment: int (��� ��������� �����)
            :type color_end: list
            :type color: list
            """
            break_ = lambda l1, l2: not len(set(l1).difference(set(l2))) > 0
            while True:
                yield color
                if break_(color, color_end): raise StopIteration
                for i, c in enumerate(color):
                    if c > color_end[i]:
                        if c - color_end[i] > increment:
                            c -= increment
                        else:
                            c = color_end[i]
                    elif c < color_end[i]:
                        if color_end[i] - c > increment:
                            c += increment
                        else:
                            c = color_end[i]
                    color[i] = c

        def switch_enabled(cls, obj):
            """
            ��������� ������� ������� ����� �������� �������� �� �����
            ��������
            :param cls: QtCore.QObject (��������� ������ 'self')
            :param obj: QtCore.QObject (������ ��������)
            :return:
            """
            cls.btn_show.setEnabled(not cls.btn_show.isEnabled())
            cls.btn_add.setEnabled(not cls.btn_add.isEnabled())
            if isinstance(obj, QtGui.QPushButton):
                obj.setEnabled(not obj.isEnabled())
            self.setFocus()

        if reverse: switch_enabled(self, obj)

        color = color if color else list(self.animation_color["hide"])
        color_end = color_end if color_end else list(
            self.animation_color["light"])
        font_color = font_color if font_color else list(
            self.animation_color["hide"])
        font_end_color = font_end_color if font_end_color else list(
            self.animation_color["font"])
        style_sheet = get_style_sheet(target=(self.animation_color["css"],))
        increment = int(self.animation_color["increment"])

        color_iter = switch(color + font_color, color_end + font_end_color,
                            increment)

        # run the animation
        for value in color_iter:
            v = style_sheet.format(*value)
            obj.setStyleSheet(v)
            sleep(.030)
            self.app.processEvents()

        # if reverse = true exit this method...
        if not reverse:
            switch_enabled(self, obj)
            return
        # ...else run this method once again
        self.animation_object(obj,
                              color=list(color_end),
                              color_end=list(self.animation_color["border"]),
                              font_color=list(font_color),
                              font_end_color=
                              list(self.animation_color["font"]))

    def widgets_clear(self):
        if threading.active_count() > 4:
            return
        try:
            if self.widgets:
                for value in self.widgets.values():
                    try:
                        self.box_connect(value, False)
                        value.deleteLater()
                        self.animation_object(value,
                                              color=
                                              list(self.animation_color[
                                                       "border"]),
                                              color_end=
                                              list(self.animation_color[
                                                       "hide"]),
                                              font_color=
                                              list(self.animation_color[
                                                       "font"]),
                                              font_end_color=
                                              list(self.animation_color[
                                                       "hide"]))
                    except KeyError:
                        continue
                self.widgets.clear()
        except AttributeError:
            return

    def form_add(self):
        # show form for add account
        if threading.active_count() > 4:
            return
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
            self.animation_object(self.widgets[index], reverse=True)

    def hide_show_accounts(self, tbl, box_layout=None, accounts=None):
        if threading.active_count() > 4:
            return
        self.widgets_clear()
        wait((self, self.my_signal, tbl, box_layout, accounts,))

    def show_accounts(self, args):
        """

        :param tbl:
        :param box_layout:
        :param accounts: tuple(id,service,login,passwd,forgot)
        :return:
        """

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
                             main.hide_show_accounts,
                             main.tables_name["accounts"]),
                         icon=main.icons["accounts_2"]
                         )
                )
            return slots_

        if threading.active_count() > 4:
            return

        self.tbl = args[0]
        box_layout = args[1] if len(args) > 2 else None
        # setup result for database
        if box_layout:
            if isinstance(box_layout, QtGui.QWidget):
                self.db.set_email_id(box_layout.id)
        else:
            self.db.set_email_id(None)
        self.email_label.setText(self.db.get_email_login())

        accounts = args[2] if len(args) > 3 else self.db.get_accounts(self.tbl)

        slots = create_slots(self)
        # create widgets for accounts
        try:
            for i, account in enumerate(accounts, 1):
                index = account[0]
                try:
                    print(self.widgets[index])
                except KeyError:
                    self.show_msg("{}/{}".format(i, len(accounts)), 1000)
                    self.widgets[index] = BoxLayout(self.tbl,
                                                    account,
                                                    slots,
                                                    self.icons["down"])
                    self.scroll_layout.addRow(self.widgets[index])
                    self.animation_object(self.widgets[index], reverse=True)
        except TypeError:
            pass
        # self.set_style_with_application()
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
        error = lambda: \
            self.animation_object(box_layout,
                                  color=
                                  list(self.animation_color["border"]),
                                  color_end=
                                  list(self.animation_color["error"]),
                                  font_color=
                                  list(self.animation_color["font"]),
                                  reverse=True)
        # showing or hide password
        account = self.db.get_account(box_layout.tbl, box_layout.id)
        passwd = rsa_decode(account[2], self.keys["private"])

        if not passwd:
            self.show_msg("Unable to retrieve your password")
            error()
            return
        self.animation_object(box_layout,
                              color=
                              list(self.animation_color["border"]),
                              color_end=
                              list(self.animation_color["light"]),
                              font_color=
                              list(self.animation_color["font"]),
                              font_end_color=
                              list(self.animation_color["font"]),
                              reverse=True)

        self.box_flag_change(box_layout, passwd, account[2])

    def box_del(self, box_layout):

        def del_confirm(cls, box):
            return message_box(
                cls.msg["confirm_del"].format(box.login.text()) \
                    if box.tbl not in cls.tables_name["emails"] else \
                    cls.msg["confirm_del_email"].format("\n", "\n",
                                                        box.login.text()),
                QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                QtGui.QMessageBox.Warning,
                cls.msg["title_confirm_del"],
                cls.icons["window"],
                parent=self)

        def del_(cls, box_layuot):
            cls.animation_object(box_layout,
                                 # [77, 136, 192]
                                 color=list(cls.animation_color["border"]),
                                 # [253, 253, 253]
                                 color_end=list(cls.animation_color["hide"]),
                                 # [41, 41, 41]
                                 font_color=list(cls.animation_color["font"]),
                                 font_end_color=list(
                                     cls.animation_color["hide"]),
                                 reverse=True)
            box_layuot.deleteLater()
            try:
                del (self.widgets[box_layout.id])
                if box_layout.flag:
                    self.box_connect(box_layout, False)
            except KeyError:
                pass

        if isinstance(box_layout.id, int) and del_confirm(self, box_layout):
            self.db.del_account(box_layout.tbl, box_layout.id)
            self.show_msg(
                self.msg["msg_account_del"].format(box_layout.login.text()))
            del_(self, box_layout)
        elif isinstance(box_layout.id, str):
            del_(self, box_layout)

    def box_update(self, box_layout):

        error = lambda: \
            self.animation_object(box_layout,
                                  color=
                                  list(self.animation_color["border"]),
                                  color_end=
                                  list(self.animation_color["error"]),
                                  font_color=
                                  list(self.animation_color["font"]),
                                  reverse=True)

        if not box_layout.flag:
            self.show_msg(self.msg["msg_update_error_1"])
            error()
            return

        passwd = box_layout.passwd.text()
        if not passwd:
            self.show_msg(self.msg["msg_update_error_2"])
            error()
            return

        passwd = rsa_encode(passwd, self.keys["public"])
        if not passwd:
            self.show_msg(self.msg["msg_update_error_3"])
            error()
            return

        result, _ = self.db.update_account(
            box_layout.tbl,
            box_layout.service.text(),
            box_layout.login.text(),
            passwd,
            box_layout.forgot.text(),
            box_layout.id
        )

        self.animation_object(box_layout,
                              color=
                              list(self.animation_color["border"]),
                              color_end=
                              list(self.animation_color["light"]),
                              font_color=
                              list(self.animation_color["font"]),
                              reverse=True)
        if result:
            self.box_flag_change(box_layout, passwd)
            self.box_connect(box_layout, False)
            box_layout.set_hint()
            self.show_msg(self.msg["msg_update_ok"])
        else:
            self.show_msg(self.msg["msg_update_error_4"])
            error()

    def box_commit(self, box_layout):

        error = lambda: \
            self.animation_object(box_layout,
                                  color=
                                  list(self.animation_color["border"]),
                                  color_end=
                                  list(self.animation_color["error"]),
                                  font_color=
                                  list(self.animation_color["font"]),
                                  reverse=True)

        passwd = box_layout.passwd.text()
        if not passwd:
            self.show_msg(self.msg["msg_password_empty"])
            error()
            return
        passwd = rsa_encode(passwd, self.keys["public"])

        if not passwd:
            self.show_msg(self.msg["msg_encrypt_error"])
            error()
            return
        # dict methods on add
        db_add = dict(emails=self.db.insert_email,
                      accounts=self.db.insert_account,
                      other_accounts=self.db.insert_other_account)
        account_info = [0,
                        box_layout.service.text(),
                        box_layout.login.text(),
                        passwd,
                        box_layout.forgot.text()]
        id = db_add[box_layout.tbl](account_info[1:])
        account_info[0] = id
        self.box_connect(box_layout, False)
        box_layout.deleteLater()
        self.animation_object(box_layout,
                              color=
                              list(self.animation_color["border"]),
                              color_end=
                              list(self.animation_color["hide"]),
                              font_color=
                              list(self.animation_color["font"]),
                              font_end_color=
                              list(self.animation_color["hide"]),
                              reverse=True)
        del self.widgets["add"]
        wait((self, self.my_signal, self.tbl, True,
              [account_info],))
        self.show_msg(
            self.msg["msg_account_add"].format(account_info[2]))

    def show_msg(self, msg, timeout=3000):
        self.status_bar.showMessage(str(msg), timeout)

    def create_menu_actions(self, menu=None):
        """������������� ������ ���� �� ����� �� ������ � ����"""
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

        # def set_style_with_application(self):
        #     self.app.setStyleSheet(get_style_sheet())
        #     return


def start(db, keys, login, ver, style=None):
    app = QtGui.QApplication([])
    app.setStyle("Plastique")
    app.setStyleSheet(style)

    main_wnd = MainWnd(db, keys, login, ver, app)
    main_wnd.create_menu_actions(
        dict(show=main_wnd.show,
             hide=main_wnd.hide, )
    )

    app.exec_()
    del main_wnd
    return
