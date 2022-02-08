# Importing packages
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure database
db = SQL("sqlite:///tantalicious.db")

@app.route("/", methods=["GET"])
@login_required
def index():
    return render_template("index.html")       

@app.route("/alert", methods=["GET"])
def alert():
    return render_template("alert.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Ensure username is filled
        if not request.form.get("username"):
            flash("Please fill in your username!", "error")
            return redirect("/register")

        # Ensure username is unique
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) > 0:
            flash("Username already taken!", "error")
            return redirect("/register")
        
        # Ensure password is filled/confirmed
        if not request.form.get("password"):
            flash("Please fill in your password!", "error")
            return redirect("/register")
        elif not request.form.get("confirmation"):
            flash("Confirm your password please!", "error")
            return redirect("/register")
        elif request.form.get("password") != request.form.get("confirmation"):
            flash("Passwords do not match!", "error")
            return redirect("/register")

        new_user = request.form.get("username")
        new_hashpass = generate_password_hash(request.form.get("password"))

        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", new_user, new_hashpass)
        flash("Successfully registered!", "success")
        return redirect("/login")

    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Forget any user_id
        session.clear()
        
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username!", "error")
            return redirect("/login")

        # Ensure password Mustwas submitted
        elif not request.form.get("password"):
            flash("Must provide password!", "error")
            return redirect("/login")


        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username and/or password!", "error")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        return redirect("/")
    else:
        if session.get("user_id"):
            return redirect("/")
        else: 
            return render_template("login.html")

@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

# Index page
# Buy page
# Cart page