from flask import Blueprint, flash, session, redirect, render_template, request, url_for
from datetime import datetime, timezone
from .auth import login_required, user_admin_required
from .models import db, User

bp = Blueprint ('users', __name__)

@bp.route('/users')
@login_required
@user_admin_required
def index():
        users = User.query.order_by(User.last_edited.desc()).limit(10).all()
        return render_template('users.html', users=users)

@bp.route('/users/create', methods=('GET', 'POST'))
@login_required
@user_admin_required
def create():
        if request.method == 'POST':
                if not User.query.filter_by(user_name=request.form['user_name']).first():
                        new_user = User(user_name=request.form['user_name'])
                        new_user.set_password(request.form['password'])  
                        new_user.is_user_admin=bool(request.form.get('user_admin'))
                        new_user.is_provider_admin=bool(request.form.get('provider_admin'))
                        new_user.is_customer_admin=bool(request.form.get('customer_admin'))
                        db.session.add(new_user)
                        db.session.commit()
                        return redirect(url_for('users.index'))
                else:
                        flash("User already exists")
        return render_template('users_create.html')

@bp.route('/users/search', methods=('GET', 'POST'))
@login_required
@user_admin_required
def search():
        search_string = request.args.get('search_string', '')
        users = User.query.filter(
                User.user_name.like(f"{search_string}%")
        ).order_by(
                User.user_name != search_string,
                User.user_name.asc()
        ).all()
        return render_template('users.html', users=users)

@bp.route('/users/update/<string:id>', methods=('GET', 'POST'))
@login_required
@user_admin_required
def update(id):
        user = User.query.filter_by(id=id).first()
        if not user:
                flash("User not found")
                return redirect(url_for('users.index'))
        if request.method == "POST":
                collision = User.query.filter_by(user_name=request.form['user_name']).first()
                if collision and collision.id != user.id:
                        flash("User name must be unique.")
                        return redirect(url_for('users.index'))
                user.user_name=request.form['user_name']
                user.is_user_admin=bool(request.form.get('user_admin'))
                user.is_provider_admin=bool(request.form.get('provider_admin'))
                user.is_customer_admin=bool(request.form.get('customer_admin'))
                user.last_edited=datetime.now(timezone.utc)
                db.session.commit()
                flash("User updated.")
                return redirect(url_for('users.index'))

        return render_template('users_update.html', user=user)  

@bp.route('/users/set_password/<string:id>', methods=('GET', 'POST'))
@login_required
@user_admin_required
def set_password(id):
        user = User.query.filter_by(id=id).first()
        if not user:
                flash("User not found")
                return redirect(url_for('users.index'))
        if request.method == "POST":
                user.set_password(request.form['new_password'])
                user.last_edited=datetime.now(timezone.utc)
                db.session.commit()
                flash(f"Password updated for {user.user_name}.")
                return redirect(url_for('users.index'))

        return render_template('users_set_password.html', user=user)      

@bp.route('/users/delete/<string:id>', methods=('GET', 'POST'))
@login_required
@user_admin_required
def delete(id):
        user = User.query.filter_by(id=id).first()
        if not user:
                flash("User not found")
                return redirect(url_for('users.index'))
        if user.user_name == session['user_name']:
                flash("You can't delete yourself")
                return redirect(url_for('users.index'))
        db.session.delete(user)
        db.session.commit()
        flash(f"User {user.user_name} has been deleted.")
        return redirect(url_for('users.index'))
