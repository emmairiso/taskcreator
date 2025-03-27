from flask import Flask, render_template, redirect, request
from storage.database import db
from models import task, user
from models.user import User
from models.task import Task
from models.user import create_user
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "supersecretkey"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
db.init_app(app)


def create_tables():
    db.create_all() 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)



@app.route("/") # This command "adds" a link to a new page that is coded in HTML.
def index(): # This is the page itself, the 
    return render_template("index.html") # This is how you link html files to the website.

@app.route("/signup", methods=["POST", "GET"])
def sign():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
            user.create_user(email=email, password=hashed_password)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            db.session.rollback()
            return f"There was an error: {e}"
            return render_template("signup.html")
 
    return render_template("signup.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        current_user = User.query.filter_by(email=email).first()

        if current_user and check_password_hash(current_user.password, password):
            login_user(current_user)
            return redirect("/dashboard")
        else:
            return "Login failed"
    return render_template("login.html")

@app.route("/dashboard", methods=["POST", "GET"])
def dashboard(): 
    return render_template("dashboard.html")

@app.route("/add_task", methods=["POST", "GET"])
def add_task():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        due_date = request.form.get("due_date")
        try:
            due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date() if due_date else None
            new_task = Task(title=title, description=description, user_id=current_user.id, due_date=due_date_obj)
            db.session.add(new_task)
            db.session.commit()
            return redirect("/dashboard")
        except Exception as e:
            db.session.rollback()
            return f"There was an error: {e}"
    return render_template("add_task.html")


if __name__ in "__main__":
    with app.app_context():
        create_tables()
    app.run(debug=True)