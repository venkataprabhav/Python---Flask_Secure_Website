

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


@app.route("/")
def index():
    """
    Main Page.
    """

    #Get data from the DB using meta function
    
    rows = query_db("SELECT * FROM product")
    app.logger.info(rows)
    
    return flask.render_template("index.html",
                                 bookList = rows)


@app.route("/adminindex")
def adminindex():
    """
    Main Page.
    """

    # Get data from the DB using meta function

    rows = query_db("SELECT * FROM product")
    app.logger.info(rows)

    return flask.render_template("adminindex.html",
                                 bookList = rows)


@app.route("/products", methods=["GET","POST"])
def products():
    """
    Single Page (ish) Application for Products
    """
    theItem = flask.request.args.get("item")
    if theItem:
        
        #We Do A Query for It
        itemQry = query_db(f"SELECT * FROM product WHERE id = ?",[theItem], one=True)

        #And Associated Reviews
        #reviewQry = query_db("SELECT * FROM review WHERE productID = ?", [theItem])
        theSQL = f"""
        SELECT * 
        FROM review
        INNER JOIN user ON review.userID = user.id
        WHERE review.productID = {itemQry['id']};
        """
        reviewQry = query_db(theSQL)
        
        #If there is form interaction and they put somehing in the basket
        if flask.request.method == "POST":

            quantity = markupsafe.escape(flask.request.form.get("quantity"))
            try:
                quantity = int(quantity)
            except ValueError:
                flask.flash("Error Buying Item")
                return flask.render_template("product.html",
                                             item = itemQry,
                                             reviews=reviewQry)
            
            app.logger.warning("Buy Clicked %s items", quantity)
            
            #And we add something to the Session for the user to keep track
            basket = flask.session.get("basket", {})

            basket[theItem] = quantity
            flask.session["basket"] = basket
            flask.flash("Item Added to Cart")

            
        return flask.render_template("product.html",
                                     item = itemQry,
                                     reviews=reviewQry)
    else:
        
        books = query_db("SELECT * FROM product")        
        return flask.render_template("products.html",
                                     books = books)


@app.route("/adminproducts", methods=["GET", "POST"])
def adminproducts():
    """
    Single Page (ish) Application for Products
    """
    theItem = flask.request.args.get("item")

    books = query_db("SELECT * FROM product")
    return flask.render_template("adminproducts.html",
                                 books=books)

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

        vls = (user,)
        app.logger.info("Attempt to login as %s:%s", vls)
        theQry = "Select * FROM user WHERE email = ?"
        userQry = query_db(theQry, vls, one=True)


        if userQry:
            app.logger.info("User is Ok")

            if bcrypt.checkpw(password.encode('utf-8'), userQry["password"].encode('utf-8')):
                app.logger.info("Login as %s Success", userQry["email"])
                flask.session["user"] = userQry["id"]
                flask.flash("Login Successful")


                return (flask.redirect(flask.url_for("index")))

        else:
            vls = (user,)
            app.logger.info("Attempt to login as %s:%s", vls)
            theQry = "Select * FROM b055 WHERE nimda = ?"
            userQry = query_db(theQry, vls, one=True)

            if userQry:
                app.logger.info("User is Ok")
                if userQry["ssapnimda"] == password:
                    app.logger.info("Login as %s Success", userQry["nimda"])
                    flask.session["user"] = userQry["id"]
                    flask.flash("Login Successful")
                    return (flask.redirect(flask.url_for("adminindex")))

                else:
                    flask.flash("Details Incorrect")


        if userQry is None:
            flask.flash("Details Incorrect")




    return flask.render_template("login.html")



@app.route("/user/create", methods=["GET","POST"])
def create():
    """ Create a new account,
    we will redirect to a homepage here
    """

    if flask.request.method == "GET":
        return flask.render_template("create_account.html")

    #Get the form data
    email = markupsafe.escape(flask.request.form.get("email"))
    password = markupsafe.escape(flask.request.form.get("password"))


    #Sanity check do we have a name, email and password
    if not email or not password: 
        flask.flash("Not all info supplied")
        return flask.render_template("create_account.html",
                                     email = email,
                                     password = password)

    elif email and password:
        def validpass(password):
            global goodpass

            # calculating the length
            badlength = len(password) < 8
            # searching for digits
            badnumber = re.search(r"\d", password) is None
            # searching for uppercase
            badupper = re.search(r"[A-Z]", password) is None
            # searching for lowercase
            badlower = re.search(r"[a-z]", password) is None
            # searching for symbols
            badspecchar = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password) is None
            # overall result
            goodpass = not (badlength or badnumber or badupper or badlower or badspecchar or badlength)

            return {
                'goodpass': goodpass,
                'badlength': badlength,
                'badlength2': badlength2,
                'badnumber': badnumber,
                'badupper': badupper,
                'badlower': badlower,
                'badspecchar': badspecchar,
            }
        validpass(password)
        if goodpass == True:

            #Otherwise we can add the user
            vls = (email, )
            theQry = "Select * FROM user WHERE email = ?"
            userQry =  query_db(theQry,vls, one=True)

            if userQry:
                flask.flash("A User with that Email Exists")
                return flask.render_template("create_account.html",
                                             email = email)

            else:
                #Crate the user
                app.logger.info("Create New User")
                password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                vls = (email, password)
                password = password.decode('utf-8')
                vls = (email, password)
                theQry = f"INSERT INTO user (id, email, password) VALUES (NULL, ?, ?)"
                userQry = write_db(theQry, vls)

                flask.flash("Account Created, you can now Login")
                return flask.redirect(flask.url_for("login"))

        else:
            flask.flash("Password requirements not met!")
            return flask.render_template("create_account.html",
                                         email=email)

#<li>Email {{user.email}}</li>

@app.route("/user/<userId>/settings")
def settings(userId):
    """
    Update a users settings,
    Allow them to make reviews
    """
    flask.session.get("user")
    vls = (userId)
    theQry = "Select * FROM User WHERE id = ?;"
    vls = (userId)
    thisUser =  query_db(theQry, vls, one=True)

    if not thisUser:
        flask.flash("No Such User")
        return flask.redirect(flask.url_for("index"))

    #Purchases
    if flask.session["user"] == thisUser["id"]:
        theSQL = f"Select * FROM purchase WHERE userID = ?"
        purchaces = query_db(theSQL, vls)

        theSQL = """
        SELECT productId, date, product.name
        FROM purchase
        INNER JOIN product ON purchase.productID = product.id
        WHERE userID = ?;
        """

        purchaces = query_db(theSQL, vls)

        return flask.render_template("usersettings.html",
                                    user = thisUser,
                                    purchaces = purchaces)

    else:
        flask.flash("No Such User")
        return flask.redirect(flask.url_for("index"))





@app.route("/logout")
def logout():
    """
    Login Page
    """
    flask.session.clear()
    return flask.redirect(flask.url_for("index"))
    


@app.route("/user/<userId>/update", methods=["GET","POST"])
def updateUser(userId):
    """
    Process any chances from the user settings page
    """
    flask.session.get("user")
    id = (userId)
    theQry = "Select * FROM user WHERE id = ?"
    thisUser = query_db(theQry, id, one=True)
    if not thisUser:
        flask.flash("No Such User")
        return flask.redirect(flask_url_for("index"))

    #otherwise we want to do the checks
    if flask.session["user"] == thisUser["id"]:
        if flask.request.method == "POST":

            current = markupsafe.escape(flask.request.form.get("current"))
            password = markupsafe.escape(flask.request.form.get("password"))

            app.logger.info("Attempt password update for %s from %s to %s", userId, current, password)
            app.logger.info("%s == %s", current, thisUser["password"])
            if current:

                x = bcrypt.hashpw(current.encode('utf-8'), thisUser["password"].encode('utf-8'))

                if thisUser["password"] == x.decode('utf-8'):
                    def validpass(password):
                        global goodpass

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
                        goodpass = not (badlength or badnumber or badupper or badlower or badspecchar or badlength)

                        return {
                            'goodpass': goodpass,
                            'badlength': badlength,
                            'badlength2': badlength2,
                            'badnumber': badnumber,
                            'badupper': badupper,
                            'badlower': badlower,
                            'badspecchar': badspecchar,
                        }
                    validpass(password)
                    if goodpass == True:

                        app.logger.info("Password OK, update")
                        #Update the Password
                        password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                        password = password.decode('utf-8')

                        vls = (password, id)
                        theSQL = f"UPDATE user SET password = ? WHERE id = ?"
                        app.logger.info("SQL %s", theSQL)
                        write_db(theSQL, vls)
                        flask.flash("Password Updated")
                    else:
                        flask.flash("Password requirements not met!")
                        return flask.render_template("settings.html",
                                                 email=email)


                else:
                    app.logger.info("Mismatch")
                    flask.flash("Current Password is incorrect")
                return flask.redirect(flask.url_for("settings",
                                                    userId = thisUser['id']))



            flask.flash("Update Error")

    return flask.redirect(flask.url_for("settings", userId=userId))

# -------------------------------------
#
# Functionality to allow user to review items
#
# ------------------------------------------

@app.route("/review/<userId>/<itemId>", methods=["GET", "POST"])
def reviewItem(userId, itemId):
    """Add a Review"""

    flask.session.get("user")
    id = (userId)
    theQry = "Select * FROM user WHERE id = ?"
    thisUser = query_db(theQry, id, one=True)
    if not thisUser:
        flask.flash("No Such User")
        return flask.redirect(flask_url_for("index"))

    # otherwise we want to do the checks
    if flask.session["user"] == thisUser["id"]:

        #Handle input
        if flask.request.method == "POST":
            reviewStars = markupsafe.escape(flask.request.form.get("rating"))
            reviewComment = markupsafe.escape(flask.request.form.get("review"))

            #Clean up review whitespace
            reviewComment = reviewComment.strip()
            reviewId = markupsafe.escape(flask.request.form.get("reviewId"))

            app.logger.info("Review Made %s", reviewId)
            app.logger.info("Rating %s  Text %s", reviewStars, reviewComment)

            if reviewId:
                #Update an existing oe
                app.logger.info("Update Existing")

                theSQL = f"""
                UPDATE review
                SET stars = {reviewStars},
                    review = '{reviewComment}'
                WHERE
                    id = {reviewId}"""

                app.logger.debug("%s", theSQL)
                write_db(theSQL)

                flask.flash("Review Updated")

            else:
                app.logger.info("New Review")

                theSQL = f"""
                INSERT INTO review (userId, productId, stars, review)
                VALUES ({userId}, {itemId}, {reviewStars}, '{reviewComment}');
                """

                app.logger.info("%s", theSQL)
                write_db(theSQL)

                flask.flash("Review Made")

        #Otherwise get the review
        theQry = f"SELECT * FROM product WHERE id = {itemId};"
        item = query_db(theQry, one=True)

        theQry = f"SELECT * FROM review WHERE userID = {userId} AND productID = {itemId};"
        review = query_db(theQry, one=True)
        app.logger.debug("Review Exists %s", review)

        return flask.render_template("reviewItem.html",
                                     item = item,
                                     review = review,
                                     userId=userId, itemId=itemId)

# ---------------------------------------
#
# BASKET AND PAYMEN
#
# ------------------------------------------



@app.route("/basket", methods=["GET","POST"])
def basket():

    #Check for user
    if not flask.session["user"]:
        flask.flash("You need to be logged in")
        return flask.redirect(flask.url_for("index"))


    theBasket = []
    #Otherwise we need to work out the Basket
    #Get it from the session
    sessionBasket = flask.session.get("basket", None)
    if not sessionBasket:
        flask.flash("No items in basket")
        return flask.redirect(flask.url_for("index"))

    totalPrice = 0
    for key in sessionBasket:

        vls = (key)
        theQry = f"SELECT * FROM product WHERE id = ?"
        theItem =  query_db(theQry, vls, one=True)
        quantity = int(sessionBasket[key])
        thePrice = theItem["price"] * quantity
        totalPrice += thePrice
        theBasket.append([theItem, quantity, thePrice])
    
        
    return flask.render_template("basket.html",
                                 basket = theBasket,
                                 total=totalPrice)

@app.route("/basket/payment", methods=["GET", "POST"])
def pay():
    """
    Fake paymeent.

    YOU DO NOT NEED TO IMPLEMENT PAYMENT
    """

    if not flask.session["user"]:
        flask.flash("You need to be logged in")
        return flask.redirect(flask.url_for("index"))

    # Get the total cost
    cost = markupsafe.escape(flask.request.form.get("total"))

    # Fetch USer ID from Sssion
    theQry = "Select * FROM User WHERE id = {0}".format(flask.session["user"])
    theUser = query_db(theQry, one=True)

    # Add products to the user
    sessionBasket = flask.session.get("basket", None)

    theDate = datetime.datetime.utcnow()
    for key in sessionBasket:
        # As we should have a trustworthy key in the basket.
        theQry = "INSERT INTO PURCHASE (userID, productID, date) VALUES ({0},{1},'{2}')".format(theUser['id'],
                                                                                                key,
                                                                                                theDate)

        app.logger.debug(theQry)
        write_db(theQry)

    # Clear the Session
    flask.session.pop("basket", None)

    return flask.render_template("pay.html",
                                 total=cost)


@app.route("/noofusers")
def noofusers():

    headings = ("email", "id")
    theQry = ("SELECT email,id FROM user")
    head = query_db(theQry)

    print(head)


    return flask.render_template("noofusers.html", headings=headings, head=head)

@app.route("/addstock", methods=["GET","POST"])
def addstock():

    if flask.request.method == "GET":
        return flask.render_template("addstock.html")


    name = markupsafe.escape(flask.request.form.get("name"))
    description = markupsafe.escape(flask.request.form.get("description"))
    price = markupsafe.escape(flask.request.form.get("price"))
    image = markupsafe.escape(flask.request.form.get("image"))

    vls = (name, description, price, image)


    theQry = "Select * FROM product WHERE (id, name, description, price, image) = (NULL, ?, ?, ?, ?)"
    userQry = query_db(theQry, vls, one=True)

    if userQry:
        flask.flash("That product already exists")
        return flask.render_template("addstock.html",
                                     name=name,
                                     description=description,
                                     price=price,
                                     image=image)

    else:

        theQry = f"INSERT INTO product (id, name, description, price, image) VALUES (NULL, ?, ?, ?, ?)"
        userQry = write_db(theQry, vls,)

        flask.flash("New product created!")
        return flask.redirect(flask.url_for("adminindex"))



    return flask.render_template("addstock.html")



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

    You are free to ignore scurity implications of this
    """
    init_db()
    return "Done"

@app.route("/terms")
def terms():
    return flask.render_template("terms.html")

