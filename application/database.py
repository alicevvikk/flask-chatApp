from datetime import datetime
from flask import Flask
from werkzeug.security import generate_password_hash, check_password_hash

from . import db

members = db.Table(
    'mems',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('room_id', db.Integer, db.ForeignKey('room.id'), primary_key=True),
    db.Column('is_super', db.Boolean, default=False)

)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(12))
    created_rooms = db.relationship('Room', cascade='all,delete', backref='creator', lazy=True)
    messages = db.relationship('Message', cascade='all,delete', backref='owner', lazy=True)

class Room(db.Model):
    active = db.Column(db.Boolean, default=False)
    protected = db.Column(db.Boolean, default= False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable= False)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(12))
    password = db.Column(db.String(), nullable=True)
    max_users = db.Column(db.Integer, default=4)
    all_super = db.Column(db.Boolean, default= False)
    users = db.relationship('User' ,secondary=members,
    backref=db.backref('rooms', lazy='dynamic'))
    link = db.Column(db.String(70))
    messages = db.relationship('Message', cascade='all,delete', backref='room', lazy=True)


    def set_hash(self):
        self.password = generate_password_hash(self.password)

    def check_pass(self, password):
        return check_password_hash(password, self.password)

    def generate_link(self):
        self.link = f'rooms-{self.creator_id}-{self.id}'
        self.active = True
        return self.link


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    roomPid = db.Column(db.Integer, db.ForeignKey('room.id'))
    content = db.Column(db.String(125))
