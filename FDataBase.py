# -*- coding: utf-8 -*- #

import sqlite3
import time
import math
import re
from flask import url_for

class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Ошибка чтения из БД")
        return []

    def addPost(self, study, work, about_student, user_id):
        try:
            # self.__cur.execute(f"SELECT COUNT() as `count` FROM info_student WHERE user_id == '{user_id}'")
            # res = self.__cur.fetchone()
            # if res['count'] > 0:
            #     print("Информация об этом пользователе уже существует")
            #     return False
            # base = url_for('static', filename='images_html')
            # about_student = re.sub(r"(?P<tag><img\s+[^>]*src=)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)>",
            #               "\\g<tag>" + base + "/\\g<url>>",
            #               about_student)
            date_ = math.floor(time.time())
            self.__cur.execute("INSERT INTO info_student VALUES(NULL, ?, ?, ?, ?, ?)", (study, work, about_student, date_, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления статьи в БД "+str(e))
            return False
        return True

    def getComments(self, location_id):
        try:
            self.__cur.execute(f"SELECT id, author_id, date_, content FROM comments WHERE location_id == '{location_id}' ")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД" + str(e))
        return False

    def getAuthorCom(self, com_id):
        try:
            self.__cur.execute(
                f"SELECT location_id FROM comments WHERE id == '{com_id}' ")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД" + str(e))
        return False

    def getComment(self, com_id):
        try:
            self.__cur.execute(f"SELECT id, author_id, location_id, date_, content FROM comments WHERE id == '{com_id}' ")
            res = self.__cur.fetchone()

            print(res[0])
            if res:
                print(res[0])
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД" + str(e))
        return False

    def getUsers(self):
        try:
            self.__cur.execute('''SELECT * FROM users''')
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД" + str(e))
        return False


    # def getPost(self, alias):
    #     try:
    #         self.__cur.execute(f"SELECT study, work_, about_student FROM info_student WHERE url LIKE '{alias}' LIMIT 1")
    #         res = self.__cur.fetchone()
    #         if res:
    #             return res
    #     except sqlite3.Error as e:
    #         print("Ошибка получения статьи из БД "+str(e))
    #     return (False, False, False)

    def getInfo_by_id(self, user_id):
        try:
            self.__cur.execute(
                f"SELECT study, work_, about_student FROM info_student WHERE user_id == '{user_id}' LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД " + str(e))
        return (False, False, False)

    def getStudentProfiles(self):
        try:
            self.__cur.execute(f"SELECT id, study, work_, about_student, user_id FROM info_student ORDER BY date_ DESC")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД1 "+str(e))
        return []

    def addUser(self, name, email, hpsw):
        # try:
        self.__cur.execute(f"SELECT COUNT() as `count` FROM users WHERE email LIKE '{email}'")
        res = self.__cur.fetchone()
        if res['count'] > 0:
            print("Пользователь с таким email уже существует")
            return False
        tm = math.floor(time.time())
        self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, NULL, ?, ?)", (name, email, hpsw, tm, 0))
        self.__db.commit()
        return True

    def add_comment(self, author, location, content):
        try:
            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO comments VALUES(NULL, ?, ?, ?, ?)", (author, location, content, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления комментария в БД " + str(e))
            return False

        return True

    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД "+str(e))

        return False

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД "+str(e))

        return False

    def updateUserAvatar(self, avatar, user_id):
        if not avatar:
            return False
        try:
            binary = sqlite3.Binary(avatar)
            self.__cur.execute(f"UPDATE users SET avatar = ? WHERE id = ?", (binary, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка обновления аватара в БД: "+str(e))
            return False
        return True

    def updateInfo(self, study, work, info, user_id):
        try:
            self.__cur.execute(f"UPDATE info_student SET study = ?, work_ = ?, about_student = ? WHERE user_id = ?", (study, work, info, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка обновления информации в БД: " + str(e))
            return False
        return True

    def delete_user(self, user_id):
        try:
            self.__cur.execute(f"DELETE FROM users WHERE id =='{user_id}'")
            self.__cur.execute(f"DELETE FROM info_student WHERE user_id =='{user_id}'")
            self.__cur.execute(f"DELETE FROM comments WHERE author_id =='{user_id}'")
            self.__cur.execute(f"SELECT * FROM users WHERE id = '{user_id}' LIMIT 1")
            self.__db.commit()
            res = self.__cur.fetchone()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка при удалении пользователя из БД " + str(e))
        return False

    def delete_com(self, com_id):
        try:
            self.__cur.execute(f"DELETE FROM comments WHERE id =='{com_id}'")
            self.__db.commit()
            res = self.__cur.fetchone()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка при удалении комментария из БД " + str(e))
        return False
