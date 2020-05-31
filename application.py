import os
import datetime

from flask import Flask, session, render_template, request, g
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import date,time

app = Flask(__name__)


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = 'Punctual12@'
Session(app)


# Set up database
engine = create_engine("postgres://rviahcqoevlwmu:cfcedf636911f809d3c6c439d89b5b84c6f9b607d6c5a08dad91d9e9c2f3edb4@ec2-34-200-116-132.compute-1.amazonaws.com:5432/d433ee1iibk4td")
db = scoped_session(sessionmaker(bind=engine))


@app.before_request
def before_request():
    if 'username' in session:
        users = db.execute("SELECT * FROM logins").fetchall()
        user = [x for x in users if x.username == session['username']][0]
        g.user = user

@app.route("/")
def index():
    flights = db.execute(
        "SELECT * FROM logins WHERE username= 'nitesh' ").fetchall()
    return render_template("index.html", flights=flights)


@app.route("/history")
def history():
    return render_template("history.html")


@app.route("/practice")
def practice():
    return render_template("practice.html")


@app.route("/blog")
def blog():
    flights = db.execute("SELECT * FROM blogs ORDER BY date DESC").fetchall()
    return render_template("blogs.html", flights=flights)


@app.route("/contact")
def contact():
    return render_template("index.html")


medicine = {"turmuric":"one of the most well-known, widely researched, and commonly used Ayurvedic spices in the world. It can be used in many ways and has enormous health benefits. People use it in cooking, drinks and also as a beauty product for bright glowing skin. Due to its particular affinity for the blood it is able to circulate its powerful health benefits throughout the body. It is used to support a number of systems and functions in the body. Promotes digestion, Supports the brain and nervous system, Maintains comfortable joint movement, Supports healthy blood sugar levels already normal range especially when combined with neem and amalaki, Supports proper functioning of the liver, Nourishes the heart and circulatory system and Bolsters the immune system."}


@app.route("/medicine")
def medicine():
    return render_template("medicine.html", medicines=medicine)


@app.route("/yourblog")
def yourblog():
    return render_template("signin.html", button="SIGN IN")


@app.route("/signin")
def signin():
    return render_template("signin.html", button="SIGN IN")


@app.route("/addblog")
def addblog():
    if "username" not in session:
        return render_template("signin.html", message="Please Sign in First.", button="SIGN IN")
    return render_template("addblog.html", author=session["username"] )


@app.route("/blogtodb", methods=["POST", "GET"])
def blogtodb():
    title1 = request.form.get("title")
    body = request.form.get("body")
    date = datetime.datetime.now().date()
    time = datetime.datetime.now().time()
    try:
        db.execute("INSERT INTO blogs (title, body,author, date, time) VALUES (:title, :body, :author, :date, :time)",{"title": title1, "body": body, "author": session["username"], "date": date, "time":time})
        db.commit()
        return render_template("addblog.html", message="Successful")
    except:
        return render_template("addblog.html", message="Error")



@app.route("/signup")
def signup():
    return render_template("signup.html", button="SIGN UP")


@app.route("/signout")
def signout():
    session.pop('username', None)
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    session.pop('username', None)

    username = request.form.get("name")
    password = request.form.get("password")
    if db.execute("SELECT username,password FROM logins WHERE username= :email AND password = :password", {"email": username, "password": password}).fetchone() is None:
        return render_template("signin.html", button="SIGN IN", message="No users found. Sign up instead.", showdiv="yes")
        db.commit()
    else:
        session["username"] = username
        flights = db.execute("SELECT * FROM blogs WHERE author = :email", {"email": username}).fetchall()
        db.commit()
        return render_template("blogs.html", user=username, flights=flights)


@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name")
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    if db.execute("SELECT username FROM logins WHERE username= :username", {"username": username}).fetchone() is None:
        db.execute("INSERT INTO logins (name, username,email, password) VALUES (:name, :username, :email, :password)",{"name": name, "username": username, "email": email, "password": password})
        db.commit()
        return render_template("signup.html", button="SIGN UP", message="Account has been made.")
    else:
        return render_template("signup.html", button="SIGN UP", message="Username Already exist. Try Another.")



@app.route("/book", methods=["POST"])
def book():
    """Book a flight."""

    # Get form information.
    name = request.form.get("name")
    try:
        flight_id = int(request.form.get("flight_id"))
    except ValueError:
        return render_template("error.html", message="Invalid flight number.")

    # Make sure flight exists.
    if db.execute("SELECT * FROM flights WHERE id = :id", {"id": flight_id}).rowcount == 0:
        return render_template("error.html", message="No such flight with that id.")
    db.execute("INSERT INTO passengers (name, flight_id) VALUES (:name, :flight_id)",
               {"name": name, "flight_id": flight_id})
    db.commit()
    return render_template("success.html")
