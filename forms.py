from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    IntegerField,
    PasswordField,
    TextAreaField,
    SelectMultipleField,
    BooleanField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    InputRequired,
    URL,
    Optional,
    NumberRange,
)


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField("Username", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[Length(min=6)])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[Length(min=6)])


class UserEditForm(FlaskForm):
    """Form for editing users."""

    username = StringField("Username")
    email = StringField("E-mail", validators=[Email(), Optional()])
    image_url = StringField("Image URL", validators=[URL(), Optional()])
    password = PasswordField("Current Password", validators=[InputRequired()])


class PlantSearchForm(FlaskForm):
    """Form for searching plants."""

    search = StringField("Search", validators=[Optional()])
    # edible_parts = SelectMultipleField(
    #     "Edible Parts",
    #     choices=[
    #         ("roots", "Roots"),
    #         ("stem", "Stem"),
    #         ("leaves", "Leaves"),
    #         ("flowers", "Flowers"),
    #         ("fruits", "Fruits"),
    #         ("seeds", "Seeds"),
    #     ],
    #     validators=[Optional()],
    # )
    edible_part = BooleanField(
        "Only show plants some edible part?", validators=[Optional()]
    )
    nitrogen_fixation = BooleanField("Nitrogen fixing?", validators=[Optional()])


class ProjectAddForm(FlaskForm):
    """Form for adding new project."""

    name = StringField(
        "Project Name", validators=[DataRequired(message="Project name required.")]
    )
    description = TextAreaField("Description", validators=[Optional()])
    is_public = BooleanField(
        "Would you like this project to be available for other users to copy?",
        validators=[Optional()],
        default=False,
    )


class PlantListAddForm(FlaskForm):
    """Form for adding new plant list."""

    name = StringField(
        "Plant List Name",
        validators=[DataRequired(message="Plant List name required.")],
    )
    description = TextAreaField("Description", validators=[Optional()])
    is_public = BooleanField(
        "Would you like this list to be available for other users to copy?",
        validators=[Optional()],
        default=False,
    )


class PlotAddForm(FlaskForm):
    """Form for adding new plot."""

    name = StringField(
        "Plot Name", validators=[DataRequired(message="Plot name required.")]
    )
    description = TextAreaField("Description", validators=[Optional()])
    width = IntegerField(
        "Width (to the nearest foot)",
        validators=[
            DataRequired(
                message="Please estimage the plot width to the nearest whole foot."
            ),
            NumberRange(min=1, message="Width cannot be less than 1 foot."),
        ],
    )
    length = IntegerField(
        "Length (to the nearest foot)",
        validators=[
            DataRequired(
                message="Please estimage the plot length to the nearest whole foot."
            ),
            NumberRange(min=1, message="Width cannot be less than 1 foot."),
        ],
    )
    is_public = BooleanField(
        "Would you like this list to be available for other users to copy?",
        validators=[Optional()],
        default=False,
    )
