from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_user, logout_user
from flask_mail import Mail, Message
from passlib.hash import sha256_crypt

from artistic.db import db
from artistic.models.user import User

auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()
mail = Mail()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('auth.login'))

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

def send_reset_email(user):
    token = user.get_reset_token()
    #token = 'Test Token'
    msg = Message('Password Reset Request',
                  sender='artistic-photos@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('auth.reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home.main'))

    if request.method == 'GET':
        return render_template('home/reset_password.html', title='Reset Password')

    user = User.query.filter_by(email=request.form['email']).first()
    if user:
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('auth.login'))
    return render_template('home/reset_password.html', title='Reset Password')

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home.main'))

    user = User.verify_reset_token(token)
    if user is None:
        flash('This is an invalid or expired token', 'warning')
        return redirect(url_for('auth.reset_request'))

    if request.method == 'GET':
        return render_template('home/reset_token.html', title='Reset Password')

    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        flash('Passwords don\'t match.', 'warning')
        return redirect(url_for('auth.reset_token', token=token))

    if password:
        hashed_password = sha256_crypt.hash(request.form['password'])
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been reset! You can now login.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('reset_token.html', title='Reset Password')



