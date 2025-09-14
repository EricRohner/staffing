from flask import Blueprint, flash, session, redirect, render_template, request, url_for

bp = Blueprint ('dashboard', __name__)

@bp.route("/dashboard")
def dashboard():
    if "username" in session:
        return render_template("dashboard.html", username=session['username'])