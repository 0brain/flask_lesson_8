from flask import Blueprint

# ввів admin - екземпляр класу Blueprint, та перечислив його параметри: 'admin', __name__, template_folder, static_folder
admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')
#'admin' - ім'я Blueprint, яке буде суфіксом до всіх імен методів, даного модуля
#__name__ - ім'я виконуваного модуля, щодо якого буде шукатися папка admin і відповідні підкаталоги
#template_folder - підкаталог для шаблонів
#static_folder - підкаталог для статичних файлів


@admin.route('/')  # викликаємо route для admin, а не app, як це робили в основному додатку. Тим самим вказуємо, що коренева (головна) сторінка - це сторінка Blueprint, а не програми app.
def index():
    return "admin"


@admin.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST": # Спочатку перевіряємо, що прийшли дані по POST-запиту
        if request.form['user'] == "admin" and request.form['psw'] == "123456": # потім, перевіряємо правильність логіна і пароля
            login_admin() # і при істинності умов, виконуємо авторизацію за допомогою функції login_admin, яку пропишемо трохи пізніше
            return redirect(url_for('.index'))  # далі, робиться перенаправлення на головну сторінку адмін-панелі
        else: # а інакше - формується миттєве повідомлення Невірна пара логін/пароль
            flash("Невірна пара логін/пароль", "error")

    return render_template('admin/login.html', title='Панель адміністратора')  #в кінці повертає шаблон 'admin/login.html' з заголовком 'Панель адміністратора'