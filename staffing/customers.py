from flask import Blueprint, flash, redirect, render_template, request, url_for
from datetime import datetime, timezone
from .auth import login_required, customer_admin_required
from .models import db, Customer

bp = Blueprint ('customers', __name__)

@bp.route('/customers')
@login_required
def index():
        customers = Customer.query.order_by(Customer.last_edited.desc()).limit(10).all()
        return render_template('Customers.html', customers=customers)

@bp.route('/customers/create', methods=("GET", "POST"))
@login_required
@customer_admin_required
def create():
        if request.method == "POST":
                if not Customer.query.filter_by(customer_name=request.form['customer_name']).first():
                        new_customer = Customer(customer_name=request.form['customer_name'])
                        new_customer.customer_address = request.form['customer_address']
                        db.session.add(new_customer)
                        db.session.commit()
                        return redirect(url_for('customers.index'))
                else:
                        flash('customer name already exists.')                 
        return render_template("customers_create.html")

@bp.route('/customers/search', methods=('GET', 'POST'))
@login_required
def search():
        search_string = request.args.get('search_string', '')
        customers = Customer.query.filter(
                Customer.customer_name.like(f"{search_string}%")
        ).order_by(
                Customer.customer_name != search_string,
                Customer.customer_name.asc()
        ).all()
        return render_template('customers.html', customers=customers)

@bp.route('/customers/update/<string:id>', methods=("GET", "POST"))
@login_required
@customer_admin_required
def update(id):
        customer = Customer.query.filter_by(id=id).first()
        if not customer:
                flash("Customer not found")
                return redirect(url_for('customers.index'))
        if request.method == "POST":
                collision = Customer.query.filter_by(customer_name=request.form['customer_name']).first()
                if collision and collision.id != customer.id:
                        flash("Customer name already exists.")
                        return redirect(url_for('customers.update', id=id))
                customer.customer_name=request.form['customer_name']
                customer.customer_address=request.form['customer_address']
                customer.last_edited=datetime.now(timezone.utc)
                db.session.commit()
                flash("Customer updated.")
                return redirect(url_for('customers.index'))
        return render_template('customers_update.html', customer=customer)

@bp.route('/customers/delete/<string:id>')
@login_required
@customer_admin_required
def delete(id):
        customer = Customer.query.filter_by(id=id).first()
        if not customer:
                flash("Customer not found")
                return redirect(url_for('customers.index'))
        db.session.delete(customer)
        db.session.commit()
        flash(f"Customer {customer.customer_name} has been deleted.")
        return redirect(url_for('customers.index'))