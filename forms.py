import re

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, Email, ValidationError

from models import User


def password_check(form, field):
    msg = 'Пароль должен содержать латинские сивмолы в верхнем и нижнем регистре и цифры'
    pattern1 = re.compile('[a-z]+')
    pattern2 = re.compile('[A-Z]+')
    pattern3 = re.compile('\d+')
    if (not pattern1.search(field.data) or
            not pattern2.search(field.data) or
            not pattern3.search(field.data)):
        raise ValidationError(msg)


def email_unique_check(form, field):
    msg = 'Пользователь с указанной почтой уже существует'
    user = User.query.filter_by(mail=field.data).first()
    if user:
        raise ValidationError(msg)


class LoginForm(FlaskForm):
    mail = StringField('Электропочта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])


class RegistrationForm(FlaskForm):
    mail = StringField('Электропочта',
                       validators=[DataRequired(),
                                   Email(message='Это не похоже на почту, попробуйте еще раз!'),
                                   email_unique_check]
                       )
    password = PasswordField(
        'Пароль',
        validators=[
            DataRequired(),
            Length(min=5, message='Пароль должен быть не менее 5 символов'),
            password_check])


class OrderForm(FlaskForm):
    name = StringField('Ваше имя', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    mail = StringField('Электропочта',
                       validators=[DataRequired(),
                                   Email(message='Это не похоже на почту, попробуйте еще раз!')]
                       )
    phone = StringField('Телефон',
                        validators=[
                            DataRequired(),
                            Length(min=5, max=11,
                                   message='Телефон должен быть не менее 5 и не более 11 цифр')])
