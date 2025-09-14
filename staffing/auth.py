import functools
from flask import Blueprint, flash, session, redirect, render_template, request, url_for
from .models import User

bp = Blueprint ('auth', __name__)

@bp.route('/')
def index():
    return render_template('auth.html')

@bp.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("Username not found")
        return redirect(url_for('auth.index'))
    if not user.check_password(password):
        flash("Incorrect password")
        return redirect(url_for('auth.index'))
    session["username"] = user.username
    session["is_user_admin"] = user.is_user_admin
    session["is_provider_admin"] = user.is_provider_admin
    session["is_customer_admin"] = user.is_customer_admin

    return redirect(url_for("dashboard.dashboard"))

@bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('auth.index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if "username" not in session:
            flash("You have to be logged in")
            return redirect(url_for('auth.index'))
        return view(**kwargs)
    return wrapped_view