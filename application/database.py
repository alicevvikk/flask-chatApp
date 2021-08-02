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

    def serialize(self):
        data = {
            'id':self.id,
            'name':self.name,
            'created_rooms':[room.id for room in self.created_rooms],
        }

        return data

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

    def serialize(self):
        data = {
            'id':self.id,
            'active':self.active,
            'protected':self.protected,
            'creator_id':self.creator_id,
            'name':self.name,
            'password':self.password,
            'max_users':self.max_users,
            'all_super':self.all_super,
            'users':[user.serialize() for user in self.users],
        }

        return data


    def set_hash(self):
        print(self.password)
        self.password = generate_password_hash(self.password)
        db.session.commit()

    def check_pass(self, password):
        print(password==self.password)
        return password==self.password
    

    def generate_link(self):
        self.link = f'ratvj{self.creator_id}lmfao{self.id}'
        self.active = True
        db.session.commit()
        return self.link



class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    roomPid = db.Column(db.Integer, db.ForeignKey('room.id'))
    content = db.Column(db.String(125))

    def serialize(self):
        data = {
            'id':self.id,
            'owner_id':self.owner_id,
            'date':self.serialize_date(),
            'room_id':self.roomPid,
            'content':self.content
        }

        return data
    
    def serialize_date(self):
        year = self.date.year
        month = self.date.month
        day = self.date.day

        hour = self.date.hour
        minutes = self.date.minute

        return f"{year}/{month}/{day} - {hour}.{minutes}"