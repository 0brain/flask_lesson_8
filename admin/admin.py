from flask import Blueprint, request, redirect, url_for, render_template, flash, session

# ввів admin - екземпляр класу Blueprint, та перечислив його параметри: 'admin', __name__, template_folder, static_folder
admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')
#'admin' - ім'я Blueprint, яке буде суфіксом до всіх імен методів, даного модуля
#__name__ - ім'я виконуваного модуля, щодо якого буде шукатися папка admin і відповідні підкаталоги
#template_folder - підкаталог для шаблонів
#static_folder - підкаталог для статичних файлів


def login_admin():
    session['admin_logged'] = 1  # в сесії створюємо і зберігаємо запис 'admin_logged' зі значенням 1. І в подальшому будемо вважати, якщо запис в сесії існує, то користувач зайшов в панель адміністратора.


def isLogged():  # Функція перевіряє авторизований адміністратор чи ні.
    return True if session.get('admin_logged') else False  # Повертає True, якщо запис 'admin_logged' існує в сесії і False, якщо не існує.


def logout_admin():  # Функція за допомогою якої ми будемо виходити з панелі адміністратора.
    session.pop('admin_logged', None)  # Видаляє з сесії запис про авторизацію користувача як адміністратора.


menu = [{'url': '.index', 'title': 'Панель'},
        {'url': '.logout', 'title': 'Вийти'}]


db = None # якщо з’єднання з БД не було встановлено то змінна db приймає значення None
@admin.before_request
def before_request(): # встановлення зєднання з БД перед виконанням запиту
    global db  # у функції before_request звертаємося до глобальної змінної g контексту програми і беремо звідти значення 'link_db', яке пов'язане з посиланням на з'єднання з БД.
    db = g.get('link_db')


@admin.teardown_request  # закриває зєднання з БД
def teardown_request(request): # тут коли ми завершуємо виконання запиту, db знову приймає значення None
    global db
    db = None
    return request


@admin.route('/')  # викликаємо route для admin, а не app, як це робили в основному додатку. Тим самим вказуємо, що коренева (головна) сторінка - це сторінка Blueprint, а не програми app.
def index():
    if not isLogged(): # Змінив функцію index додав умову: Якщо користувач не залогінився, то перенаправляю його на форму авторизації адміністратора.
        return redirect(url_for('.login'))
    # далі відображаємо шаблон сторінки адміністратора, в ньому буде відображено меню і назва Панель адміністратора
    return render_template("admin/index.html", menu=menu, title="Панель адміністратора")



@admin.route('/login', methods=["POST", "GET"])
def login():
    if isLogged(): #Якщо користувач залогінився, то перенаправляю його на головну строніку панелі адміністратора.
        return redirect(url_for('.index.html'))
    if request.method == "POST": # Спочатку перевіряємо, що прийшли дані по POST-запиту
        if request.form['user'] == "admin" and request.form['psw'] == "123456": # потім, перевіряємо правильність логіна і пароля
            login_admin() # і при істинності умов, виконуємо авторизацію за допомогою функції login_admin, яку пропишемо трохи пізніше
            return redirect(url_for('.index'))  # далі, робиться перенаправлення на головну сторінку адмін-панелі. Параметр у функції url_for ( '. index'). Перед index вказана точка. Ця точка означає, що функцію index слід брати для поточного Blueprint, а не глобальну з програми.
        else: # а інакше - формується миттєве повідомлення Невірна пара логін/пароль
            flash("Невірна пара логін/пароль", "error")

    return render_template('admin/login.html', title='Панель адміністратора')  #в кінці повертає шаблон 'admin/login.html' з заголовком 'Панель адміністратора'


@admin.route('/logout', methods=["POST", "GET"])
def logout():
    if not isLogged(): # Якщо користувач не ввійшов в панель адміністратора, то переводимо його на сторінку login.
        return redirect(url_for('.login'))

    logout_admin() # А інакше, якщо користувач авторизований, то видаляємо запис з сесії і

    return redirect(url_for('.login'))  # переводимо його на сторінку login.