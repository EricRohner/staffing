from flask import Blueprint, flash, session, redirect, render_template, request, url_for
from .auth import login_required, user_admin_required
from staffing.models import db, User

bp = Blueprint ('users', __name__)

@bp.route('/users')
@login_required
@user_admin_required
def users():
        return render_template('users.html')

@bp.route('/users/create', methods=('GET', 'POST'))
@login_required
@user_admin_required
def create():
        if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                error = None
                if not username:
                        error = "Username is required"
                if not password:
                        error = "Password is required"
                if error is not None:
                        flash(error)
                else:
                        if not User.query.filter_by(username=username).first():
                                new_user = User(username=username)
                                new_user.set_password(password)  
                                new_user.set_user_admin(bool(request.form.get('user_admin')))
                                new_user.set_provider_admin(bool(request.form.get('provider_admin')))
                                new_user.set_customer_admin(bool(request.form.get('customer_admin')))
                                db.session.add(new_user)
                                db.session.commit()
                                return redirect(url_for('users.users'))
                        else:
                                flash("User already exists")
        return render_template('users_create.html')