import os, requests

from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    session,
    g,
    url_for,
    jsonify,
)
from functools import wraps
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

from forms import (
    UserAddForm,
    LoginForm,
    UserEditForm,
    PlantSearchForm,
    ProjectAddForm,
    PlotAddForm,
    PlantListAddForm,
)
from models import db, connect_db, User, Project, Plot, PlantList, Plant
from secret import TREFLE_API_KEY, FLASK_SECRET

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgres:///plot_planner"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = True
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", FLASK_SECRET)
toolbar = DebugToolbarExtension(app)

connect_db(app)

db.drop_all()
db.create_all()

API_BASE_URL = "https://trefle.io/api/v1"
CURR_USER_KEY = "curr_user"


# ##############################################################################
# # User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


def check_authorized(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect(url_for("homepage"))
        return func(*args, **kwargs)

    return wrapper


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", "danger")
            return render_template("users/signup.html", form=form)

        do_login(user)

        return redirect(url_for("homepage"))

    else:
        return render_template("users/signup.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect(url_for("homepage"))

        flash("Invalid credentials.", "danger")

    return render_template("users/login.html", form=form)


@app.route("/logout")
def logout():
    """Logs user out and redirects to login."""

    do_logout()
    flash("User logged out!", "success")

    return redirect(url_for("login"))


##############################################################################
# Homepage and error pages


@app.route("/")
def homepage():
    """Show homepage"""
    if g.user:
        return render_template("home.html")

    else:
        return render_template("home.html")


##############################################################################
# User pages


@app.route("/users/<int:user_id>", methods=["GET", "POST"])
def user_profile(user_id):
    """Shows user profile page"""

    user = User.query.get_or_404(user_id)

    if user:
        return render_template("users/profile.html", user=user)

    else:
        flash("Must be logged in to see user profile.")
        redirect(url_for("login"))


##############################################################################
# Project Pages
@app.route("/projects", methods=["GET", "POST"])
def projects_list():
    """Shows existing projects, and form to add new projects"""
    form = ProjectAddForm()

    if form.validate_on_submit():

        try:
            project = Project.add(
                name=form.name.data,
                description=form.description.data,
                is_public=form.is_public.data,
            )
            db.session.commit()
            g.user.projects.append(project)
            db.session.commit()

        except IntegrityError:
            flash("Failed to create Project.", "danger")
            return render_template("users/project.html", form=form)

        flash("Successfully created project!", "success")

        return redirect(url_for("homepage"))

    return render_template("users/projects.html", form=form)


##############################################################################
# Plant List Pages
@app.route("/plant_lists", methods=["GET", "POST"])
def plant_lists():
    """Shows existing plant lists, and form to add new plant lists"""
    form = PlantListAddForm()

    if form.validate_on_submit():

        try:
            plant_list = PlantList.add(
                name=form.name.data,
                description=form.description.data,
                is_public=form.is_public.data,
            )
            db.session.commit()
            g.user.plant_lists.append(plant_list)
            db.session.commit()

        except IntegrityError:
            flash("Failed to create plant list.", "danger")
            return render_template("users/plant_list.html", form=form)

        flash("Successfully created plant list!", "success")

        return redirect(url_for("homepage"))

    return render_template("users/plant_lists.html", form=form)


##############################################################################
# Plot Pages
@app.route("/plots", methods=["GET", "POST"])
def plots_list():
    """Shows existing plots, and form to add new plots"""
    form = PlotAddForm()

    if form.validate_on_submit():

        try:
            plot = Plot.add(
                name=form.name.data,
                description=form.description.data,
                width=form.width.data,
                length=form.length.data,
                is_public=form.is_public.data,
            )
            db.session.commit()
            g.user.plots.append(plot)
            db.session.commit()

        except IntegrityError:
            flash("Failed to create plot.", "danger")
            return render_template("users/plot.html", form=form)

        flash("Successfully created plot!", "success")

        return redirect(url_for("homepage"))

    return render_template("users/plots.html", form=form)


###########################################################################
# Plant Pages


@app.route("/plants", methods=["GET"])
def plants_list():
    """Shows Plant search form and default plant table"""
    form = PlantSearchForm()

    # Default plant list. /plants/search route replaces this list when search is submitted.
    payload = {
        "token": TREFLE_API_KEY,
        "order[common_name]": "asc",
    }

    plants = requests.get(f"{API_BASE_URL}/plants", params=payload)
    plant_list = [plant for plant in plants.json()["data"]]

    return render_template("plants/list.html", form=form, plant_list=plant_list)


@app.route("/plants/<plant_slug>", methods=["GET"])
def plant_profile(plant_slug):
    """Shows specific plant page"""

    payload = {
        "token": TREFLE_API_KEY,
    }

    plant = requests.get(f"{API_BASE_URL}/plants/{plant_slug}", params=payload).json()[
        "data"
    ]
    if "main_species" in plant:
        main_species = plant["main_species"]
    else:
        main_species = plant
    # plant_list = [plant for plant in plants.json()["data"]]

    return render_template("plants/profile.html", main_species=main_species)


##############################################################################
# Trefle API Routes


@app.route("/api/plants/search", methods=["POST", "GET"])
def search_plants():
    """Lists all plants from Trefle API, 20 plants at a time"""
    form_data = request.json
    print("form_data", form_data)
    form = PlantSearchForm(obj=form_data)
    # print("TTTEEEESST", request.json["edible_parts"])

    if form.validate():
        # Intialize payload with api key
        payload = {"token": TREFLE_API_KEY}

        if "search" in form_data and form_data["search"] != "":
            search_term = form_data["search"]
            print("search_term", search_term)
            payload["q"] = search_term
            request_string = f"{API_BASE_URL}/plants/search"

        else:
            request_string = f"{API_BASE_URL}/plants"

        if "edible_part" in form_data:
            # payload["filter_not[image_url]"] = ("null",)
            # payload["filter_not[family_common_name]"] = ("null",)
            payload["filter_not[edible_part]"] = "null"

        if "nitrogen_fixation" in form_data:
            payload["filter_not[toxicity]"] = "null"

        print("REQUEST STRING:", request_string, payload)
        plants = requests.get(request_string, params=payload)
        # print("PLANTS DIR", dir(plants))
        print("PLANTS", plants.url)

        plant_list = [plant for plant in plants.json()["data"]]
        # raise
        return jsonify(plant_list)

    else:
        print("FAILURE TO VALIDATE", form.errors)
        response = {"errors": form.errors}
        return jsonify(response)


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask


@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers["Cache-Control"] = "public, max-age=0"
    return req
