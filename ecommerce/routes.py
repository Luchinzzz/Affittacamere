from flask import render_template, redirect, url_for, abort, request
from flask_login import logout_user, login_required, current_user
import requests

from ecommerce import current_dir, app, db
from ecommerce.forms import SearchForm, RegistrationForm, LoginForm, ProfilePictureForm, AddRoomForm, PrenotationForm
from ecommerce.utils import check_login_register

from werkzeug.utils import secure_filename
from os import path, makedirs, remove


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

    # Form data are valids, ask results at the backend
    search_data = {
        'address': str(search_form.address.data),
        'start_date': str(search_form.start_date.data),
        'end_date': str(search_form.end_date.data),
        'persons': str(search_form.persons.data)
    }

    results_rooms = requests.post('http://localhost:5000/api/search', json=search_data).json()

    return render_template('results.html',
        search_form=search_form,
        registration_form=registration_form,
        login_form=login_form,
        results_rooms=results_rooms
    )


@app.route("/profile/<requested_user_id>", methods=['GET', 'POST'])
@login_required
def profile(requested_user_id):
    # Convert to integer for later confrontations
    requested_user_id = int(requested_user_id)

    # Get requested user
    requested_user = requests.post('http://localhost:5000/api/profile/get',
        json={'id': requested_user_id},
        cookies=request.cookies
    ).json()
    if not requested_user:
        return abort(404)

    # Prepare forms
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
            f.save(path_img)
            # Update DB
            current_user.picture = '/static/img/users/' + filename
            db.session.commit()
        
    # New Room?
    if addroom_form.submit.data:
        if addroom_form.validate():
            # Prepare room's datas
            room_data = {
                'name': addroom_form.name.data,
                'description': addroom_form.description.data,
                'address': addroom_form.address.data,
                'available_from': str(addroom_form.available_from.data),
                'available_to': str(addroom_form.available_to.data),
                'price': addroom_form.price.data,
                'max_persons': addroom_form.max_persons.data,
                'owner_id': requested_user_id,
            }
            
            # Ask backend to create a new room for this user
            room = requests.post('http://localhost:5000/api/room/add',
                json=room_data,
                cookies=request.cookies
            ).json()

            # Save picture in room directory
            makedirs(path.join('ecommerce', 'static', 'img', 'rooms', str(room['id'])))
            for picture in addroom_form.pictures.data:
                filename = secure_filename(picture.filename)
                if filename != "":
                    path_img = path.join(current_dir, 'static', 'img', 'rooms', str(room['id']), filename)
                    picture.save(path_img)

    # Get current user rooms to display them
    requested_user_rooms = requests.post('http://localhost:5000/api/room/get_by_owner',
        json={'id': requested_user_id},
        cookies=request.cookies
    ).json()

    # Get user prenotation if current_user is the proprietary of the requested profile page
    requested_user_prenotations = requests.post('http://localhost:5000/api/prenotation/get_by_owner',
        json={'id': requested_user_id},
        cookies=request.cookies
    ).json()

    return render_template('profile.html',
        trasparent_navbar=True,
        profilepicture_form=profilepicture_form,
        addroom_form=addroom_form,
        requested_user=requested_user,
        requested_user_rooms=requested_user_rooms,
        requested_user_prenotations=requested_user_prenotations
    )


@app.route("/room/<requested_room_id>", methods=['GET', 'POST'])
def room(requested_room_id):
    # Get requested room, if it exists
    requested_room = requests.post('http://localhost:5000/api/room/get_by_id',
        json={'id': requested_room_id},
    ).json()
    if not requested_room:
        return abort(404)

    # Get user's owner
    room_owner = requests.post('http://localhost:5000/api/profile/get',
        json={'id': requested_room['owner_id']},
        cookies=request.cookies
    ).json()

    # Check if user has performed a login or registration
    registration_form, login_form = check_login_register()

    # Prepare prenotation form
    prenotation_form = PrenotationForm()
    
    # New prenotation?
    if prenotation_form.submit.data:
        if prenotation_form.validate():
            result_prenotation = requests.post('http://localhost:5000/api/prenotation/add',
                json={
                    'room_id': int(requested_room_id),
                    'buyer_id': current_user.id,
                    'start_date': str(prenotation_form.start_date.data),
                    'end_date': str(prenotation_form.end_date.data),
                    'persons': int(prenotation_form.persons.data),
                },
                cookies=request.cookies
            )
            
            # If the operation was a success, redirect to profile page
            if result_prenotation.ok:
                return redirect(f'/profile/{current_user.id}')
            
            # Managing errors
            result_prenotation = result_prenotation.json()
            # Date Error?
            if 'date' in result_prenotation:
                prenotation_form.start_date.errors = [result_prenotation['date']]
                prenotation_form.end_date.errors = [result_prenotation['date']]
            if 'persons' in result_prenotation:
                prenotation_form.persons.errors = [result_prenotation['persons']]

    # Ask for prenotations if the user has the rights to do so
    prenotations = requests.post('http://localhost:5000/api/prenotation/get_by_room_id',
        json={'id': requested_room_id},
        cookies=request.cookies
    ).json()

    return render_template('room.html',
        registration_form=registration_form,
        login_form=login_form,
        prenotation_form=prenotation_form,
        requested_room=requested_room,
        room_owner=room_owner,
        prenotations=prenotations
    )


@app.route("/room/<requested_room_id>/delete")
@login_required
def room_delete(requested_room_id):
    # Try to remove the requested room
    operation_return = requests.post('http://localhost:5000/api/room/delete',
        json={'id': requested_room_id},
        cookies=request.cookies
    )

    # Error?
    if not operation_return.ok:
        return abort(operation_return.status_code)

    # Redirect to the user's profile page who requested the remove
    return redirect(f'/profile/{current_user.id}')


@app.route("/logout")
@login_required
def logout():
    # Simply let flask-login perform the logout and redirect to the homepage
    logout_user()
    return redirect(url_for('home'))