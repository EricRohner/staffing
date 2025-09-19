from flask import Blueprint, flash, session, redirect, render_template, request, url_for
from .auth import login_required
from .models import db, Provider

bp = Blueprint ('providers', __name__)

@bp.route('/providers')
@login_required
def providers():
        providers = Provider.query.order_by(Provider.last_edited.desc()).limit(10).all()
        return render_template('providers.html', providers=providers)

@bp.route('/providers/create', methods=("GET", "POST"))
@login_required
def create():
        if request.method == "POST":
                if not Provider.query.filter_by(provider_email=request.form['provider_email']).first():
                        new_provider = Provider(provider_email=request.form['provider_email'])
                        new_provider.provider_name = request.form['provider_name']
                        db.session.add(new_provider)
                        db.session.commit()
                        return redirect(url_for('providers.providers'))
                else:
                        flash('Provider email already exists.')
                        
        return render_template("providers_create.html")

@bp.route('/providers/search')
@login_required
def search():
        return "Privider search stub"

@bp.route('/providers/update/<string:id>')
@login_required  
def update():
        return "Privider update stub"

@bp.route('/providers/delete/<string:id>')
@login_required
def delete():
        return "Privider create stub"