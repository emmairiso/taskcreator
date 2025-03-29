from flask import Flask, render_template, redirect, request, flash
from storage.database import db
from models import task, user
from models.user import User
from models.task import Task
from models.user import create_user
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta, time
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "supersecretkey"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
db.init_app(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Use your email provider's SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'testerer261@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'hita qxjl gcif emxp '  # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = 'testerer261@gmail.com'

mail = Mail(app)

def create_tables():
    db.create_all() 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def send_reminder_email(user_email, task_title, due_date):
    with app.app_context():
        try:
            msg = Message(
                subject="Task Reminder",
                recipients=[user_email],
                body=f"Reminder: Your task '{task_title}' is due on {due_date}. Please complete it on time."
            )
            mail.send(msg)
            print(f"Reminder email sent to {user_email} for task '{task_title}'.")
        except Exception as e:
            print(f"Failed to send email: {e}")

@app.route("/") # This command "adds" a link to a new page that is coded in HTML.
def index(): # This is the page itself, the 
    return render_template("index.html") # This is how you link html files to the website.

@app.route("/signup", methods=["POST", "GET"])
def sign():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash("User already exists. Log in.", "warning")
                return redirect("/")
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
        if request.method == "POST":
            title = request.form.get("title")
            description = request.form.get("description")
            first_date = request.form.get("due_date")
            try:
                due_date_obj = datetime.strptime(first_date, "%Y-%m-%d").date() if first_date else None
                new_task = Task(title=title, description=description, user_id=current_user.id, due_date=due_date_obj)
                db.session.add(new_task)
                db.session.commit()
                schedule_reminders_for_task(new_task)
                return redirect("/dashboard")
            except Exception as e:
                db.session.rollback()
                return f"There was an error: {e}"
            
            
        user_tasks = Task.query.filter_by(user_id=current_user.id).all()
        # Mark overdue tasks as completed
        for task in user_tasks:
            if task.is_overdue() and not task.completed:
                task.completed = True
                db.session.commit()
        return render_template("dashboard.html", tasks=user_tasks)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/add_task", methods=["POST", "GET"])
def add_task():
    return render_template("add_task.html")

@app.route("/delete_task", methods=["POST", "GET"])
def delete_task():
    if request.method == "POST":
        # Handle the task deletion
        task_id = request.form.get("task_id")
        try:
            # Query the task by ID and ensure it belongs to the current user
            task_to_delete = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
            if task_to_delete:
                 # Remove scheduled jobs for the task
                days_until_due = (task_to_delete.due_date - date.today()).days
                for day in range(days_until_due + 1):
                    job_id = f"reminder_{task_to_delete.id}_{day}"
                    scheduler.remove_job(job_id)  # Remove the job from the scheduler
                db.session.delete(task_to_delete)  # Delete the task
                db.session.commit()
                return redirect("/dashboard")  # Redirect back to the dashboard
            else:
                return "Task not found or you do not have permission to delete it.", 404
        except Exception as e:
            db.session.rollback()
            return f"There was an error deleting the task: {e}"
    else:
        # Handle the GET request: Fetch tasks for the current user
        user_tasks = Task.query.filter_by(user_id=current_user.id).all()
        return render_template("delete_task.html", tasks=user_tasks)
    
@app.route("/edit_task/<int:task_id>", methods=["POST", "GET"])
def edit_task(task_id):
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            return "Task not found or you do not have permission to edit it."
        
        if request.method == "POST":
            task.title = request.form.get("title")
            task.description = request.form.get("description")
            due_date_str = request.form.get("due_date")
            if due_date_str:
                task.due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            db.session.commit()
            return redirect("/dashboard")
        return render_template("edit_task.html", task=task)
    
scheduler = BackgroundScheduler()

def schedule_task_reminders():
    # Query all tasks that are not completed and are due in the future
    tasks = Task.query.filter(Task.completed == False, Task.due_date >= date.today()).all()
    for task in tasks:
        # Calculate the number of days until the due date
        days_until_due = (task.due_date - date.today()).days

        # Schedule a daily email reminder until the due date
        for day in range(days_until_due + 1):
            reminder_time = time(22, 34)
            reminder_date = datetime.combine(date.today() + timedelta(days=day), reminder_time)
            scheduler.add_job(
                func=send_reminder_email,
                args=[task.user.email, task.title, task.due_date],
                trigger="date",
                run_date=reminder_date,
                id=f"reminder_{task.id}_{day}",
                replace_existing=True
            )
def schedule_reminders_for_task(task):
    # Calculate the number of days until the due date
    days_until_due = (task.due_date - date.today()).days

    # Schedule a daily email reminder until the due date
    for day in range(days_until_due + 1):
        reminder_time = time(22, 34)  # Set the time for the reminder (e.g., 10:07 PM)
        reminder_date = datetime.combine(date.today() + timedelta(days=day), reminder_time)
        scheduler.add_job(
            func=send_reminder_email,
            args=[task.user.email, task.title, task.due_date],
            trigger="date",
            run_date=reminder_date,
            id=f"reminder_{task.id}_{day}",
            replace_existing=True
        )

# Start the scheduler
scheduler.start()

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


if __name__ == "__main__":
    with app.app_context():
        create_tables()
        schedule_task_reminders()
    app.run(debug=True)