from flask import Flask, render_template, redirect, url_for, session, Blueprint, request, g
from sqlalchemy import delete
import json
from werkzeug.wrappers import PlainRequest

from application import db, socketio
from application.database import Message, User, Room, members

from functools import wraps

from application.viewHandlers import (get_room, get_current_userId, get_current_userObject, if_logged, login_required, userInRoom
                                     ,userInRoom, get_rooms, get_room_byLink)

from flask_socketio import SocketIO, send, emit

bp = Blueprint('views', __name__)



@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(id=user_id).first()


@bp.route('/', methods=('POST', 'GET',))
@if_logged
def index():
    if request.method == 'POST':
        username = request.form['username']
        new_user = User(name=username)
        
        db.session.add(new_user)
        db.session.commit()
        #session['user_object'] = new_user
        session['username'] = username
        session['user_id'] = new_user.id

        return redirect('main')

    return render_template('index.html')

@bp.route('/main')
@login_required
def main():

    data = {
        'room':'lala'
    }
    return render_template('main.html', data=data)


@bp.route('/create-room', methods=('POST', 'GET'))
@login_required
def create_room():
    if request.method == 'POST':
        password = None
        
        name = request.form['username']
        try:
         if request.form['isProtected'] == "on":
            is_protected = True 
            password = request.form['password']      
        except:
            is_protected = False
            password = None            
        
        try:
            if request.form['all_super'] == "on":
                all_super = True
        except:
            all_super= False
        

        max_users = request.form['max_users']

        current_userId = get_current_userId()
        
        if is_protected:
            print('protected')
            new_room = Room(name=name, 
                        password=password, all_super=all_super, max_users=max_users, creator_id=current_userId, protected=True)
            #new_room.set_hash()
        else:
            print('not protected')
            new_room = Room(name=name, 
                        all_super=all_super, max_users=max_users, creator_id=current_userId)

        
        db.session.add(new_room)
        db.session.commit()
        
        current_userObj = get_current_userObject()
        room_id = new_room.id

        new_room.users.append(current_userObj)

        db.session.commit()
        db.session.query(members).filter(
        members.c.user_id==current_userId, members.c.room_id==room_id).update((current_userId,room_id,True))
        db.session.commit()
        
        session['room_id'] = room_id
        new_room.generate_link()
        

        return redirect( url_for('views.rooms', link=new_room.link))
        
        
    return render_template('createRoom.html')




@bp.route('/join-room', methods=('GET', 'POST'))
@login_required
def join_room():
    if request.method == 'POST':
        error = None
        room = None
        try:
            password = request.form['password']
        except:
            password = None

        link = request.form['link']

        room = get_room_byLink(link)
        if not room:
            error = 'This link does not belong to any room'
            return redirect(url_for('views.error', error_msg= error))
        else:

            check_user_in = userInRoom(room)
            if not check_user_in:
                is_protected = room.protected
                
                if is_protected:
                    if password:
                        print(room.check_pass(password), 'here')
                        if room.check_pass(password):
                            print('right pass')
                            current_userObj = get_current_userObject()
                            room.users.append(current_userObj)
                            db.session.commit()
                            
                            db.session.query(members).filter(
                            members.c.user_id==room.creator_id, members.c.room_id==room.id).update((room.creator_id, room.id, room.all_super))
                            db.session.commit()

                            session['room_id'] = room.id
                        else:
                            
                            error = 'Wrong password.'
                            return redirect(url_for('views.error', error_msg= error))


                    else:
                        
                        error = 'This room is protected with a password.'
                        return redirect(url_for('views.error', error_msg= error))
                else:

                    current_userObj = get_current_userObject()
                    room.users.append(current_userObj)
                    db.session.commit()
                    
                    db.session.query(members).filter(
                    members.c.user_id==room.creator_id, members.c.room_id==room.id).update((room.creator_id, room.id, room.all_super))
                    db.session.commit()

                    session['room_id'] = room.id

            return redirect(url_for('views.rooms', link=link))

        
    return render_template('joinRoom.html')


@bp.route('/error/<error_msg>')
def error(error_msg):
    return render_template('error.html', error_msg=error_msg)

@bp.route('/room/<link>')
@login_required
def rooms(link):
    error = None
    room = None

    room = get_room_byLink(link)

    if not room:
        error = 'This link does not belong to any room'
        return redirect(url_for('views.error', error_msg=error))
    
    check_user_in = userInRoom(room)
    if not check_user_in:
        error = 'You can not join this room unless a super user gives you the join link.'
        return redirect(url_for('views.error', error_msg= error))

    messages = Message.query.filter_by(roomPid=room.id).all()
    print(messages)
    data = {
        'room':room,
        'messages':messages
    }
    return render_template('room.html', data=data)
    

@bp.route('/leave-room', methods=('POST',))
def leave_room():
    if request.method == 'POST':
        print('leave 1')
        try:
            user_id = request.get_json()['user_id']
            room_id = int(request.get_json()['room_id'])
        except:
            user_id = None
            room_id = None
        print(user_id, room_id)
        db.session.query(members).filter(members.c.user_id==user_id, members.c.room_id==room_id).delete()
        db.session.commit()

        session.pop('room_id')
        user =get_current_userObject()
        user = user.serialize()
        socketio.emit('leave room', user)
        
    
    return redirect(url_for('views.main'))


@bp.route('/get_user')
def get_user():

    user = get_current_userObject()
    user = user.serialize()
    data = {
        'user':user
    }
    return data or {}


@bp.route('/get-active-room')
def get_active_room():
    room = get_room()
    if room:
        room = room.serialize()

    return room or {}

