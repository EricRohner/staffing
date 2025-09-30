import os
from flask import Flask
from flask_migrate import Migrate
from .models import db

#TODO: Write tests
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SESSION_PERMANENT=False,
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'staffing.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    
    #Load config
    if test_config is None:
        app.config.from_pyfile('config.py', silent=False)
    else:
        app.config.from_mapping(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    #DB, include migrate for manual use if Models are changed
    db.init_app(app)
    migrate = Migrate(app, db)

    #Can't import these until app is created
    from . import auth, dashboard, users, providers, customers, api

    #Blueprints
    app.register_blueprint(api.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(providers.bp)
    app.register_blueprint(customers.bp)

    app.add_url_rule('/', endpoint='index')
    
    return app