from ecommerce import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    birth_date = db.Column(db.DateTime)
    password = db.Column(db.String(20), nullable=False)
    picture = db.Column(db.String(50), default='/static/img/profilepics/default.png')

    def __repr__(self):
        return f"User({self.id}, '{self.name}', '{self.surname}', '{self.username}', '{self.email}', '{self.birth_date}', '{self.password}')"

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    price = db.Column(db.Integer, nullable=False)
    persons = db.Column(db.Integer, nullable=False, default=1)
    address = db.Column(db.String(70), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
