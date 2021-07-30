from flask_wtf import FlaskForm  # FlaskForm - базовий клас, який ми будемо розширювати за допомогою дочірнього класу LoginForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):  # LoginForm - клас для форми авторизації
    email = StringField("Email: ", validators=[Email("Некоректний email")])  # StringField - клас для роботи з полем введення # змінна email буде зсилатися на екземпляр класу StringField, назва поля "Email: ", параметр validators, який буде зсилатися на список валідаторів необхідних для перевірки коректності введених даних в полі емейл
    psw = PasswordField("Пароль: ", validators=[DataRequired(),
                                                Length(min=4, max=100, message="Пароль повинен бути від 4 до 100 символів")])  # PasswordField клас для роботи з полем введення паролю # DataRequired() - вимагає, щоб в даному полі був хоча би 1 символ
    remember = BooleanField("Запам’ятати", default = False)  # BooleanField - клас для чекбокс полів # за замовчуванням False, тобто не встановлена галочка запамятати
    submit = SubmitField("Увійти")  # SubmitField - клас для кнопки submit


class RegisterForm(FlaskForm):
    name = StringField("Имя: ", validators=[Length(min=4, max=100, message="Ім’я повинно бути від 4 до 100 символів")])
    email = StringField("Email: ", validators=[Email("Некоректний пароль")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(),
                                                Length(min=4, max=100, message="Пароль повинен бути від 4 до 100 символів")])

    psw2 = PasswordField("Повторення паролю: ", validators=[DataRequired(), EqualTo('psw', message="Паролі не співпадають")]) # валідатор EqualTo перевіряє чи відповідає вміст поля psw2 вмісту поля psw. Якщо psw==psw2 то валідатор поверне True.
    submit = SubmitField("Реєстрація")