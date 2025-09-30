from flask import Blueprint, flash, redirect, render_template, request, url_for
from datetime import datetime, timezone
from .auth import login_required, admin_required
from .models import db, Customer, Job, Provider

bp = Blueprint ('customers', __name__)

############################################################################################
## Customer Routes
############################################################################################

#Index
@bp.route('/customers')
@login_required
def index():
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        customers = Customer.to_collection_dict(Customer.query.order_by(Customer.last_edited.desc()), page, per_page, 'customers.index')
        return render_template('customers/customers.html', customers=customers)

#Create
@bp.route('/customers/create', methods=["GET", "POST"])
@login_required
@admin_required('is_customer_admin', 'customers.index')
def create():
        if request.method == "POST":
                if not Customer.query.filter_by(customer_name = request.form['customer_name']).first():
                        customer = Customer()
                        customer.from_dict(request.form)
                        db.session.add(customer)
                        db.session.commit()
                        return redirect(url_for('customers.index'))
                else:
                        flash('customer name already exists.')                 
        return render_template("customers/customers_create.html")

#Search
@bp.route('/customers/search', methods=['GET', 'POST'])
@login_required
def search():
        search_string = request.args.get('search_string', '')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        customers = Customer.to_collection_dict(Customer.query.filter(
                Customer.customer_name.like(f"{search_string}%")
                ).order_by(
                Customer.customer_name != search_string,
                Customer.customer_name.asc()
                ), page, per_page, 'customers.search', search_string=search_string)
        return render_template('customers/customers.html', customers = customers)

#Update Customer
@bp.route('/customers/update/<string:customer_id>', methods = ["GET", "POST"])
@login_required
@admin_required('is_customer_admin', 'customers.index')
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
                customer.from_dict(request.form)
                db.session.commit()
                flash("Customer updated.")
                return redirect(url_for('customers.index'))
        return render_template('customers/customers_update.html', customer = customer)

#Delete Customer and all attached jobs
@bp.route('/customers/delete/<string:customer_id>')
@login_required
@admin_required('is_customer_admin', 'customers.index')
def delete(customer_id):
        customer = Customer.query.filter_by(id = customer_id).first()
        if not customer:
                flash("Customer not found")
                return redirect(url_for('customers.index'))
        for job in customer.jobs:
               db.session.delete(job)
        db.session.delete(customer)
        db.session.commit()
        flash(f"Customer {customer.customer_name} has been deleted.")
        return redirect(url_for('customers.index'))

############################################################################################
## Jobs Routes
############################################################################################

#Create Job
@bp.route('/customers/customer_jobs_create/<string:customer_id>', methods = ["GET", "POST"])
@login_required
@admin_required('is_job_admin', 'customers.index')
def customer_jobs_create(customer_id):
        customer = Customer.query.filter_by(id = customer_id).first()
        if not customer:
                flash("Customer not found")
                return redirect(url_for('customers.index'))
        if request.method == "POST":
                job = Job()
                job.customer_id = customer_id
                job.from_dict(request.form)
                db.session.add(job)
                db.session.commit()
                return redirect(url_for('customers.customer_jobs', customer_id=customer_id))
        return render_template('customers/customer_jobs_create.html', customer=customer)

#Display single user and all attached jobs
@bp.route('/customers/customer_jobs/<string:customer_id>')
@login_required
def customer_jobs(customer_id):
        customer = Customer.query.filter_by(id = customer_id).first()
        if not customer:
                flash("Customer not found")
                return redirect(url_for('customers.index'))
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        jobs = Job.to_collection_dict(Job.query.filter_by(customer_id=customer_id), page, per_page, 'customers.customer_jobs', customer_id=customer_id)
        return render_template('customers/customer_jobs.html', customer = customer, jobs = jobs)

#Display single user, single job, search for a provider
@bp.route('/customers/customer_job_provider_search/<string:customer_id>/<string:job_id>', methods = ["GET", "POST"])
@login_required
def customer_job_provider_search(customer_id, job_id):
        customer = Customer.query.filter_by(id = customer_id).first()
        job = Job.query.filter_by(id = job_id).first()
        if not customer or not job:
                flash("Customer or job not found")
                return redirect(url_for('customers.index'))
        if request.method == "GET":
                providers = {"items": [], "_links": {}}
                search_string = request.args.get('search_string', '')
                page = request.args.get('page', 1, type=int)
                per_page = min(request.args.get('per_page', 10, type=int), 100)
                providers = Provider.to_collection_dict(Provider.query.filter(
                db.or_(Provider.provider_name.like(f"{search_string}%"),
                Provider.provider_email.like(f"{search_string}%")
                )).order_by(
                Provider.provider_email != search_string,
                Provider.provider_name != search_string,
                Provider.provider_email.asc()
                ), page, per_page, 'customers.customer_job_provider_search', customer_id=customer_id, job_id=job_id, search_string=search_string)
        return render_template('customers/customer_job_provider_search.html', customer = customer, job = job, providers = providers)

#Assign provider to job
@bp.route('/customers/customer_job_assign_provider/<string:customer_id>/<string:job_id>/<string:provider_id>')
@login_required
@admin_required('is_job_admin', 'customers.index')
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

#Remove provider from a job
@bp.route('/customers/customer_job_remove_provider/<string:customer_id>/<string:job_id>')
@login_required
@admin_required('is_job_admin', 'customers.index')
def customer_job_remove_provider(customer_id, job_id):
        job = Job.query.filter_by(id=job_id).first()
        if not job:
                flash("Job not found")
                return redirect(url_for('customers.customer_jobs', customer_id=customer_id))
        job.provider_id = None
        db.session.add(job)
        db.session.commit()
        return redirect(url_for('customers.customer_jobs', customer_id=customer_id))

#Delete job
@bp.route('/customers/delete_job/<string:customer_id>/<string:job_id>')
@login_required
@admin_required('is_job_admin', 'customers.index')
def delete_job(customer_id, job_id):
        job = Job.query.filter_by(id = job_id).first()
        if not job:
                flash("Job not found")
                return redirect(url_for('customers.index'))
        db.session.delete(job)
        db.session.commit()
        flash(f"Job {job.id} has been deleted.")
        return redirect(url_for('customers.customer_jobs', customer_id=customer_id))