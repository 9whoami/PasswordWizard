# -*- coding: utf-8 -*-
__author__ = "whoami"
__version__ = "1.1.2"

"""
Реазилует интерфейс работы с базой данных.
"""

from mysql.connector import MySQLConnection, Error
from config_read import read_cfg
from datetime import datetime


class DataBase(MySQLConnection):
    def __init__(self):
        """
        Подключаемся к БД. Создаем курсор.
        :return:
        """
        db_config = read_cfg(file="config.ini",
                             section="mysql")
        self.tables = read_cfg("resources.ini", "table_db")
        try:
            super().__init__(**db_config)
            self.cursor = self.cursor()
            self.__userid = None
            self.__emailid = None
            self.__email_login = None
            self.all = False
            self.username = None
        except Error as e:
            print(e)
            raise RuntimeError()

    def sign_in(self, password):
        """
        Пытаемся войти в аккаунт.
        :param password: str
        :return: str в случае успеха иначе False
        """
        rows = self.query_fetch("select * from {} where passwd = {!r}".format(
            self.tables["users"], password))
        if rows:
            self.set_user_id(rows[0][0])
            self.query_insert("insert into sys_info(id_user,time) "
                              "values (%s,%s)",
                              [rows[0][0], datetime.now()])
            return rows[0][1]
        else:
            return False

    def set_user_id(self, id):
        self.__userid = id

    def get_version(self):
        rows = self.query_fetch("""
          select * from update_info
        """)
        return rows[0][1:] if rows else None

    def get_email_id(self):
        return self.__emailid

    def get_email_login(self):
        return self.__email_login

    def set_email_id(self, id):
        """
        Устанавливает email id. Это важно для отображения списка аккаунтов.
        Если all = True то при запросе списка аккаунтов отобразятся все
         аккаунты пользователя иначе только для текущего email id
        :param id: int
        :return:
        """
        if id:
            self.__emailid = id
            rows = self.query_fetch("select login " \
                                    "from {} " \
                                    "where id = {}".format(
                self.tables["emails"], id
            ))
            self.__email_login = rows[0][0]
            self.all = False
        else:
            self.__email_login = self.__emailid = None
            self.all = True

    def check_user(self, login):
        """
        Доступность имя пользователя
        :param login: str
        :return: bool
        """
        try:
            self.cursor.execute("select username "
                                "from {}".format(self.tables["users"]))
            rows = self.cursor.fetchall()
            for row in rows:
                if login in row:
                    raise Error("Invalid username")
            return True
        except Error:
            return False

    def get_accounts(self, table_name):
        """
        получение списка аккаунтов
        :param table_name:
        :return: tuple in tuple
        """
        if self.all and table_name in self.tables["accounts"]:
            return self.query_fetch("""
                select accounts.id, accounts.service, accounts.login,
                    accounts.passwd, accounts.forgot, emails.login
                from accounts, emails
                where accounts.id_user = {0} and emails.id = accounts.id_email;
                """.format(self.__userid))

        if self.__emailid:
            id1 = "id_email"
            id2 = self.__emailid
        else:
            id1 = "id_user"
            id2 = self.__userid

        return self.query_fetch("select id,service,login,passwd,forgot " \
                                "from {} " \
                                "where {} = {}".format(
                                    table_name, id1, id2))

    def get_account(self, table_name, id):
        """
        получение одного аккаунта из таблице по его id
        :param table_name: str
        :param id: int
        :return: tuple
        """
        rows = self.query_fetch("select service,login,passwd,forgot " \
                                "from {} " \
                                "where id = {}".format(table_name, id))
        return rows[0]

    def insert_users(self, data):
        """
        добавление пользователя в бд
        :param data: list
        :return: bool
        """
        query = "insert into {}(passwd,username) " \
                "values(%s,%s)".format(self.tables["users"])
        if self.check_user(data[-1]):
            self.query_insert(query, data)
            return True
        else:
            return False

    def insert_email(self, data):
        """
        добавление email в bd
        :param data: list
        :return: bool
        """
        data.append(self.__userid)
        query = "insert into {}(service,login,passwd,forgot,id_user) " \
                "values (%s,%s,%s,%s,%s)".format(self.tables["emails"])
        return self.query_insert(query, data)

    def insert_account(self, data):
        """
        :param data: list
        :return: bool
        """
        data.append(self.__userid)
        data.append(self.__emailid)
        query = "insert into " \
                "{}(service,login,passwd,forgot,id_user,id_email) " \
                "values (%s,%s,%s,%s,%s,%s)".format(self.tables["accounts"])
        return self.query_insert(query, data)

    def insert_other_account(self, data):
        """
        :param data: service, login, passwd, forgot,id_user
        :return: bool
        """
        data.append(self.__userid)
        query = "insert into " \
                "{}(service,login,passwd,forgot,id_user) " \
                "values (%s,%s,%s,%s,%s)".format(self.tables["other"])
        return self.query_insert(query, data)

    def update_account(self, *args):
        """
        Обновление данных об аккаунте
        :param args: tabel name, service, login, passwd, forgot, field id
        :return: bool
        """
        query = (
            "update {} "
            "set service = {!r}, login = {!r}, passwd = {!r}, forgot = {!r} "
            "where id = {};".format(*args)
        )
        try:
            self.cursor.execute(query)
            self.commit()
            return True, None
        except Error as e:
            print(e)
            return False, e

    def del_account(self, *args):
        """
        :param args: table_name, id
        :return: bool
        """
        query = "delete " \
                "from {} " \
                "where id = {}".format(*args)
        try:
            self.cursor.execute(query)
            self.commit()
            return True
        except Error:
            return False

    def query_insert(self, sql, data):
        try:
            self.cursor.execute(sql, data)
            self.commit()
            return True
        except Error as e:
            print(e)
            return False

    def query_fetch(self, sql):
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Error:
            return None

    def __del__(self):
        try:
            self.cursor.close()
            self.close()
        except:
            pass
