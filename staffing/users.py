from flask import Blueprint, flash, session, redirect, render_template, request, url_for
from datetime import datetime, timezone
from .auth import login_required, user_admin_required
from .models import db, User

bp = Blueprint ('users', __name__)

############################################################################################
## User Routes
############################################################################################

@bp.route('/users')
@login_required
@user_admin_required
def index():
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        users = User.to_collection_dict(User.query.order_by(User.last_edited.desc()), page, per_page, 'users.index')
        #users = User.query.order_by(User.last_edited.desc()).limit(10).all()
        return render_template('users.html', users=users)

@bp.route('/users/create', methods=('GET', 'POST'))
@login_required
@user_admin_required
def create():
        if request.method == 'POST':
                if not User.query.filter_by(user_name=request.form['user_name']).first():
                        user = User()
                        #HTML behavior only includes the checkbox name if true so we explicitly define the values by whether the checkbox is in the form data
                        form_data = request.form.to_dict()
                        form_data['is_user_admin'] = 'user_admin' in request.form
                        form_data['is_provider_admin'] = 'provider_admin' in request.form
                        form_data['is_customer_admin'] = 'customer_admin' in request.form
                        user.from_dict(form_data, new_user=False)
                        db.session.add(user)
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

    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)

    query = User.query.filter(
        User.user_name.like(f"{search_string}%")
    ).order_by(
        User.user_name != search_string,
        User.user_name.asc()
    )

    users = User.to_collection_dict(query, page, per_page, 'users.search', search_string=search_string)

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
                
                #HTML behavior only includes the checkbox name if true so we explicitly define the values by whether the checkbox is in the form data
                form_data = request.form.to_dict()
                form_data['is_user_admin'] = 'user_admin' in request.form
                form_data['is_provider_admin'] = 'provider_admin' in request.form
                form_data['is_customer_admin'] = 'customer_admin' in request.form
                user.from_dict(form_data, new_user=False)
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