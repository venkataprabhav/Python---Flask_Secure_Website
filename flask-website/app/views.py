from .meta import *

import os
import flask
import markupsafe
import datetime
import smtplib
from email.message import EmailMessage
from random import *
from markupsafe import escape
import email.message
import csrf
from flask_wtf.csrf import CSRFProtect
from functools import wraps


def login_required(f):
    """Decorator to require login for protected routes"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in flask.session:
            flask.flash("You need to be logged in to access this page")
            return flask.redirect(flask.url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """Decorator to require admin access"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in flask.session:
            flask.flash("You need to be logged in to access this page")
            return flask.redirect(flask.url_for("login"))

        # Check if user is admin by checking b055 table
        user_id = flask.session.get('user')
        admin_query = query_db("SELECT * FROM b055 WHERE id = ?", [user_id], one=True)
        if not admin_query:
            flask.flash("Access denied - Admin privileges required")
            return flask.redirect(flask.url_for("index"))
        return f(*args, **kwargs)

    return decorated_function


def validate_user_access(user_id):
    """Validate that current session user can access the requested user_id"""
    session_user_id = flask.session.get('user')
    if not session_user_id:
        return False

    try:
        if int(session_user_id) != int(user_id):
            return False
    except (ValueError, TypeError):
        return False

    return True


@app.route("/")
def index():
    """
    Main Page.
    """
    # Get data from the DB using meta function
    rows = query_db("SELECT * FROM product")
    app.logger.info(rows)

    return flask.render_template("index.html", bookList=rows)


@app.route("/adminindex")
@admin_required
def adminindex():
    """
    Admin Main Page.
    """
    # Get data from the DB using meta function
    rows = query_db("SELECT * FROM product")
    app.logger.info(rows)

    return flask.render_template("adminindex.html", bookList=rows)


@app.route("/products", methods=["GET", "POST"])
def products():
    """
    Single Page (ish) Application for Products
    """
    theItem = flask.request.args.get("item")
    if theItem:
        # Validate item ID is numeric
        try:
            item_id = int(theItem)
        except (ValueError, TypeError):
            flask.flash("Invalid item ID")
            return flask.redirect(flask.url_for("products"))

        # We Do A Query for It using parameterized query
        itemQry = query_db("SELECT * FROM product WHERE id = ?", [item_id], one=True)

        if not itemQry:
            flask.flash("Product not found")
            return flask.redirect(flask.url_for("products"))

        # And Associated Reviews using parameterized query
        theSQL = """
        SELECT review.*, user.email 
        FROM review
        INNER JOIN user ON review.userID = user.id
        WHERE review.productID = ?
        """
        reviewQry = query_db(theSQL, [itemQry['id']])

        # If there is form interaction and they put something in the basket
        if flask.request.method == "POST":
            if 'user' not in flask.session:
                flask.flash("You need to be logged in to add items to cart")
                return flask.redirect(flask.url_for("login"))

            quantity = markupsafe.escape(flask.request.form.get("quantity"))
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    raise ValueError("Quantity must be positive")
            except ValueError:
                flask.flash("Error: Invalid quantity")
                return flask.render_template("product.html",
                                             item=itemQry,
                                             reviews=reviewQry)

            app.logger.warning("Buy Clicked %s items", quantity)

            # And we add something to the Session for the user to keep track
            basket = flask.session.get("basket", {})
            basket[str(item_id)] = quantity
            flask.session["basket"] = basket
            flask.flash("Item Added to Cart")

        return flask.render_template("product.html",
                                     item=itemQry,
                                     reviews=reviewQry)
    else:
        books = query_db("SELECT * FROM product")
        return flask.render_template("products.html", books=books)


@app.route("/adminproducts", methods=["GET", "POST"])
@admin_required
def adminproducts():
    """
    Admin Products Page
    """
    books = query_db("SELECT * FROM product")
    return flask.render_template("adminproducts.html", books=books)


# ------------------
# USER Level Stuff
# ---------------------

@app.route("/user/login", methods=["GET", "POST"])
def login():
    """
    Login Page
    """
    if flask.request.method == "POST":
        # Get data
        user = markupsafe.escape(flask.request.form.get("email"))
        password = markupsafe.escape(flask.request.form.get("password"))

        if not user or not password:
            flask.flash("Email and password are required")
            return flask.render_template("login.html")

        app.logger.info("Attempt to login as %s", user)

        # First check regular users
        theQry = "SELECT * FROM user WHERE email = ?"
        userQry = query_db(theQry, [user], one=True)

        if userQry:
            app.logger.info("User found in user table")
            # Properly verify password using bcrypt
            if bcrypt.checkpw(password.encode('utf-8'), userQry["password"].encode('utf-8')):
                app.logger.info("Login as %s Success", userQry["email"])
                flask.session["user"] = userQry["id"]
                flask.session["is_admin"] = False
                flask.flash("Login Successful")
                return flask.redirect(flask.url_for("index"))
            else:
                flask.flash("Details Incorrect")
        else:
            # Check admin users
            app.logger.info("Checking admin table")
            theQry = "SELECT * FROM b055 WHERE nimda = ?"
            adminQry = query_db(theQry, [user], one=True)

            if adminQry:
                app.logger.info("Admin user found")
                # Check admin password (assuming plain text for admin - should be hashed in production)
                if adminQry["ssapnimda"] == password:
                    app.logger.info("Admin login as %s Success", adminQry["nimda"])
                    flask.session["user"] = adminQry["id"]
                    flask.session["is_admin"] = True
                    flask.flash("Admin Login Successful")
                    return flask.redirect(flask.url_for("adminindex"))
                else:
                    flask.flash("Details Incorrect")
            else:
                flask.flash("Details Incorrect")

    return flask.render_template("login.html")


@app.route("/user/create", methods=["GET", "POST"])
def create():
    """ Create a new account,
    we will redirect to a homepage here
    """
    if flask.request.method == "GET":
        return flask.render_template("create_account.html")

    # Get the form data
    email = markupsafe.escape(flask.request.form.get("email"))
    password = markupsafe.escape(flask.request.form.get("password"))

    # Sanity check do we have a name, email and password
    if not email or not password:
        flask.flash("Not all info supplied")
        return flask.render_template("create_account.html", email=email)

    def validpass(password):
        # calculating the length
        badlength = len(password) < 8
        badlength2 = len(password) > 20

        # searching for digits
        badnumber = re.search(r"\d", password) is None
        # searching for uppercase
        badupper = re.search(r"[A-Z]", password) is None
        # searching for lowercase
        badlower = re.search(r"[a-z]", password) is None
        # searching for symbols
        badspecchar = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password) is None
        # overall result
        goodpass = not (badlength or badnumber or badupper or badlower or badspecchar or badlength2)

        return goodpass

    if not validpass(password):
        flask.flash("Password requirements not met!")
        return flask.render_template("create_account.html", email=email)

    # Check if user already exists
    theQry = "SELECT * FROM user WHERE email = ?"
    userQry = query_db(theQry, [email], one=True)

    if userQry:
        flask.flash("A User with that Email Exists")
        return flask.render_template("create_account.html", email=email)

    # Create the user
    app.logger.info("Create New User")
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    password_str = hashed_password.decode('utf-8')

    theQry = "INSERT INTO user (email, password) VALUES (?, ?)"
    write_db(theQry, [email, password_str])

    flask.flash("Account Created, you can now Login")
    return flask.redirect(flask.url_for("login"))


@app.route("/user/<int:userId>/settings")
@login_required
def settings(userId):
    """
    Update a users settings,
    Allow them to make reviews
    """
    if not validate_user_access(userId):
        flask.flash("Access denied")
        return flask.redirect(flask.url_for("index"))

    theQry = "SELECT * FROM user WHERE id = ?"
    thisUser = query_db(theQry, [userId], one=True)

    if not thisUser:
        flask.flash("No Such User")
        return flask.redirect(flask.url_for("index"))

    # Purchases
    theSQL = """
    SELECT productId, date, product.name
    FROM purchase
    INNER JOIN product ON purchase.productID = product.id
    WHERE userID = ?
    """
    purchases = query_db(theSQL, [userId])

    return flask.render_template("usersettings.html",
                                 user=thisUser,
                                 purchaces=purchases)


@app.route("/logout")
def logout():
    """
    Logout - clear session
    """
    flask.session.clear()
    return flask.redirect(flask.url_for("index"))


@app.route("/user/<int:userId>/update", methods=["GET", "POST"])
@login_required
def updateUser(userId):
    """
    Process any changes from the user settings page
    """
    if not validate_user_access(userId):
        flask.flash("Access denied")
        return flask.redirect(flask.url_for("index"))

    theQry = "SELECT * FROM user WHERE id = ?"
    thisUser = query_db(theQry, [userId], one=True)

    if not thisUser:
        flask.flash("No Such User")
        return flask.redirect(flask.url_for("index"))

    if flask.request.method == "POST":
        current = markupsafe.escape(flask.request.form.get("current"))
        new_password = markupsafe.escape(flask.request.form.get("password"))

        if not current or not new_password:
            flask.flash("Both current and new password are required")
            return flask.redirect(flask.url_for("settings", userId=userId))

        app.logger.info("Attempt password update for %s", userId)

        # Properly verify current password
        if bcrypt.checkpw(current.encode('utf-8'), thisUser["password"].encode('utf-8')):

            def validpass(password):
                badlength = len(password) < 8
                badlength2 = len(password) > 20
                badnumber = re.search(r"\d", password) is None
                badupper = re.search(r"[A-Z]", password) is None
                badlower = re.search(r"[a-z]", password) is None
                badspecchar = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password) is None
                return not (badlength or badnumber or badupper or badlower or badspecchar or badlength2)

            if validpass(new_password):
                app.logger.info("Password OK, update")
                # Update the Password
                hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                password_str = hashed_password.decode('utf-8')

                theSQL = "UPDATE user SET password = ? WHERE id = ?"
                write_db(theSQL, [password_str, userId])
                flask.flash("Password Updated")
            else:
                flask.flash("Password requirements not met!")
        else:
            app.logger.info("Current password mismatch")
            flask.flash("Current Password is incorrect")

    return flask.redirect(flask.url_for("settings", userId=userId))


# -------------------------------------
#
# Functionality to allow user to review items
#
# ------------------------------------------

@app.route("/review/<int:userId>/<int:itemId>", methods=["GET", "POST"])
@login_required
def reviewItem(userId, itemId):
    """Add a Review"""
    if not validate_user_access(userId):
        flask.flash("Access denied")
        return flask.redirect(flask.url_for("index"))

    # Handle input
    if flask.request.method == "POST":
        reviewStars = markupsafe.escape(flask.request.form.get("rating"))
        reviewComment = markupsafe.escape(flask.request.form.get("review"))
        reviewId = markupsafe.escape(flask.request.form.get("reviewId"))

        # Validate rating
        try:
            rating = int(reviewStars)
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
        except (ValueError, TypeError):
            flask.flash("Invalid rating")
            return flask.redirect(flask.url_for("reviewItem", userId=userId, itemId=itemId))

        # Clean up review whitespace
        reviewComment = reviewComment.strip()

        if reviewId:
            # Update an existing review
            app.logger.info("Update Existing Review")
            try:
                review_id_int = int(reviewId)
                theSQL = "UPDATE review SET stars = ?, review = ? WHERE id = ? AND userID = ?"
                write_db(theSQL, [rating, reviewComment, review_id_int, userId])
                flask.flash("Review Updated")
            except (ValueError, TypeError):
                flask.flash("Invalid review ID")
        else:
            app.logger.info("New Review")
            theSQL = "INSERT INTO review (userId, productId, stars, review) VALUES (?, ?, ?, ?)"
            write_db(theSQL, [userId, itemId, rating, reviewComment])
            flask.flash("Review Made")

    # Get the product and existing review
    theQry = "SELECT * FROM product WHERE id = ?"
    item = query_db(theQry, [itemId], one=True)

    if not item:
        flask.flash("Product not found")
        return flask.redirect(flask.url_for("products"))

    theQry = "SELECT * FROM review WHERE userID = ? AND productID = ?"
    review = query_db(theQry, [userId, itemId], one=True)
    app.logger.debug("Review Exists %s", review)

    return flask.render_template("reviewItem.html",
                                 item=item,
                                 review=review,
                                 userId=userId, itemId=itemId)


# ---------------------------------------
#
# BASKET AND PAYMENT
#
# ------------------------------------------

@app.route("/basket", methods=["GET", "POST"])
@login_required
def basket():
    """Display user's shopping basket"""
    theBasket = []
    # Get basket from session
    sessionBasket = flask.session.get("basket", None)
    if not sessionBasket:
        flask.flash("No items in basket")
        return flask.redirect(flask.url_for("index"))

    totalPrice = 0
    for key in sessionBasket:
        try:
            item_id = int(key)
        except (ValueError, TypeError):
            continue

        theQry = "SELECT * FROM product WHERE id = ?"
        theItem = query_db(theQry, [item_id], one=True)

        if theItem:
            quantity = int(sessionBasket[key])
            thePrice = theItem["price"] * quantity
            totalPrice += thePrice
            theBasket.append([theItem, quantity, thePrice])

    return flask.render_template("basket.html",
                                 basket=theBasket,
                                 total=totalPrice)


@app.route("/basket/payment", methods=["GET", "POST"])
@login_required
def pay():
    """
    Fake payment.
    YOU DO NOT NEED TO IMPLEMENT PAYMENT
    """
    # Get the total cost
    cost = markupsafe.escape(flask.request.form.get("total"))

    # Fetch User ID from Session
    user_id = flask.session["user"]
    theQry = "SELECT * FROM user WHERE id = ?"
    theUser = query_db(theQry, [user_id], one=True)

    if not theUser:
        flask.flash("User not found")
        return flask.redirect(flask.url_for("index"))

    # Add products to the user
    sessionBasket = flask.session.get("basket", None)
    if not sessionBasket:
        flask.flash("No items in basket")
        return flask.redirect(flask.url_for("index"))

    theDate = datetime.datetime.utcnow()
    for key in sessionBasket:
        try:
            product_id = int(key)
        except (ValueError, TypeError):
            continue

        theQry = "INSERT INTO purchase (userID, productID, date) VALUES (?, ?, ?)"
        write_db(theQry, [theUser['id'], product_id, theDate])

    # Clear the Session
    flask.session.pop("basket", None)

    return flask.render_template("pay.html", total=cost)


@app.route("/noofusers")
@admin_required
def noofusers():
    """Display number of users - Admin only"""
    headings = ("email", "id")
    theQry = "SELECT email, id FROM user"
    head = query_db(theQry)

    return flask.render_template("noofusers.html", headings=headings, head=head)


@app.route("/addstock", methods=["GET", "POST"])
@admin_required
def addstock():
    """Add new product to stock - Admin only"""
    if flask.request.method == "GET":
        return flask.render_template("addstock.html")

    name = markupsafe.escape(flask.request.form.get("name"))
    description = markupsafe.escape(flask.request.form.get("description"))
    price = markupsafe.escape(flask.request.form.get("price"))
    image = markupsafe.escape(flask.request.form.get("image"))

    if not name or not description or not price:
        flask.flash("Name, description, and price are required")
        return flask.render_template("addstock.html",
                                     name=name,
                                     description=description,
                                     price=price,
                                     image=image)

    # Validate price
    try:
        price_float = float(price)
        if price_float < 0:
            raise ValueError("Price must be positive")
    except (ValueError, TypeError):
        flask.flash("Invalid price")
        return flask.render_template("addstock.html",
                                     name=name,
                                     description=description,
                                     price=price,
                                     image=image)

    # Check if product already exists
    theQry = "SELECT * FROM product WHERE name = ? AND description = ? AND price = ?"
    userQry = query_db(theQry, [name, description, price], one=True)

    if userQry:
        flask.flash("That product already exists")
        return flask.render_template("addstock.html",
                                     name=name,
                                     description=description,
                                     price=price,
                                     image=image)

    # Create the product
    theQry = "INSERT INTO product (name, description, price, image) VALUES (?, ?, ?, ?)"
    write_db(theQry, [name, description, price, image])

    flask.flash("New product created!")
    return flask.redirect(flask.url_for("adminindex"))


# ---------------------------
# HELPER FUNCTIONS
# ---------------------------

@app.route('/uploads/<name>')
def serve_image(name):
    """
    Helper function to serve an uploaded image
    """
    return flask.send_from_directory(app.config["UPLOAD_FOLDER"], name)


@app.route("/initdb")
def database_helper():
    """
    Helper / Debug Function to create the initial database
    You are free to ignore security implications of this
    """
    init_db()
    return "Done"


@app.route("/terms")
def terms():
    return flask.render_template("terms.html")
