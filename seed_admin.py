
from staffing import create_app
from staffing.models import db, User

app = create_app()

with app.app_context():
    db.create_all()  # Ensure tables are created

    # Check if the admin user already exists
    if not User.query.filter_by(user_name='admin').first():
        admin_user = User(user_name='admin')
        admin_user.set_password('admin')  # Set a secure password
        admin_user.is_user_admin=True
        admin_user.is_provider_admin=True
        admin_user.is_customer_admin=True
        admin_user.is_job_admin=True

        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created.")
    else:
        print("Admin user already exists.")
