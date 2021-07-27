from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[Email("Некоректний email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(),
                                                Length(min=4, max=100, message="Пароль повинен бути від 4 до 100 символів")])
    remember = BooleanField("Запам’ятати", default = False)
    submit = SubmitField("Увійти")