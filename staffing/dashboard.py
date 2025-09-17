from flask import Blueprint, flash, session, redirect, render_template, request, url_for
from .auth import login_required

bp = Blueprint ('dashboard', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
        return render_template('dashboard.html')