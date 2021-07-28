from flask import Flask, render_template, redirect, url_for, session, Blueprint, request, g

from application import db
from application.database import User, Room, members

from functools import wraps

bp = Blueprint('views', __name__)

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(id=user_id).first()

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
        name = request.form['username']
        try:
            password = request.form['password']
        except:
            pass

        try:
            if request.form['all_super'] == "on":
                all_super = True
        except:
            all_super = False
        
        try:
            if request.form['isProtected'] == "on":
                is_protected = True
        except:
            is_protected = False


        max_users = request.form['max_users']

        current_userId = get_current_userId()

        if is_protected:
            new_room = Room(name=name, 
                        password=password, all_super=all_super, max_users=max_users, creator_id=current_userId, protected=True)
        else:
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

        return redirect(f"http://127.0.0.1:5000/room/{current_userId}/{room_id}", code=302)
        
        
    return render_template('createRoom.html')

@bp.route('/join-room', methods=('GET','POST'))
@login_required
def join_room():

    if request.method == 'POST':

        password = None
        creator = None
        room = None
        error = None
        link = request.form['link']

        try:
            password = request.form['password']
        except:
            pass

        link = link.split('-')
        creator_id = int(link[1])
        room_id = int(link[2])

        current_userObj = get_current_userObject()
        try:
            creator = User.query.filter_by(id=creator_id).first()
            room = Room.query.filter_by(id=room_id).first()

        except:
            creator = None
            room = None
        
        if creator is None or room is None:
            error = 'This link does not belong to any room.'


        if error is None:
            
            room.users.append(current_userObj)
            db.session.commit()
            
            db.session.query(members).filter(
            members.c.user_id==creator_id, members.c.room_id==room_id).update((creator_id, room_id, room.all_super))
            db.session.commit()

            return redirect(f"http://127.0.0.1:5000/room/{creator_id}/{room_id}")

        return redirect(url_for('views.error', error_msg=error))

    return render_template('joinRoom.html')

@bp.route('/error/<error_msg>')
def error(error_msg):
    return render_template('error.html', error_msg=error_msg)


@bp.route('/room/<int:creator_id>/<int:room_id>')
@login_required
def rooms(creator_id, room_id):
    try:
        creator = User.query.filter_by(id=creator_id).first()
        room = Room.query.filter_by(id=room_id).first()
    except:
        creator = None
        room = None
    error = None

    if creator is None or room is None:
        error = "This link doesn't belong to any room."
        return render_template('error.html', error_msg=error)
    
    current_userObj = get_current_userObject()
    current_userId = get_current_userId()

    room_mems = room.users

    error = "You are not registered to this room. Get a link from a super user and click the join button."
    for user in room_mems:
        if user.id == current_userId:
            error= None

    data = {
        'room':'lala'
    }
    print(room, creator,current_userObj,current_userId)
    
    if error:
        return render_template('error.html', error_msg=error)
    
    error= 'lala'
    return render_template('room.html', error_msg=error)

@bp.route('/leave-room/<int:creator_id>/<int:room_id>')
def leave_room(creator_id, room_id):
    
    print(db.session.query(members).filter(
        members.c.user_id==creator_id, members.c.room_id==room_id
    ))
