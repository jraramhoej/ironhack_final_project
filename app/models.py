from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))

class Slack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reply_users = db.Column(db.String(150))
    user = db.Column(db.String(150))
    text = db.Column(db.String(150))
    ts = db.Column(db.DateTime)
