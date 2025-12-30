from app import db, User, app

with app.app_context():
    user = User(username="deva", password="1234")
    db.session.add(user)
    db.session.commit()