from flask import Blueprint, flash, session, redirect, render_template, request, url_for
from .auth import login_required
from .models import User, db

bp = Blueprint ('dashboard', __name__)

############################################################################################
## Dashboard Routes
############################################################################################

@bp.route('/dashboard', methods=['GET'])
@login_required
def index():
        return render_template('dashboard/dashboard.html')

@bp.route('/dashboard/self_password_set', methods=['GET', 'POST'])
@login_required
def self_password_set():
        if request.method == 'POST':
                user = User.query.filter_by(user_name=session['user_name']).first()
                if request.form.get('new_password') != request.form.get('repeat_new_password'):
                        flash("New password and repeat new password must match.")
                        return redirect(url_for('dashboard.index'))
                if user.check_password(request.form.get('current_password')):
                        user.set_password(request.form.get('new_password'))
                        db.session.commit()
                        flash("Password set")
                        return redirect(url_for('dashboard.index'))
                else:
                        if not request.form.get('cancel'):
                                flash("Current password incorrect.")
                        return redirect(url_for('dashboard.index'))
        return render_template('dashboard/dashboard_self_password_set.html')


@bp.route('/dashboard/get_api_token', methods=['GET'])
@login_required
def get_api_token():
    user = User.query.filter_by(user_name=session['user_name']).first()
    token = user.generate_api_token()
    return render_template('dashboard/dashboard.html', api_token=token)

