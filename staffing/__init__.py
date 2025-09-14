import os
from flask import Flask
from .models import db

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SESSION_PERMANENT=False,
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'staffing.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    
    
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
        #print("SECRET_KEY loaded:", app.config.get('SECRET_KEY'))
    else:
        app.config.from_mapping(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    from . import auth, dashboard
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)

    app.add_url_rule('/', endpoint='index')

    return app
