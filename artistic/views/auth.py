from flask import Blueprint, redirect, render_template, request, url_for
from passlib.hash import sha256_crypt
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
)
from artistic.models.user import User
from artistic.db import db

auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home.main'))

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
            return redirect(url_for('home.main'))
    return render_template('home/login.html')

@auth_bp.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
