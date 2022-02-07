# Importing packages
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure database
db = SQL("sqlite:///tantalicious.db")

@app.route("/", methods=["GET"])
def index():
        return render_template("login.html")   

@app.route("/register", methods=["GET"])
def register():
    if request.method == "POST":
        print("todo")
    else:
        return render_template("register.html")