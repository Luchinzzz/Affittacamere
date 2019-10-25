from flask import render_template
from ecommerce import app

@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html')

@app.route("/profile")
def profile():
    return render_template('profile.html')

@app.route("/results")
def results():
    return render_template('results.html')