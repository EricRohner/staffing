
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
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

class Provider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider_name = db.Column(db.String(25), nullable=False)
    provider_email = db.Column(db.String(25), unique=True, nullable=False)
    created = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    last_edited = db.Column(db.DateTime, default=datetime.now(timezone.utc))

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(25), unique=True, nullable=False)
    customer_address = db.Column(db.String(25), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    last_edited = db.Column(db.DateTime, default=datetime.now(timezone.utc))

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(25), nullable=False)
    job_start_date = db.Column(db.Date, nullable=False)
    created = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    last_edited = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    Provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'), nullable=True)
    provider = db.relationship('Provider', backref=db.backref('jobs'))
    customer = db.relationship('Customer', backref=db.backref('jobs'))
