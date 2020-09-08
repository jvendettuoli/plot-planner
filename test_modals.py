"""View Tests"""

import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError


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
    Projects_Plots,
    Projects_PlantLists,
    Plots_PlantLists,
    Users_Projects,
    Users_Plots,
    Users_PlantLists,
)
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

os.environ["DATABASE_URL"] = "postgresql:///plot_planner_test"

from app import app, CURR_USER_KEY
from secret import TREFLE_API_KEY, FLASK_SECRET

db.create_all()

app.config["WTF_CSRF_ENABLED"] = False


class ModalsTestCase(TestCase):
    """Test views for users"""

    def setUp(self):
        """Create test client, add sample data"""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(
            username="testuser", email="test@test.com", password="testpw",
        )
        self.testuser_id = 100
        self.testuser.id = self.testuser_id

        self.testproject = Project(
            name="Project_Test", description="Project_Test test description.",
        )

        self.testproject_id = 110
        self.testproject.id = self.testproject_id
        db.session.add(self.testproject)

        self.testplot = Plot(
            name="Plot_Test",
            width=5,
            length=10,
            description="Plot_Test test description.",
        )

        self.testplot_id = 120
        self.testplot.id = self.testplot_id
        db.session.add(self.testplot)

        self.testplantlist = PlantList(
            name="plantlist_Test", description="plantlist_Test test description.",
        )
        self.testplantlist_id = 130
        self.testplantlist.id = self.testplantlist_id
        db.session.add(self.testplantlist)

        self.testplant = Plant(
            trefle_id=1231,
            slug="plantus-slugs1",
            common_name="common plant1",
            scientific_name="plantus testus1",
            family="Plantaceae1",
            family_common_name="Plant Family1",
        )

        self.testplant_id = 140
        self.testplant.id = self.testplant_id

        db.session.add(self.testplant)

        self.testsymbol = Symbol(
            symbol="<i class='symbol fas fa-seedling' style='color:#228B22;'></i>"
        )

        self.testsymbol_id = 1
        self.testsymbol.id = self.testsymbol_id
        db.session.add(self.testsymbol)

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    # #####################################################
    # Plant Modal
    # #####################################################

    def test_plant_model(self):
        plant = Plant(
            trefle_id=123,
            slug="plantus-slugs",
            common_name="common plant",
            scientific_name="plantus testus",
            family="Plantaceae",
            family_common_name="Plant Family",
        )

        db.session.add(plant)
        db.session.commit()

        plant = Plant.query.filter(Plant.trefle_id == 123).first()
        self.assertIsNotNone(plant)

    def test_plant_invalid(self):
        plant = Plant(
            trefle_id=123,
            slug=None,
            common_name="common plant",
            scientific_name="plantus testus",
            family="Plantaceae",
            family_common_name="Plant Family",
        )

        db.session.add(plant)

        with self.assertRaises(IntegrityError) as context:
            db.session.commit()

    def test_plant_add(self):
        plant = Plant.add(
            trefle_id=123,
            slug="plantus-slugs",
            common_name="common plant",
            scientific_name="plantus testus",
            family="Plantaceae",
            family_common_name="Plant Family",
        )

        db.session.commit()

        plant = Plant.query.filter(Plant.slug == "plantus-slugs").first()

        self.assertIsNotNone(plant)

    # #####################################################
    # User Modal
    # #####################################################

    def test_user_model(self):
        u = User(
            email="newtest@test.com", username="newtestuser", password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        user = User.query.filter(User.username == "testuser").one_or_none()

        self.assertIsNotNone(user)

    def test_user_model_existing_user(self):
        u = User(email="test@test.com", username="testuser", password="HASHED_PASSWORD")

        db.session.add(u)

        with self.assertRaises(IntegrityError) as context:
            db.session.commit()

    def test_user_signup(self):
        u_test = User.signup("testtesttest", "testtest@test.com", "password")
        uid = 99999
        u_test.id = uid
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, "testtesttest")
        self.assertEqual(u_test.email, "testtest@test.com")
        self.assertNotEqual(u_test.password, "password")
        # Bcrypt strings should start with $2b$
        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        invalid = User.signup(None, "test@test.com", "password")
        uid = 123456789
        invalid.id = uid
        with self.assertRaises(IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid = User.signup("testtest", None, "password")
        uid = 123789
        invalid.id = uid
        with self.assertRaises(IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup(
                "testtest", "email@email.com", "",
            )

        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", None)

    def test_valid_authentication(self):
        u = User.authenticate(self.testuser.username, "testpw")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.testuser_id)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.testuser.username, "badpassword"))

    def test_user_edit(self):
        self.testuser.edit("edit_username", "edit@email.com", None)

        self.assertEqual(self.testuser.username, "edit_username")
        self.assertEqual(self.testuser.email, "edit@email.com")

    # #####################################################
    # Project Modal
    # #####################################################

    def test_project_model(self):
        project = Project(
            name="Project_Test_New", description="Project_Test test description.",
        )

        db.session.add(project)
        db.session.commit()

        project = Project.query.filter(Project.name == "Project_Test_New").first()

        self.assertIsNotNone(project)

    def test_project_invalid(self):
        project = Project(name=None, description="Project_Test test description.",)

        db.session.add(project)

        with self.assertRaises(IntegrityError) as context:
            db.session.commit()

    def test_project_add(self):
        project = Project.add(
            name="Project_Test_Add", description="Project_Test test description.",
        )

        db.session.commit()

        project = Project.query.filter(Project.name == "Project_Test_Add").first()

        self.assertIsNotNone(project)

    def test_project_edit(self):
        project = self.testproject.edit(
            name="Project_edit", description="Edit project desc"
        )

        project = Project.query.get(self.testproject.id)

        self.assertIsNotNone(project)
        self.assertEqual(self.testproject.name, "Project_edit")
        self.assertEqual(self.testproject.description, "Edit project desc")

    # #####################################################
    # Plot Modal
    # #####################################################

    def test_plot_model(self):
        plot = Plot(
            name="Plot_Test_New",
            description="Plot_Test test description.",
            width=6,
            length=3,
        )

        db.session.add(plot)
        db.session.commit()

        plot = Plot.query.filter(Plot.name == "Plot_Test_New").first()

        self.assertIsNotNone(plot)

    def test_plot_invalid_name(self):
        plot = Plot(
            name=None, description="Plot_Test test description.", width=6, length=3,
        )

        db.session.add(plot)

        with self.assertRaises(IntegrityError) as context:
            db.session.commit()

    def test_plot_invalid_width(self):
        plot = Plot(
            name=None, description="Plot_Test test description.", width=None, length=3,
        )

        db.session.add(plot)

        with self.assertRaises(IntegrityError) as context:
            db.session.commit()

    def test_plot_invalid_length(self):
        plot = Plot(
            name=None, description="Plot_Test test description.", width=6, length=None,
        )

        db.session.add(plot)

        with self.assertRaises(IntegrityError) as context:
            db.session.commit()

    def test_plot_add(self):
        plot = Plot.add(
            name="Plot_Test_Add",
            description="Plot_Test test description.",
            width=6,
            length=3,
        )

        db.session.commit()

        plot = Plot.query.filter(Plot.name == "Plot_Test_Add").first()

        self.assertIsNotNone(plot)

    def test_plot_edit(self):
        plot = self.testplot.edit(
            name="Plot_edit", description="Edit plot desc", width=5, length=2,
        )

        plot = Plot.query.get(self.testplot.id)

        self.assertIsNotNone(plot)
        self.assertEqual(self.testplot.name, "Plot_edit")
        self.assertEqual(self.testplot.description, "Edit plot desc")
        self.assertEqual(self.testplot.width, 5)
        self.assertEqual(self.testplot.length, 2)

    # #####################################################
    # PlantList Modal
    # #####################################################

    def test_plantlist_model(self):
        plantlist = PlantList(
            name="PlantList_Test_New", description="PlantList_Test test description.",
        )

        db.session.add(plantlist)
        db.session.commit()

        plantlist = PlantList.query.filter(
            PlantList.name == "PlantList_Test_New"
        ).first()

        self.assertIsNotNone(plantlist)

    def test_plantlist_invalid(self):
        plantlist = PlantList(
            name=None, description="PlantList_Test test description.",
        )

        db.session.add(plantlist)

        with self.assertRaises(IntegrityError) as context:
            db.session.commit()

    def test_plantlist_add(self):
        plantlist = PlantList.add(
            name="PlantList_Test_Add", description="PlantList_Test test description.",
        )

        db.session.commit()

        plantlist = PlantList.query.filter(
            PlantList.name == "PlantList_Test_Add"
        ).first()

        self.assertIsNotNone(plantlist)

    def test_plantlist_edit(self):
        plantlist = self.testplantlist.edit(
            name="PlantList_edit", description="Edit plantlist desc"
        )

        plantlist = PlantList.query.get(self.testplantlist.id)

        self.assertIsNotNone(plantlist)
        self.assertEqual(self.testplantlist.name, "PlantList_edit")
        self.assertEqual(self.testplantlist.description, "Edit plantlist desc")

    # #####################################################
    # Symbol Modal
    # #####################################################

    def test_symbol_model(self):
        symbol = Symbol(
            id=2, symbol="<i class='symbol fas fa-seedling' style='color:#228B22;'></i>"
        )

        db.session.add(symbol)
        db.session.commit()

        symbol = Symbol.query.filter(
            Symbol.symbol
            == "<i class='symbol fas fa-seedling' style='color:#228B22;'></i>"
        ).first()

        self.assertIsNotNone(symbol)

    def test_symbol_default(self):
        symbol = Symbol(id=2, symbol=None)

        db.session.add(symbol)
        db.session.commit()

        self.assertEqual(
            symbol.symbol,
            "<i class='symbol fas fa-seedling' style='color:#228B22;'></i>",
        )

    # def test_symbol_add(self):
    #     symbol = Symbol.add(
    #         symbol="<i class='symbol fas fa-seedling' style='color:#118B24;'></i>",
    #     )

    #     db.session.commit()

    #     symbol = Symbol.query.filter(
    #         Symbol.symbol
    #         == "<i class='symbol fas fa-seedling' style='color:#118B24;'></i>"
    #     ).first()

    #     self.assertIsNotNone(symbol)

    #####################################################
    # Through Tables
    #####################################################
    def test_users_projects(self):
        self.testuser.projects.append(self.testproject)
        connection = Users_Projects.query.filter(
            Users_Projects.user_id == self.testuser_id,
            Users_Projects.project_id == self.testproject_id,
        ).one_or_none()

        self.assertIsNotNone(connection)

        self.testuser.projects.remove(self.testproject)
        connection = Users_Projects.query.filter(
            Users_Projects.user_id == self.testuser_id,
            Users_Projects.project_id == self.testproject_id,
        ).one_or_none()

        self.assertIsNone(connection)

    def test_users_plots(self):
        self.testuser.plots.append(self.testplot)
        connection = Users_Plots.query.filter(
            Users_Plots.user_id == self.testuser_id,
            Users_Plots.plot_id == self.testplot_id,
        ).one_or_none()

        self.assertIsNotNone(connection)

        self.testuser.plots.remove(self.testplot)
        connection = Users_Plots.query.filter(
            Users_Plots.user_id == self.testuser_id,
            Users_Plots.plot_id == self.testplot_id,
        ).one_or_none()

        self.assertIsNone(connection)

    def test_users_plantlists(self):
        self.testuser.plantlists.append(self.testplantlist)
        connection = Users_PlantLists.query.filter(
            Users_PlantLists.user_id == self.testuser_id,
            Users_PlantLists.plantlist_id == self.testplantlist_id,
        ).one_or_none()

        self.assertIsNotNone(connection)

        self.testuser.plantlists.remove(self.testplantlist)
        connection = Users_PlantLists.query.filter(
            Users_PlantLists.user_id == self.testuser_id,
            Users_PlantLists.plantlist_id == self.testplantlist_id,
        ).one_or_none()

        self.assertIsNone(connection)

    def test_projects_plantlists(self):
        self.testproject.plantlists.append(self.testplantlist)
        connection = Projects_PlantLists.query.filter(
            Projects_PlantLists.project_id == self.testproject_id,
            Projects_PlantLists.plantlist_id == self.testplantlist_id,
        ).one_or_none()

        self.assertIsNotNone(connection)

        self.testproject.plantlists.remove(self.testplantlist)
        connection = Projects_PlantLists.query.filter(
            Projects_PlantLists.project_id == self.testproject_id,
            Projects_PlantLists.plantlist_id == self.testplantlist_id,
        ).one_or_none()

        self.assertIsNone(connection)

    def test_projects_plots(self):
        self.testproject.plots.append(self.testplot)
        connection = Projects_Plots.query.filter(
            Projects_Plots.project_id == self.testproject_id,
            Projects_Plots.plot_id == self.testplot_id,
        ).one_or_none()

        self.assertIsNotNone(connection)

        self.testproject.plots.remove(self.testplot)
        connection = Projects_Plots.query.filter(
            Projects_Plots.project_id == self.testproject_id,
            Projects_Plots.plot_id == self.testplot_id,
        ).one_or_none()

        self.assertIsNone(connection)

    def test_plots_plantlists(self):
        self.testplot.plantlists.append(self.testplantlist)
        connection = Plots_PlantLists.query.filter(
            Plots_PlantLists.plot_id == self.testplot_id,
            Plots_PlantLists.plantlist_id == self.testplantlist_id,
        ).one_or_none()

        self.assertIsNotNone(connection)

        self.testplot.plantlists.remove(self.testplantlist)
        connection = Plots_PlantLists.query.filter(
            Plots_PlantLists.plot_id == self.testplot_id,
            Plots_PlantLists.plantlist_id == self.testplantlist_id,
        ).one_or_none()

        self.assertIsNone(connection)

    #####################################################
    # Plantlists_Plants Modal
    #####################################################

    def test_plantlists_plants(self):
        self.testplantlist.plants.append(self.testplant)
        connection = PlantLists_Plants.query.filter(
            PlantLists_Plants.plantlist_id == self.testplantlist_id,
            PlantLists_Plants.plant_id == self.testplant_id,
        ).one_or_none()

        self.assertIsNotNone(connection)

        self.testplantlist.plants.remove(self.testplant)
        connection = PlantLists_Plants.query.filter(
            PlantLists_Plants.plantlist_id == self.testplot_id,
            PlantLists_Plants.plant_id == self.testplant_id,
        ).one_or_none()

        self.assertIsNone(connection)

    def test_plantlists_plants_conns(self):
        plantlists_plants = PlantLists_Plants(
            plantlist_id=self.testplantlist_id,
            plant_id=self.testplant_id,
            symbol_id=self.testsymbol_id,
        )
        db.session.add(plantlists_plants)
        db.session.commit()

        plant = plantlists_plants.plant
        symbol = plantlists_plants.symbol

        self.assertEqual(symbol, self.testsymbol)
        self.assertEqual(plant, self.testplant)

    def test_plantlist_edit(self):
        plantlists_plants = PlantLists_Plants(
            plantlist_id=self.testplantlist_id,
            plant_id=self.testplant_id,
            symbol_id=self.testsymbol_id,
        )

        symbol = Symbol(
            id=2, symbol="<i class='symbol fas fa-seedling' style='color:#24AE24></i>"
        )
        db.session.add(symbol)
        db.session.commit()

        plantlists_plants.edit(
            plantlist_id=self.testplantlist_id,
            plant_id=self.testplant_id,
            symbol_id=symbol.id,
        )

        self.assertIsNotNone(plantlists_plants)
        self.assertEqual(plantlists_plants.symbol_id, symbol.id)

    # #####################################################
    # Plots_Cells_Symbols Modal
    # #####################################################

    def test_plots_cells_symbols(self):
        plantlists_plants = PlantLists_Plants(
            plantlist_id=self.testplantlist_id,
            plant_id=self.testplant_id,
            symbol_id=self.testsymbol_id,
        )
        db.session.add(plantlists_plants)
        db.session.commit()
        cell_x = 1
        cell_y = 2

        plot_cells_symbols = Plot_Cells_Symbols(
            plot_id=self.testplot_id,
            plantlists_plants_id=plantlists_plants.id,
            cell_x=cell_x,
            cell_y=cell_y,
        )
        db.session.add(plot_cells_symbols)
        db.session.commit()
        self.assertIsNotNone(plot_cells_symbols)

    def test_plots_cells_symbols_invalid(self):
        plantlists_plants = PlantLists_Plants(
            plantlist_id=self.testplantlist_id,
            plant_id=self.testplant_id,
            symbol_id=self.testsymbol_id,
        )
        db.session.add(plantlists_plants)
        db.session.commit()
        cell_x = 1

        plot_cells_symbols = Plot_Cells_Symbols(
            plot_id=self.testplot_id,
            plantlists_plants_id=plantlists_plants.id,
            cell_x=cell_x,
            cell_y=None,
        )

        db.session.add(plot_cells_symbols)
        with self.assertRaises(IntegrityError) as context:
            db.session.commit()

    def test_plots_cells_symbols_add(self):
        plantlists_plants = PlantLists_Plants(
            plantlist_id=self.testplantlist_id,
            plant_id=self.testplant_id,
            symbol_id=self.testsymbol_id,
        )
        db.session.add(plantlists_plants)
        db.session.commit()
        cell_x = 1
        cell_y = 2

        plot_cells_symbols = Plot_Cells_Symbols.add(
            plot_id=self.testplot_id,
            plantlists_plants_id=plantlists_plants.id,
            cell_x=cell_x,
            cell_y=cell_y,
        )
        db.session.commit()
        self.assertIsNotNone(plot_cells_symbols)
