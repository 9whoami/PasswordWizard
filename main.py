# -*- coding: cp1251 -*-
__author__ = 'whoami'
__version__ = "1.2.1"

from sys import exit
from argparse import ArgumentParser, FileType
from key_gen import rsa_load_key, encode_md5
from db.data_base import DataBase
from gui import master, welcome

style_file = "./gui/main.styl"
style = open(style_file).read()


def main():
    db = DataBase() # Connect to DataBase
    pubkey, privkey, username = welcome.register(db, style)
    keys = dict(public=pubkey, private=privkey)

    if username:
        master.start(db, keys, username, __version__, style)
    else:
        exit()

if __name__ == '__main__':
    main()
