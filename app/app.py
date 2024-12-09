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
from pytz import timezone

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
            "CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password TEXT NOT NULL);"
        )
        db.execute(
            "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?);",
            ("ADMIN", generate_password_hash("CSC@2024@BDAY")),
        )
        db.execute("CREATE TABLE IF NOT EXISTS admin_email (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, email TEXT NOT NULL UNIQUE);")
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


@app.route("/index", methods=["GET", "POST"])
def names():
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
        return redirect(url_for("index"))
    else:
        return render_template("index.html")


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

@app.route("/delete_admin_email", methods=["POST"])
def delete_admin_email():
    username = request.form.get("username")
    email = request.form.get("email")
    
    if not username or not email:
        flash("Username and email are required!")
        return redirect(url_for("email"))

    try:
        connection = sqlite3.connect(db_birthday)
        db = connection.cursor()

        db.execute("SELECT username, email FROM admin_email WHERE username = ? AND email = ?", (username, email,))
        admin_email = db.fetchone()
        
        if admin_email:
            db.execute("DELETE FROM admin_email WHERE username = ? AND email = ?", (username, email,))
            flash("Admin email deleted successfully!")
            connection.commit()
            connection.close()
            return redirect(url_for("admin"))

        else:
            flash("Incorrect username or email!")
            return redirect(url_for("email"))

    except Exception as e:
        flash(f"Error deleting admin email: {e}")
    return redirect(url_for("admin"))

@app.route("/email", methods=["GET", "POST"])
def email():

    if not session.get("logged_in"):
        return redirect(url_for("login"))
    
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email").lower()

        try:
            connection = sqlite3.connect(db_birthday)
            db = connection.cursor()
            
            # Check if email already exists
            db.execute("SELECT email FROM admin_email WHERE email = ?", (email,))
            existing_email = db.fetchone()
        
            if existing_email:
                flash("Email already exists, use a different email❗")
                return render_template("email.html")  # Return if email already exists

            else:
                # Insert new record
                db.execute("INSERT INTO admin_email (username, email) VALUES (?, ?)", (username, email,))
                connection.commit()

        except sqlite3.Error as e:
            flash(f"An error occurred while processing your request: {str(e)}")
            return render_template("email.html")

        finally:
            connection.close()
        
        flash("User details recorded successfully!")
        return redirect(url_for("admin"))

    else:
        return render_template("email.html")


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
            today = datetime.now(timezone('Africa/Lagos')).date()
            birthday_count = 0 #Initialize birthday variable
            celebrants = []

            connection = sqlite3.connect(db_birthday)
            db = connection.cursor()

            # fetch all users
            db.execute(
                "SELECT name, part, phone_number, school_address, email, birthday FROM register"
            )
            all_users = db.fetchall()
            db.execute("SELECT username, email FROM admin_email")
            all_emails = db.fetchall()

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
                    message = (f"Wishing a joyful birthday to you, {user[0]}, our melody-making friend! Your beautiful voice and uplifting spirit bring so much joy to our rehearsals and performances. May this special day be filled with love, music, and all the things that bring smile to your face. Keep shining bright like the star you are!🌟 Enjoy every moment and have a melodious birthday!🎶\n🎈#HappyBirthday{user[0].replace(' ', '')}")
                    print(f"Sending birthday message to: {user[4]}")  # Debug statement
                    send_email_notification("Birthdays are special! 🎂", message, user[4])     
                    
            if birthday_count > 0:
                celebrant_names = ", ".join([user[0] for user in celebrants[:-1]]) + ", and " + celebrants[-1][0] if len(celebrants) > 1 else celebrants[0][0]  # Create a string of celebrants' names
                celebrant_info = "\n".join([f"Name: {user[0]}\nPart: {user[1].capitalize()}\nPhone: {user[2]}\nLocation: {user[3]}\n" for user in celebrants])

                for email in all_emails:
                    message = (f"Hello {email[0]}! \nToday is a special day, and we want to remind you to sing a happy birthday tune "
                        f"for {celebrant_names}! 🎉 \n\nCelebrants' Info:\n{celebrant_info}\n\nNever forget to reach out, "
                        "showing them how much you care and make their day shine! ✨")
                    print(f"Sending message to: {email[1]}")  # Debug statement
                    send_email_notification("Birthdays are special! 🎂", message, email[1])
    
            if birthday_count == 0:
                print("No birthdays found today.")  # Debug statement for no birthdays
            else:
                print(f"Total birthdays found today: {birthday_count}")  # Summary statement
    except Exception as e:
        print(f"An error occurred while checking birthdays: {e}")       

scheduler = BackgroundScheduler()
scheduler.configure(timezone=timezone('Africa/Lagos'))
scheduler.add_job(lambda: check_birthdays(), 'interval', days=1, start_date='2024-11-28 00:00:00', timezone=timezone('Africa/Lagos')) #check daily
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    app.run(debug=True, host="birthday.cscunn.ng", port=5005)
    