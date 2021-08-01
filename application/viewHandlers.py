from flask import session, redirect, render_template, g, url_for

from application.database import User, Room, members

from functools import wraps

from application import db

def get_room():
    
    room_id = session.get('room_id')
    if not room_id:
        return None
    
    room = Room.query.filter_by(id=room_id).first()

    return room

def get_room_id():
    return session.get('room_id')

def login_required(r):
    @wraps(r)
    def wrapper(*args, **kwargs):
        try:
             if session['username']:
                return r(*args, **kwargs)

        except:
            return redirect(url_for('views.index'))
    return wrapper

def if_logged(r):
    @wraps(r)
    def wrapper(*args, **kwargs):
        try:
            if session['username']:
                return redirect(url_for('views.main'))
        except:
            return r(*args, **kwargs) 
    return wrapper

def get_current_userId():
    try:
        return session['user_id']
    except:
        return None

def get_current_userObject():
    user_id = get_current_userId()

    if user_id:
        user = User.query.filter_by(id=user_id).first()
        return user
    return None


def get_room_byLink(link):
    all_rooms = Room.query.all()
    if all_rooms:
        for r in all_rooms:
            if r.link == link:
                error = None
                return r
    return None

def userInRoom(room):
    all_users = room.users

    current_userId = get_current_userId()

    for user in all_users:
        if user.id == current_userId:
            return True
    return False

def get_users():
    users = User.query.all()

    return [user.serialize() for user in users]

def get_rooms():
    rooms = Room.query.all()

    return [room.serialize() for room in rooms]


