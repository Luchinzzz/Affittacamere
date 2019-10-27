from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from ecommerce.config import Config

# Initializing and configuring application
app = Flask(__name__)
app.config.from_object(Config)
# Initializing dbms utility
db = SQLAlchemy(app)
# Initializing Password Encrypter utility
bcrypt = Bcrypt(app)
# Initializing Flask Login utility
login_manager = LoginManager(app)

from ecommerce import routes