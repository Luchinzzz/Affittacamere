from flask_wtf import FlaskForm
from wtforms import StringField, DateField, RadioField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(min=2, max=30)])
    surname = StringField('Cognome', validators=[DataRequired(), Length(min=2, max=30)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Length(min=2,max=40), Email()])
    birth_date = DateField('Data di nascita', format='%d/%m/%Y')
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5,max=20)])
    confirm_password = PasswordField('Conferma Password', validators=[DataRequired(), EqualTo('password')])

class LoginForm(FlaskForm):
    username_email = StringField('Username/Email', validators=[DataRequired(), Length(min=2,max=40)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5,max=20)])