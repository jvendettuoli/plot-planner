"""View Tests"""

import os
from unittest import TestCase

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
    Users_Projects,
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


class ViewsTestCase(TestCase):
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

        self.otheruser = User.signup(
            username="otheruser", email="other@test.com", password="otherpw",
        )

        self.otheruser_id = 200
        self.otheruser.id = self.otheruser_id

        self.testproject = Project(
            name="Project_Test", description="Project_Test test description.",
        )
        self.testproject_name = self.testproject.name
        self.testproject_id = 110
        self.testproject.id = self.testproject_id
        db.session.add(self.testproject)

        self.testplot = Plot(
            name="Plot_Test",
            width=5,
            length=10,
            description="Plot_Test test description.",
        )
        self.testplot_name = self.testplot.name
        self.testplot_id = 120
        self.testplot.id = self.testplot_id
        db.session.add(self.testplot)

        self.testplantlist = PlantList(
            name="Plantlist_Test", description="Plantlist_Test test description.",
        )
        self.testplantlist_name = self.testplantlist.name
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
        self.testplant_common_name = self.testplant.common_name
        self.testplant_id = 140
        self.testplant.id = self.testplant_id

        db.session.add(self.testplant)

        self.testsymbol = Symbol(
            symbol="<i class='symbol fas fa-seedling' style='color:#228B22;'></i>"
        )

        self.testsymbol_id = 1
        self.testsymbol.id = self.testsymbol_id
        db.session.add(self.testsymbol)

        # Connections
        self.testuser.projects.append(self.testproject)
        self.testuser.plots.append(self.testplot)
        self.testuser.plantlists.append(self.testplantlist)
        self.testproject.plots.append(self.testplot)
        self.testproject.plantlists.append(self.testplantlist)
        self.testplot.plantlists.append(self.testplantlist)
        self.testplantlist.plants.append(self.testplant)

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

        # #####################################################
        # Signup
        # #####################################################

        # def test_signup_get(self):
        #     with self.client as c:
        #         resp = c.get("/signup")

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Signup", str(resp.data))

        # def test_signup_post(self):
        #     signup_data = {
        #         "username": "signup_user",
        #         "email": "signup@test.com",
        #         "password": "signup_pw",
        #     }
        #     with self.client as c:
        #         resp = c.post("/signup", data=signup_data, follow_redirects=True)

        #         user = User.query.filter(
        #             User.username == signup_data["username"]
        #         ).one_or_none()

        #         self.assertIsNotNone(user)
        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Welcome to Plot Planner", str(resp.data))

        # def test_signup_post_existing(self):
        #     existing_user = User.query.get(self.testuser_id)
        #     signup_data = {
        #         "username": existing_user.username,
        #         "email": existing_user.email,
        #         "password": "signup_pw",
        #     }
        #     with self.client as c:
        #         resp = c.post("/signup", data=signup_data, follow_redirects=True)

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Username already taken", str(resp.data))

        # ######################################################
        # # Login
        # ######################################################

        # def test_login_get(self):
        #     with self.client as c:
        #         resp = c.get("/login")

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Login", str(resp.data))

        # def test_login_post(self):
        #     username = self.testuser.username
        #     password = "testpw"
        #     with self.client as c:
        #         resp = c.post(
        #             "/login",
        #             data=dict(username=username, password=password),
        #             follow_redirects=True,
        #         )

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("My Content", str(resp.data))

        # def test_login_post_wrong_pw(self):
        #     username = self.testuser.username
        #     password = "wrongpw"
        #     with self.client as c:
        #         resp = c.post(
        #             "/login",
        #             data=dict(username=username, password=password),
        #             follow_redirects=True,
        #         )

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Login", str(resp.data))

        # ####################################################################
        # # Homepage and About pages
        # #####################################################################

        # def test_homepage(self):
        #     with self.client as c:
        #         resp = c.get("/")

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Welcome to Plot Planner", str(resp.data))

        # def test_about(self):
        #     with self.client as c:
        #         resp = c.get("/about")

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("What is Plot Planner", str(resp.data))

        # #####################################################################
        # # User Routes
        # #####################################################################

        # def test_user_profile(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.get(f"/users/{self.testuser_id}")

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("User Profile", str(resp.data))

        # def test_user_profile_unauthorized(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.otheruser_id

        #         resp = c.get(f"/users/{self.testuser_id}", follow_redirects=True)

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn(
        #             "Users are only permitted to access their own profiles", str(resp.data)
        #         )

        # def test_user_profile_edit(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.get(f"/users/{self.testuser_id}/edit")

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Edit Your Profile", str(resp.data))

        # def test_user_profile_edit_unauthorized(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.otheruser_id

        #         resp = c.get(f"/users/{self.testuser_id}/edit", follow_redirects=True)

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Not authorized to view this page.", str(resp.data))

        # def test_user_profile_edit_post(self):
        #     username = "new_name"
        #     password = "testpw"
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.post(
        #             f"/users/{self.testuser_id}/edit",
        #             data=dict(username=username, password=password),
        #             follow_redirects=True,
        #         )

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Profile updates successful", str(resp.data))

        # def test_user_profile_edit_post_wrong_pw(self):
        #     username = "new_name"
        #     password = "wrongpw"
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.post(
        #             f"/users/{self.testuser_id}/edit",
        #             data=dict(username=username, password=password),
        #             follow_redirects=True,
        #         )

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Password incorrect", str(resp.data))
        #         self.assertIn("Edit Your Profile", str(resp.data))

        # def test_user_profile_edit_post_existing_user(self):
        #     username = "otheruser"
        #     password = "testpw"
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.post(
        #             f"/users/{self.testuser_id}/edit",
        #             data=dict(username=username, password=password),
        #             follow_redirects=True,
        #         )

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Username already taken", str(resp.data))
        #         self.assertIn("Edit Your Profile", str(resp.data))

        # def test_user_content(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.get(f"/users/{self.testuser_id}/content", follow_redirects=True,)

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("My Content", str(resp.data))

        # def test_user_delete(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.post(f"/users/delete", follow_redirects=True,)

        #         user = User.query.get(self.testuser_id)

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Signup", str(resp.data))
        #         self.assertIsNone(user)

        # ###################################################################
        # Project Routes
        #####################################################################
        # def test_add_projects_get(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.get(f"/projects", follow_redirects=True,)

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Add a new project.", str(resp.data))

        # def test_add_projects_post(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.post(
        #             f"/projects", data=dict(name="Project Post"), follow_redirects=True,
        #         )

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Project Post", str(resp.data))

        # def test_add_projects_post_invalid(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.post(f"/projects", data=dict(name=None), follow_redirects=True,)

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Project name required", str(resp.data))

        # def test_show_project(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.get(f"/projects/{self.testproject_id}", follow_redirects=True,)

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn(self.testproject_name, str(resp.data))

        # def test_edit_project_get(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.get(
        #             f"/projects/{self.testproject_id}/edit", follow_redirects=True,
        #         )

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Edit Project", str(resp.data))

        # def test_edit_project_post(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.post(
        #             f"/projects/{self.testproject_id}/edit",
        #             data=dict(name="Edit Project Name"),
        #             follow_redirects=True,
        #         )

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Edit Project Name", str(resp.data))

        # def test_delete_project(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.post(
        #             f"/projects/{self.testproject_id}/delete", follow_redirects=True,
        #         )
        #         project = Project.query.get(self.testproject_id)

        #         self.assertIsNone(project)
        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("My Content", str(resp.data))
        #         self.assertNotIn(self.testproject_name, str(resp.data))

        # def test_project_remove_plot(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.post(
        #             f"/projects/{self.testproject_id}/remove/plot/{self.testplot_id}",
        #             follow_redirects=True,
        #         )
        #         project = Project.query.get(self.testproject_id)
        #         plot = Plot.query.get(self.testplot_id)

        #         self.assertNotIn(plot, project.plots)
        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn(
        #             f"Plot {plot.id} removed from Project {project.id} successfully",
        #             str(resp.data),
        #         )

        # def test_project_add_plot(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         plot = Plot.add(name="AddPlot", width=1, length=1)
        #         project = Project.query.get(self.testproject_id)

        #         resp = c.post(
        #             f"/projects/{project.id}/add/plot/{plot.id}", follow_redirects=True,
        #         )

        #         self.assertIn(plot, project.plots)
        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn(
        #             f"Plot {plot.id} connected to Project {project.id} successfully.",
        #             str(resp.data),
        #         )

        # def test_project_remove_plantlist(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.post(
        #             f"/projects/{self.testproject_id}/remove/plantlist/{self.testplantlist_id}",
        #             follow_redirects=True,
        #         )
        #         project = Project.query.get(self.testproject_id)
        #         plantlist = PlantList.query.get(self.testplantlist_id)

        #         self.assertNotIn(plantlist, project.plantlists)
        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn(
        #             f"Plant List {plantlist.id} removed from Project {project.id} successfully",
        #             str(resp.data),
        #         )

        # def test_project_add_plantlist(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         plantlist = PlantList.add(name="AddPlantlist")
        #         project = Project.query.get(self.testproject_id)

        #         resp = c.post(
        #             f"/projects/{project.id}/add/plantlist/{plantlist.id}",
        #             follow_redirects=True,
        #         )

        #         self.assertIn(plantlist, project.plantlists)
        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn(
        #             f"Plant List {plantlist.id} connected to Project {project.id} successfully.",
        #             str(resp.data),
        #         )

        # ###################################################################
        # Plot Routes
        #####################################################################
        # def test_add_plots_get(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.get(f"/plots", follow_redirects=True,)

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Add a new plot.", str(resp.data))

        # def test_add_plots_post(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.post(
        #             f"/plots", data=dict(name="Plot Post"), follow_redirects=True,
        #         )

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Plot Post", str(resp.data))

        # def test_add_plots_post_invalid(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.post(f"/plots", data=dict(name=None), follow_redirects=True,)

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Plot name required", str(resp.data))

        # def test_show_plot(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.get(f"/plots/{self.testplot_id}", follow_redirects=True,)

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn(self.testplot_name, str(resp.data))

        # def test_edit_plot_get(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.get(f"/plots/{self.testplot_id}/edit", follow_redirects=True,)

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Edit Plot", str(resp.data))

        # def test_edit_plot_post(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.post(
        #             f"/plots/{self.testplot_id}/edit",
        #             data=dict(name="Edit Plot Name"),
        #             follow_redirects=True,
        #         )

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Edit Plot Name", str(resp.data))

        # def test_delete_plot(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.post(f"/plots/{self.testplot_id}/delete", follow_redirects=True,)
        #         plot = Plot.query.get(self.testplot_id)

        #         self.assertIsNone(plot)
        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("No Plots connected yet", str(resp.data))

        # def test_plot_remove_plantlist(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.post(
        #             f"/plots/{self.testplot_id}/remove/plantlist/{self.testplantlist_id}",
        #             follow_redirects=True,
        #         )
        #         plot = Plot.query.get(self.testplot_id)
        #         plantlist = PlantList.query.get(self.testplantlist_id)

        #         self.assertNotIn(plantlist, plot.plantlists)
        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn(
        #             f"Plant List {plantlist.id} removed from Plot {plot.id} successfully",
        #             str(resp.data),
        #         )

        # def test_plot_add_plantlist(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         plantlist = PlantList.add(name="AddPlantlist")
        #         plot = Plot.query.get(self.testplot_id)

        #         resp = c.post(
        #             f"/plots/{plot.id}/add/plantlist/{plantlist.id}", follow_redirects=True,
        #         )

        #         self.assertIn(plantlist, plot.plantlists)
        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn(
        #             f"Plant List {plantlist.id} connected to Plot {plot.id} successfully.",
        #             str(resp.data),
        #         )

        ##################################################################
        # Plot Cells Routes
        ###################################################################
        # def test_plot_cell_add_symbol(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         plantlists_plants = PlantLists_Plants(
        #             plantlist_id=self.testplantlist_id,
        #             plant_id=self.testplant_id,
        #             symbol_id=self.testsymbol_id,
        #         )
        #         db.session.add(plantlists_plants)
        #         db.session.commit()

        #         cell_x = 1
        #         cell_y = 2

        #         resp = c.post(
        #             f"/plots/{self.testplot_id}/add/symbol/{plantlists_plants.id}/x/{cell_x}/y/{cell_y}",
        #             follow_redirects=True,
        #         )

        #         plot_cells_symbols = Plot_Cells_Symbols.query.filter(
        #             Plot_Cells_Symbols.plot_id == self.testplot_id,
        #             Plot_Cells_Symbols.cell_x == cell_x,
        #             Plot_Cells_Symbols.cell_y == cell_y,
        #         ).one_or_none()

        #         self.assertEqual(
        #             plantlists_plants.id, plot_cells_symbols.plantlists_plants_id
        #         )
        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn(
        #             f"Plantlists_Plants ID {plantlists_plants.id} added to Plot cell {plot_cells_symbols.id} successfully.",
        #             str(resp.data),
        #         )

        # def test_plot_cell_delete_row(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         plantlists_plants = PlantLists_Plants(
        #             plantlist_id=self.testplantlist_id,
        #             plant_id=self.testplant_id,
        #             symbol_id=self.testsymbol_id,
        #         )

        #         db.session.add(plantlists_plants)
        #         db.session.commit()

        #         cell_x = 1
        #         cell_y = 2
        #         Plot_Cells_Symbols.add(
        #             plot_id=self.testplot_id,
        #             plantlists_plants_id=plantlists_plants.id,
        #             cell_x=cell_x,
        #             cell_y=cell_y,
        #         )
        #         db.session.commit()

        #         resp = c.post(
        #             f"/plots/{self.testplot_id}/delete/cell/x/{cell_x}/y/{cell_y}",
        #             follow_redirects=True,
        #         )

        #         plot_cells_symbols = Plot_Cells_Symbols.query.filter(
        #             Plot_Cells_Symbols.plot_id == self.testplot_id,
        #             Plot_Cells_Symbols.cell_x == cell_x,
        #             Plot_Cells_Symbols.cell_y == cell_y,
        #         ).one_or_none()

        #         self.assertIsNone(plot_cells_symbols)
        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn(
        #             f"Plot {self.testplot_id} removed symbol from plot cell {cell_x},{cell_y} successfully.",
        #             str(resp.data),
        #         )

        # ###################################################################
        # # Plantlist Routes
        # ####################################################################
        # def test_add_plantlists_get(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.get(f"/plantlists", follow_redirects=True,)

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Add a new plant list.", str(resp.data))

        # def test_add_plantlists_post(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.post(
        #             f"/plantlists", data=dict(name="PlantList Post"), follow_redirects=True,
        #         )

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("PlantList Post", str(resp.data))

        # def test_add_plantlists_post_invalid(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.post(f"/plantlists", data=dict(name=None), follow_redirects=True,)

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Plant List name required", str(resp.data))

        # def test_show_plantlist(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.get(f"/plantlists/{self.testplantlist_id}", follow_redirects=True,)

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn(self.testplantlist_name, str(resp.data))

        # def test_edit_plantlist_get(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.get(
        #             f"/plantlists/{self.testplantlist_id}/edit", follow_redirects=True,
        #         )

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Edit Plant List", str(resp.data))

        # def test_edit_plantlist_post(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.post(
        #             f"/plantlists/{self.testplantlist_id}/edit",
        #             data=dict(name="Edit PlantList Name"),
        #             follow_redirects=True,
        #         )

        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("Edit PlantList Name", str(resp.data))

        # def test_delete_plantlist(self):
        #     with self.client as c:
        #         with c.session_transaction() as sess:
        #             sess[CURR_USER_KEY] = self.testuser_id

        #         resp = c.post(
        #             f"/plantlists/{self.testplantlist_id}/delete", follow_redirects=True,
        #         )
        #         plantlist = PlantList.query.get(self.testplantlist_id)

        #         self.assertIsNone(plantlist)
        #         self.assertEqual(resp.status_code, 200)
        #         self.assertIn("No Plant Lists connected yet", str(resp.data))

        def test_plantlist_remove_plant(self):
            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testuser_id

                resp = c.post(
                    f"/plantlists/{self.testplantlist_id}/remove/plantlist/{self.testplant_id}",
                    follow_redirects=True,
                )
                plantlist = PlantList.query.get(self.testplantlist_id)
                plant = Plant.query.get(self.testplant_id)

                self.assertNotIn(plant, plantlist.plants)
                self.assertEqual(resp.status_code, 200)
                self.assertIn(
                    f"Plant List {plantlist.id} removed from PlantList {plantlist.id} successfully",
                    str(resp.data),
                )

    # def test_plantlist_add_plant(self):
    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser_id

    #         plant = Plant(
    #             trefle_id=1232,
    #             slug="plantus-slugs2",
    #             common_name="common plant2",
    #             scientific_name="plantus testus2",
    #             family="Plantaceae2",
    #             family_common_name="Plant Family2",
    #         )
    #         db.session.add(plant)
    #         db.session.commit()
    #         plantlist = PlantList.query.get(self.testplantlist_id)

    #         resp = c.post(
    #             f"/plantlists/{plantlist.id}/add/plant/{plant.id}",
    #             follow_redirects=True,
    #         )

    #         self.assertIn(plant, plantlist.plants)
    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn(
    #             f"Plant {plant.id} added to plantlist {plantlist.id} successfully.",
    #             str(resp.data),
    #         )

