"""SQLAlchemy models for Plot Planner."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class Plant(db.Model):
    """Plant Model - handles storing a subset of the Trefle API data for each plant added to a plant list.
    Methods for adding a new plant."""

    __tablename__ = "plants"

    id = db.Column(db.Integer, primary_key=True)
    trefle_id = db.Column(db.Integer, nullable=False, unique=True)
    slug = db.Column(db.Text, nullable=False)
    common_name = db.Column(db.Text)
    scientif_name = db.Column(db.Text)
    family = db.Column(db.Text)
    family_common_name = db.Column(db.Text)
    image_url = db.Column(db.Text)


class User(db.Model):
    """User Model - handles users in the database.
    Methods for signing up a new user, authenticating existing user 
    and editing an existing user."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    image_url = db.Column(db.Text, default="/static/images/default-pic.png")
    password = db.Column(db.Text, nullable=False)

    projects = db.relationship("Project", secondary="users_projects", backref="users")
    plots = db.relationship("Plot", secondary="users_plots", backref="users")
    plantlists = db.relationship(
        "PlantList", secondary="users_plantlists", backref="users"
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user. Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")

        user = User(username=username, email=email, password=hashed_pwd)

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    def edit(self, username, email, image_url):
        """Edit user's profile information"""
        self.username = username or self.username
        self.email = email or self.email
        self.image_url = image_url or self.image_url
        db.session.add(self)
        db.session.commit()


class Project(db.Model):
    """Projects Model - handles projects for users."""

    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean)

    plots = db.relationship("Plot", secondary="projects_plots", backref="projects")
    plantlists = db.relationship(
        "PlantList", secondary="projects_plantlists", backref="projects"
    )

    @classmethod
    def add(cls, name, description="No project description.", is_public=False):
        """Adds new project for user."""

        project = Project(name=name, description=description, is_public=is_public)

        db.session.add(project)

        return project


class PlantList(db.Model):
    """PlantList Model - handles plant lists for users."""

    __tablename__ = "plantlists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean)

    @classmethod
    def add(cls, name, description="No plant list description.", is_public=False):
        """Adds new plant list for user."""

        plant_list = PlantList(name=name, description=description, is_public=is_public)

        db.session.add(plant_list)

        return plant_list


class Plot(db.Model):
    """Plot Model - handles plots for users."""

    __tablename__ = "plots"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    width = db.Column(db.Integer, nullable=False)
    length = db.Column(db.Integer, nullable=False)
    is_public = db.Column(db.Boolean)

    @classmethod
    def add(
        cls, name, width, length, description="No plot description.", is_public=False
    ):
        """Adds new plot for user."""

        plot = Plot(
            name=name,
            description=description,
            width=width,
            length=length,
            is_public=is_public,
        )

        db.session.add(plot)

        return plot


class Users_Projects(db.Model):
    """Through table for user's projects."""

    __tablename__ = "users_projects"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))


class Users_PlantLists(db.Model):
    """Through table for user's plant lists."""

    __tablename__ = "users_plantlists"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    plant_list_id = db.Column(db.Integer, db.ForeignKey("plantlists.id"))


class Users_Plots(db.Model):
    """Through table for user's plots."""

    __tablename__ = "users_plots"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    plot_id = db.Column(db.Integer, db.ForeignKey("plots.id"))


class Projects_PlantLists(db.Model):
    """Through table for projects' plants lists."""

    __tablename__ = "projects_plantlists"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))
    plant_list_id = db.Column(db.Integer, db.ForeignKey("plantlists.id"))


class Projects_Plots(db.Model):
    """Through table for projects' plots."""

    __tablename__ = "projects_plots"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))
    plot_id = db.Column(db.Integer, db.ForeignKey("plots.id"))


class Plots_PlantLists(db.Model):
    """Through table for plot's lists."""

    __tablename__ = "plots_plantlists"

    id = db.Column(db.Integer, primary_key=True)
    plot_id = db.Column(db.Integer, db.ForeignKey("plots.id"))
    plant_list_id = db.Column(db.Integer, db.ForeignKey("plantlists.id"))


class PlantLists_Plants(db.Model):
    """Through table for plant lists's plants."""

    __tablename__ = "plantlists_plants"

    id = db.Column(db.Integer, primary_key=True)
    plant_list_id = db.Column(db.Integer, db.ForeignKey("plantlists.id"))
    plant_id = db.Column(db.Integer, db.ForeignKey("plants.id"))


def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)

