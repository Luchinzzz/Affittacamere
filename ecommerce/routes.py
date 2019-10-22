from flask import render_template
from ecommerce import app

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')