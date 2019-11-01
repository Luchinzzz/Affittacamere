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
    birth_date = db.Column(db.Date)
    password = db.Column(db.String(20), nullable=False)
    picture = db.Column(db.String(40), default='/static/img/users/default.png')
    privilege = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return f"User({self.id}, '{self.name}', '{self.surname}', '{self.username}', '{self.email}', '{self.birth_date}', '{self.privilege}')"

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20))
    description = db.Column(db.Text)
    address = db.Column(db.String(70), nullable=False)
    available_from = db.Column(db.Date, nullable=False)
    available_to = db.Column(db.Date, nullable=False)
    price = db.Column(db.Float, nullable=False)
    max_persons = db.Column(db.Integer, nullable=False, default=1)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Room({self.id}, '{self.name}', '{self.address}', '{self.available_from}', '{self.available_to}', '{self.price}', '{self.max_persons}')"

class Prenotation(db.Model):
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.Date, primary_key=True, nullable=False)
    end_date = db.Column(db.Date, primary_key=True, nullable=False)
    persons = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)