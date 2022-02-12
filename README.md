# An Emart Web App
#### Video Demo:  https://youtu.be/qkveln5CCOc
#### Description:

For my CS50 Final Project, I created a web application for an emart.

I guess one of the cool features is that there are multiple html templates to differentiate between the admin account and a normal user's account. It was quite fun creating all of this.

Feel free to reference my code (not thank it is very impressive) or contact me should there be any queries. Now, allow me to explain what is actually happening step by step according to the sequence in app.py:

HEADERS and APPLICATION:
I imported the usual libraries as referenced in CS50 Finance.
Also referenced the application settings. 

DATABASE:
Had 4 main databases: users, stocks, cart, orders
The users db stored all registered users and their contacts
The stocks db stored all the emart stocks and their details like sold, instock, price, cost, etc
The cart db stored every user's carts which are not commited to purchase
The orders db stored every user's orders

@app.route("/")
For users:
    If post: submit order to cart
    If get: load template which shows order form and catalogue
For admin:
    If post: Changes the catalogue
    If get: load template which shows change form and catalogue

@app.route("/register")
Self-explanatory.
There is a hash-pass system from the library werkzeug.security

@app.route("/login")
Checks for valid username and matching password before letting user in.
Logging in with TB_Admin will from now on, render different templates. For instance, index, cart, purchases and profile templates will be different because admin has privileges to know other user's actions on the webpage.

@app.route("/logout")
Clears session

@app.route("/cart")
For users:
    If post: Delete the item from the cart
    If get: Shows the current cart
For admin:
    Can only get, and see who still has items left in cart.

@app.route("/purchases")
For users:
    If post: Commit cart items to purchase
    If get: Shows currently purchased items
For admin:
    Can only get, and who purchases what item and what time

@app.route("/contact")
Link to various contact webpages of the company

@app.route("/profile")
For users:
    If post: Updates their profile settings
    If get: Shows the template with change form and profile
For admin:
    If post: Updates their profile settings
    If get: Shows the template with change form and profile AND USERS PROFILES (except password)

Thank you!
~ Aaron
~ IG: @aarontanky