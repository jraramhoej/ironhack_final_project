from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import json
from sqlalchemy.ext.hybrid import hybrid_property

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    slack_user_id = db.Column(db.String(150), unique=True)

class Slack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_msg_id = db.Column(db.String(150), unique=True)
    user_id = db.Column(db.String(150))
    reply_users = db.Column(db.String(150))
    user = db.Column(db.String(150))
    text = db.Column(db.String(150))
    ts = db.Column(db.DateTime)
