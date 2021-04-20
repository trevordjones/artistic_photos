__version__ = '0.1.0'

import binascii
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_migrate import Migrate
import os
from pathlib import Path

from artistic.db import db
from artistic.views import auth_bp, home_bp
from artistic.views.auth import login_manager

load_dotenv()
FLASK_ENV = os.getenv('FLASK_ENV')
PG_URL = os.getenv('PGURL')
ROOT = Path(__file__).parent


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True, static_url_path='/artistic/static', static_folder='static')
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        )

    app.config['DEBUG'] = FLASK_ENV != 'production'
    app.config['SQLALCHEMY_DATABASE_URI'] = PG_URL

    db.init_app(app)

    login_manager.init_app(app)

    migrate = Migrate(app, db) # this variable needed for Flask-Migrate
    from artistic.models import Image, User

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)

    return app
