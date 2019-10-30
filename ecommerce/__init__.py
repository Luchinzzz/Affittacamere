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

# Creating db and directories if db doesn't exists
if not path.exists(path.join(current_dir, 'ecommerce.db')):
    # Delete Users and Rooms data, since they are all invalid if they exists
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
    
    # Add First User
    from ecommerce.models import User
    user = User(
        name='Nome',
        surname='Cognome',
        username='asd123',
        email='asd123@gmail.com',
        birth_date=datetime(2019, 10, 30),
        password=bcrypt.generate_password_hash('asd123').decode('utf-8')
    )
    db.session.add(user)
    db.session.commit()

from ecommerce import routes