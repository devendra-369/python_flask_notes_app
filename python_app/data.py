from app import db, User, app
from werkzeug.security import generate_password_hash

with app.app_context():
    username = "deva"
    password = "1234"

    # Check if user already exists
    if not User.query.filter_by(username=username).first():
        hashed_pw = generate_password_hash(password)
        user = User(username=username, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        print("User created successfully")
    else:
        print("User already exists")
