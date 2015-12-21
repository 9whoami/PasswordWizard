# -*- coding: cp1251 -*-
__author__ = 'whoami'
__version__ = "2.2.2"

from argparse import ArgumentParser, FileType
from key_gen import rsa_load_key, encode_md5
from db.data_base import DataBase
from gui import master, welcome, get_style

if __name__ == '__main__':
    db = DataBase()  # Connect to DataBase

    style_sheet = get_style.get_style_sheet()

    pubkey, privkey, username = welcome.register(db, style_sheet)
    keys = dict(public=pubkey, private=privkey)

    if username:
        master.start(db, keys, username, __version__, style_sheet)
    else:
        raise SystemExit(0)
    raise SystemExit(0)
