import functools
from flask import Blueprint, flash, session, redirect, render_template, request, url_for
from .models import User

bp = Blueprint ('auth', __name__)

############################################################################################
## Auth Routes
############################################################################################

@bp.route('/')
def index():
    return render_template('auth.html')

@bp.route('/login', methods=['POST'])
def login():
    user_name = request.form['user_name']
    password = request.form['password']
    user = User.query.filter_by(user_name=user_name).first()
    if not user:
        flash("User name not found")
        return redirect(url_for('auth.index'))
    if not user.check_password(password):
        flash("Incorrect password")
        return redirect(url_for('auth.index'))
    session['user_name'] = user.user_name
    session['is_user_admin'] = user.is_user_admin
    session['is_provider_admin'] = user.is_provider_admin
    session['is_customer_admin'] = user.is_customer_admin

    return redirect(url_for("dashboard.index"))

@bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('auth.index'))

############################################################################################
## Decorators
############################################################################################

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_name' not in session:
            flash("You have to be logged in")
            return redirect(url_for('auth.index'))
        return view(**kwargs)
    return wrapped_view

def user_admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session['is_user_admin'] is not True:
            flash("You must be a user admin")
            return redirect(url_for('users.index'))
        return view(**kwargs)
    return wrapped_view

def provider_admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session['is_provider_admin'] is not True:
            flash("You must be a provider admin")
            return redirect(url_for('providers.index'))
        return view(**kwargs)
    return wrapped_view

def customer_admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session['is_customer_admin'] is not True:
            flash("You must be a customer admin")
            return redirect(url_for('customers.index'))
        return view(**kwargs)
    return wrapped_view