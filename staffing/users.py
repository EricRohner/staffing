from flask import Blueprint, flash, session, redirect, render_template, request, url_for
from .auth import login_required, user_admin_required
from staffing.models import db, User

bp = Blueprint ('users', __name__)

@bp.route('/users')
@login_required
@user_admin_required
def users():
        users = User.query.order_by(User.created.desc()).limit(10).all()
        return render_template('users.html', users=users)

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

@bp.route('/users/search', methods=('GET', 'POST'))
@login_required
@user_admin_required
def user_search():
        search_string = request.args.get('search_string', '')
        users = User.query.filter(User.username.like(f"{search_string}%")).all()
        return render_template('users.html', users=users)

@bp.route('/users/update/<string:id>', methods=('GET', 'POST'))
@login_required
@user_admin_required
def update_user(id):
        user = User.query.filter_by(id=id).first_or_404()
        return render_template('users_update.html', user=user)

@bp.route('/users/delete/<string:id>', methods=('GET', 'POST'))
@login_required
@user_admin_required
def delete_user(id):
        user = User.query.filter_by(id=id).first_or_404()
        if user.username == session['username']:
                flash("You can't delete yourself")
                return redirect(url_for('users.users'))
        db.session.delete(user)
        db.session.commit()
        flash(f"User '{user.username}' has been deleted.")
        return redirect(url_for('users.users'))
