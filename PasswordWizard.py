# -*- coding: cp1251 -*-
__author__ = 'whoami'
__version__ = "2.2.5"

from PyQt4.QtGui import *
from functools import partial
import webbrowser
from db.data_base import DataBase
from gui import master, welcome, get_style
from config_read import read_cfg


def check_version(version_info):
    def open_url(url):
        webbrowser.open(url)

    if version_info[0] not in __version__:
        text_update = read_cfg("resources.ini", "update")

        version_info = list(version_info)
        version_info.append(__version__)
        version_info.append("\n")

        info = text_update["text"].format(*version_info)

        app = QApplication([])

        btn_update = QPushButton(info, None)
        btn_update.clicked.connect(partial(open_url, version_info[1]))
        btn_update.show()

        app.exec_()
        return True
    else:
        return False


if __name__ == '__main__':
    try:
        db = DataBase()  # Connect to DataBase
        if check_version(db.get_version()):
            raise SystemExit(0)
    except RuntimeError as e:
        raise SystemExit(e)

    style_sheet = get_style.get_style_sheet()

    pubkey, privkey, username = welcome.register(db, style_sheet)
    keys = dict(public=pubkey, private=privkey)

    if username:
        master.start(db, keys, username, __version__, style_sheet)
    else:
        raise SystemExit(0)
    raise SystemExit(0)
