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

    ####################################################################
    # Project Routes
    # ####################################################################
    def test_projects_get(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/projects", follow_redirects=True,)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Add a new project.", str(resp.data))

    def test_projects_post(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post(
                f"/projects", data=dict(name="Project Post"), follow_redirects=True,
            )

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Project Post", str(resp.data))

    def test_projects_post_invalid(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post(f"/projects", data=dict(name=None), follow_redirects=True,)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Add a new project.", str(resp.data))

