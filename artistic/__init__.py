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
from passlib.hash import sha256_crypt
from pathlib import Path
from artistic.db import db

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

    login_manager = LoginManager()
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

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect(url_for('login'))

    @app.route('/', methods=['GET', 'POST'])
    @login_required
    def main():
        import subprocess

        from artistic.kaggle_script import create_kaggle_script

        if request.method == 'GET':
            return render_template('home/index.html')
        else:
            image_name = binascii.b2a_hex(os.urandom(5)).decode('utf-8')
            names = {'content': '', 'style': ''}
            try:
                for key in request.files:
                    image = Image.upload_to_gcp(request.files[key], key, image_name)
                    names[key] = image.source_name
                    with app.app_context():
                        image.save()
                create_kaggle_script(names['content'], names['style'], 'random')
                subprocess.run([f'kaggle kernels push -p {ROOT.joinpath("temp")}/'], shell=True)
                os.remove(ROOT.joinpath('temp/nst.py'), missing_ok=True)
                os.remove(ROOT.joinpath('temp/kernel-metadata.json'), missing_ok=True)
            except Exception as e:
                print(e)

            return redirect(url_for('main'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('main'))

        if request.method == 'GET':
            return render_template('home/login.html')

        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            password = user.password
            if sha256_crypt.verify(request.form['password'], user.password):
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                return redirect(url_for('main'))
        return render_template('home/login.html')

    @app.route('/logout', methods=['POST'])
    def logout():
        logout_user()
        return redirect(url_for('login'))


    return app
