__version__ = '0.1.0'

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import os

load_dotenv()
FLASK_ENV = os.getenv('FLASK_ENV')
PG_URL = os.getenv('PGURL')

db = SQLAlchemy()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        )

    app.config['DEBUG'] = FLASK_ENV != 'production'
    app.config['SQLALCHEMY_DATABASE_URI'] = PG_URL

    db.init_app(app)
    migrate = Migrate(app, db) # this variable needed for Flask-Migrate
    from artistic.models import User

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

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app
