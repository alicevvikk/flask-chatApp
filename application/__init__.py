from flask import Flask 

from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, send, emit

db = SQLAlchemy()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.secret_key = 'gizli'
    db.init_app(app)
    socketio.init_app(app)

    from .views import bp
    app.register_blueprint(bp)


    return app