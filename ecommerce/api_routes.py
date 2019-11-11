from flask import request
from flask_json import as_json
from sqlalchemy import and_, or_
from flask_login import login_required, login_user, current_user

from ecommerce import app, db, bcrypt, current_dir
from ecommerce.models import User, Room, Prenotation
from ecommerce.utils import truncate_descriptions, add_room_pictures_path, add_prenotation_picture_path

from os import path
from datetime import datetime
import shutil


@app.route("/api/search", methods=['POST'])
@as_json
def search():
    search_data = request.json

    # Form data are valids, save datas for the query
    address = search_data['address']
    start_date = search_data['start_date']
    end_date = search_data['end_date']
    persons = search_data['persons']

    # Get data from DB
    results_rooms = Room.query.filter(and_(
        Room.address.like(f'%{address}%'),
        Room.available_from <= start_date,
        Room.available_to >= end_date,
        Room.max_persons >= persons
    )).all()

    # Converting to dict to compatibility with JSON format
    for i in range(0, len(results_rooms)):
        results_rooms[i] = results_rooms[i].as_dict()

    # Truncate description of results rooms if necessary
    results_rooms = truncate_descriptions(results_rooms)

    # Add room pictures path to the results
    results_rooms = add_room_pictures_path(results_rooms)

    return results_rooms


@app.route("/api/profile/register", methods=['POST'])
@as_json
def profile_register():
    """
    Register a new user
    """
    new_user_data = request.json

    # Check for errors
    out = {}

    # If username already exists
    if User.query.filter_by(username=new_user_data['username']).first():
        out['username'] = 'Questo username è già stato preso'
    # If email already exists
    if User.query.filter_by(email=new_user_data['email']).first():
        out['email'] = 'Questa email è già stata presa'

    if not out:
        # Registration compiled successfully
        user = User(
            name=new_user_data['name'],
            surname=new_user_data['surname'],
            username=new_user_data['username'],
            email=new_user_data['email'],
            birth_date=datetime.strptime(new_user_data['birth_date'], "%Y-%m-%d").date(),
            privilege=new_user_data['privilege'],
            password=bcrypt.generate_password_hash(new_user_data['password']).decode('utf-8')
        )
        db.session.add(user)
        db.session.commit()

        return {'user_id': user.id}, 200
    
    return out, 400


@app.route("/api/profile/login", methods=['POST'])
@as_json
def profile_login():
    """
    Login a user
    """
    user_data = request.json
    
    # Username given?
    user = User.query.filter_by(username=user_data['username_email']).first()
    if not user:
        # Email given?
        user = User.query.filter_by(email=user_data['username_email']).first()
        if not user:
            # No match in DB
            return {'username_email': "Username o email non esistenti"}, 400

    # Check password
    if bcrypt.check_password_hash(user.password, user_data['password']):
        return {'user_id': user.id}, 200
    else:
        return {'password': "Password errata"}, 400


@app.route("/api/profile/get", methods=['POST'])
@as_json
@login_required
def profile_get():
    query_data = request.json
    return User.query.filter_by(id=query_data['id']).first().as_dict()


@app.route("/api/room/get_by_id", methods=['POST'])
@as_json
def rooom_get_by_id():
    """
    Get a room information by room_ID
    """
    room_id = request.json['id']

    # Collect rooms of wanted owner
    requested_user_room = Room.query.filter_by(id=room_id).first()

    if requested_user_room:
        # Converting to dict to compatibility with JSON format
        requested_user_room = requested_user_room.as_dict()

        # Truncate description of results rooms if necessary and add pictures' path
        requested_user_room = truncate_descriptions([requested_user_room])[0]
        requested_user_room = add_room_pictures_path([requested_user_room])[0]

        return requested_user_room
    else:
        return [], 404


@app.route("/api/room/get_by_owner", methods=['POST'])
@as_json
def rooom_get_by_owner():
    """
    Get a room information by owner_ID 
    """
    requested_user_id = request.json['id']

    # Collect rooms of wanted owner
    requested_user_rooms = Room.query.filter_by(owner_id=requested_user_id).all()

    # Converting to dict to compatibility with JSON format
    for i in range(0, len(requested_user_rooms)):
        requested_user_rooms[i] = requested_user_rooms[i].as_dict()

    # Truncate description of results rooms if necessary and add pictures' path
    requested_user_rooms = truncate_descriptions(requested_user_rooms)
    requested_user_rooms = add_room_pictures_path(requested_user_rooms)
    
    return requested_user_rooms


@app.route("/api/room/add", methods=['POST'])
@as_json
@login_required
def rooom_add():
    """
    Create new room entry
    """
    room_data = request.json
    
    # Is the user authorized to do this operation? 
    if room_data['owner_id'] == current_user.id:
        # Create Room entry
        room = Room(
            name=room_data['name'],
            description=room_data['description'],
            address=room_data['address'],
            available_from=datetime.strptime(room_data['available_from'], "%Y-%m-%d"),
            available_to=datetime.strptime(room_data['available_to'], "%Y-%m-%d"),
            price=room_data['price'],
            max_persons=room_data['max_persons'],
            owner_id=room_data['owner_id']
        )
        db.session.add(room)
        db.session.commit()

        return room.as_dict()
    else:
        return None, 401


@app.route("/api/room/delete", methods=['POST'])
@as_json
@login_required
def rooom_delete():
    """
    Delete room entry
    """
    requested_room_id = request.json['id']
    
    # Get requested room, if it exists
    requested_room = Room.query.filter_by(id=requested_room_id).first()
    if not requested_room:
        return None, 404

    # Check if current user has the rights to remove this room
    if requested_room.owner_id != current_user.id:
        return None, 401

    # Delete room from DB, delete room's directory with all the images inside
    db.session.delete(requested_room)
    db.session.commit()
    rooms_dir = path.join(current_dir, 'static', 'img', 'rooms')
    shutil.rmtree( path.join(rooms_dir, str(requested_room_id)) )
    return None, 200


@app.route("/api/prenotation/get_by_owner", methods=['POST'])
@as_json
@login_required
def prenotation_get_by_owner():
    """
    Get prenotation of a certain user
    """
    requested_user_id = request.json['id']

    requested_user_prenotations = []
    if requested_user_id == current_user.id:
        requested_user_prenotations = Prenotation.query.filter_by(buyer_id=requested_user_id).all()
        for i in range(0, len(requested_user_prenotations)):
            requested_user_prenotations[i] = requested_user_prenotations[i].as_dict()
            referenced_room = Room.query.filter_by(id=requested_user_prenotations[i]['room_id']).first()
            requested_user_prenotations[i]['name'] = referenced_room.name
            requested_user_prenotations[i]['address'] = referenced_room.address

        requested_user_prenotations = add_prenotation_picture_path(requested_user_prenotations)    
        return requested_user_prenotations
    else:
        return None, 401


@app.route("/api/prenotation/get_by_room_id", methods=['POST'])
@as_json
@login_required
def prenotation_get_by_room_id():
    """
    Get all the prenotations of a certain room
    """
    room_id = request.json['id']
    room_owner_id = Room.query.filter_by(id=room_id).first().owner_id

    if room_owner_id == current_user.id:
        requested_user_prenotations = Prenotation.query.filter_by(room_id=room_id).all()
        for i in range(0, len(requested_user_prenotations)):
            requested_user_prenotations[i] = requested_user_prenotations[i].as_dict()

            requested_user_prenotations[i]['username'] = User.query.filter_by(id=requested_user_prenotations[i]['buyer_id']).first().username

            referenced_room = Room.query.filter_by(id=requested_user_prenotations[i]['room_id']).first()
            requested_user_prenotations[i]['name'] = referenced_room.name
            requested_user_prenotations[i]['address'] = referenced_room.address

        requested_user_prenotations = add_prenotation_picture_path(requested_user_prenotations)
        return requested_user_prenotations
    else:
        return None, 401


@app.route("/api/prenotation/add", methods=['POST'])
@as_json
@login_required
def prenotation_add():
    """
    Add a new prenotation to a certain room
    """
    prenotation_data = request.json
    prenotation_data['start_date'] = datetime.strptime(prenotation_data['start_date'], "%Y-%m-%d").date()
    prenotation_data['end_date']   = datetime.strptime(prenotation_data['end_date'], "%Y-%m-%d").date()

    # Check to see if there are other prenotations in this period of time
    prenotations_conflicts = Prenotation.query.filter(and_(
        Prenotation.room_id == prenotation_data['room_id'],
        or_(
            and_(
                prenotation_data['start_date'] >= Prenotation.start_date,
                prenotation_data['start_date'] <= Prenotation.end_date
            ),
            and_(
                prenotation_data['end_date'] >= Prenotation.start_date,
                prenotation_data['end_date'] <= Prenotation.end_date
            )
        )
    )).all()

    # Get requested room
    requested_room = Room.query.filter_by(id=prenotation_data['room_id']).first()

    out = {}
    # Check for conflicts with other prenotations
    if prenotations_conflicts:
        out['date'] = "La stanza non è disponibile in questa data, riprova."
    # Check max persons
    if prenotation_data['persons'] > requested_room.max_persons:
        out['persons'] = "Errore, numero MAX disponibile: " + str(requested_room.max_persons)
    
    # No errors?
    if not out:
        # Calculate days difference
        delta = prenotation_data['end_date'] - prenotation_data['start_date']
        # Calculate price
        price = float(delta.days + 1) * float(requested_room.price) * float(prenotation_data['persons'])

        # Create new prenotation entry
        prenotation = Prenotation(
            room_id=prenotation_data['room_id'],
            buyer_id=prenotation_data['buyer_id'],
            start_date=prenotation_data['start_date'],
            end_date=prenotation_data['end_date'],
            persons=prenotation_data['persons'],
            price=price,
        )
        db.session.add(prenotation)
        db.session.commit()

        return None, 200
    else:
        # Return custom error
        return out, 500