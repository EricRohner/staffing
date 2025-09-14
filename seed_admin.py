
from staffing import create_app
from staffing.models import db, User

app = create_app()

with app.app_context():
    db.create_all()  # Ensure tables are created

    # Check if the admin user already exists
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin')
        admin_user.set_password('admin')  # Set a secure password
        admin_user.set_user_admin(True)
        admin_user.set_provider_admin(True)
        admin_user.set_customer_admin(True)

        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created.")
    else:
        print("Admin user already exists.")
