import sqlite3
import time
import math


class FDataBase:
    def __init__(self, db):  # посилання на звязок з базою даних db
        self.__db = db  # ми зберігаємо посилання в екземплярі цього класу
        self.__cur = db.cursor()  # створюємо курсор. через екземпляр класу курсор ми будемо працювати з таблицями БД: робити запити і отримузвати результати.

    def getMenu(self):  # в методі getMenu відбувається вибір всіх записів з таблиці mainmenu
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)  # викликаємо метод execute класу курсор і передаємо йому sql запит. execute(sql) - означає виконати sql запит
            res = self.__cur.fetchall()  # читає всі строки результату запиту
            if res: return res  # і повертаємо їх(тобто колекцію), якщо записи були прочитані успішно
        except:
            print("Помилка читання з бази даних")
        return []


    def addPost(self, title, text, url):  # метод додавання статті приймає 2 параметри: title, text
        try:  # в блоці try намагаємося додати запис в базу даних
            tm = math.floor(time.time())  # отримуємо поточний час додавання статті, округлений до секунд
            self.__cur.execute("INSERT INTO posts VALUES(NULL, ?, ?, ?, ?)", (title, text, url, tm))  # добавляємо записи в таблицю posts і беремо дані з кортежу (title, text, url, tm)
            self.__db.commit()  # зберігає в базу даних цей запис "INSERT INTO posts VALUES(NULL, ?, ?, ?, ?)"
        except sqlite3.Error as e:  # якщо при додаванні виникла помилка, то
            print("Помилка додавання статті в БД "+str(e))  # виводимо повідомлення про помилку і повертаємо False
            return False

        return True  # якщо стаття додана успішно, то повертаємо True


    def getPost(self, postId):  # метод getPost буде приймати параметр postId
        try:
            self.__cur.execute(f"SELECT title, text FROM posts WHERE id={postId} LIMIT 1")  # і якраз по параметру postId ми будем вибирати статтю з нашої бази даних з таблиці posts. Вибираємо титул, текст з таблиці posts, id статі має співпадати з postId, який ми передаємо в метод getPost
            res = self.__cur.fetchone()  # метод fetchone - беремо лише 1 запис, він там і є один
            if res:  # якщо запис був прочитаний успішно, то
                return res  # повертаємо запис в вигляді кортежа
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД "+str(e))  # а інакше формуємо помилку і повертаємо фолс

        return (False, False)