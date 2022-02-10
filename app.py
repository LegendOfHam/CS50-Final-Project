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

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        id = session["user_id"]
        stock = request.form.get("stock")
        try:
            quantity = int(request.form.get("quantity"))
        except:
            flash("Please fill in an integer for quantity!", "error")
            return redirect("/")

        # Get necessary values from databases
        sold = db.execute("SELECT sold FROM stocks WHERE product = ?", stock)[0]["sold"]
        instock = db.execute("SELECT instock FROM stocks WHERE product = ?", stock)[0]["instock"]
        
        # Testing if they are buying more than we currently have
        if quantity > instock:
            flash(f"As we currently only have {instock} of {stock} left in-store, there might be delivery delays.", "error")
        
        # Update databases
        rows = db.execute("SELECT quantity FROM cart WHERE product = ?", stock)
        if len(rows) == 0:
            db.execute("INSERT INTO cart (user_id, product, quantity) VALUES (?, ?, ?)", id, stock, quantity)
        else:
            initial_quantity = rows[0]["quantity"]
            db.execute("UPDATE cart SET quantity = ? WHERE product = ?", initial_quantity + quantity, stock)
        
        flash("Successfully added to cart!", "success")
        return redirect("/")
    else:
        stocks = db.execute("SELECT product FROM stocks")
        return render_template("index.html", stocks=stocks)       

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
        username = rows[0]["username"]
        
        flash(f"Welcome, {username}!","success")
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

@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():
    if request.method == "POST":
        # Implementing a delete mechanism
        delete = request.form.get("unwanted")
        id = session["user_id"]
        db.execute("DELETE FROM cart WHERE user_id = ? AND product = ?", id, delete)
        flash("Successfully deleted!", "success")
        return redirect("/cart")
    else:
        id = session["user_id"]
        cart = []
        total = 0
        orders = db.execute("SELECT * FROM cart WHERE user_id = ?", id)
        for i in range(len(orders)):
            temp = {} 
            temp["product"] = db.execute("SELECT product FROM cart WHERE user_id = ?", id)[i]["product"]
            temp["quantity"] = db.execute("SELECT quantity FROM cart where product = ? AND user_id = ?", temp["product"], id)[0]["quantity"]
            temp["uprice"] = db.execute("SELECT price FROM stocks WHERE product = ?", temp["product"])[0]["price"]
            temp["tprice"] = round(temp["quantity"] * temp["uprice"], 2)
            cart.append(temp)

        for j in range(len(orders)):
            total += cart[j]["tprice"]

        return render_template("cart.html", cart=cart, total=total)


@app.route("/purchases", methods=["GET", "POST"])
@login_required
def purchases():
    if request.method == "POST":
        id = session["user_id"]
        stock = db.execute("SELECT product, quantity FROM cart WHERE user_id = ?", id)
        for i in range(len(stock)):
            # Update orders db
            db.execute("INSERT INTO orders (user_id, product, quantity) VALUES (?, ?, ?)", id, stock[i]["product"], stock[i]["quantity"])
            
            # Update stocks db
            og_sold = db.execute("SELECT sold FROM stocks WHERE product = ?", stock[i]["product"])[0]["sold"]
            og_instock = db.execute("SELECT instock FROM stocks WHERE product = ?", stock[i]["product"])[0]["instock"]
            db.execute("UPDATE stocks SET sold = ?, instock = ? WHERE product = ?", og_sold + stock[i]["quantity"], og_instock - stock[i]["quantity"], stock[i]["product"])
        
            # Empty cart db
            db.execute("DELETE FROM cart") 

        flash("Successful purchase!", "success")
        return redirect("/purchases")
    else:
        id = session["user_id"]
        purchases = []
        total = 0
        orders = db.execute("SELECT * FROM orders WHERE user_id = ?", id)
        for i in range(len(orders)):
            temp = {} 
            temp["product"] = db.execute("SELECT product FROM orders WHERE user_id = ?", id)[i]["product"]
            temp["quantity"] = db.execute("SELECT quantity FROM orders WHERE product = ? AND user_id = ?", temp["product"], id)[0]["quantity"]
            temp["uprice"] = db.execute("SELECT price FROM stocks WHERE product = ?", temp["product"])[0]["price"]
            temp["tprice"] = round(temp["quantity"] * temp["uprice"], 2)
            purchases.append(temp)

        for j in range(len(orders)):
            total += purchases[j]["tprice"]

        return render_template("purchases.html", purchases=purchases, total=total)
