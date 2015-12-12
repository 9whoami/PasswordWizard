# -*- coding: cp1251 -*-
__author__ = 'whoami'

from rsa import newkeys, PublicKey, PrivateKey, encrypt, decrypt
from rsa.pkcs1 import DecryptionError
from base64 import b64decode, b64encode
from hashlib import new
from os.path import sep
from os.path import exists


def encode_md5(data):
    """
    Кодирует переданную строку в md5
    :param data: str строку для кодирования
    :return: str md5-хэш
    """
    md5 = new("md5")
    md5.update(data)
    return str(md5.hexdigest())


def rsa_gen_key(publicfile='public.key', privatefile='private.key'):
    """
    генерируем ключи доступа
    :param publicfile: имя будущего файла
    :param privatefile: имя будущего файла
    :return: в случае успеха возвращаем публичный и приватный ключи
    """
    (pubkey, privkey) = newkeys(2048)
    pckey = pubkey.save_pkcs1()
    ptkey = privkey.save_pkcs1()

    try:
        with open(publicfile, 'wb') as f:
            f.write(pckey)
        with open(privatefile, 'wb') as f:
            f.write(ptkey)
    except IOError as e:
        print("Error: %s" % e)
        return None, None
    else:
        return pubkey, privkey


def rsa_load_key(public_file=None, private_file=None, dir=None):
    """
    Загружаем ключи из файлов
    :param public_file: файл публичного ключа
    :param private_file: файл приватного ключа
    :param dir: папка с ключами
    :return: возвращаем публичный и приватный ключи
    """
    try:
        if dir:
            if dir[-1] not in sep:
                dir += sep
            public_file = dir + 'public.key'
            private_file = dir + 'private.key'

            if not exists(public_file) or not exists(private_file):
                raise IOError("Key files not found!")

            with open(public_file, 'rb') as f:
                public_file = f.read()
            with open(private_file, 'rb') as f:
                private_file = f.read()
        pubkey = PublicKey.load_pkcs1(keyfile=public_file)
        privkey = PrivateKey.load_pkcs1(keyfile=private_file)
        return pubkey, privkey
    except IOError as e:
        print("Error: %s" % e)
        return None, None


def rsa_encode(data, key):
    """
    кодируем строку
    :param data: строка для кодирования
    :param key: публичный ключ
    :return: результат кодирования
    """
    try:
        data = data.encode("utf8")
        result = encrypt(data, key)
        result = b64encode(result)
        result = result.decode("ascii")
        return result
    except (UnicodeDecodeError,
            UnicodeEncodeError) as e:
        print(e)
        return None


def rsa_decode(data, key):
    """
    декодируем строку
    :param data: строка
    :param key: приватный ключ
    :return: результат
    """
    try:
        data = data.encode("ascii")
        data = b64decode(data)
        result = decrypt(data, key)
        result = result.decode("utf8")
        return result
    except (UnicodeDecodeError,
            UnicodeEncodeError,
            DecryptionError) as e:
        print(e)
        return None


# from base64 import b64decode, b64encode
#
# from Crypto.PublicKey import RSA
# from Crypto.Cipher import PKCS1_OAEP
#
#
# private_key = """-----BEGIN RSA PRIVATE KEY-----
# MIIBOQIBAAJBAKYbe7zyOFICAleubFhB9wxrhUmVjA6l0HHA9oV10z4dzVl9hd0v
# OVZe7kpK6X8+daRPdPHVDLmE/EReZE/8SlcCAwEAAQJAGtQLizvv/sbWTAUe+K5G
# 0Zm4IGdoBKGhZg4NgwbBxKFV9gXhykBoi3oVPJQdlHbxQeqapmt88QMhfA3WUj3+
# qQIhAPYfKjK2vqdgJLGImTBbU3z/70sAGou3KqQ2qe9QczSLAiEArMYxLgwAI2PX
# +tw3gv/3T/pn102OZ9gySAOpCFUSHuUCIDgqrIqeQawYuMb7EVqDvO3NymInR+eS
# iVyoTOecSG45AiBfnYtoDVIiQ8YqWacLA3cttsmy+IPf6mDhQ81PBC10FQIgEAuK
# 3lX7voXU2gb1xJ8yup7xvpfVhzWNjfvVSVoHZLY=
# -----END RSA PRIVATE KEY-----"""
#
# public_key = """-----BEGIN PUBLIC KEY-----
# MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAKYbe7zyOFICAleubFhB9wxrhUmVjA6l
# 0HHA9oV10z4dzVl9hd0vOVZe7kpK6X8+daRPdPHVDLmE/EReZE/8SlcCAwEAAQ==
# -----END PUBLIC KEY-----"""
#
#
# def decrypt(private_key, message):
#     rsa_key = RSA.importKey(private_key)
#     rsa_key = PKCS1_OAEP.new(rsa_key)
#     raw_cipher_data = b64decode(message)
#     decrypted = rsa_key.decrypt(raw_cipher_data)
#     return decrypted.decode('utf8')
#
#
# def encrypt(public_key, message):
#     message = 'hello'.encode('utf8')
#     rsa_key = RSA.importKey(public_key)
#     rsa_key = PKCS1_OAEP.new(rsa_key)
#     encrypted = rsa_key.encrypt(message)
#     return b64encode(encrypted)
#
# encrypted_text = encrypt(public_key, 'привет мир')
# print(encrypted_text)
# decrypted_text = decrypt(private_key, encrypted_text)
# print(decrypted_text)
