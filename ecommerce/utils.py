from ecommerce.forms import SearchForm, RegistrationForm, LoginForm, ProfilePictureForm, AddRoomForm
from ecommerce.models import User
from ecommerce import db, bcrypt
from flask_login import login_user

def check_login_register():
    """
    General function to check if a login or registration was performed,
    since they could be performed in every page due to navbar
    """
    login_form = LoginForm()
    registration_form = RegistrationForm()

    # Registration performed?
    if registration_form.register.data:
        errors = not registration_form.validate()
        # If username already exists
        if User.query.filter_by(username=registration_form.username.data).first():
            errors = True
            registration_form.username.errors = ['Questo username è già stato preso']
        if User.query.filter_by(email=registration_form.email.data).first():
            errors = True
            registration_form.email.errors = ['Questa email è già stata presa']
        
        if not errors:
            # Registration compiled successfully
            user = User(
                name=registration_form.name.data,
                surname=registration_form.surname.data,
                username=registration_form.username.data,
                email=registration_form.email.data,
                birth_date=registration_form.birth_date.data,
                password=bcrypt.generate_password_hash(registration_form.password.data).decode('utf-8')
            )
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)

    # Login performed?
    if login_form.login.data and login_form.validate():
        errors = False
        # Username given?
        user = User.query.filter_by(username=login_form.username_email.data).first()
        if not user:
            # Email given?
            user = User.query.filter_by(email=login_form.username_email.data).first()
        if not user:
            # No match in DB
            errors = True
            login_form.username_email.errors = ['Username o email non esistenti']
        if not errors:
            # Check password
            if bcrypt.check_password_hash(user.password, login_form.password.data):
                login_user(user, remember=True)
            else:
                errors = True
                login_form.password.errors = ['Password errata']

    return registration_form, login_form

def truncate_descriptions(requested_user_rooms):
    # Cut descriptions if too long
    for i in range(0, len(requested_user_rooms)):
        if len(requested_user_rooms[i].description) >= 85:
            requested_user_rooms[i].description = requested_user_rooms[i].description[0:85] + "..."

    return requested_user_rooms