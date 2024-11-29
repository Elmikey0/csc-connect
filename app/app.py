import os
import bcrypt
from flask import Flask, session, redirect, render_template, request, flash, url_for
from flask import current_app
from flask_session import Session
from flask_mail import Mail, Message
import sqlite3
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import time

db_birthday = "birthday.db"

# initialize the Flask application
app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# For managing email messaging
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = "cscunnchorale@gmail.com"
app.config["MAIL_PASSWORD"] = (
    "rqqy ynys dlwt bjpr"  # App password
)
mail = Mail(app)


def init_db():
    print("Initializing database...")
    try:
        connection = sqlite3.connect(db_birthday)
        db = connection.cursor()

        db.execute(
            "CREATE TABLE IF NOT EXISTS register (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, birthday DATE NOT NULL, part TEXT NOT NULL, phone_number TEXT NOT NULL, email TEXT NOT NULL UNIQUE, school_address TEXT NOT NULL);"
        )
        db.execute(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, password TEXT NOT NULL);"
        )
        db.execute(
            "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?);",
            ("ADMIN", generate_password_hash("CSC@2024@BDAY")),
        )

        connection.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        connection.close()


init_db()


# for managine cache
@app.after_request
def after_request(response):
    response.headers["cache-control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/index", methods=["POST"])
def names():

    name = request.form.get("name")
    birthday = request.form.get("birthday")
    part = request.form.get("part")
    number = request.form.get("phone_number")
    email = request.form.get("email").lower()
    location = request.form.get("school_address")

    connection = sqlite3.connect(db_birthday)
    db = connection.cursor()
    
    db.execute("SELECT email FROM register WHERE email = ?", (email,))
    existing_email = db.fetchone()
    
    if existing_email:
        flash("Email already exist, use a different email❗")

    else:
        db.execute(
            "INSERT INTO register (name, birthday, part, phone_number, email, school_address) VALUES (?, ?, ?, ?, ?, ?)",
            (name, birthday, part, number, email, location),
        )

    connection.commit()
    connection.close()
    flash("User details recorded successfully!")
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username").upper()
        password = request.form.get("password")

        connection = sqlite3.connect(db_birthday)
        db = connection.cursor()

        db.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = db.fetchone()

        connection.close()

        if user is None or not check_password_hash(user[2], password):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        session["logged_in"] = True
        session["user_id"] = user[0]
        return redirect(url_for("admin"))

    else:
        return render_template("login.html")


@app.route("/flash")
def flash_messages():
    flash("This is a flash message")
    return redirect(url_for("index"))


@app.route("/admin", methods=["GET", "POST"])
def admin():

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form.get("name")
        birthday = request.form.get("birthday")
        part = request.form.get("part")
        number = request.form.get("phone_number")
        email = request.form.get("email").lower()
        location = request.form.get("school_address")

        connection = sqlite3.connect(db_birthday)
        db = connection.cursor()

        db.execute("SELECT email FROM register WHERE email = ?", (email,))
        existing_email = db.fetchone()
    
        if existing_email:
            flash("Email already exist, use a different email❗")

        else:
            db.execute(
                "INSERT INTO register (name, birthday, part, phone_number, email, school_address) VALUES (?, ?, ?, ?, ?, ?)",
                (name, birthday, part, number, email, location),
            )

        connection.commit()
        connection.close()
        flash("User details recorded successfully!")
        return redirect(url_for("admin"))

    else:
        return render_template("admin.html")


@app.route("/logout")
def logout():

    session.pop("logged_in", None)
    session.pop("user_id", None)
    return redirect(url_for("login"))


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if request.method == "POST":
        # Step 2: Process the form submission
        email = request.form.get("email").lower()  # Get the email from the form
        name = request.form.get("name")
        birthday = request.form.get("birthday")
        part = request.form.get("part")
        phone_number = request.form.get("phone_number")
        school_address = request.form.get("school_address")

        # Step 2: Update user information in the database
        connection = sqlite3.connect(db_birthday)
        db = connection.cursor()

        db.execute(
            "UPDATE register SET name = ?, birthday = ?, part = ?, phone_number = ?, school_address = ? WHERE email = ?",
            (name, birthday, part, phone_number, school_address, email)
        )

        connection.commit()
        connection.close()

        flash("User details updated successfully!")
        return redirect(url_for("admin"))

    else:
        # Step 1: Show the edit form with user data if email exists
        email = request.args.get("email")  # Get the email from query parameter

        if not email:
            flash("Please enter an email address to start editing.")
            return render_template("edit.html", user=None)

        connection = sqlite3.connect(db_birthday)
        db = connection.cursor()

        db.execute("SELECT name, birthday, part, phone_number, email, school_address FROM register WHERE email = ?", (email,))
        user_data = db.fetchone()

        connection.close()

        if user_data:
            # Render the form with the existing user data
            return render_template("edit.html", user=user_data, email=email)
        else:
            flash("No user found with that email.")
            return render_template("edit.html", user=None)
        
@app.route("/delete")
def delete():
    email = request.args.get("email")
    
    connection = sqlite3.connect(db_birthday)
    db = connection.cursor()

    db.execute("DELETE FROM register WHERE email = ?", (email,))
    
    connection.commit()
    connection.close()

    flash("User details deleted successfully!")
    return redirect(url_for("admin"))


def send_email_notification(subject, message, recipient_email):
    try:
        app = current_app._get_current_object()
        with app.app_context():
            print(f"Sending email to: {recipient_email}")
            msg = Message(
                subject, sender="cscunnchorale@gmail.com", recipients=[recipient_email]
            )
            msg.body = message
            mail.send(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")
    
def check_birthdays():
    try:
        # Push an application context explicitly
        with app.app_context():  # Ensure we're inside the application context
            today = datetime.now().date()
            birthday_count = 0 #Initialize birthday variable
            celebrants = []

            connection = sqlite3.connect(db_birthday)
            db = connection.cursor()

            # fetch all users
            db.execute(
                "SELECT name, part, phone_number, school_address, email, birthday FROM register"
            )
            all_users = db.fetchall()

            # Loop through each user and send birthday email if it's their birthday
            for user in all_users:
                print(
                    f"Checking user: {user[0]} with birthday: {user[5]}"
                )  # Debug statement
                # Check if today is their birthday
                if user[5] and datetime.strptime(user[5], "%Y-%m-%d").strftime(
                    "%m-%d"
                ) == today.strftime(
                    "%m-%d"
                ):  # user[5] is the birthday
                    celebrants.append(user)
                    birthday_count +=1 #update birthday variable          
                    message = f"Wishing a joyful birthday to you, {user[0]}, our melody-making friend!"
                    print(f"Sending birthday message to: {user[4]}")  # Debug statement
                    send_email_notification("Birthdays are special! 🎂", message, user[4])     
                    time.sleep(1)
                    
            if birthday_count > 0:
                celebrant_names = ", ".join([user[0] for user in celebrants[:-1]]) + ", and " + celebrants[-1][0] if len(celebrants) > 1 else celebrants[0][0]  # Create a string of celebrants' names
                celebrant_info = "\n".join([f"Name: {user[0]}\nPart: {user[1].capitalize()}\nPhone: {user[2]}\nLocation: {user[3]}\n" for user in celebrants])

                for user in all_users:
                    if user not in celebrants:
                        message = (f"Hello {user[0]}! \nToday is a special day, and we want to remind you to sing a happy birthday tune "
                            f"for {celebrant_names}! 🎉 \n\nCelebrants' Info:\n{celebrant_info}\n\nNever forget to reach out, "
                            "showing them how much you care and make their day shine! ✨")
                        print(f"Sending message to: {user[4]}")  # Debug statement
                        send_email_notification("Birthdays are special! 🎂", message, user[4])
                        time.sleep(1)
                    else:
                        print("No birthdays today.")
    
            if birthday_count == 0:
                print("No birthdays found today.")  # Debug statement for no birthdays
            else:
                print(f"Total birthdays found today: {birthday_count}")  # Summary statement
    except Exception as e:
        print(f"An error occurred while checking birthdays: {e}")       

scheduler = BackgroundScheduler()
scheduler.add_job(lambda: check_birthdays(), 'interval', days=1, start_date='2024-11-28 06:00:00') #check daily
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    app.run(debug=True)
    