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
        return render_template("auth.html")
    if not user.check_password(password):
        flash("Incorrect password")
        return render_template("auth.html")
    session["username"] = username
    return redirect(url_for("dashboard.dashboard"))

@bp.route("/logout")
def logout():
    session.pop('username',None)
    return redirect(url_for('index'))