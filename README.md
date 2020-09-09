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
Plot Planner uses Flask with Postgresql to handle routes, API calls, and data storage, and a mix of HTML templates (Jinja), CSS, and Javascript for the front-end. SQLAlchemy and WTForms are used for handling data models and delivering forms, respectively. Bootstrap, jQuery, and Axios are used to aid the front-end display and for making calls to the backend to allow for dynamic changes on pages.

