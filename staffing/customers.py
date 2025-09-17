from flask import Blueprint, flash, session, redirect, render_template, request, url_for
from .auth import login_required

bp = Blueprint ('customers', __name__)

@bp.route('/customers')
@login_required
def customers():
        return render_template('customers.html')