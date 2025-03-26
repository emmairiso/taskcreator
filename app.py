from flask import Flask, render_template, redirect, request
from storage.database import db
from models import task, user

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


def create_tables():
    db.create_all() 



@app.route("/") # This command "adds" a link to a new page that is coded in HTML.
def index(): # This is the page itself, the 
    return render_template("index.html") # This is how you link html files to the website.

@app.route("/signup")
def sign():
    return render_template("signup.html")

@app.route("/login")
def login():
    return render_template("login.html")

if __name__ in "__main__":
    with app.app_context():
        create_tables()
    app.run(debug=True)