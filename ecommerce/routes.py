from flask import render_template, redirect, url_for, abort
from flask_login import logout_user, login_required, current_user
from sqlalchemy import and_

from ecommerce import current_dir, app, db
from ecommerce.models import User, Room
from ecommerce.forms import SearchForm, RegistrationForm, LoginForm, ProfilePictureForm, AddRoomForm
from ecommerce.utils import check_login_register, truncate_descriptions, add_room_pictures_path

from werkzeug.utils import secure_filename
from os import path, makedirs, remove
import shutil


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

    # Check if we received a search form from the homepage, if not create a SearchForm object
    if not search_form:
        search_form = SearchForm()

    # Check if the search form is invalid
    if not(search_form.submit.data and search_form.validate()):
        return render_template('results.html',
            search_form=search_form,
            registration_form=registration_form,
            login_form=login_form,
            results_rooms=[]
        )

    # Form data are valids, save datas for the query
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

    # Truncate description of results rooms if necessary
    results_rooms = truncate_descriptions(results_rooms)

    # Add room pictures path to the results
    results_rooms = add_room_pictures_path(results_rooms)

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
    
    # Truncate description of results rooms if necessary
    requested_user_rooms = truncate_descriptions(requested_user_rooms)

    # Add room pictures path to the results
    requested_user_rooms = add_room_pictures_path(requested_user_rooms)

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
    
    # Add room pictures path
    requested_room = add_room_pictures_path([requested_room])[0]

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
@login_required
def logout():
    # Simply let flask-login perform the logout and redirect to the homepage
    logout_user()
    return redirect(url_for('home'))