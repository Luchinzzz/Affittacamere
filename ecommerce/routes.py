from flask import render_template
from ecommerce import app, db
from ecommerce.models import User, Room
from ecommerce.forms import RegistrationForm, LoginForm


def check_login_register(template_filename, registration_form, login_form):
    # No Post request?
    if not registration_form.is_submitted() and not login_form.is_submitted():
        return False
    
    # If Registration POST was submitted, is it valid?
    if registration_form.validate_on_submit():
        # Successfull Registration
        # TODO
        return render_template(template_filename, login_form=login_form, registration_form=registration_form)
    elif not login_form.is_submitted():
        # Something went wrong during registration
        return render_template(template_filename, login_form=login_form, registration_form=registration_form, register_error=True)

    if login_form.validate_on_submit():
        # Successfull Login
        # TODO
        return render_template(template_filename, login_form=login_form, registration_form=registration_form)
    
    # Wrong Credentials for Login
    return render_template(template_filename, login_form=login_form, registration_form=registration_form, login_error=True)


@app.route("/", methods=['GET', 'POST'])
@app.route("/home")
def home():
    login_form = LoginForm()
    registration_form = RegistrationForm()
    result_forms = check_login_register('index.html', registration_form, login_form)
    if result_forms:
        return result_forms
    return render_template('index.html', login_form=login_form, registration_form=registration_form)


@app.route("/profile", methods=['GET', 'POST'])
def profile():
    login_form = LoginForm()
    registration_form = RegistrationForm()
    result_forms = check_login_register('profile.html', registration_form, login_form)
    if result_forms:
        return result_forms
    return render_template('profile.html', login_form=login_form, registration_form=registration_form)


@app.route("/results", methods=['GET', 'POST'])
def results():
    login_form = LoginForm()
    registration_form = RegistrationForm()
    result_forms = check_login_register('results.html', registration_form, login_form)
    if result_forms:
        return result_forms
    return render_template('results.html', login_form=login_form, registration_form=registration_form)