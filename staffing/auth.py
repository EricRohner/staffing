import functools
from flask import Blueprint, flash, session, redirect, render_template, request, url_for, abort
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
    for key, value in user.to_dict().items():
        session[key] = value
    return redirect(url_for("dashboard.index"))

@bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('auth.index'))

############################################################################################
## View Decorators
############################################################################################

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_name' not in session:
            flash("You have to be logged in")
            return redirect(url_for('auth.index'))
        return view(**kwargs)
    return wrapped_view

def admin_required(required_role, redirect_to):
    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if not session.get(required_role, False):
                flash(f"You do not have required role: {required_role}")
                return redirect(url_for(redirect_to))
            return view(**kwargs)
        return wrapped_view
    return decorator

############################################################################################
## API Decorators
############################################################################################

def require_token_with_role(required_role):
    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            token = request.headers.get('X-API-Token')
            if not token or '.' not in token:
                abort(403, description="Missing or malformed token")

            token_id, raw_token = token.split('.', 1)
            user = User.query.filter_by(api_token_id=token_id).first()

            if not user:
                abort(403, description="Token ID not found")

            if not user.check_token(raw_token):
                abort(403, description="Token not accepted")

            if not getattr(user, required_role, False):
                abort(403, description=f"User does not have required role: {required_role}")

            return view(**kwargs)
        return wrapped_view
    return decorator

