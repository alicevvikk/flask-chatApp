from application import create_app, db, socketio
from application.database import User, Room, Message, members

from application.viewHandlers import *
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask import session, g

from pathlib import Path



app = create_app()
#socketio = SocketIO(app, cors_allowed_origins="*")

with app.app_context():


    p = Path("/Users/azc/Desktop/chat/application/database.db")
    if not p.exists():
        db.create_all()


@socketio.on('new connection')
def new_connection(data):
    print('new connection socket')
    user_id = data['data']['user']['id']
    user = User.query.filter_by(id= user_id).first()
    user_serialized = user.serialize()

    room = get_room()
    join_room(str(room.id))
    
    emit('new connection', user_serialized, to=str(room.id))


@socketio.on('leave room')
def leave_room(data):
    print('in leave room')
    user_id = data['user_id']
    user = User.query.filter_by(id= user_id).first()

    user = user.serialize()

    session.pop('room_id')
    room = get_room()
    leave_room(str(room.id))


    emit('leave room', user, to=str(room.id))

@socketio.on('new message')
def new_message(data):
    creator_id = get_current_userId()
    creator_name = get_current_userObject().name
    room_id = get_room_id()
    content = data['newMsg']

    new_message = Message(owner_id=creator_id, roomPid=room_id, content=content)
    db.session.add(new_message)
    db.session.commit()

    msg = new_message.serialize()
    print(msg)
    data = {
        'msg':msg,
        'creator_name':creator_name
    }

    emit('new message', data, to=str(room_id))
 
if __name__=="__main__":
    socketio.run(app)

