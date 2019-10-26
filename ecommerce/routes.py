from flask import render_template
from ecommerce import app, db
from ecommerce.models import User, Room

@app.route("/")
@app.route("/home")
def home():
    """
    user = User(
        username='Cino',
        email='cino@gmail.com',
        password='ErbaGatta',
        name="Cino",
        surname='Gatto'
    )
    db.session.add(user)
    db.session.commit()
    """
    return render_template('index.html')

@app.route("/profile")
def profile():
    return render_template('profile.html')

@app.route("/results")
def results():
    return render_template('results.html')