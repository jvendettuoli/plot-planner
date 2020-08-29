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
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy import or_

from forms import (
    UserAddForm,
    LoginForm,
    UserEditForm,
    PlantSearchForm,
    ProjectAddForm,
    PlotAddForm,
    PlantListAddForm,
    AddPlotForm,
    AddProjectForm,
    AddPlantListForm,
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

# db.drop_all()
# db.create_all()

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
# User Routes


@app.route("/users/<int:user_id>", methods=["GET", "POST"])
def user_profile(user_id):
    """Shows user profile page"""

    user = User.query.get_or_404(user_id)

    if user:
        return render_template("users/profile.html", user=user)

    else:
        flash("Must be logged in to see user profile.")
        redirect(url_for("login"))


@app.route("/users/edit", methods=["GET", "POST"])
def edit_user():
    """Shows user profile page"""

    form = UserEditForm()
    user = g.user

    if form.validate_on_submit():
        user = User.authenticate(user.username, form.password.data)
        if user:
            try:
                user.edit(
                    form.username.data, form.email.data, form.image_url.data,
                )

            except IntegrityError:
                flash("Username already taken", "danger")
                return redirect(url_for("edit_user"))

            flash("Profile updates successful.", "success")
            return redirect(url_for("user_profile", user_id=user.id))

        else:
            flash("Password incorrect.", "danger")
            return redirect(url_for("edit_user"))

    return render_template("users/edit.html", form=form, user=user)


@app.route("/users/<int:user_id>/content", methods=["GET", "POST"])
@check_authorized
def user_content(user_id):
    """Shows user content page, which is an overview of projects, plots, and plant lists saved to user's profile"""

    user = User.query.get_or_404(user_id)

    form_plot = AddPlotForm()
    form_plot.plots.choices = [(plot.id, plot.name,) for plot in g.user.plots]
    form_plantlist = AddPlantListForm()
    form_plantlist.plantlists.choices = [
        (plantlist.id, plantlist.name,) for plantlist in g.user.plantlists
    ]

    form_project = AddProjectForm()
    form_project.projects.choices = [
        (project.id, project.name,) for project in g.user.projects
    ]

    if g.user.id != user.id:
        flash("Not authorized to view this page.", "danger")
        return redirect(url_for("homepage"))

    return render_template(
        "users/content.html",
        user=user,
        form_plot=form_plot,
        form_plantlist=form_plantlist,
        form_project=form_project,
    )


@app.route("/users/delete", methods=["POST"])
@check_authorized
def delete_user():
    """Delete user"""
    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect(url_for("signup"))


##############################################################################
# Project Routes
@app.route("/projects", methods=["GET", "POST"])
def add_projects():
    """Explains what projects are and shows form to add new projects"""
    form = ProjectAddForm()
    form.plots.choices = [(plot.id, plot.name,) for plot in g.user.plots]
    form.plantlists.choices = [
        (plantlist.id, plantlist.name,) for plantlist in g.user.plantlists
    ]
    if form.validate_on_submit():

        try:
            project = Project.add(
                name=form.name.data,
                description=form.description.data,
                is_public=form.is_public.data,
            )
            db.session.commit()
            g.user.projects.append(project)

            # Append selected plots to the project
            for plot in form.plots.data:
                plot = Plot.query.get(plot)
                project.plots.append(plot)
            # Append selected plant list to the project
            for plantlist in form.plantlists.data:
                plantlist = PlantList.query.get(plantlist)
                project.plantlists.append(plantlist)

            db.session.commit()

        except IntegrityError:
            flash("Failed to create Project.", "danger")
            return render_template("projects/add.html", form=form)

        flash("Successfully created project!", "success")

        return redirect(url_for("homepage"))

    return render_template("projects/add.html", form=form)


@app.route("/projects/<int:project_id>", methods=["GET"])
def show_project(project_id):
    """Show specific project"""

    project = Project.query.get_or_404(project_id)

    form_plot = AddPlotForm()
    form_plot.plots.choices = [
        (plot.id, plot.name,) for plot in g.user.plots if plot not in project.plots
    ]
    form_plantlist = AddPlantListForm()
    form_plantlist.plantlists.choices = [
        (plantlist.id, plantlist.name,)
        for plantlist in g.user.plantlists
        if plantlist not in project.plantlists
    ]

    return render_template(
        "projects/show.html",
        form_plot=form_plot,
        form_plantlist=form_plantlist,
        project=project,
    )


@app.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
def edit_project(project_id):
    """Edit specific project"""

    project = Project.query.get_or_404(project_id)
    form = ProjectAddForm(obj=project)
    form.plantlists.choices = [
        (plantlist.id, plantlist.name,) for plantlist in g.user.plantlists
    ]
    form.plots.choices = [(plot.id, plot.name,) for plot in g.user.plots]

    if form.validate_on_submit():

        try:
            project.edit(
                name=form.name.data,
                description=form.description.data,
                is_public=form.is_public.data,
            )
            db.session.commit()
            g.user.projects.append(project)

            # Append selected plots to the project
            for plot in form.plots.data:
                plot = Plot.query.get(plot)
                project.plots.append(plot)
            # Append plot to selected projects
            for plantlist in form.plantlists.data:
                plantlist = PlantList.query.get(plantlist)
                project.plantlists.append(plantlist)

            db.session.commit()

        except IntegrityError:
            flash("Failed to edit project.", "danger")
            return render_template("projects/edit.html", form=form, project=project)

        flash("Successfully edited project!", "success")

        return redirect(url_for("show_project", project_id=project.id))

    return render_template("projects/edit.html", form=form, project=project)


@app.route("/projects/<int:project_id>/delete", methods=["POST"])
@check_authorized
def delete_project(project_id):
    """Delete plant list"""
    project = Project.query.get_or_404(project_id)

    db.session.delete(project)
    db.session.commit()

    return redirect(url_for("user_content", user_id=g.user.id))


@app.route("/projects/<int:project_id>/remove/plot/<int:plot_id>", methods=["POST"])
def project_remove_plot(project_id, plot_id):
    """Remove specific plot from a project"""

    project = Project.query.get_or_404(project_id)
    plot = Plot.query.get_or_404(plot_id)

    project.plots.remove(plot)
    db.session.commit()

    return (f"Plot {plot_id} remove from Project {project_id} successfully.", 200)


@app.route("/projects/<int:project_id>/add/plot/<int:plot_id>", methods=["POST"])
def project_add_plot(project_id, plot_id):
    """Add specific plot to a project"""

    project = Project.query.get_or_404(project_id)
    plot = Plot.query.get_or_404(plot_id)

    project.plots.append(plot)
    db.session.commit()

    return (f"Plot {plot_id} connected to Project {project_id} successfully.", 200)


@app.route(
    "/projects/<int:project_id>/remove/plantlist/<int:plantlist_id>", methods=["POST"]
)
def project_remove_plantlist(project_id, plantlist_id):
    """Remove specific plantlist from a project"""
    project = Project.query.get_or_404(project_id)
    plantlist = PlantList.query.get_or_404(plantlist_id)

    project.plantlists.remove(plantlist)
    db.session.commit()

    return (
        f"Plant List {plantlist_id} remove from Project {project_id} successfully.",
        200,
    )


@app.route(
    "/projects/<int:project_id>/add/plantlist/<int:plantlist_id>", methods=["POST"]
)
def project_add_plantlist(project_id, plantlist_id):
    """Add specific plantlist to a project"""
    project = Project.query.get_or_404(project_id)
    plantlist = PlantList.query.get_or_404(plantlist_id)

    project.plantlists.append(plantlist)
    db.session.commit()

    return (
        f"Plant List {plantlist_id} added to project {project_id} successfully.",
        200,
    )


##############################################################################
# Plant List Routes
@app.route("/plantlists", methods=["GET", "POST"])
def add_plantlists():
    """Shows existing plant lists, and form to add new plant lists"""
    form = PlantListAddForm()
    form.projects.choices = [(project.id, project.name,) for project in g.user.projects]
    form.plots.choices = [(plot.id, plot.name,) for plot in g.user.plots]

    if form.validate_on_submit():

        try:
            plantlist = PlantList.add(
                name=form.name.data,
                description=form.description.data,
                is_public=form.is_public.data,
            )
            db.session.commit()
            g.user.plantlists.append(plantlist)

            # Append selected plots to the project
            for plot in form.plots.data:
                plot = Plot.query.get(plot)
                plantlist.plots.append(plot)
            # Append plot to selected projects
            for project in form.projects.data:
                project = Project.query.get(project)
                plantlist.projects.append(project)

            db.session.commit()

        except IntegrityError:
            flash("Failed to create plant list.", "danger")
            return render_template("plantlists/add.html", form=form)

        flash("Successfully created plant list!", "success")

        return redirect(url_for("show_plantlist", plantlist_id=plantlist.id))

    return render_template("plantlists/add.html", form=form)


@app.route("/plantlists/<int:plantlist_id>", methods=["GET"])
def show_plantlist(plantlist_id):
    """Show specific plant list"""
    plantlist = PlantList.query.get_or_404(plantlist_id)

    form_plot = AddPlotForm()
    form_plot.plots.choices = [
        (plot.id, plot.name,) for plot in g.user.plots if plot not in plantlist.plots
    ]
    form_project = AddProjectForm()
    form_project.projects.choices = [
        (project.id, project.name,)
        for project in g.user.projects
        if project not in plantlist.projects
    ]

    return render_template(
        "plantlists/show.html",
        form_plot=form_plot,
        form_project=form_project,
        plantlist=plantlist,
    )


@app.route("/plantlists/<int:plantlist_id>/edit", methods=["GET", "POST"])
def edit_plantlist(plantlist_id):
    """Edit specific plant list"""
    plantlist = PlantList.query.get_or_404(plantlist_id)
    form = PlantListAddForm(obj=plantlist)
    form.projects.choices = [(project.id, project.name,) for project in g.user.projects]
    form.plots.choices = [(plot.id, plot.name,) for plot in g.user.plots]

    if form.validate_on_submit():

        try:
            plantlist.edit(
                name=form.name.data,
                description=form.description.data,
                is_public=form.is_public.data,
            )
            db.session.commit()
            g.user.plantlists.append(plantlist)

            # Append selected plots to the project
            for plot in form.plots.data:
                plot = Plot.query.get(plot)
                plantlist.plots.append(plot)
            # Append plot to selected projects
            for project in form.projects.data:
                project = Project.query.get(project)
                plantlist.projects.append(project)

            db.session.commit()

        except IntegrityError:
            flash("Failed to edit plant list.", "danger")
            return render_template(
                "plantlists/edit.html", form=form, plantlist=plantlist
            )

        flash("Successfully edited plant list!", "success")

        return redirect(url_for("show_plantlist", plantlist_id=plantlist.id))

    return render_template("plantlists/edit.html", form=form, plantlist=plantlist)


@app.route("/plantlists/<int:plantlist_id>/add/plant/<int:plant_id>", methods=["POST"])
def plantlist_add_plant(plantlist_id, plant_id):
    """Add specific plant to plantlist"""
    plant = Plant.query.get_or_404(plot_id)
    plantlist = PlantList.query.get_or_404(plantlist_id)

    plantlist.plants.append(plant)
    db.session.commit()

    return (
        f"Plant {plant_id} added to plantlist {plantlist_id} successfully.",
        200,
    )


@app.route("/plantlists/<int:plantlist_id>/delete", methods=["POST"])
@check_authorized
def delete_plantlist(plantlist_id):
    """Delete plant list"""
    plantlist = PlantList.query.get_or_404(plantlist_id)

    db.session.delete(plantlist)
    db.session.commit()

    return redirect(url_for("user_content", user_id=g.user.id))


##############################################################################
# Plot Routes
@app.route("/plots", methods=["GET", "POST"])
def add_plots():
    """Explains what plots are and shows form to add new plots"""
    form = PlotAddForm()
    form.projects.choices = [(project.id, project.name,) for project in g.user.projects]

    form.plantlists.choices = [
        (plantlist.id, plantlist.name,) for plantlist in g.user.plantlists
    ]

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

            # Append plot to selected projects
            for project in form.projects.data:
                project = Project.query.get(project)
                plot.projects.append(project)
            # Append selected plant list to the project
            for plantlist in form.plantlists.data:
                plantlist = PlantList.query.get(plantlist)
                plot.plantlists.append(plantlist)

            db.session.commit()

        except IntegrityError:
            flash("Failed to create plot.", "danger")
            return render_template("plots/add.html", form=form)

        flash("Successfully created plot!", "success")

        return redirect(url_for("homepage"))

    return render_template("plots/add.html", form=form)


@app.route("/plots/<int:plot_id>", methods=["GET"])
def show_plot(plot_id):
    """Show specific plot details"""

    plot = Plot.query.get_or_404(plot_id)

    form_plantlist = AddPlantListForm()
    form_plantlist.plantlists.choices = [
        (plantlist.id, plantlist.name,)
        for plantlist in g.user.plantlists
        if plantlist not in plot.plantlists
    ]
    form_project = AddProjectForm()
    form_project.projects.choices = [
        (project.id, project.name,)
        for project in g.user.projects
        if project not in plot.projects
    ]

    return render_template(
        "plots/show.html",
        form_plantlist=form_plantlist,
        form_project=form_project,
        plot=plot,
    )


@app.route("/plots/<int:plot_id>/edit", methods=["GET", "POST"])
def edit_plot(plot_id):
    """Edit specific plant list"""
    plot = Plot.query.get_or_404(plot_id)
    form = PlotAddForm(obj=plot)
    form.projects.choices = [(project.id, project.name,) for project in g.user.projects]
    form.plantlists.choices = [
        (plantlist.id, plantlist.name,) for plantlist in g.user.plantlists
    ]

    if form.validate_on_submit():

        try:
            plot.edit(
                name=form.name.data,
                description=form.description.data,
                width=form.width.data,
                length=form.length.data,
                is_public=form.is_public.data,
            )
            db.session.commit()
            g.user.plots.append(plot)

            # Append selected plantlists to the plot
            for plantlist in form.plantlists.data:
                plantlist = PlantList.query.get(plantlist)
                plot.plantlists.append(plantlist)
            # Append selected projects to the plot
            for project in form.projects.data:
                project = Project.query.get(project)
                plot.projects.append(project)

            db.session.commit()

        except IntegrityError:
            flash("Failed to edit plot.", "danger")
            return render_template("plots/edit.html", form=form, plot=plot)

        flash("Successfully edited plot!", "success")

        return redirect(url_for("show_plot", plot_id=plot.id))

    return render_template("plots/edit.html", form=form, plot=plot)


@app.route("/plots/<int:plot_id>/delete", methods=["POST"])
@check_authorized
def delete_plot(plot_id):
    """Delete plot"""
    plot = Plot.query.get_or_404(plot_id)

    db.session.delete(plot)
    db.session.commit()

    flash(f"{plot.name} successfully deleted.")

    return redirect(url_for("user_content", user_id=g.user.id))


@app.route("/plots/<int:plot_id>/remove/plantlist/<int:plantlist_id>", methods=["POST"])
def plot_remove_plantlist(plot_id, plantlist_id):
    """Remove specific plantlist from a plot"""
    plot = Plot.query.get_or_404(plot_id)
    plantlist = PlantList.query.get_or_404(plantlist_id)

    plot.plantlists.remove(plantlist)
    db.session.commit()

    return (
        f"Plant List {plantlist_id} removed from plot {plot_id} successfully.",
        200,
    )


@app.route("/plots/<int:plot_id>/add/plantlist/<int:plantlist_id>", methods=["POST"])
def plot_add_plantlist(plot_id, plantlist_id):
    """Add specific plantlist to a plot"""
    plot = Plot.query.get_or_404(plot_id)
    plantlist = PlantList.query.get_or_404(plantlist_id)

    plot.plantlists.append(plantlist)
    db.session.commit()

    return (
        f"Plant List {plantlist_id} added to plot {plot_id} successfully.",
        200,
    )


###########################################################################
# Plant Routes


@app.route("/plants", methods=["GET"])
def plants_search_table():
    """Shows Plant search form and default plant table"""
    form = PlantSearchForm()

    # Default plant list. api/plants/search route replaces this list when search is submitted.
    payload = {
        "token": TREFLE_API_KEY,
        "order[common_name]": "asc",
    }

    plants = requests.get(f"{API_BASE_URL}/plants", params=payload)
    print(plants.json())
    plantlist = [plant for plant in plants.json()["data"]]
    links = plants.json()["links"]

    return render_template(
        "plants/search_table.html", form=form, plantlist=plantlist, links=links
    )


@app.route("/plants/<plant_slug>", methods=["GET", "POST"])
def plant_profile(plant_slug):
    """Shows specific plant page"""

    form = AddPlantListForm()

    payload = {
        "token": TREFLE_API_KEY,
    }

    trefle_plant = requests.get(
        f"{API_BASE_URL}/plants/{plant_slug}", params=payload
    ).json()["data"]
    if "main_species" in trefle_plant:
        main_species = trefle_plant["main_species"]
    else:
        main_species = trefle_plant

    plant = Plant.query.filter(Plant.trefle_id == main_species["id"]).one_or_none()
    print("PLANT @@@@@@@@@@@@@", plant)
    print("PLANT @@@@@@@@@@@@@", plant.plantlists)
    print("PLANT @@@@@@@@@@@@@", g.user.plantlists)

    if plant:
        form.plantlists.choices = [
            (plantlist.id, plantlist.name,)
            for plantlist in g.user.plantlists
            if plantlist not in plant.plantlists
        ]

    else:
        print("ELSE")
        form.plantlists.choices = [
            (plantlist.id, plantlist.name,) for plantlist in g.user.plantlists
        ]

    if request.method == "POST":
        print("POST METHOD")
        # print(main_species)
        if not plant:

            try:
                plant = Plant.add(
                    trefle_id=main_species["id"],
                    slug=main_species["slug"],
                    common_name=main_species["common_name"],
                    scientific_name=main_species["scientific_name"],
                    family=main_species["family"],
                    family_common_name=main_species["family_common_name"],
                    image_url=main_species["image_url"],
                )

                db.session.commit()

            except IntegrityError:
                flash("Failed to create plant.", "danger")
                return render_template(
                    "plants/profile.html", main_species=main_species, form=form
                )

        # Append selected plantlists to the plant
        for plantlist in form.plantlists.data:
            plantlist = PlantList.query.get(plantlist)
            plant.plantlists.append(plantlist)

        db.session.commit()

    return render_template("plants/profile.html", main_species=main_species, form=form)


##############################################################################
# Query Routes
@app.route("/query/<primary_type>/<int:primary_id>/<secondary_type>", methods=["GET"])
def query_connections(primary_type, primary_id, secondary_type):
    """Returns JSON of connections based on request types and primary ID. Used for dynamically populating connection lists and form options via JS requests."""

    def get_options(primary):
        return [
            (getattr(item, "id"), getattr(item, "name"))
            for item in getattr(g.user, secondary_type)
            if item not in getattr(primary, secondary_type)
        ]

    def get_list(primary):
        return [
            (getattr(item, "id"), getattr(item, "name"))
            for item in getattr(primary, secondary_type)
        ]

    if primary_type == "project":
        project = Project.query.get_or_404(primary_id)
        form_options = get_options(project)
        list_items = get_list(project)

    elif primary_type == "plot":
        plot = Plot.query.get_or_404(primary_id)
        form_options = get_options(plot)
        list_items = get_list(plot)

    elif primary_type == "plantlist":
        plantlist = PlantList.query.get_or_404(primary_id)
        form_options = get_options(plantlist)
        list_items = get_list(plantlist)

    return jsonify({"options": form_options, "list_items": list_items})


##############################################################################
# Trefle API Routes


@app.route("/api/plants/search", methods=["POST", "GET"])
def search_plants():
    """Lists all plants from Trefle API, 20 plants at a time"""
    form_data = request.json
    print("form_data", form_data)
    form = PlantSearchForm(obj=form_data)

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

        plantlist = [plant for plant in plants.json()["data"]]
        # raise
        links = plants.json()["links"]
        return jsonify(plantlist, links)

    else:
        print("FAILURE TO VALIDATE", form.errors)
        response = {"errors": form.errors}
        return jsonify(response)


@app.route("/api/plants/pagination", methods=["POST"])
def plant_pagination():
    """Allows for navigation through Trefle's Pagination routes. Takes in the pagination link and adds API Key"""

    pagination_link = request.json["pagination_link"][7:]
    auth_pagination_link = pagination_link + f"&token={TREFLE_API_KEY}"
    print(auth_pagination_link)

    plants = requests.get(f"{API_BASE_URL}{auth_pagination_link}")
    print("RES", plants)
    print("RES", plants.json())

    plantlist = [plant for plant in plants.json()["data"]]
    links = plants.json()["links"]

    return jsonify(plantlist, links)


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
