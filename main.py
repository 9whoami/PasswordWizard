# -*- coding: cp1251 -*-
__author__ = 'whoami'
__version__ = "0.2.0"

from argparse import ArgumentParser, FileType
from key_gen import rsa_load_key, encode_md5
from db.data_base import DataBase
from gui import master, welcome


def main():
    db = DataBase() # Connect to DataBase
    pubkey, privkey, username = welcome.register(db)
    keys = dict(public=pubkey, private=privkey)

    if username:
        master.start(db, keys, username, __version__)
    else:
        quit()

if __name__ == '__main__':
    main()
