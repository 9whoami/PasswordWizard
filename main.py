# -*- coding: cp1251 -*-
__author__ = 'whoami'

from argparse import ArgumentParser, FileType
from key_gen import rsa_load_key, encode_md5
from db.data_base import DataBase
from gui import register


def main(pubkey, privkey):
    """
    Инициализирующий метод.
    :param pubkey: публичный ключ
    :param privkey: приватный ключ
    :return: -
    """
    db = DataBase() # подключаемся к бд
    access = False # флаг
    keys = dict(public=pubkey, private=privkey)
    pubkey_in_md5 = encode_md5(keys["public"].save_pkcs1())
    rows = db.query_fetch('select * from users')

    for row in rows:
        if row[2] == pubkey_in_md5:
            db.set_user_id(row[0])
            access = True
            login = row[1]
            break

    if not access:
        print("Access denied!")
        quit()
    else:
        import gui
        gui.start(db, keys, login)


def create_parser():
    """
    создаем парсер аргументов командной строки
    :return: -
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument('-ok', '--openkey', type=FileType(mode='rb'),
                        help='the file containing the public key')
    parser.add_argument('-pk', '--privatekey',
                        type=FileType(mode='rb'),
                        help='the file containing the private key')
    parser.add_argument('-dk', '--dirkey',
                        help='the folder containing the files with keys')
    parser.add_argument('-p', '--passwd', default="31337",
                        help='password to access')

    return parser.parse_args()


if __name__ == '__main__':
    parser = create_parser()

    if parser.passwd == '31337':
        FLAG = False
    else:
        FLAG = True

    if FLAG:
        if (parser.openkey) and (parser.privatekey):
            pubkey, privkey = rsa_load_key(publicfile=parser.openkey.read(),
                                           privatefile=parser.privatekey.read())
            main(pubkey, privkey)
        elif parser.dirkey:
            pubkey, privkey = rsa_load_key(dir=parser.dirkey)
            main(pubkey, privkey)
        else:
            db = DataBase()
            register(db)
            quit()
    else:
        print("Suck my prick!")
