
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_user_admin = db.Column(db.Boolean, default=False)
    is_provider_admin = db.Column(db.Boolean, default=False)
    is_customer_admin = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_user_admin(self, admin):
        if isinstance(admin, bool):
            self.is_user_admin = admin
    def set_provider_admin(self, admin):
        if isinstance(admin, bool):
            self.is_provider_admin = admin
    def set_customer_admin(self, admin):
        if isinstance(admin, bool):
            self.is_customer_admin = admin
