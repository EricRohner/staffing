from flask import Blueprint, flash, session, redirect, render_template, request, url_for
from .auth import login_required

bp = Blueprint ('dashboard', __name__)

@bp.route("/dashboard")
@login_required
def dashboard():
    if "username" in session:
        return render_template("dashboard.html", 
        username=session['username'],
        is_user_admin=session['is_user_admin'],
        is_provider_admin=session['is_provider_admin'],
        is_customer_admin=session['is_customer_admin']
        )