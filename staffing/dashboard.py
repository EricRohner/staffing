from flask import Blueprint, flash, session, redirect, render_template, request, url_for
from .auth import login_required
from .models import User, db

bp = Blueprint ('dashboard', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
        return render_template('dashboard.html')

@bp.route('/dashboard/self_password_set', methods=('GET', 'POST'))
@login_required
def self_password_set():
        if request.method == 'POST':
                user = User.query.filter_by(username=session['username']).first()
                if request.form.get('new_password') != request.form.get('repeat_new_password'):
                        flash("New password and repeat new password must match.")
                        return redirect(url_for('dashboard.dashboard'))
                if user.check_password(request.form.get('current_password')):
                        user.set_password(request.form.get('new_password'))
                        db.session.commit()
                        flash("Password set")
                        return redirect(url_for('dashboard.dashboard'))
                else:
                        flash("Current password incorrect.")
                        return redirect(url_for('dashboard.dashboard'))
        return render_template('dashboard_self_password_set.html')