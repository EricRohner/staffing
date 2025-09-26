from datetime import datetime
from flask import Blueprint, request, abort, url_for
from .models import db, User, Provider, Customer, Job

bp = Blueprint ('api', __name__)

############################################################################################
## User API
############################################################################################

#Create
@bp.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if 'user_name' not in data or 'password' not in data or 'is_user_admin' not in data or 'is_provider_admin' not in data or 'is_customer_admin' not in data:
        abort(400, description="Missing one or more user field in request data")
    if User.query.filter_by(user_name=data['user_name']).first():
        abort(400, description="user_name already taken")
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    return user.to_dict(), 201, {'Location': url_for('api.get_user', id=user.id)}

#Read 1
@bp.route('/api/users/<int:id>', methods = ['GET'])
def get_user(id):
       return db.get_or_404(User, id).to_dict()

#Read users paginated
@bp.route('/api/users', methods=['GET'])
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    return User.to_collection_dict(db.select(User), page, per_page, 'api.get_users')

#Update
@bp.route('/api/users/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    user = db.get_or_404(User, id)
    collision = User.query.filter_by(user_name=data['user_name']).first()
    if collision and collision.id != id:
        abort(400, description="user_name already taken")
    user.from_dict(data)
    db.session.add(user)
    db.session.commit()
    return user.to_dict(), 202, {'Location': url_for('api.get_user', id=user.id)}

#Delete
@bp.route('/api/users/<id>', methods=['DELETE'])
def delete_user(id):
    user = db.get_or_404(User, id)
    db.session.delete(user)
    db.session.commit()
    return {'message': f'User id={id} deleted'}, 202

############################################################################################
## Provider API
############################################################################################

#Create
@bp.route('/api/providers', methods=['POST'])
def create_provider():
    data = request.get_json()
    if 'provider_name' not in data or 'provider_email' not in data:
        abort(400, description="Missing one or more user field in request data")
    if Provider.query.filter_by(provider_email=data['provider_email']).first():
        abort(400, description="provider_email already taken")
    provider = Provider()
    provider.from_dict(data, new_provider=True)
    db.session.add(provider)
    db.session.commit()
    return provider.to_dict(), 201, {'Location': url_for('api.get_provider', id=provider.id)}

#Read 1
@bp.route('/api/providers/<int:id>', methods = ['GET'])
def get_provider(id):
       return db.get_or_404(Provider, id).to_dict()

#Update
@bp.route('/api/providers/<int:id>', methods=['PUT'])
def update_provider(id):
    data = request.get_json()
    provider = db.get_or_404(Provider, id)
    collision = Provider.query.filter_by(provider_email=data['provider_email']).first()
    if collision and collision.id != id:
        abort(400, description="provider_email already taken")
    provider.from_dict(data)
    db.session.add(provider)
    db.session.commit()
    return provider.to_dict(), 202, {'Location': url_for('api.get_provider', id=provider.id)}

#Delete
@bp.route('/api/providers/<id>', methods=['DELETE'])
def delete_provider(id):
    provider = db.get_or_404(Provider, id)
    db.session.delete(provider)
    db.session.commit()
    return {'message': f'Provider id={id} deleted'}, 202

############################################################################################
## Customer API
############################################################################################

#Create
@bp.route('/api/customers', methods=['POST'])
def create_customer():
    data = request.get_json()
    if 'customer_name' not in data or 'customer_address' not in data:
        abort(400, description="Missing one or more user field in request data")
    if Customer.query.filter_by(customer_name=data['customer_name']).first():
        abort(400, description="customer_name already taken")
    customer = Customer()
    customer.from_dict(data, new_customer=True)
    db.session.add(customer)
    db.session.commit()
    return customer.to_dict(), 201, {'Location': url_for('api.get_customer', id=customer.id)}

#Read 1
@bp.route('/api/customers/<int:id>', methods = ['GET'])
def get_customer(id):
    return db.get_or_404(Customer, id).to_dict()

#Update
@bp.route('/api/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    data = request.get_json()
    customer = db.get_or_404(Customer, id)
    collision = Customer.query.filter_by(customer_name=data['customer_name']).first()
    if collision and collision.id != id:
        abort(400, description="customer_name already taken")
    customer.from_dict(data)
    db.session.add(customer)
    db.session.commit()
    return customer.to_dict(), 202, {'Location': url_for('api.get_customer', id=customer.id)}

#Delete
@bp.route('/api/customers/<id>', methods=['DELETE'])
def delete_customer(id):
    customer = db.get_or_404(Customer, id)
    for job in customer.jobs:
        db.session.delete(job)
    db.session.delete(customer)
    db.session.commit()
    return {'message': f'Customer id={id} deleted'}, 202

############################################################################################
## Jobs API
############################################################################################

#Create
@bp.route('/api/jobs', methods=['POST'])
def create_job():
    data = request.get_json()
    if 'job_title' not in data or 'job_start_date' not in data or 'customer_id' not in data:
        abort(400, description="Missing one or more user field in request data")
    try:
        datetime.strptime(data['job_start_date'], "%Y-%m-%d").date()
    except ValueError:
        abort(400, "Invalid date format for job_start_date. Expected YYYY-MM-DD.")
    job = Job()
    job.from_dict(data, new_job=True)
    db.session.add(job)
    db.session.commit()
    return job.to_dict(), 201, {'Location': url_for('api.get_customer', id=job.id)}

#Read 1
@bp.route('/api/jobs/<int:id>', methods = ['GET'])
def get_job(id):
       return db.get_or_404(Job, id).to_dict()

#Update
@bp.route('/api/jobs/<int:id>', methods=['PUT'])
def update_job(id):
    data = request.get_json()
    if 'job_start_date' in data: 
        try:
            datetime.strptime(data['job_start_date'], "%Y-%m-%d").date()
        except ValueError:
            abort(400, "Invalid date format for job_start_date. Expected YYYY-MM-DD.")
    job = db.get_or_404(Job, id)
    job.from_dict(data)
    db.session.add(job)
    db.session.commit()
    return job.to_dict(), 202, {'Location': url_for('api.get_job', id=job.id)}

#Delete
@bp.route('/api/jobs/<id>', methods=['DELETE'])
def delete_job(id):
    job = db.get_or_404(Job, id)
    db.session.delete(job)
    db.session.commit()
    return {'message': f'Job id={id} deleted'}, 202