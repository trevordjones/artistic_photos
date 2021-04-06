__version__ = '0.1.0'

from dotenv import load_dotenv
from flask import Flask, render_template, redirect, request, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import os

load_dotenv()
FLASK_ENV = os.getenv('FLASK_ENV')
PG_URL = os.getenv('PGURL')
APPLICATION_PAGE = 'application.html'

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
    from artistic.models import User, Image

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
    @app.route('/', methods=['GET', 'POST'])
    def main():
        if request.method == 'GET':
            return render_template(APPLICATION_PAGE, page='home/index')
        else:
            try:
                for key in request.files:
                    image = Image.upload_to_gcp(request.files[key], key)
                    with app.app_context():
                        image.save()
            except Exception as e:
                print(e)

            return redirect(url_for('main'))

    return app
