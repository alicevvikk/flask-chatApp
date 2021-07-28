from flask import Flask 

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.secret_key = 'gizli'
    db.init_app(app)

    from .views import bp
    app.register_blueprint(bp)


    return app