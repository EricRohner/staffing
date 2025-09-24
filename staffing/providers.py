from flask import Blueprint, flash, redirect, render_template, request, url_for
from datetime import datetime, timezone
from .auth import login_required, provider_admin_required
from .models import db, Provider

bp = Blueprint ('providers', __name__)

############################################################################################
## Provider Routes
############################################################################################

@bp.route('/providers')
@login_required
def index():
        providers = Provider.query.order_by(Provider.last_edited.desc()).limit(10).all()
        return render_template('providers.html', providers=providers)

@bp.route('/providers/create', methods=("GET", "POST"))
@login_required
@provider_admin_required
def create():
        if request.method == "POST":
                if not Provider.query.filter_by(provider_email=request.form['provider_email']).first():
                        new_provider = Provider(provider_email=request.form['provider_email'])
                        new_provider.provider_name = request.form['provider_name']
                        db.session.add(new_provider)
                        db.session.commit()
                        return redirect(url_for('providers.index'))
                else:
                        flash('Provider email already exists.')                        
        return render_template("providers_create.html")

@bp.route('/providers/search', methods=('GET', 'POST'))
@login_required
def search():
        search_string = request.args.get('search_string', '')
        providers = Provider.query.filter(
                db.or_(Provider.provider_name.like(f"{search_string}%"),
                        Provider.provider_email.like(f"{search_string}%")
                )).order_by(
                        Provider.provider_email != search_string,
                        Provider.provider_name != search_string,
                        Provider.provider_email.asc()
                ).all()
        return render_template('providers.html', providers=providers)

@bp.route('/providers/update/<string:id>', methods=("GET", "POST"))
@login_required
@provider_admin_required
def update(id):
        provider = Provider.query.filter_by(id=id).first()
        if not provider:
                flash("Provider not found")
                return redirect(url_for('providers.index'))
        if request.method == "POST":
                collision = Provider.query.filter_by(provider_email=request.form['provider_email']).first()
                if collision and collision.id != provider.id:
                        flash("Provider email already exists.")
                        return redirect(url_for('providers.update', id=id))
                provider.provider_name=request.form['provider_name']
                provider.provider_email=request.form['provider_email']
                provider.last_edited=datetime.now(timezone.utc)
                db.session.commit()
                flash("Provider updated.")
                return redirect(url_for('providers.index'))

        return render_template('providers_update.html', provider=provider)

@bp.route('/providers/delete/<string:id>')
@login_required
@provider_admin_required
def delete(id):
        provider = Provider.query.filter_by(id=id).first()
        if not provider:
                flash("Provider not found")
                return redirect(url_for('providers.index'))
        db.session.delete(provider)
        db.session.commit()
        flash(f"Provider {provider.provider_name} has been deleted.")
        return redirect(url_for('providers.index'))