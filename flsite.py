import sqlite3
import os
from flask import Flask, render_template, request, g, flash, abort, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash  # імпортуємо функції для кодування бази даних і співставлення хеша з паролем
from FDataBase import FDataBase
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
from forms import LoginForm # імпортували клас для форми авторизації

# конфигурация
DATABASE = '/tmp/flsite.db'  # шлях до бази даних
DEBUG = True  # щоб було видно помилки
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'  # ввів секретний ключ
MAX_CONTENT_LENGTH = 1024 * 1024   # (1 Мб) константа дозволяє вказати максимальний об’єм файла (в байтах), який можна загрузити на сервер.

app = Flask(__name__)
app.config.from_object(__name__)  # загрузив конфігурацію з поточної програми, тобто на основі змінних DATABASE, DEBUG, SECRET_KEY буде сформована початкова конфігурація
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))  # вказуємо шлях до бази даних, вона буде знаходитися в робочому каталозі нашої програми


login_manager = LoginManager(app)  # створюємо екземпляр класу LoginManager і звязуємо його з нашою програмою (app)
login_manager.login_view = 'login'  #  після того як ми створили екземпляр класу LoginManager, ми можемо атрибуту login_view присвоїти функцію 'login', яка викликатиме форму авторизації. Тобто, якщо користувач не авторизований, і він хоче зайти в ту частину сайту, яка вимагає авторизації, то замість помилки 401(неавторизований) спрацює функція логін і викличе шаблон авторизації.
# в шаблоні авторизаці буде виведено флеш повідомлення англійською мовою, щоб його змінити треба передати новий текст атрибуту login_message екземпляра класу LoginManager
login_manager.login_message = "Потрібна авторизація для доступу до закритих сторінок"
login_manager.login_message_category = "success"  # категорія флеш повідомлення

@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, dbase)  # декоратор буде загружати, формувати екземпляр класу UserLogin при кожному запиті від клієнта


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
@login_required  #обмежуємо доступ до статей. Тепер тільки для авторизованих користувачів.
def showPost(alias):   # функція showPost буде приймати параметр alias, який якраз відображається в URL /post/alias - унікальна адреса статті на сайті.
    title, post = dbase.getPost(alias)  # за допомогою методу getPost з бази даних ми будемо брати статтю по унікальному url - alias.
    if not title:   # якщо з якоїсь причини стаття не була отримана з бази даних, то
        abort(404)  # буде виведена помилка 404

    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)  # а якщо все пройде добре, то буде відображено шаблон post.html, тобто стаття з заголовком title=title і вмістом post=post


@app.route("/login", methods=["POST", "GET"])  # метод прийматиме дані по POST і GET запитах.
def login():
    # робимо так, щоб для авторизованих користувачів форма авторизації більше не відображалася, тобто при переході на форму авторизації їх відправляло на форму їхнього профілю
    if current_user.is_authenticated:  # через глобальну змінну current_user ми перевіряємо чи користувач авторизований
        return redirect(url_for('profile'))  # і якщо він авторизований, то ми відправимо його на сторінку його профілю

    form = LoginForm()  # Створюємо екземпляр класу LoginForm
    if form.validate_on_submit(): # перевіряємо чи були відправлені дані POST запитом(це еквівалентно if request.method == "POST"), крім того цей метод перевіряє коректність введених даних. Тобто, якщо дані були введені коректно і відправлені POST запитом, то переходимо далі
        user = dbase.getUserByEmail(form.email.data)  # ми звертаємося до бази даних і беремо інформацію про користувача по емейлу (оскільки при реєстрації користувач вводить свій емейл і відповідно іемейл є унікальним) # (form.email.data) через змінну form звертаємося до класу LoginForm, в ньому до змінної email і властивість data, щоб отримати дані з цього поля.
        if user and check_password_hash(user['psw'], form.psw.data):  # якщо дані були отримані і пароль було введено вірно, то
            userlogin = UserLogin().create(user)  # створюємо екземпляр класу UserLogin, передаємо йому user(всю ту інформацію, що прочитали з бази даних)
            # коли користувач авторизується, то ми повинні отримати інформацію про кнопку "Запам’ятати мене". Інформація має бути представлена в 2 видах True або False.
            rm = form.remember.data  # в login.html ми дали імя кнопці remainme, тому саме по цьому імені ми її беремо і якщо користувач поставив галочку запамятати його, то ми отримаємо значення True, а інакше False
            login_user(userlogin, remember=rm)  # та авторизуємо користувача за допомогою функції login_user# доповнюю: щоб модуль flask_login запамятав користувача, то ми вводимо параметр remember і присвоюємо йому значення rm. Тобто, якщо True, то користувач буде запамятовуватися, а якщо False, то ні.
            # Якщо ми не авторизовані і намагаємося відкрити статтю, яка вимагає авторизації користувача, то нас перенаправляє на форму авторизації. А після авторизації, ми потрапимо на сторінку профіля користувача.
            # Через параметр next зробив так, щоб після авторизації користувач був перенаправлений на ту сторінку, яку він намагався відвідати неавторизованим.
            return redirect(request.args.get("next") or url_for("profile"))  # після чого робимо перенаправлення на головну сторінку сайту #вніс зміни, тепер буде перенаправляти на сторінку /profile# вніс зміни: ми робимо redirect і якщо параметр next в нашому запиті існує, то request.args.get("next") - ми переходимо по url, який вказаний в адресній строці після next, а інакше перейдемо в профіль url_for("profile")

        flash("Пара логін/пароль є невірною", "error")  # якщо під час отримання даних щось пішло не так, то ми повідомляємо користувача через флеш повідомлення

    return render_template("login.html", menu=dbase.getMenu(), title="Авторизація", form=form)  # в шаблон login.html передаємо посилання на екземпляр класу LoginForm, тобто через іменований параметр form=form ми зможемо в шаблоні login.html звернутися до класу LoginForm і виконати певні дії

    #if request.method == "POST":  # якщо прийшов POST запит, то
    #    user = dbase.getUserByEmail(request.form['email'])  # ми звертаємося до бази даних і беремо інформацію про користувача по емейлу (оскільки при реєстрації користувач вводить свій емейл і відповідно іемейл є унікальним)
    #    if user and check_password_hash(user['psw'], request.form['psw']):  # якщо дані були отримані і пароль було введено вірно, то
    #        userlogin = UserLogin().create(user)  # створюємо екземпляр класу UserLogin, передаємо йому user(всю ту інформацію, що прочитали з бази даних)
    #        # коли користувач авторизується, то ми повинні отримати інформацію про кнопку "Запам’ятати мене". Інформація має бути представлена в 2 видах True або False.
    #        rm = True if request.form.get('remainme') else False  # в login.html ми дали імя кнопці remainme, тому саме по цьому імені ми її беремо і якщо користувач поставив галочку запамятати його, то ми отримаємо значення True, а інакше False
    #        login_user(userlogin, remember=rm)  # та авторизуємо користувача за допомогою функції login_user# доповнюю: щоб модуль flask_login запамятав користувача, то ми вводимо параметр remember і присвоюємо йому значення rm. Тобто, якщо True, то користувач буде запамятовуватися, а якщо False, то ні.
    #        # Якщо ми не авторизовані і намагаємося відкрити статтю, яка вимагає авторизації користувача, то нас перенаправляє на форму авторизації. А після авторизації, ми потрапимо на сторінку профіля користувача.
    #        # Через параметр next зробив так, щоб після авторизації користувач був перенаправлений на ту сторінку, яку він намагався відвідати неавторизованим.
    #        return redirect(request.args.get("next") or url_for("profile"))  # після чого робимо перенаправлення на головну сторінку сайту #вніс зміни, тепер буде перенаправляти на сторінку /profile# вніс зміни: ми робимо redirect і якщо параметр next в нашому запиті існує, то request.args.get("next") - ми переходимо по url, який вказаний в адресній строці після next, а інакше перейдемо в профіль url_for("profile")
#
     #   flash("Пара логін/пароль є неверною", "error")  # якщо під час отримання даних щось пішло не так, то ми повідомляємо користувача через флеш повідомлення
#
    #return render_template("login.html", menu=dbase.getMenu(), title="Авторизація")  # і знову відображаємо сторінку авторизації


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()  # Створюємо екземпляр класу LoginForm
    if form.validate_on_submit(): # перевіряємо чи були відправлені дані POST запитом(це еквівалентно if request.method == "POST"), крім того цей метод перевіряє коректність введених даних. Тобто, якщо дані були введені коректно і відправлені POST запитом, то переходимо далі
        hash = generate_password_hash(request.form['psw'])  # генеруємо хеш паролю
        res = dbase.addUser(form.name.data, form.email.data, hash)  # добавляємо користувача
        if res:  # якщо користувач доданий успішно, то
            flash("Ви успішно зареєстровані", "success")  # флеш повідомлення про те, що зареєстрований
            return redirect(url_for('login')) # і редірект на форму логін
        else:
            flash("Помилка при додаванні в базу даних", "error")

    return render_template("register.html", menu=dbase.getMenu(), title="Реєстрація", form=form)  #параметр form і посилання (form=form) на створений клас RegisterForm

    #if request.method == "POST":
        #if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
            #and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            #hash = generate_password_hash(request.form['psw'])
            #res = dbase.addUser(request.form['name'], request.form['email'], hash)
            #if res:
                #flash("Ви успішно зареєстровані", "success")
                #return redirect(url_for('login'))
            #else:
                #flash("При додаванні в базу даних виникла помилка", "error")
        #else:
            #flash("Невірно заповнені поля", "error")
#
    #return render_template("register.html", menu=dbase.getMenu(), title="Реєстрація")


@app.route('/logout')  # декоратор route, щоб сказати flask який url буде запускати функцію
@login_required  # сторінка буде доступна тільки для авторизованих користувачів
def logout():  # функція logout буде викликати спеціальну функцію logout_user(), яка реалізована в модулі flask_login
    logout_user()  # коли дана функція спрацьовує, то вся сесійна інформація по поточному користувачеві буде очищена, і користувач стане неавторизованим.
    flash("Ви вийшли з акаунта", "success")
    return redirect(url_for('login'))  # після того як ми вийшли з профіля, нас має повернути на сторінку login і ми отримаюємо флеш повідомлення про те, що ми вийшли з акаунта


@app.route('/profile')  # декоратор route, щоб сказати flask який url буде запускати функцію
@login_required  # сторінка буде доступна тільки для авторизованих користувачів
def profile():
    return render_template("profile.html", menu=dbase.getMenu(), title="Профиль")
    # return f"""<p><a href="{url_for('logout')}">Вийти з профілю</a>
    #<p>user info:{current_user.get_id()}"""  # буде виводити пусту сторінку, на якій буде посилання "Вийти з профіля", а також фраза user info: з поточним id користувача. Через глобальну змінну current_user можна звертатися до методів класу UserLogin(), зокрема до get_id, щоб отримати id з таблиці в БД users # дана форма виводу була тимчасовою, тому видаляю її і підключаю шаблон profile.html

@app.route('/userava') # ввів функцію userava для опрацювання логотипу користувача
@login_required
def userava():  # ТОБТО ПО ЦЬОМУ АДРЕСУ /userava БУДЕ ПОВЕРТАТИСЯ ЗОБРАЖЕННЯ В ФОРМАТІ PNG
    img = current_user.getAvatar(app)  # берем аватар нашого поточного користувача
    if not img:  # якщо при отриманні аватарки виникла помилка, тобто вона не була загружена, то повертаємо порожню строку
        return ""

    h = make_response(img)  # а інакше створюється об’єкт запиту
    h.headers['Content-Type'] = 'image/png'  # і в обєкті запиту параметру Content-Type встановлюється таке значення 'image/png', тому що ми припускаємо, що всі зображення, які ми будемо загружати будуть мати розширення png
    return h  # повертаємо відповідь сервера браузеру


# Ввів декоратор upload, який буде загружати нову аватарку в профіль користувача.
@app.route('/upload', methods=["POST", "GET"])  # юрл, яка буде запускати функцію upload - '/upload'. Буде отримувати дані по методу "POST", "GET"
@login_required # доступний тільки для авторизованих
def upload():
    if request.method == 'POST':  # якщо дані прийшли через метод пост, то
        file = request.files['file']  # береться поле file з обєкта request, яке асоційоване з загруженим на сервер файлом, тобто тим файлом, який був вибраний в профілі користувача
        if file and current_user.verifyExt(file.filename):  # якщо файл був успішно загружений і якщо в нього розширення png
            try:
                img = file.read()  # далі ми намагаємося прочитати файл
                res = dbase.updateUserAvatar(img, current_user.get_id())   # якщо нам вдається прочитати цей файл, то ми викликаємо метод updateUserAvatar, де відбувається зміна аватару користувача в базі даних
                if not res:
                    flash("Помилка оновлення аватара", "error")  # якщо виникли помилки, то формується флеш повідомлення
                flash("Аватар оновлено", "success")  # якщо все добре, то формуємо повідомлення
            except FileNotFoundError as e:
                flash("Помилка читання файлу", "error")  # тут помилки повязані з читанням файлу та його оновленням
        else:
            flash("Помилка оновлення аватара", "error")

    return redirect(url_for('profile'))


if __name__ == "__main__":
    app.run(debug=True)