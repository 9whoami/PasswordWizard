# -*- coding: cp1251 -*-
__author__ = 'whoami'

from mysql.connector import MySQLConnection, Error
from db.dbconfig import read_db_config


class DataBase(MySQLConnection):
    def __init__(self):
        db_config = read_db_config()
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
        rows = self.query_fetch("select * "
                                "from users "
                                "where passwd = '%s'"
                                % password)
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
                                    "from emails " \
                                    "where id = %d" % id)
            self.__email_login = ' '.join(rows[0])
            self.all = False
        else:
            self.__email_login = self.__emailid = None
            self.all = True

    def check_user(self, login):
        try:
            self.cursor.execute("SELECT username "
                                "FROM users")
            rows = self.cursor.fetchall()
            for row in rows:
                if login in row:
                    raise Error("Invalid username")
            return True
        except Error:
            return False

    def get_all_accounts(self):
        # TODO the horror remake in the future!!!
        # creating accounts list
        buf = self.query_fetch(
            "select id,service,login,passwd,forgot,id_email "
            "from accounts "
            "where id_user = %s" % self.__userid
        )
        account_info = [ ]

        for i in buf:
            email = self.query_fetch("select login "
                                     "from emails "
                                     "where id = %d" % i[5])
            buf_account = [ ]
            for j in i:
                buf_account.append(j)
            buf_account[5] = ''.join(email[0])
            account_info.append(buf_account)
        return account_info

    def get_all_emails(self):
        return self.query_fetch("select id,login " \
                                "from emails " \
                                "where id_user = %d" % self.__userid)

    def get_accounts(self, table_name):
        if self.all and table_name in "accounts":
            return self.get_all_accounts()

        if self.__emailid:
            id1 = "id_email"
            id2 = self.__emailid
        else:
            id1 = "id_user"
            id2 = self.__userid

        return self.query_fetch("select id,service,login,passwd,forgot " \
                                "from %s " \
                                "where %s = %s" % (
                                    table_name, id1, id2))

    def get_account(self, table_name, id):
        rows = self.query_fetch("select service,login,passwd,forgot " \
                                "from %s " \
                                "where id = %s" % (table_name, id))
        return rows[0]

    def insert_users(self, data):
        query = "insert into users(passwd,username) " \
                "values(%s,%s)"
        if self.check_user(data[-1]):
            self.query_insert(query, data)
            return True
        else:
            return False

    def insert_email(self, data):
        data.append(self.__userid)
        query = "insert into emails(service,login,passwd,forgot,id_user) " \
                "values (%s,%s,%s,%s,%s)"
        return self.query_insert(query, data)

    def insert_account(self, data):
        data.append(self.__userid)
        data.append(self.__emailid)
        query = "insert into " \
                "accounts(service,login,passwd,forgot,id_user,id_email) " \
                "values (%s,%s,%s,%s,%s,%s)"
        return self.query_insert(query, data)

    def insert_other_account(self, data):
        data.append(self.__userid)
        query = "insert into " \
                "other_accounts(service,login,passwd,forgot,id_user) " \
                "values (%s,%s,%s,%s,%s)"
        return self.query_insert(query, data)

    def update_account(self, tabel, service, login, passwd, forgot, id):
        query = "update %s " \
                "set service = '%s', login = '%s', passwd = '%s', forgot = '%s' " \
                "where id = %d;" % (tabel, service, login, passwd, forgot, id)
        try:
            self.cursor.execute(query)
            self.commit()
            return True, None
        except Error as e:
            print(e)
            return False, e

    def del_account(self, table_name, id):
        query = "delete " \
                "from %s " \
                "where id = %s" % (table_name, id)
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
