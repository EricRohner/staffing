from flask import Blueprint, flash, redirect, render_template, request, url_for
from datetime import datetime, timezone
from .auth import login_required, customer_admin_required
from .models import db, Customer, Job, Provider

bp = Blueprint ('customers', __name__)

############################################################################################
## Customer Routes
############################################################################################

@bp.route('/customers')
@login_required
def index():
        customers = Customer.query.order_by(Customer.last_edited.desc()).limit(10).all()
        return render_template('Customers.html', customers = customers)

@bp.route('/customers/create', methods=("GET", "POST"))
@login_required
@customer_admin_required
def create():
        if request.method == "POST":
                if not Customer.query.filter_by(customer_name = request.form['customer_name']).first():
                        new_customer = Customer(customer_name = request.form['customer_name'])
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
        return render_template('customers.html', customers = customers)

@bp.route('/customers/update/<string:customer_id>', methods = ("GET", "POST"))
@login_required
@customer_admin_required
def update(customer_id):
        customer = Customer.query.filter_by(id = customer_id).first()
        if not customer:
                flash("Customer not found")
                return redirect(url_for('customers.index'))
        if request.method == "POST":
                collision = Customer.query.filter_by(customer_name = request.form['customer_name']).first()
                if collision and collision.id != customer.id:
                        flash("Customer name already exists.")
                        return redirect(url_for('customers.update', id=customer_id))
                customer.customer_name = request.form['customer_name']
                customer.customer_address = request.form['customer_address']
                customer.last_edited = datetime.now(timezone.utc)
                db.session.commit()
                flash("Customer updated.")
                return redirect(url_for('customers.index'))
        return render_template('customers_update.html', customer = customer)

@bp.route('/customers/delete/<string:customer_id>')
@login_required
@customer_admin_required
def delete(customer_id):
        customer = Customer.query.filter_by(id = customer_id).first()
        if not customer:
                flash("Customer not found")
                return redirect(url_for('customers.index'))
        db.session.delete(customer)
        db.session.commit()
        flash(f"Customer {customer.customer_name} has been deleted.")
        return redirect(url_for('customers.index'))

@bp.route('/customers/customer_jobs/<string:customer_id>')
@login_required
def customer_jobs(customer_id):
        customer = Customer.query.filter_by(id = customer_id).first()
        if not customer:
                flash("Customer not found")
                return redirect(url_for('customers.index'))
        return render_template('customer_jobs.html', customer = customer, jobs = customer.jobs)

@bp.route('/customers/customer_jobs_add/<string:customer_id>', methods = ("GET", "POST"))
@login_required
def customer_jobs_add(customer_id):
        customer = Customer.query.filter_by(id = customer_id).first()
        if not customer:
                flash("Customer not found")
                return redirect(url_for('customers.index'))
        if request.method == "POST":
                print(request.form['job_title'])
                new_job = Job(job_title = request.form['job_title'])
                new_job.job_start_date = datetime.strptime(request.form['job_start_date'], '%Y-%m-%d')
                new_job.customer_id = customer_id
                db.session.add(new_job)
                db.session.commit()
                return redirect(url_for('customers.customer_jobs', customer_id=customer_id))
        return render_template('customer_jobs_add.html', customer=customer)

@bp.route('/customers/customer_job_provider_search/<string:customer_id>/<string:job_id>', methods = ("GET", "POST"))
@login_required
def customer_job_provider_search(customer_id, job_id):
        customer = Customer.query.filter_by(id = customer_id).first()
        job = Job.query.filter_by(id = job_id).first()
        providers = []
        if request.method == "POST":
                search_string = request.form.get('search_string')
                providers = Provider.query.filter(
                        db.or_(Provider.provider_name.like(f"{search_string}%"),
                                Provider.provider_email.like(f"{search_string}%")
                        )).order_by(
                                Provider.provider_email != search_string,
                                Provider.provider_name != search_string,
                                Provider.provider_email.asc()
                        ).all()

        return render_template('customer_job_provider_search.html', customer = customer, jobs = [job], providers = providers)

@bp.route('/customers/customer_job_assign_provider/<string:customer_id>/<string:job_id>/<string:provider_id>')
@login_required
@customer_admin_required
def customer_job_assign_provider(customer_id, job_id, provider_id):
    job = Job.query.filter_by(id=job_id).first()
    if not job:
        flash("Job not found")
        return redirect(url_for('customers.customer_jobs', customer_id=customer_id))
    provider = Provider.query.filter_by(id=provider_id).first()
    if not provider:
        flash("Provider not found")
        return redirect(url_for('customers.customer_jobs', customer_id=customer_id))
    job.provider_id = provider_id
    db.session.add(job)
    db.session.commit()
    print(f"Assigning provider {provider_id} to job {job_id}")
    flash("Provider assigned to job.")
    return redirect(url_for('customers.customer_jobs', customer_id=customer_id))