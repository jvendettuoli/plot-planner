import os, requests, logging

logging.basicConfig(level=logging.DEBUG)
logging.debug("app.py start")


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

logging.debug("flask imported")

from functools import wraps
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy import or_

logging.debug("modules imported")


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

logging.debug("forms imported")

from models import (
    db,
    connect_db,
    User,
    Project,
    Plot,
    PlantList,
    Plant,
    Symbol,
    PlantLists_Plants,
    Plot_Cells_Symbols,
    default_plant_symbol,
)

logging.debug("models imported")

# from secret import TREFLE_API_KEY, FLASK_SECRET

logging.debug("secrets imported")


app = Flask(__name__)
logging.debug("app = Flask")

# Get DB_URI from environ variable or,
# if not set there, use development local db.
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgres:///plot_planner"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "defaultsecret")
toolbar = DebugToolbarExtension(app)

connect_db(app)
logging.debug("Database Modals connected")


# Trefle API base url
API_BASE_URL = "https://trefle.io/api/v1"
TREFLE_API_KEY = os.environ.get("TREFLE_API_KEY")
CURR_USER_KEY = "curr_user"


########################################################################
# User signup/login/logout
########################################################################


@app.before_request
def add_user_to_g():
    """If user is logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user to session."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user from sesssion."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


def check_authorized(func):
    """Checks if user is logged in while accessing view and redirects to homepage if not."""

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

    If form not valid, present form with errors.

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
            return redirect(url_for("user_content", user_id=user.id))

        flash("Invalid credentials.", "danger")

    return render_template("users/login.html", form=form)


@app.route("/logout")
def logout():
    """Logs user out and redirects to login."""

    do_logout()
    flash("User logged out!", "success")

    return redirect(url_for("login"))


########################################################################
# Homepage and About pages
########################################################################


@app.route("/")
def homepage():
    """Show homepage"""

    return render_template("home.html")


@app.route("/about")
def about():
    """Show homepage"""

    return render_template("about.html")


########################################################################
# User Routes
########################################################################


@app.route("/users/<int:user_id>", methods=["GET", "POST"])
@check_authorized
def user_profile(user_id):
    """Shows user profile page"""

    user = User.query.get_or_404(user_id)

    if user == g.user:
        return render_template("users/profile.html", user=user)

    else:
        flash("Users are only permitted to access their own profiles.", "danger")
        return redirect(url_for("login"))


@app.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@check_authorized
def edit_user(user_id):
    """Shows user profile page"""

    form = UserEditForm()
    user = User.query.get_or_404(user_id)

    if g.user != user:
        flash("Not authorized to view this page.", "danger")
        return redirect(url_for("homepage"))

    if form.validate_on_submit():
        user = User.authenticate(user.username, form.password.data)
        if user:
            try:
                user.edit(
                    form.username.data, form.email.data, form.image_url.data,
                )
            except (IntegrityError, InvalidRequestError) as e:
                db.session.rollback()
                flash("Username already taken", "danger")
                return redirect(url_for("edit_user", user_id=g.user.id))

            flash("Profile updates successful.", "success")
            return redirect(url_for("user_profile", user_id=user.id))
        else:
            flash("Password incorrect.", "danger")
            return redirect(url_for("edit_user", user_id=g.user.id))

    return render_template("users/edit.html", form=form, user=user)


@app.route("/users/<int:user_id>/content", methods=["GET", "POST"])
@check_authorized
def user_content(user_id):
    """Shows user content page, which is an overview of projects, plots, and plant lists saved to user's profile"""

    user = User.query.get_or_404(user_id)

    if g.user != user:
        flash("Not authorized to view this page.", "danger")
        return redirect(url_for("homepage"))

    form_plot = AddPlotForm()

    # Load in choices based on users currently connected components
    form_plot.plots.choices = [(plot.id, plot.name,) for plot in g.user.plots]

    form_plantlist = AddPlantListForm()
    form_plantlist.plantlists.choices = [
        (plantlist.id, plantlist.name,) for plantlist in g.user.plantlists
    ]

    form_project = AddProjectForm()
    form_project.projects.choices = [
        (project.id, project.name,) for project in g.user.projects
    ]

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


########################################################################
# Project Routes
########################################################################


@app.route("/projects", methods=["GET", "POST"])
@check_authorized
def add_projects():
    """Explains what projects are and shows form to add new projects. POST adds new project"""

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
                # is_public=form.is_public.data,
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
        return redirect(url_for("show_project", project_id=project.id))

    return render_template("projects/add.html", form=form)


@app.route("/projects/<int:project_id>", methods=["GET"])
@check_authorized
def show_project(project_id):
    """Show specific project"""

    project = Project.query.get_or_404(project_id)

    if g.user not in project.users:
        flash("Not authorized to view this page.", "danger")
        return redirect(url_for("homepage"))

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
@check_authorized
def edit_project(project_id):
    """Edit specific project"""

    project = Project.query.get_or_404(project_id)

    if g.user not in project.users:
        flash("Not authorized to view this page.", "danger")
        return redirect(url_for("homepage"))

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
                # is_public=form.is_public.data,
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
@check_authorized
def project_remove_plot(project_id, plot_id):
    """Remove specific plot from a project"""

    project = Project.query.get_or_404(project_id)
    plot = Plot.query.get_or_404(plot_id)

    project.plots.remove(plot)
    db.session.commit()

    return (f"Plot {plot_id} removed from Project {project_id} successfully.", 200)


@app.route("/projects/<int:project_id>/add/plot/<int:plot_id>", methods=["POST"])
@check_authorized
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
@check_authorized
def project_remove_plantlist(project_id, plantlist_id):
    """Remove specific plantlist from a project"""
    project = Project.query.get_or_404(project_id)
    plantlist = PlantList.query.get_or_404(plantlist_id)

    project.plantlists.remove(plantlist)
    db.session.commit()

    return (
        f"Plant List {plantlist_id} removed from Project {project_id} successfully.",
        200,
    )


@app.route(
    "/projects/<int:project_id>/add/plantlist/<int:plantlist_id>", methods=["POST"]
)
@check_authorized
def project_add_plantlist(project_id, plantlist_id):
    """Add specific plantlist to a project"""
    project = Project.query.get_or_404(project_id)
    plantlist = PlantList.query.get_or_404(plantlist_id)

    project.plantlists.append(plantlist)
    db.session.commit()

    return (
        f"Plant List {plantlist_id} connected to Project {project_id} successfully.",
        200,
    )


########################################################################
# Plot Routes
########################################################################


@app.route("/plots", methods=["GET", "POST"])
@check_authorized
def add_plots():
    """Explains what plots are and shows form to add new plots. POST adds new plot to user"""
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
                # is_public=form.is_public.data,
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

        return redirect(url_for("show_plot", plot_id=plot.id))

    return render_template("plots/add.html", form=form)


@app.route("/plots/<int:plot_id>", methods=["GET"])
@check_authorized
def show_plot(plot_id):
    """Show specific plot details"""

    plot = Plot.query.get_or_404(plot_id)
    if g.user not in plot.users:
        flash("Not authorized to view this page.", "danger")
        return redirect(url_for("homepage"))

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
@check_authorized
def edit_plot(plot_id):
    """Edit specific plant list"""
    plot = Plot.query.get_or_404(plot_id)
    if g.user not in plot.users:
        flash("Not authorized to view this page.", "danger")
        return redirect(url_for("homepage"))

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
                # is_public=form.is_public.data,
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

    flash(f"{plot.name} successfully deleted.", "success")
    return redirect(url_for("user_content", user_id=g.user.id))


@app.route("/plots/<int:plot_id>/remove/plantlist/<int:plantlist_id>", methods=["POST"])
@check_authorized
def plot_remove_plantlist(plot_id, plantlist_id):
    """Remove specific plantlist from a plot"""
    plot = Plot.query.get_or_404(plot_id)
    plantlist = PlantList.query.get_or_404(plantlist_id)

    plot.plantlists.remove(plantlist)
    db.session.commit()

    return (
        f"Plant List {plantlist_id} removed from Plot {plot_id} successfully.",
        200,
    )


@app.route("/plots/<int:plot_id>/add/plantlist/<int:plantlist_id>", methods=["POST"])
@check_authorized
def plot_add_plantlist(plot_id, plantlist_id):
    """Add specific plantlist to a plot"""
    plot = Plot.query.get_or_404(plot_id)
    plantlist = PlantList.query.get_or_404(plantlist_id)

    plot.plantlists.append(plantlist)
    db.session.commit()

    return (
        f"Plant List {plantlist_id} connected to Plot {plot_id} successfully.",
        200,
    )


@app.route(
    "/plots/<int:plot_id>/add/symbol/<int:plantlists_plants_id>/x/<int:cell_x>/y/<int:cell_y>",
    methods=["POST"],
)
@check_authorized
def plot_cell_add_symbol(plot_id, plantlists_plants_id, cell_x, cell_y):
    """Adds the plantlists_plants id to a plot cell, which effectively keeps the symbol updated even if changed via a plantlist"""

    plot_cells_symbols = Plot_Cells_Symbols.add(
        plot_id=plot_id,
        plantlists_plants_id=plantlists_plants_id,
        cell_x=cell_x,
        cell_y=cell_y,
    )
    db.session.commit()

    return (
        f"Plantlists_Plants ID {plantlists_plants_id} added to Plot cell {plot_cells_symbols.id} successfully.",
        200,
    )


@app.route(
    "/plots/<int:plot_id>/delete/cell/x/<int:cell_x>/y/<int:cell_y>", methods=["POST"],
)
@check_authorized
def plot_cell_delete_row(plot_id, cell_x, cell_y):
    """Deletes a cell symbol connection by deleting the row from database"""

    plot_cells_symbols = Plot_Cells_Symbols.query.filter(
        Plot_Cells_Symbols.plot_id == plot_id,
        Plot_Cells_Symbols.cell_x == cell_x,
        Plot_Cells_Symbols.cell_y == cell_y,
    ).delete()

    db.session.commit()

    return (
        f"Plot {plot_id} removed symbol from plot cell {cell_x},{cell_y} successfully.",
        200,
    )


########################################################################
# Plant List Routes
########################################################################


@app.route("/plantlists", methods=["GET", "POST"])
@check_authorized
def add_plantlists():
    """Shows existing plant lists, and form to add new plant lists. Post adds new Plant List"""
    form = PlantListAddForm()
    form.projects.choices = [(project.id, project.name,) for project in g.user.projects]
    form.plots.choices = [(plot.id, plot.name,) for plot in g.user.plots]

    if form.validate_on_submit():

        try:
            plantlist = PlantList.add(
                name=form.name.data,
                description=form.description.data,
                # is_public=form.is_public.data,
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
@check_authorized
def show_plantlist(plantlist_id):
    """Show specific plant list"""
    plantlist = PlantList.query.get_or_404(plantlist_id)
    if g.user not in plantlist.users:
        flash("Not authorized to view this page.", "danger")
        return redirect(url_for("homepage"))

    # In order to get the appropriate symbols for each plant on a per plantlist basis,
    # we get the plantlist_plants instance which houses the specific symbol for each
    # plant on a given plantlist
    plantlists_plants = PlantLists_Plants.query.filter(
        PlantLists_Plants.plantlist_id == plantlist_id
    ).all()

    # Map the symbols to the plants for use in generating on frontend
    plant_symbol_map = {item.plant_id: item.symbol for item in plantlists_plants}

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
        plant_symbol_map=plant_symbol_map,
        symbol_size="fa-4x",
    )


@app.route("/plantlists/<int:plantlist_id>/edit", methods=["GET", "POST"])
@check_authorized
def edit_plantlist(plantlist_id):
    """Edit specific plant list"""
    plantlist = PlantList.query.get_or_404(plantlist_id)
    if g.user not in plantlist.users:
        flash("Not authorized to view this page.", "danger")
        return redirect(url_for("homepage"))

    form = PlantListAddForm(obj=plantlist)
    form.projects.choices = [(project.id, project.name,) for project in g.user.projects]
    form.plots.choices = [(plot.id, plot.name,) for plot in g.user.plots]

    if form.validate_on_submit():

        try:
            plantlist.edit(
                name=form.name.data,
                description=form.description.data,
                # is_public=form.is_public.data,
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


@app.route("/plantlists/<int:plantlist_id>/delete", methods=["POST"])
@check_authorized
def delete_plantlist(plantlist_id):
    """Delete plant list"""
    plantlist = PlantList.query.get_or_404(plantlist_id)

    db.session.delete(plantlist)
    db.session.commit()

    return redirect(url_for("user_content", user_id=g.user.id))


@app.route("/plantlists/<int:plantlist_id>/add/plant/<int:plant_id>", methods=["POST"])
@check_authorized
def plantlist_add_plant(plantlist_id, plant_id):
    """Add specific plant to plantlist"""
    plant = Plant.query.get_or_404(plant_id)
    plantlist = PlantList.query.get_or_404(plantlist_id)

    plantlist.plants.append(plant)
    db.session.commit()

    return (
        f"Plant {plant_id} added to plantlist {plantlist_id} successfully.",
        200,
    )


@app.route(
    "/plantlists/<int:plantlist_id>/remove/plant/<int:plant_id>", methods=["POST"]
)
@check_authorized
def plantlist_remove_plant(plantlist_id, plant_id):
    """Add specific plant to plantlist"""
    plant = Plant.query.get_or_404(plant_id)
    plantlist = PlantList.query.get_or_404(plantlist_id)
    plantlists_plants = PlantLists_Plants.query.filter(
        PlantLists_Plants.plant_id == plant.id,
        PlantLists_Plants.plantlist_id == plantlist.id,
    ).one_or_none()

    plot_cells_symbols = Plot_Cells_Symbols.query.filter(
        Plot_Cells_Symbols.plantlists_plants_id == plantlists_plants.id
    ).delete()
    db.session.delete(plantlists_plants)
    db.session.commit()

    # return (
    #     f"Plant {plant_id} removed from plantlist {plantlist_id} successfully.",
    #     200,
    # )
    return redirect(url_for("show_plantlist", plantlist_id=plantlist.id))


@app.route(
    "/plantlists/<int:plantlist_id>/plant/<int:plant_id>/symbol/add", methods=["POST"]
)
@check_authorized
def add_symbol(plantlist_id, plant_id):
    """Creates symbol and add connection to a plant on plantlist page"""

    print("REQUEST", request.json)
    plantlists_plants = PlantLists_Plants.query.filter(
        PlantLists_Plants.plantlist_id == plantlist_id,
        PlantLists_Plants.plant_id == plant_id,
    ).first()

    # Check to see if they symbol has been created before, and use it as opposed to creating a duplicate
    symbol = Symbol.query.filter(Symbol.symbol == request.json["symbol"]).first()
    # If the symbol hasn't been created by anyone yet, create a new one
    if not symbol:
        try:
            symbol = Symbol.add(symbol=request.json["symbol"])
            db.session.commit()

        except IntegrityError as e:
            flash("Failed to create symbol.", "danger")
            return redirect(url_for("show_plantlist", plantlist_id=plantlist_id))

    # Update which symbol is connected to plant on plantlist
    plantlists_plants.edit(
        plantlist_id=plantlist_id, plant_id=plant_id, symbol_id=symbol.id
    )

    # return symbol for display on frontend
    return jsonify(symbol.symbol)


########################################################################
# Plant Routes
########################################################################


@app.route("/plants", methods=["GET"])
def plants_search_table():
    """Shows Plant search form and default plant table"""
    form = PlantSearchForm()

    # Default plant list. api/plants/search route replaces this list when search is submitted.
    payload = {
        "token": TREFLE_API_KEY,
    }

    plants = requests.get(f"{API_BASE_URL}/plants", params=payload)
    # Build list of plants to be generated into a plant table on frontend
    plantlist = [plant for plant in plants.json()["data"]]
    # Trefle returns links to the next set of plants in a search. We use this for pagination
    links = plants.json()["links"]

    return render_template(
        "plants/search_table.html", form=form, plantlist=plantlist, links=links
    )


@app.route("/plants/<plant_slug>", methods=["GET", "POST"])
def plant_profile(plant_slug):
    """Shows specific plant profile page"""

    payload = {
        "token": TREFLE_API_KEY,
    }

    trefle_plant = requests.get(
        f"{API_BASE_URL}/plants/{plant_slug}", params=payload
    ).json()["data"]
    # Some responses have data nested in "main_species"
    if "main_species" in trefle_plant:
        main_species = trefle_plant["main_species"]
    else:
        main_species = trefle_plant

    form = AddPlantListForm()

    # If user is logged in, they can add this plant to their plantlists
    # Otherwise ask them to signup/login.
    if g.user:
        plant = Plant.query.filter(Plant.trefle_id == main_species["id"]).one_or_none()

        if request.method == "POST":
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

        if plant:
            form.plantlists.choices = [
                (plantlist.id, plantlist.name,)
                for plantlist in g.user.plantlists
                if plantlist not in plant.plantlists
            ]

        else:
            form.plantlists.choices = [
                (plantlist.id, plantlist.name,) for plantlist in g.user.plantlists
            ]

    return render_template("plants/profile.html", main_species=main_species, form=form)


########################################################################
# Query Routes
########################################################################


@app.route("/query/<primary_type>/<int:primary_id>/<secondary_type>", methods=["GET"])
@check_authorized
def query_connections(primary_type, primary_id, secondary_type):
    """Returns JSON of connections based on request types and primary ID. Used for 
    dynamically populating connection lists and form options via Axios requests."""

    # Gets options to be placed in HTML select form. Only returns
    # options that are not currently connected to primary type
    def get_options(primary):
        return [
            (getattr(item, "id"), getattr(item, "name"))
            for item in getattr(g.user, secondary_type)
            if item not in getattr(primary, secondary_type)
        ]

    # Gets list items to be placed in HTML connected list. Only returns
    # items that are  currently connected to primary type
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


@app.route("/query/plantlist/<int:plantlist_id>", methods=["GET"])
@check_authorized
def query_plantlist(plantlist_id):
    """Returns plants from a plant list and a plant - symbol map. Currently used 
    for generating plant - symbol lists for plot design."""
    plantlist = PlantList.query.get_or_404(plantlist_id)
    plantlist_plants = PlantLists_Plants.query.filter(
        PlantLists_Plants.plantlist_id == plantlist_id
    ).all()

    plantlist_plants_symbols = []
    response = {
        "plantlist_plants_symbols": plantlist_plants_symbols,
    }
    for item in plantlist_plants:
        plant_data = {}
        plant_data["plantlist_plants_id"] = item.id
        plant_data["plant_id"] = item.plant.id
        plant_data["plant_name"] = item.plant.common_name.capitalize()
        plant_data["symbol"] = item.symbol.symbol
        plantlist_plants_symbols.append(plant_data)

    return response


@app.route("/query/plot_cells/<int:plot_id>", methods=["GET"])
@check_authorized
def query_plot_cells(plot_id):
    """Returns a specific plot's plot cell - symbol map. Currently used for 
    populating the correct symbol for each cell of a plot."""
    plot_cells_symbols = Plot_Cells_Symbols.query.filter(
        Plot_Cells_Symbols.plot_id == plot_id
    ).all()

    cells_symbols = []

    for item in plot_cells_symbols:
        plantlists_plants = PlantLists_Plants.query.get_or_404(
            item.plantlists_plants_id
        )
        symbol = plantlists_plants.symbol.symbol
        cell = {}
        cell["cell_x"] = item.cell_x
        cell["cell_y"] = item.cell_y
        cell["symbol"] = symbol
        cells_symbols.append(cell)

    return jsonify(cells_symbols)


########################################################################
# Trefle API Routes
########################################################################


@app.route("/api/plants/search", methods=["POST", "GET"])
def search_plants():
    """Lists all plants from Trefle API, 20 plants at a time"""
    form_data = request.json
    form = PlantSearchForm(obj=form_data)

    if form.validate():
        # Intialize payload with api key
        payload = {"token": TREFLE_API_KEY}

        # If the search filter was used, use the API's /search endpoint
        if "search" in form_data and form_data["search"][0] != "":
            search_term = form_data["search"][0]
            payload["q"] = search_term
            request_string = f"{API_BASE_URL}/plants/search"

        # Otherwise use /plants endpoint, which should only return main_species of
        # plants, not subspecies/varieties
        else:
            request_string = f"{API_BASE_URL}/plants"

        # For any of the filters applied, add them to the payload
        if "edible_part" in form_data:
            payload["filter[edible_part]"] = ",".join(form_data["edible_part"])

        if "flower_color" in form_data:
            payload["filter[flower_color]"] = ",".join(form_data["flower_color"])

        if "growth_months" in form_data:
            payload["filter[growth_months]"] = ",".join(form_data["growth_months"])

        if "bloom_months" in form_data:
            payload["filter[bloom_months]"] = ",".join(form_data["bloom_months"])

        if "fruit_months" in form_data:
            payload["filter[fruit_months]"] = ",".join(form_data["fruit_months"])

        if "ligneous_type" in form_data:
            payload["filter[ligneous_type]"] = ",".join(form_data["ligneous_type"])

        if "duration" in form_data:
            payload["filter[duration]"] = ",".join(form_data["duration"])

        if "vegetable" in form_data:
            payload["filter[vegetable]"] = "true"

        if "evergreen" in form_data:
            payload["filter[leaf_retention]"] = "true"

        # Create a request string "manually", as requests built in feature was replacing
        # characters and resulting in an error from API
        payload_str = "&".join("%s=%s" % (k, v) for k, v in payload.items())
        plants = requests.get(request_string, params=payload_str)

        plantlist = [plant for plant in plants.json()["data"]]
        links = plants.json()["links"]
        return jsonify(plantlist, links)

    else:
        response = {"errors": form.errors}
        return jsonify(response)


@app.route("/api/plants/pagination", methods=["POST"])
def plant_pagination():
    """Allows for navigation through Trefle's Pagination routes. Takes in the 
    agination link and adds API Key"""

    pagination_link = request.json["pagination_link"][7:]
    auth_pagination_link = pagination_link + f"&token={TREFLE_API_KEY}"

    # requests next set of plants
    plants = requests.get(f"{API_BASE_URL}{auth_pagination_link}")

    plantlist = [plant for plant in plants.json()["data"]]
    links = plants.json()["links"]

    return jsonify(plantlist, links)


logging.debug("End of app.py")


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask


# @app.after_request
# def add_header(req):
#     """Add non-caching headers on every request."""

#     req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     req.headers["Pragma"] = "no-cache"
#     req.headers["Expires"] = "0"
#     req.headers["Cache-Control"] = "public, max-age=0"
#     return req
