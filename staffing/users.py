from flask import Blueprint, flash, session, redirect, render_template, request, url_for
from .auth import login_required

bp = Blueprint ('users', __name__)

@bp.route("/users")
@login_required
def users():
        username=session['username'],
        is_user_admin=session['is_user_admin'],
        is_provider_admin=session['is_provider_admin'],
        is_customer_admin=session['is_customer_admin'],
        return render_template("users.html"
        )