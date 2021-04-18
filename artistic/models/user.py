from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt

from artistic.models.base import Base, db


class User(Base):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128))
    password = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)


    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False

    def create_new_user(self, email, password):
        user = User.query.filter_by(email=email).first()
        if user:
            return f'{email} already exists!'

        hashed_password = sha256_crypt.hash(password)
        self.email = email
        self.password = hashed_password
        print(self)
        db.session.add(self)
        db.session.commit()
        return f'User {email} created'
