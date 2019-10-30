from flask import render_template, redirect, url_for, abort
from ecommerce import current_dir, app, db, bcrypt
from ecommerce.models import User, Room
from ecommerce.forms import RegistrationForm, LoginForm, ProfilePictureForm, AddRoomForm
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from os import path, makedirs, remove


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


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    registration_form, login_form = check_login_register()
    return render_template('index.html', registration_form=registration_form, login_form=login_form)


@app.route("/results", methods=['GET', 'POST'])
def results():
    registration_form, login_form = check_login_register()
    return render_template('results.html', registration_form=registration_form, login_form=login_form)


@app.route("/profile/<requested_user_id>", methods=['GET', 'POST'])
@login_required
def profile(requested_user_id):
    # Get requested user
    requested_user = User.query.filter_by(id=requested_user_id).first()
    if not requested_user:
        return abort(404)
    
    # Login and Register Forms (useless, so let's create two empty ones and not call check_login_register)
    login_form = LoginForm()
    registration_form = RegistrationForm()
    # ProfilePicture Change Form
    profilepicture_form = ProfilePictureForm()
    # AddRoom Form
    addroom_form = AddRoomForm()

    # New Profile Picture?
    if profilepicture_form.image.data:
        if profilepicture_form.validate():
            # Try to remove old picture image
            if current_user.picture != '/static/img/users/default/profile.png':
                try:
                    remove( current_dir + current_user.picture )
                except OSError:
                    pass
            # Save new image
            f = profilepicture_form.image.data
            filename = secure_filename(
                "%s.%s" % (str(current_user.id), f.filename.split('.')[-1])
            )
            path_img = path.join(current_dir, 'static', 'img', 'users', filename)
            print(path_img)
            f.save(path_img)
            # Update DB
            current_user.picture = '/static/img/users/' + filename
            db.session.commit()
        
    # New Room?
    if addroom_form.submit.data:
        if addroom_form.validate():
            # Create new room entry
            room = Room(
                name=addroom_form.name.data,
                description=addroom_form.description.data,
                address=addroom_form.address.data,
                price=addroom_form.price.data,
                max_persons=addroom_form.max_persons.data,
                owner_id=requested_user_id
            )
            db.session.add(room)
            db.session.commit()
            makedirs(path.join('ecommerce', 'static', 'img', 'rooms', str(room.id)))
            # Save picture in room directory
            for picture in addroom_form.pictures.data:
                filename = secure_filename(picture.filename)
                if filename != "":
                    path_img = path.join(current_dir, 'static', 'img', 'rooms', str(room.id), filename)
                    picture.save(path_img)

    # Get Current User Rooms
    requested_user_rooms = Room.query.filter_by(owner_id=requested_user_id).all()

    return render_template('profile.html',
        login_form=login_form,
        registration_form=registration_form,
        profilepicture_form=profilepicture_form,
        addroom_form=addroom_form,
        requested_user=requested_user,
        requested_user_rooms=requested_user_rooms
    )


@app.route("/room/<requested_room_id>", methods=['GET', 'POST'])
def room(requested_room_id):
    requested_room = Room.query.filter_by(id=requested_room_id).first()
    if not requested_room:
        return abort(404)

    room_owner = User.query.filter_by(id=requested_room.owner_id).first()

    registration_form, login_form = check_login_register()
    return render_template('room.html',
        registration_form=registration_form,
        login_form=login_form,
        requested_room=requested_room,
        room_owner=room_owner
    )


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))