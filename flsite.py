import sqlite3
import os
from flask import Flask, render_template, request, g
from FDataBase import FDataBase

# конфигурация
DATABASE = '/tmp/flsite.db'  # шлях до бази даних
DEBUG = True  # щоб було видно помилки
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'  # ввів секретний ключ

app = Flask(__name__)
app.config.from_object(__name__)  # загрузив конфігурацію з поточної програми, тобто на основі змінних DATABASE, DEBUG, SECRET_KEY буде сформована початкова конфігурація
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))  # вказуємо шлях до бази даних, вона буде знаходитися в робочому каталозі нашої програми


def connect_db():  # Функція для встановлення зєднання з базою даних
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():  # Функція яка буде створювати базу даних
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():  # функція буде встановлювати зєднання з бд, якщо воно не встановлено
    if not hasattr(g, 'link_db'):  # в змінну g буде записуватися будь-яка інформація про користувача. В даному випадку запишемо інформацію про встановлення з’єднання з базою даних.
        g.link_db = connect_db()  # перевіряємо чи існує в даного об’єкта g властивість link_db. Якщо існує, то зв’язок з БД вже було встановлено. І його просто треба повернути функції через ретурн.
    return g.link_db  # а якщо зв’язок не був встановлений, то викликаємо функцію connect_db(), яка встановить звя’зок з БД.


@app.teardown_appcontext
def close_db(error):  # функція буде закривати зєднання з бд, якщо воно було встановлено
    if hasattr(g, 'link_db'):  # перевіряємо чи існує в даного об’єкта g властивість link_db. Якщо існує, то зв’язок з БД вже було встановлено. І його треба закрити.
        g.link_db.close()  # ми звертаємося до встановленого з’єднання g.link_db і викликаємо метод close() щоб його закрити.


@app.route("/")
def index():
    db = get_db()  # викликаємо функцію, щоб встановити зєднання з базою даних
    dbase = FDataBase(db)  # вводимо екземпляр dbase класу FDataBase
    return render_template('index.html', menu = dbase.getMenu())  # через екземпляр dbase викликаємо метод getMenu
    #  getMenu повертає колекцію із словників, і використовуючи посилання (menu=dbase.getMenu()) на цю колекцію, в шаблоні 'index.html' формується меню нашої сторінки


if __name__ == "__main__":
    app.run(debug=True)