# Libraries import
import requests
import psycopg2
from os import environ

# Static variables
from helpers import info_filter, image_check, login_required, search, time_elapsed_string
from models import signup, user_login, get_user_recipes, add_to_favorites, delete_from_favorites, share, display_feed, get_username, get_recipe, get_password_hash, change_pass_hash, deactivate_user

from flask_session import Session
from tempfile import mkdtemp
from flask import Flask, render_template, request, redirect, flash, session, url_for, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

application = Flask(__name__)

# Environment variables
api_id = environ["API_ID"]
api_key = environ["SECRET_KEY"]
db_host = environ["DB_HOST"]
db_name = environ["DB_NAME"]
db_user = environ["DB_USERNAME"]
db_pass = environ["DB_PASSWORD"]

connect_string = 'host=%s dbname=%s user=%s password=%s' % (db_host, db_name, db_user, db_pass)

conn = psycopg2.connect(connect_string)
conn.autocommit = True

# Configure session to use filesystem (instead of signed cookies)
application.config["SESSION_FILE_DIR"] = mkdtemp()
application.config["SESSION_PERMANENT"] = False
application.config["SESSION_TYPE"] = "filesystem"
Session(application)


@application.route('/', methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        return render_template("index.html")
    else:
        search_string = "?q=%s" % request.form.get('query')
        food_data = search(api_id, api_key, search_string)
        session["search_data"] = info_filter(food_data)

        params = {
        'page': 'search',
        'title': 'Search results for \'%s\'' % request.form.get('query'),
        'button_class': 'search-btn'
        }

        return render_template("cards.html", data=session["search_data"], params=params)

@application.route("/adv_search", methods=["GET", "POST"])
@login_required
def adv_search():
    if request.method == "GET":
        return render_template("adv_search.html")
    else:
        search_string = "?q=%s" % request.form.get('query')
        if request.form.get('diet'):
            search_string = search_string + "&diet=%s" % request.form.get('diet')
        for key, value in request.form.to_dict().items():
            if key != 'diet' and key != 'query':
                search_string = search_string + "&health=%s" % value

        food_data = search(api_id, api_key, search_string)
        session["search_data"] = info_filter(food_data)

        params = {
        'page': 'search',
        'title': 'Search results for \'%s\'' % request.form.get('query'),
        'button_class': 'search-btn'
        }

        return render_template("cards.html", data=session["search_data"], params=params)

@application.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        user = user_login(conn, request.form.get("username").lower())

        # Ensure username exists and password is correct
        if not user or not check_password_hash(user[2], request.form.get("password")):
            flash("Invalid username or password", 'danger')
            return render_template("login.html")

        # If user is not active
        if not user[3]:
            flash("Account has been deactivated", 'danger')
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = user[0]

        # Check if 'Remember me' checkbox checked
        if (request.form.get('remember') == 'on'):
            session.permanent = True

        # Redirect user to home page
        flash("Welcome, " + user[1], 'success')
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@application.route('/register', methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")

    try:
        signup(conn, username.lower(), generate_password_hash(password))
    except psycopg2.errors.UniqueViolation:
        print("User exists")
        flash("User already exists", "danger")
        return redirect(url_for('.login', code="exists"))
    
    print("User created")
    flash("User created successfully", "success")
    return redirect(url_for("login", code="success"))

@application.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/login")

@application.route("/favorites")
@login_required
def favorites():
    recipes = get_user_recipes(conn, session['user_id'])

    params = {
        'title': 'Your favorites',
        'button_class': 'favorites-btn',
        'favorites': True
    }

    return render_template("cards.html", data=recipes, params=params)

@application.route("/add_to_favorites", methods=["POST"])
def add():
    recipe_id = int(request.form.to_dict()['id'])
    path = request.form.to_dict()['path']
    recipe_data = {}

    if path == '/feed':
        recipe_data = get_recipe(conn, recipe_id)
    else:
        recipe_data = session["search_data"][recipe_id]

    add_to_favorites(conn, session['user_id'], recipe_data)
    return "True"

@application.route("/delete_from_favorites", methods=["POST"])
def delete():
    recipe_id = request.form.to_dict()['id']
    delete_from_favorites(conn, recipe_id)
    return "False"

@application.route("/share_to_feed", methods=["POST"])
def share_to_feed():
    recipe_id = request.form.to_dict()['id']
    msg = request.form.to_dict()['msg']
    share(conn, msg, recipe_id)
    return "True"

@application.route("/feed")
@login_required
def feed():
    feed_data = []
    items = display_feed(conn)
    for item in items:
        feed_item = {}
        feed_item["id"] = item[0]
        feed_item["user_id"] = item[1]
        feed_item["user"] = get_username(conn, item[1])
        feed_item["msg"] = item[3]
        feed_item["time_elapsed"] = time_elapsed_string(item[4])
        feed_item["image"] = item[2]["image"]
        feed_item["name"] = item[2]["name"]
        feed_item["healthLabels"] = item[2]["healthLabels"]
        feed_item["url"] = item[2]["url"]

        feed_data.append(feed_item)

    return render_template("feed.html", data=feed_data)

@application.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "GET":
        return render_template("profile.html")
    else:
        curr_pass = request.form.get('curr-pass')
        new_pass = request.form.get('new-pass')
        pass_hash = get_password_hash(conn, session["user_id"])

        if not check_password_hash(pass_hash, curr_pass):
            flash("Current password incorrect", "danger")
            return render_template("profile.html")

        change_pass_hash(conn, generate_password_hash(new_pass), session['user_id'])
        flash("Password has been changed", "success")
        return redirect("/")

@application.route("/user_delete", methods=["POST"])
def user_delete():
    deactivate_user(conn, session["user_id"])
    session.clear()
    return "True"