from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from artistic import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128))
