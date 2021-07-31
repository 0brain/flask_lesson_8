from flask import Blueprint

# ввів admin - екземпляр класу Blueprint, та перечислив його параметри: 'admin', __name__, template_folder, static_folder
admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')
#'admin' - ім'я Blueprint, яке буде суфіксом до всіх імен методів, даного модуля
#__name__ - ім'я виконуваного модуля, щодо якого буде шукатися папка admin і відповідні підкаталоги
#template_folder - підкаталог для шаблонів
#static_folder - підкаталог для статичних файлів


@admin.route('/')  # Для змінної admin ввів декоратор route.
def index():
    return "admin"
