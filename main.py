from application import create_app, db
from application.database import User, Room, Message, members

from application.views import get_current_userObject
from flask_socketio import SocketIO, send, emit
from flask import session



app = create_app()
socketio = SocketIO(app, cors_allowed_origins="*")

with app.app_context():
    db.create_all()

@socketio.on('new msg')
def new_message(data):
    current_user = get_current_userObject()
    print(current_user)

@socketio.on('my event')
def my_event(data):
    print('User connected')

    #emit('new connection',)




if __name__=="__main__":
    socketio.run(app)

