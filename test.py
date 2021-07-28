from application import db, create_app
from application.database import members, User, Room

from sqlalchemy import insert

app = create_app()

with app.app_context():

    '''
    db.create_all()

    user1 = User(name= 'alig')
    db.session.add(user1)
    db.session.commit()

    user2 = User(name= 'hacer')
    db.session.add(user2)
    db.session.commit()

    room1 = Room(name= '@alig@')
    db.session.add(room1)
    db.session.commit()

    room2 = Room(name= '@hacer@')
    db.session.add(room2)
    db.session.commit()

    room1.users.append(user1)
    room1.users.append(user2)
    db.session.commit()
    '''
    user1 = User(name= 'alig')
    user2 = User(name= 'hacer')

    room1 = Room(name= '@alig@')
    

    stmt = (
    insert(members).
    values(user_id=user1.id, room_id=room1.id, is_super=True)
)
    db.session.query(members).filter(members.c.user_id==16).update((1,2,True))
    print(type(db.session.query(members)))
    db.session.commit()
    #db.session.query(members).insert

    #member = members(user1, room1, is_super=True)
    #db.session.query(members)

    









