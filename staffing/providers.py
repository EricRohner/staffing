from flask import Blueprint, flash, session, redirect, render_template, request, url_for
from .auth import login_required

bp = Blueprint ('providers', __name__)

@bp.route('/providers')
@login_required
def providers():
        return render_template('providers.html')