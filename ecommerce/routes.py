from flask import render_template, redirect, url_for
from ecommerce import current_dir, app, db, bcrypt
from ecommerce.models import User, Room
from ecommerce.forms import RegistrationForm, LoginForm, ProfilePictureForm, AddRoomForm
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from os import path


def check_login_register(template_filename, registration_form, login_form):
    # No Post request?
    if not registration_form.is_submitted() and not login_form.is_submitted():
        return False
    
    # If Registration POST was submitted, is it valid?
    if registration_form.register.data:
        if registration_form.validate():
            errors = False
            # If username already exists
            if User.query.filter_by(username=registration_form.username.data).first():
                errors = True
                registration_form.username.errors = ['Questo username è già stato preso']
            if User.query.filter_by(email=registration_form.email.data).first():
                errors = True
                registration_form.email.errors = ['Questa email è già stata presa']
            if errors:
                return render_template(template_filename, login_form=login_form, registration_form=registration_form, register_error=True)
            
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
            return render_template(template_filename, login_form=login_form, registration_form=registration_form)
        # Something went wrong during registration
        return render_template(template_filename, login_form=login_form, registration_form=registration_form, register_error=True)

    # Login performed?
    if login_form.validate_on_submit():
        errors = False
        # Username given?
        user = User.query.filter_by(username=login_form.username_email.data).first()
        if not user:
            # Email given?
            user = User.query.filter_by(email=login_form.username_email.data).first()
        # No match in DB?
        if not user:
            errors = True
            login_form.username_email.errors = ['Username o email non esistenti']
        if not errors:
            # Check password
            if not bcrypt.check_password_hash(user.password, login_form.password.data):
                errors = True
                login_form.password.errors = ['Password errata']
        if errors:
            return render_template(template_filename, login_form=login_form, registration_form=registration_form, login_error=True)
        
        # Successfull Login, save cookie and refresh page
        login_user(user, remember=True)
        return render_template(template_filename, login_form=login_form, registration_form=registration_form)
    
    # Wrong Credentials for Login
    return render_template(template_filename, login_form=login_form, registration_form=registration_form, login_error=True)


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    login_form = LoginForm()
    registration_form = RegistrationForm()
    result_forms = check_login_register('index.html', registration_form, login_form)
    if result_forms:
        return result_forms
    return render_template('index.html', login_form=login_form, registration_form=registration_form)


@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    # Login and Register Forms (useless)
    login_form = LoginForm()
    registration_form = RegistrationForm()
    # AddRoom Form
    addroom_form = AddRoomForm()

    # ProfilePicture Change Form
    profilepicture_form = ProfilePictureForm()
    if profilepicture_form.is_submitted():
        f = profilepicture_form.image.data
        filename = secure_filename(
            "%s.%s" % (current_user.id, f.filename.split('.')[-1])
        )
        path_img = path.join(current_dir, 'static', 'img', 'profilepics', 'users', filename)
        f.save(path_img)
        current_user.picture = '/static/img/profilepics/users/' + filename
        db.session.commit()
        return render_template('profile.html', login_form=login_form, registration_form=registration_form, profilepicture_form=profilepicture_form, addroom_form=addroom_form)

    return render_template('profile.html', login_form=login_form, registration_form=registration_form, profilepicture_form=profilepicture_form, addroom_form=addroom_form)


@app.route("/results", methods=['GET', 'POST'])
def results():
    login_form = LoginForm()
    registration_form = RegistrationForm()
    result_forms = check_login_register('results.html', registration_form, login_form)
    if result_forms:
        return result_forms
    return render_template('results.html', login_form=login_form, registration_form=registration_form)


@app.route("/room", methods=['GET', 'POST'])
def room():
    login_form = LoginForm()
    registration_form = RegistrationForm()
    result_forms = check_login_register('room.html', registration_form, login_form)
    if result_forms:
        return result_forms
    return render_template('room.html', login_form=login_form, registration_form=registration_form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))