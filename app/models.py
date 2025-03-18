from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import secrets

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __bind_key__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    access_level = db.Column(db.String(), nullable=False)