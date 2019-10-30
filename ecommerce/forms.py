from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField, StringField, TextAreaField, DateField, FileField, MultipleFileField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(min=2, max=30)])
    surname = StringField('Cognome', validators=[DataRequired(), Length(min=2, max=30)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Length(min=2,max=40), Email()])
    birth_date = DateField('Data di nascita', format='%d/%m/%Y')
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5,max=20)])
    confirm_password = PasswordField('Conferma Password', validators=[DataRequired(), EqualTo('password')])
    register = SubmitField('Registrati')

class LoginForm(FlaskForm):
    username_email = StringField('Username/Email', validators=[DataRequired(), Length(min=2,max=40)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5,max=20)])
    login = SubmitField('Accedi')

class ProfilePictureForm(FlaskForm):
    image = FileField()

class AddRoomForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(min=5, max=20)])
    description = TextAreaField('Descrizione opzionale')
    address = StringField('Posizione', validators=[DataRequired()])
    price = DecimalField('Prezzo', validators=[DataRequired()])

    choices = list(range(1,11)) # From 1 to 10 people choice
    for i in range(0, len(choices)):
        choices[i] = (str(choices[i]), str(choices[i]))
    max_persons = SelectField('Numero massimo di Persone', choices=choices, validators=[DataRequired()])

    pictures = MultipleFileField('Immagini della stanza')
    submit = SubmitField('Aggiungi stanza')