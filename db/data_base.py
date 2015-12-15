# -*- coding: cp1251 -*-
__author__ = 'whoami'

from mysql.connector import MySQLConnection, Error
from config_read import read_cfg


class DataBase(MySQLConnection):
    def __init__(self):
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
        except Error:
            raise RuntimeError()

    def sign_in(self, password):
        rows = self.query_fetch("select * from {} where passwd = {!r}".format(
            self.tables["users"], password))
        if rows:
            self.set_user_id(rows[0][0])
            return rows[0][1]
        else:
            return False

    def set_user_id(self, id):
        self.__userid = id

    def get_email_id(self):
        return self.__emailid

    def get_email_login(self):
        return self.__email_login

    def set_email_id(self, id):
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

    def get_all_accounts(self):
        # creating accounts list
        accounts = self.query_fetch(
            "select id,service,login,passwd,forgot,id_email "
            "from accounts "
            "where id_user = %s" % self.__userid
        )

        for j, i in enumerate(accounts):
            email = self.query_fetch("select login "
                                     "from emails "
                                     "where id = %d" % i[5])
            i = list(i)
            i[5] = email[0][0]
            accounts[j] = i

        return accounts

    # def get_all_emails(self):
    #     return self.query_fetch("select id,login " \
    #                             "from {} " \
    #                             "where id_user = {}".format(
    #         self.tables["emails"], self.__userid))

    def get_accounts(self, table_name):
        if self.all and table_name in self.tables["accounts"]:
            return self.get_all_accounts()

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
        rows = self.query_fetch("select service,login,passwd,forgot " \
                                "from {} " \
                                "where id = {}".format(table_name, id))
        return rows[0]

    def insert_users(self, data):
        query = "insert into {}(passwd,username) " \
                "values(%s,%s)".format(self.tables["users"])
        if self.check_user(data[-1]):
            self.query_insert(query, data)
            return True
        else:
            return False

    def insert_email(self, data):
        data.append(self.__userid)
        query = "insert into {}(service,login,passwd,forgot,id_user) " \
                "values (%s,%s,%s,%s,%s)".format(self.tables["emails"])
        return self.query_insert(query, data)

    def insert_account(self, data):
        data.append(self.__userid)
        data.append(self.__emailid)
        query = "insert into " \
                "{}(service,login,passwd,forgot,id_user,id_email) " \
                "values (%s,%s,%s,%s,%s,%s)".format(self.tables["accounts"])
        return self.query_insert(query, data)

    def insert_other_account(self, data):
        data.append(self.__userid)
        query = "insert into " \
                "{}(service,login,passwd,forgot,id_user) " \
                "values (%s,%s,%s,%s,%s)".format(self.tables["other"])
        return self.query_insert(query, data)

    def update_account(self, *args):
        """
        pass tabel name, service, login, passwd, forgot, field id
        :param args:
        :return:
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
        """table_name, id"""
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
        except (AttributeError, ReferenceError):
            pass
