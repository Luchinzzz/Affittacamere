from flask import render_template, redirect, url_for, abort
from ecommerce import current_dir, app, db, bcrypt
from sqlalchemy import and_
from ecommerce.models import User, Room
from ecommerce.forms import SearchForm, RegistrationForm, LoginForm, ProfilePictureForm, AddRoomForm
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from os import path, makedirs, remove
import shutil


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
    # Check if user has performed a login or registration
    registration_form, login_form = check_login_register()

    # Prepare search form
    search_form = SearchForm()

    # Something was asked to search?
    if search_form.submit.data and search_form.validate():
        return search_results(search_form)

    return render_template('index.html',
        registration_form=registration_form,
        login_form=login_form,
        search_form=search_form,
        trasparent_navbar=True
    )


@app.route("/results", methods=['GET', 'POST'])
def search_results(search_form=None):
    # Check if user has performed a login or registration
    registration_form, login_form = check_login_register()

    if search_form:
        search_form =  SearchForm()
        if not(search_form.submit.data and search_form.validate()):
            return render_template('results.html',
                search_form=search_form,
                registration_form=registration_form,
                login_form=login_form,
                results_rooms=[]
            )

    # Get search_form datas
    address = search_form.address.data
    start_date = search_form.start_date.data
    end_date = search_form.end_date.data
    persons = search_form.persons.data

    # Get data from DB
    results_rooms = Room.query.filter(and_(
        Room.address.like(f'%{address}%'),
        Room.available_from <= start_date,
        Room.available_to >= end_date,
        Room.max_persons >= persons
    )).all()

    return render_template('results.html',
        search_form=search_form,
        registration_form=registration_form,
        login_form=login_form,
        results_rooms=results_rooms
    )


@app.route("/profile/<requested_user_id>", methods=['GET', 'POST'])
@login_required
def profile(requested_user_id):
    # Get requested user
    requested_user = User.query.filter_by(id=requested_user_id).first()
    if not requested_user:
        return abort(404)
    
    # Prepare forms
    login_form = LoginForm()
    registration_form = RegistrationForm()
    profilepicture_form = ProfilePictureForm()
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
            # Save new image as 'user_id.extension'
            f = profilepicture_form.image.data
            filename = secure_filename(
                "%s.%s" % ( str(current_user.id), path.splitext(f.filename)[-1] )
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
                available_from=addroom_form.available_from.data,
                available_to=addroom_form.available_to.data,
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

    # Get current user rooms to display them
    requested_user_rooms = Room.query.filter_by(owner_id=requested_user_id).all()
    # Cut descriptions if too long
    for i in range(0, len(requested_user_rooms)):
        if len(requested_user_rooms[i].description) >= 85:
            requested_user_rooms[i].description = requested_user_rooms[i].description[0:85] + "..."

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
    # Get requested room, if it exists
    requested_room = Room.query.filter_by(id=requested_room_id).first()
    if not requested_room:
        return abort(404)

    # Get user's owner
    room_owner = User.query.filter_by(id=requested_room.owner_id).first()

    # Check if user has performed a login or registration
    registration_form, login_form = check_login_register()
    
    return render_template('room.html',
        registration_form=registration_form,
        login_form=login_form,
        requested_room=requested_room,
        room_owner=room_owner
    )


@app.route("/room/<requested_room_id>/delete")
@login_required
def room_delete(requested_room_id):
    # Get requested room, if it exists
    requested_room = Room.query.filter_by(id=requested_room_id).first()
    if not requested_room:
        return abort(404)

    # Check if current user has the rights to remove this room
    if requested_room.owner_id != current_user.id:
        return abort(401)

    # Delete room from DB, delete room's directory with all the images inside
    db.session.delete(requested_room)
    db.session.commit()
    rooms_dir = path.join(current_dir, 'static', 'img', 'rooms')
    shutil.rmtree( path.join(rooms_dir, str(requested_room_id)) )

    # Redirect to the user's profile page who requested the remove
    return redirect(f'/profile/{current_user.id}')


@app.route("/logout")
def logout():
    # Simply let flask-login perform the logout and redirect to the homepage
    logout_user()
    return redirect(url_for('home'))