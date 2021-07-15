import sqlite3
import os
from flask import Flask, render_template, request, g, flash, abort
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


dbase = None
@app.before_request
def before_request():  # Перехват запиту. Дана функція буде спрацьовувати кожного разу безпосередньо перед виконанням запиту.
    # Встановлюємо зєднання з БД перед виконанням запиту.
    global dbase
    db = get_db()  # викликаємо функцію, щоб встановити зєднання з базою даних
    dbase = FDataBase(db)  # вводимо екземпляр dbase класу FDataBase, а щоб змінна dbase була загальнодоступною, то ми зробимо її глобальною --> dbase = None. І global dbase говорить, що всередині функції ми будемо звертатися саме до глобальної змінної dbase.


@app.teardown_appcontext
def close_db(error):  # функція буде закривати зєднання з бд, якщо воно було встановлено
    if hasattr(g, 'link_db'):  # перевіряємо чи існує в даного об’єкта g властивість link_db. Якщо існує, то зв’язок з БД вже було встановлено. І його треба закрити.
        g.link_db.close()  # ми звертаємося до встановленого з’єднання g.link_db і викликаємо метод close() щоб його закрити.


@app.route("/")
def index():
    return render_template('index.html', menu = dbase.getMenu(), posts=dbase.getPostsAnonce())  # через екземпляр dbase викликаємо метод getMenu # Добавив у функцію виводу головної сторінки колекцію posts, яку отримуєм з класу FDataBase методом getPostsAnonce для того, щоб відображати список статей на головній сторінці сайту.
    #  getMenu повертає колекцію із словників, і використовуючи посилання (menu=dbase.getMenu()) на цю колекцію, в шаблоні 'index.html' формується меню нашої сторінки


@app.route("/add_post", methods=["POST", "GET"]) # вводимо декоратор для /add_post адреси, по якій буде відображатися форма з додаванням статті. Буде приймати пост і ґет запити
def addPost():
    if request.method == "POST":  # якщо дані від форми прийшли
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:  # заголовок статті має бути більше 4 символів, вміст статті має бути більше 10 символів
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])  # якщо перевірка пройшла успішно, то ми додаємо пост в нашу базу даних. Через екземпляр dbase класу FDataBase(db) викликаємо метод addPost, в який передаємо заголовок та текст нашої статті
            if not res:  # якщо при додаванні статті виникла помилка,
                flash('Помилка додавання статті', category='error')  # то буде сформовано флеш повідомлення про невдале додавання і категорія в нього буде error
            else:
                flash('Стаття додана успішно', category='success')  # інакше буде сформовано флелеш повідомлення про успішне додавання статті і категорія в нього буде success
        else:
            flash('Помилка додавання статті', category='error')  # якщо заголовок статті менше 4 символів або/і вміст статті менше 10 символів, то буде сформовано флеш повідомлення про невдале додавання і категорія в нього буде error

    return render_template('add_post.html', menu=dbase.getMenu(), title="Додавання статті")  # після всіх перевірок буде сформовано шаблон add_post.html


@app.route("/post/<alias>")  # вводимо декоратор для /post/<int:id_post> адреси, по якій буде відображатися стаття. # Змінюємо <int:id_post> на псевдонім alias, тобіто на унікальний url статті
def showPost(alias):   # функція showPost буде приймати параметр alias, який якраз відображається в URL /post/alias - унікальна адреса статті на сайті.
    title, post = dbase.getPost(alias)  # за допомогою методу getPost з бази даних ми будемо брати статтю по унікальному url - alias.
    if not title:   # якщо з якоїсь причини стаття не була отримана з бази даних, то
        abort(404)  # буде виведена помилка 404

    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)  # а якщо все пройде добре, то буде відображено шаблон post.html, тобто стаття з заголовком title=title і вмістом post=post


@app.route("/login")
def login():
    return render_template("login.html", menu=dbase.getMenu(), title="Авторизация")

if __name__ == "__main__":
    app.run(debug=True)