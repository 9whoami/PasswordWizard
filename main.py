# -*- coding: cp1251 -*-
__author__ = 'whoami'
__version__ = "0.1.0"

from argparse import ArgumentParser, FileType
from key_gen import rsa_load_key, encode_md5
from db.data_base import DataBase
from gui import greeting, master, welcome


def main(pubkey, privkey):
    """
    Инициализирующий метод.
    :param pubkey: публичный ключ
    :param privkey: приватный ключ
    :return: -
    """
    db = DataBase() # подключаемся к бд
    keys = dict(public=pubkey, private=privkey)
    pubkey_in_md5 = encode_md5(keys["public"].save_pkcs1())

    username = db.sign_in(pubkey_in_md5)

    if username:
        master.start(db, keys, username)
    else:
        print("Access denied!")
        quit()


# def create_parser():
#     """
#     создаем парсер аргументов командной строки
#     :return: -
#     """
#     parser = ArgumentParser(add_help=False)
#     parser.add_argument('-ok', '--openkey', type=FileType(mode='rb'),
#                         help='the file containing the public key')
#     parser.add_argument('-pk', '--privatekey',
#                         type=FileType(mode='rb'),
#                         help='the file containing the private key')
#     parser.add_argument('-dk', '--dirkey',
#                         help='the folder containing the files with keys')
#     parser.add_argument('-p', '--passwd', default="31337",
#                         help='password to access')
#
#     return parser.parse_args()
#
#
# if __name__ == '__main__':
#     parser = create_parser()
#
#     if parser.passwd == '31337':
#         FLAG = False
#     else:
#         FLAG = True
#
#     if FLAG:
#         if (parser.openkey) and (parser.privatekey):
#             pubkey, privkey = rsa_load_key(publicfile=parser.openkey.read(),
#                                            privatefile=parser.privatekey.read())
#             main(pubkey, privkey)
#         elif parser.dirkey:
#             pubkey, privkey = rsa_load_key(dir=parser.dirkey)
#             main(pubkey, privkey)
#         else:
#             db = DataBase()
#             register(db)
#             quit()
#     else:
#         print("Suck my prick!")
