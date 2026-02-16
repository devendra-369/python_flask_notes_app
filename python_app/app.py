from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

# ================= DATABASE CONFIG =================
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ================= MODELS =================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

# ================= LOGIN DECORATORS =================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["logged_in"] = True
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("home"))
        else:
            flash("Invalid Credentials")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect(url_for("register"))

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful. Please log in.")
        return redirect(url_for("login"))
    return render_template("register.html")

# ================= ROUTES =================
@app.route("/")
@login_required
def home():
    notes = Notes.query.filter_by(user_id=session["user_id"]).all()
    return render_template("index.html", notes=notes)

@app.route("/add", methods=["POST"])
@login_required
def add_note():
    note = request.form.get("note")
    if note:
        new_note = Notes(content=note, user_id=session["user_id"])
        db.session.add(new_note)
        db.session.commit()
    return redirect(url_for("home"))

@app.route("/delete/<int:id>")
@login_required
def delete_note(id):
    note = Notes.query.get_or_404(id)
    if note.user_id == session["user_id"]:
        db.session.delete(note)
        db.session.commit()
    return redirect(url_for("home"))

@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_note(id):
    note = Notes.query.get_or_404(id)
    if note.user_id != session["user_id"]:
        flash("You cannot edit someone else's note")
        return redirect(url_for("home"))

    if request.method == "POST":
        new_content = request.form.get("note")
        if new_content:
            note.content = new_content
            db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", note=note)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)