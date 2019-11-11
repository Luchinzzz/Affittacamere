from flask_login import login_user
from ecommerce import current_dir, listdir
from ecommerce.forms import SearchForm, RegistrationForm, LoginForm, ProfilePictureForm, AddRoomForm
from ecommerce.models import User
from ecommerce import bcrypt
from os import path
import requests

def check_login_register():
    """
    General function to check if a login or registration was performed,
    since they could be performed in every page since the forms are in the navbar
    """
    login_form = LoginForm()
    registration_form = RegistrationForm()

    # Registration performed?
    if registration_form.register.data and registration_form.validate():
        # Attempt a registration
        registration_res = requests.post('http://localhost:5000/api/profile/register',
            json={
                'name': registration_form.name.data,
                'surname': registration_form.surname.data,
                'username': registration_form.username.data,
                'email': registration_form.email.data,
                'birth_date': str(registration_form.birth_date.data),
                'privilege': True if registration_form.privilege.data == 'True' else False,
                'password': registration_form.password.data
            }
        )

        # Good news, we have a new user!
        if registration_res.ok:
            user = User.query.filter_by(id=registration_res.json()['user_id']).first()
            login_user(user, remember=True)
        else:
            registration_res = registration_res.json()
            if 'email' in registration_res:
                registration_form.email.errors = [registration_res['email']]
            if 'username' in registration_res:
                registration_form.username.errors = [registration_res['username']]

    # Login performed?
    if login_form.login.data and login_form.validate():
        # Attempt a login
        login_res = requests.post('http://localhost:5000/api/profile/login',
            json={
                'username_email': login_form.username_email.data,
                'password': login_form.password.data
            }
        )

        # Logged in?
        if login_res.ok:
            user = User.query.filter_by(id=login_res.json()['user_id']).first()
            login_user(user, remember=True)
        else:
            login_res = login_res.json()
            if 'username_email' in login_res:
                login_form.username_email.errors = [login_res['username_email']]
            if 'password' in login_res:
                login_form.password.errors = [login_res['password']]

    return registration_form, login_form

def truncate_descriptions(requested_user_rooms):
    """
    Cut descriptions if too long
    """
    for i in range(0, len(requested_user_rooms)):
        if len(requested_user_rooms[i]['description']) >= 85:
            requested_user_rooms[i]['description'] = requested_user_rooms[i]['description'][0:85] + "..."

    return requested_user_rooms

def add_room_pictures_path(rooms):
    """
    Add pictures path to the rooms objects
    """
    for i in range(0, len(rooms)):
        rooms_dir = path.join(current_dir, 'static', 'img', 'rooms', str(rooms[i]['id']))
        rooms[i]['pictures'] = []
        files = listdir(rooms_dir)
        if not files:
            rooms[i]['pictures'] = ['/static/img/room_placeholder.jpg']
            continue
        for image in files:
            rooms[i]['pictures'].append( f"/static/img/rooms/{rooms[i]['id']}/{image}" )

    return rooms

def add_prenotation_picture_path(prenotations):
    """
    Add first picture path to the prenotations objects
    """
    for i in range(0, len(prenotations)):
        rooms_dir = path.join(current_dir, 'static', 'img', 'rooms', str(prenotations[i]['room_id']))
        prenotations[i]['picture'] = '/static/img/room_placeholder.jpg'
        for image in listdir(rooms_dir):
            prenotations[i]['picture'] = f"/static/img/rooms/{prenotations[i]['room_id']}/{image}"
            break

    return prenotations