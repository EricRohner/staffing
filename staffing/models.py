
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from flask import url_for

db = SQLAlchemy()

############################################################################################
## Mixins
############################################################################################

class paginated_mixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = db.paginate(query, page=page, per_page=per_page,
                                error_out=False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data

############################################################################################
## User Model
############################################################################################

class User(paginated_mixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(25), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_user_admin = db.Column(db.Boolean, default=False)
    is_provider_admin = db.Column(db.Boolean, default=False)
    is_customer_admin = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    last_edited = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        data = {
            'id' : self.id,
            'user_name' : self.user_name,
            'is_user_admin' : self.is_user_admin,
            'is_provider_admin' : self.is_provider_admin,
            'is_customer_admin' : self.is_customer_admin,
            'created' : self.created,
            'last_edited' : self.last_edited
        }
        return data
    
    def from_dict(self, data, new_user=False):
        for field in ['user_name', 'is_user_admin', 'is_provider_admin', 'is_customer_admin']:
            if field in data:
                setattr(self, field, data[field])
        if 'password' in data:
            self.set_password(data['password'])
        if new_user:
            self.created = datetime.now(timezone.utc)
        self.last_edited = datetime.now(timezone.utc)

############################################################################################
## Provider Model
############################################################################################

class Provider(paginated_mixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider_name = db.Column(db.String(25), nullable=False)
    provider_email = db.Column(db.String(25), unique=True, nullable=False)
    created = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    last_edited = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def to_dict(self):
        data = {
            'id' : self.id,
            'provider_name' : self.provider_name,
            'provider_email' : self.provider_email,
            'created' : self.created,
            'last_edited' : self.last_edited
        }
        return data
    
    def from_dict(self, data, new_provider=False):

        for field in ['provider_name', 'provider_email']:
            if field in data:
                setattr(self, field, data[field])
        if new_provider:
            self.created = datetime.now(timezone.utc)
        self.last_edited = datetime.now(timezone.utc)

############################################################################################
## Customer Model
############################################################################################

class Customer(paginated_mixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(25), unique=True, nullable=False)
    customer_address = db.Column(db.String(25), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    last_edited = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def to_dict(self):
        data = {
            'id' : self.id,
            'customer_name' : self.customer_name,
            'customer_address' : self.customer_address,
            'jobs': [job.to_dict() for job in self.jobs],
            'created' : self.created,
            'last_edited' : self.last_edited
        }
        return data
    
    def from_dict(self, data, new_customer=False):
        for field in ['customer_name', 'customer_address']:
            if field in data:
                setattr(self, field, data[field])
        if new_customer:
            self.created = datetime.now(timezone.utc)
        self.last_edited = datetime.now(timezone.utc)

############################################################################################
## Job Model
############################################################################################

class Job(paginated_mixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(25), nullable=False)
    job_start_date = db.Column(db.Date, nullable=False)
    created = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    last_edited = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'), nullable=True)
    provider = db.relationship('Provider', backref=db.backref('jobs'))
    customer = db.relationship('Customer', backref=db.backref('jobs'))

    def to_dict(self):
        data = {
            'id' : self.id,
            'job_title' : self.job_title,
            'job_start_date' : self.job_start_date,
            'customer_id' : self.customer_id,
            'provider_id' : self.provider_id,
            'created' : self.created,
            'last_edited' : self.last_edited,
        }
        return data
    
    def from_dict(self, data, new_job=False):
        if 'job_start_date' in data:
            self.job_start_date = datetime.strptime(data['job_start_date'], "%Y-%m-%d").date()
        for field in ['job_title', 'customer_id', 'provider_id']:
            if field in data:
                setattr(self, field, data[field])
        if new_job:
            self.created = datetime.now(timezone.utc)
        self.last_edited = datetime.now(timezone.utc)