import sqlite3
import time
import math
import re  #Імпортуємо модуль регулярного виразу
from flask import url_for


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
            self.__cur.execute(f"SELECT COUNT() as `count` FROM posts WHERE url LIKE '{url}'")  # при додаванні статті ми повинні перевірити чи існує в таблиці стаття з таким url який ми передали в функцію addPost, тому ми перевіряємо кількість рядків в таблиці, url яких є ідентична з url, яку ми передали в функцію.
            res = self.__cur.fetchone()
            if res['count'] > 0:  # якщо count>0, тобто стаття з таким url вже існує в таблиці, то виводимо відповідний текст
                print("Стаття з таким url вже існує")
                return False

            # За допомогою регулярних виразів робимо так, щоб картинки відображалися в статтях
            base = url_for('static', filename='images_html')  # вводимо змінну base, яка буде посилатися на каталог static і підкаталог images_html. Тобто перед кожною назвою картинки ми повинні додати адресу каталога static відносно папки проекту.
            # Вводимо регулярний вираз. Він звертається до тексту нашого html документа text, знаходимо теги img - img\s+[^>]*src= і модифікуємо шляхи до зображення (?P<url>.+?) так, що вони бралися саме з каталога static і підкаталога images_html, тобто прописуємо  + base +.
            text = re.sub(r"(?P<tag><img\s+[^>]*src=)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)>",  # Таким чином на модифікований текст буде посилатися змінна text
                          "\\g<tag>" + base + "/\\g<url>>",
                          text)


            tm = math.floor(time.time())  # отримуємо поточний час додавання статті, округлений до секунд
            self.__cur.execute("INSERT INTO posts VALUES(NULL, ?, ?, ?, ?)", (title, text, url, tm))  # добавляємо записи в таблицю posts і беремо дані з кортежу (title, text, url, tm)
            self.__db.commit()  # зберігає в базу даних цей запис "INSERT INTO posts VALUES(NULL, ?, ?, ?, ?)"
        except sqlite3.Error as e:  # якщо при додаванні виникла помилка, то
            print("Помилка додавання статті в БД "+str(e))  # виводимо повідомлення про помилку і повертаємо False
            return False

        return True  # якщо стаття додана успішно, то повертаємо True


    def getPost(self, alias):  # метод getPost буде приймати параметр alias
        try:
            self.__cur.execute(f"SELECT title, text FROM posts WHERE url LIKE '{alias}' LIMIT 1")  # і якраз по параметру alias ми будем вибирати статтю з нашої бази даних з таблиці posts. Вибираємо титул, текст з таблиці posts, url статі має співпадати з alias, який ми передаємо в метод getPost
            res = self.__cur.fetchone()  # метод fetchone - беремо лише 1 запис, він там і є один
            if res:  # якщо запис був прочитаний успішно, то
                return res  # повертаємо запис в вигляді кортежа
        except sqlite3.Error as e:
            print("Помилка отримання статті з БД  "+str(e))  # а інакше формуємо помилку і повертаємо фолс

        return (False, False)


    def getPostsAnonce(self):
        try:
            self.__cur.execute(f"SELECT id, title, text, url FROM posts ORDER BY time DESC")  # вибирає всі записи з таблиці posts, відсортовані від найсвіжішої і вниз
            res = self.__cur.fetchall()  # за допомогою методу fetchall() отримуємо всі записи з таблиці posts у вигляді словника
            if res: return res  # якщо записи були отримані успішно, то ми їх повертаємо
        except sqlite3.Error as e:   # якщо ні, то ми формуємо помилку і повертаємо пустий список
            print("Помилка отримання статті з БД "+str(e))

        return []


    def addUser(self, name, email, hpsw): # передаємо всі необхідні параметри name, email, hpsw
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM users WHERE email LIKE '{email}'")  # якщо користувач з таким email вже існує в таблиці users, то
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Користувач з таким email вже існує")
                return False  # то ми повертаємо False і кажемо, що Користувач з таким email вже існує (ми не добавляємо користувача з однаковим емейлом, емейл має бути унікальним)

            tm = math.floor(time.time())  # формуємо час коли відбувається реєстрація користувача
            self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, NULL, ?)", (name, email, hpsw, tm))   # NULL означає, що ми пропускаємо 1 поле при додаванні даних в таблицю users. Перший NULL - це поле id, яке автогенерується. Другий NULL - це поле avatar і тут буде зберігатися аватар користувача.
            self.__db.commit()  # викликаємо commit, щоб зберегти всі зміни в БД
        except sqlite3.Error as e:  # якщо виникли помилки повязані з БД, то
            print("Помилка додавання користувача в БД "+str(e))
            return False  # то ми повертаємо False і кажемо, що помилка додавання користувача в БД

        return True  # якщо помилок не виникло, то повертаємо True


    def getUser(self, user_id):  #передаємо параметр user_id
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")  # вибираємо з БД всі поля з таблиці users з таким id - {user_id}.
            res = self.__cur.fetchone()  # якщо зчитування даних пройшло успішно, то ми повертаємо колекцію res
            if not res:
                print("Користувач не знайдений")
                return False  # якщо зчитування даних невдале, то ми повертаємо False і повідомлення про те, що користуава не знайдено

            return res  # якщо зчитування даних пройшло успішно, то ми повертаємо колекцію res
        except sqlite3.Error as e: # якщо виникли помилки повязані з БД, то
            print("Помилка отримання даних з БД "+str(e))  # то ми повертаємо False і кажемо, що помилка отримання даних з БД

        return False

    def getUserByEmail(self, email):  #в функцію передаємо параметр email
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")  # вибираємо з БД всі поля з таблиці users в яких вказано такий email - {email} (каке поле має бути одне).
            res = self.__cur.fetchone() # якщо запит пройшов успішно, то ми повертаємо колекцію res
            if not res:
                print("Користувача не знайдено") # якщо зчитування даних невдале, то ми повертаємо False і повідомлення про те, що користуавача не знайдено
                return False

            return res
        except sqlite3.Error as e:  #Якщо виникла помилка повязана з БД, то
            print("Помилка отримання даних з БД "+str(e))  #ми повертаємо False і кажемо, що помилка отримання даних з БД

        return False


    def updateUserAvatar(self, avatar, user_id):  #даний метод змінює аватар в БД
        if not avatar:  # якщо параметр avatar немає даних, то повертаємо False і робота функції завершується
            return False

        try:  # a інакше ми поміщаємо аватар в базу даних
            binary = sqlite3.Binary(avatar)  # перетворюємо дані в бінарний об’єкт і бінарний обєкт поміщаємо в базу даних таким чином:
            self.__cur.execute(f"UPDATE users SET avatar = ? WHERE id = ?", (binary, user_id))  # виконуємо sql запит UPDATE поле аватар міняємо на поле бінарі
            self.__db.commit()  # якщо успішно, то зберігаємо значення в базі даних і повертаємо тру
        except sqlite3.Error as e: # якщо помилка, то виводимо повідомлення та повертаємо фолс
            print("Помилка оновлення аватара в БД: "+str(e))
            return False
        return True