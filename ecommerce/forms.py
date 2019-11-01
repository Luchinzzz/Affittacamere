from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField, StringField, TextAreaField, DateField, FileField, MultipleFileField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo

persons_choices = list(range(1,13)) # From 1 to 12 people choice
for i in range(0, len(persons_choices)):
    persons_choices[i] = (str(persons_choices[i]), str(persons_choices[i]))


class SearchForm(FlaskForm):
    address = StringField('Posizione')
    start_date = DateField('Inizio Soggiorno', format='%d/%m/%Y', validators=[DataRequired()])
    end_date = DateField('Fine Soggiorno', format='%d/%m/%Y', validators=[DataRequired()])
    persons = SelectField('Numero di Persone', choices=persons_choices, validators=[DataRequired()])
    submit = SubmitField('Cerca')

class RegistrationForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(min=2, max=30)])
    surname = StringField('Cognome', validators=[DataRequired(), Length(min=2, max=30)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Length(min=2,max=40), Email()])
    privilege = SelectField('Tipologia', choices=[('True', 'Proprietario'), ('False', 'Affittuario')], validators=[DataRequired()])
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
    available_from = DateField('Inizio disponibilità', format='%d/%m/%Y')
    available_to = DateField('Fine disponibilità', format='%d/%m/%Y')
    price = DecimalField('Prezzo', validators=[DataRequired()])
    max_persons = SelectField('Numero massimo di Persone', choices=persons_choices, validators=[DataRequired()])
    pictures = MultipleFileField('Immagini della stanza')
    submit = SubmitField('Aggiungi stanza')