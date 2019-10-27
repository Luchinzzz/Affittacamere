from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from ecommerce.config import Config
from os import path, makedirs

current_dir = path.dirname(path.realpath(__file__))

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

# Creating db and directories if db doesn't exists
if not path.exists(path.join(current_dir, 'ecommerce.db')):
    from ecommerce.models import *
    db.create_all()
    try:
        makedirs(path.join(current_dir, 'static', 'img', 'profilepics', 'users'))
    except OSError:
        pass

from ecommerce import routes