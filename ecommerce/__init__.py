from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from ecommerce.config import Config
from os import path, makedirs, listdir, remove
import shutil
from datetime import datetime

current_dir = path.dirname(path.realpath(__file__))

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

# Creating db if it doesn't exist
if not path.exists(path.join(current_dir, 'ecommerce.db')):
    # Delete Users and Rooms data, since they are all invalid if they exist
    users_dir = path.join(current_dir, 'static', 'img', 'users')
    rooms_dir = path.join(current_dir, 'static', 'img', 'rooms')
    for f in listdir(users_dir):
        if f != 'default.png':
            remove(path.join(users_dir, f))
    for f in listdir(rooms_dir):
        if f != 'readme.md':
            shutil.rmtree(path.join(rooms_dir, f), ignore_errors=True)

    # Create DB
    from ecommerce.models import *
    db.create_all()
    
    # Add first user with privilege
    from ecommerce.models import User, Room
    user = User(
        name='Jack',
        surname='Nickolson',
        username='asd123',
        email='asd123@gmail.com',
        birth_date=datetime(2019, 10, 30),
        password=bcrypt.generate_password_hash('asd123').decode('utf-8'),
        privilege=True
    )
    db.session.add(user)
    db.session.commit()
    # Add first room
    room = Room(
        name='Prova',
        description='Lorem ipsum non ricordo scrivo scrivo scrivo scrivo scrivo scrivo ora basta che mi sono scocciato',
        address="Perugia",
        available_from=datetime(2019, 10, 30),
        available_to=datetime(2019, 11, 30),
        price=100.0,
        max_persons=4,
        owner_id=user.id
    )
    db.session.add(room)
    db.session.commit()
    makedirs(path.join('ecommerce', 'static', 'img', 'rooms', str(room.id)))
    # Add second user with no privilege
    user = User(
        name='Povero',
        surname='Stronzo',
        username='ciaopoveri',
        email='ciaopoveri@gmail.com',
        birth_date=datetime(2019, 10, 30),
        password=bcrypt.generate_password_hash('asd123').decode('utf-8'),
        privilege=False
    )
    db.session.add(user)
    db.session.commit()

from ecommerce import routes