# Plot Planner
Plot Planner is a web app that provides users the ability search through over 1 million plants sourced from [Trefle API](https://trefle.io/) and save those plants to customizable projets, wherein users can plot out their next planting project.

## Depolyment
Plot Planner is depolyed on Heroku and is available at https://plot-planner.herokuapp.com/.

## Features
Users can search through plants based on a variety of filters and view plant specific details including taxonomy, images, distribution, growth specifications, and more. The Trefle database is still in beta so the information is constantly improving.

If users signup, they can also create and save Projects, Plots, and Plant Lists to aid in their next planting endevour. 

Plant Lists allow users to save plants they find to specific lists, and apply a custom symbol to that plant for use in plot design. 

Plots are a basic grid format (similar to a raised planting bed), and allow users to place plants they have on connected plant lists.

Projects allow users a higher level of organization for their planning needs. 

Each component can be connected to each other, or used independantly. 

### Future Goals
In the future, we will be adding in additional APIs that focus on providing a more robust source of information on growth requirements for plants. This information will then be used to create custom reports for users to aid in their planting projects.

There are a great many of improvements planned for the site, including from quality of life features such as sortable tables, improved symbols for plants, sharing and collaboration on projects components, and more.

## Tech Stack
### Back-end:
 - Python 3.8.5 
 - Flask
 - PostgreSQL
 - SQLalchemy
 - WTForms
 
### Front-end:
 - HTML5, with Jinja
 - CSS3, with Bootstrap
 - Javascript, with jQuery and Axios

## Installation
If you would like to work on a personal version of Plot Planner, it is fairly simple to get up and running in your environment.

Change the current working directory to the location where you want the cloned directory. Enter the following:


    $ git clone https://github.com/jvendettuoli/plot-planner.git

Press **Enter** to create your local clone.

You will need a version of Python 3. To reduce unintended issues you should use **`Python 3.8.5`**, which is Plot Planner's native version.

Ensure you have a virtual environment running in your working directory. A virtual environment folder named venv is common.

    python3 -m venv venv

Then start your virtual environment.

    source venv venv/bin/activate

Now any modules downloaded will only be present in your virtual envrionment. So let's download the requirements. The following command will install all modules from the requirements.txt file. You may need to use `pip3`.

    pip install -r requirements.txt

You should now have all the dependencies you need to start up the server. But first, lets create the database. You can either set up an environmental variable with the key "DATABASE_URL" and value of whatever you plan on naming your database, or from PostgreSQL interactive terminal `psql`, enter the following:

    CREATE DATABASE plot_planner;

Now seed the database with the required tables and data. Plot Planner requires a symbol to be in the database to work, so this is a required step. You may need to ensure you have the correct version of python in your virtual environment, but when configured properly you do not need to type `python3`, `python` will point to the correct version.

    python seed.py

Your database should be set up, so now you can start your server.

    flask run

If you would like to start Flask in development mode, which can be done by first including:

    FLASK_ENV=development flask run

You should see, though you'll have your own debugger PIN:

    * Environment: development
    * Debug mode: on
    * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    * Restarting with stat
    * Debugger is active!
    * Debugger PIN: ###-###-###


By clicking on the http address you'll be brough to your functionion Plot Planner!

### Thanks for checking out V1 of Plot Planner, and let me know if you have any questions, advice, or suggestions.