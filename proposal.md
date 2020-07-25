# PLOT PLANNER
## Work in progress

**1. What goal will your website be designed to achieve?**
> Plot Planner will be designed to allow easy access to plant attributes related to growing, tending, and harvesting. It will assist users in planning and designing their home garden plot and provide the necessary information on how to have a successful growing season.
>
>At its core, the site will gather and organize information from relevant APIs (and possibly web scraping at a later date) on specific plant specifications (planting spacing, watering regime, preferred sun, regions, companion plants, etc.) and allow users to search through this information. This information can then be used to build user specific plots that can be saved and used to generate reports on a planting schedule. Saved plots could also be shared, and if the user allows, could be displayed to other users to help inspire/allow other users to save their plot for their own use.
 
**2. What kind of users will visit your site? In other words, what is the demographic of
your users?**
>The core demographic will be homesteaders and gardeners with small plots. Generally hobbyists or people attempting to live more sustainably by growing some of their own food. The site will not likely provide any information beyond what you could find searching the web, but it will provide it in an organized fashion associated with user designed plots and needs. 
>
>The demographic can be extended to general plant enthusiasts by providing information on other plants besides crop species and with features such as plant ID, information on pests/pathogens, plant-centric blog/news, etc. It could also be extended to larger plots, or smart farms, through the inclusion of smart farm APIs

**3. What data do you plan on using? You may have not picked your actual API yet,
which is fine, just outline what kind of data you would like it to contain.**

>Possible APIs: 
>- OpenFarm, https://github.com/openfarmcc/OpenFarm
>- Trefle, https://trefle.io/
>- ETwater, http://etwater.com/developer/
>
>Plot Planner will use any APIs that have data on plant species characteristics and growth requirements. Several possibilities are listed at the top of this document. This data could also be webscraped from a variety of sites/documents that have plant data present in tables. The core features of the site would function best with the following attributes:
>- Plant Name
>- Species
>- Region/Biome
>- Preferred Sun Conditions
>- Preferred Water Regime
>- Plant spacing (individuals & rows)
>- Ideal Planting Season
>- Ideal Harvesting Season  
>
>Additional data will depend on what is freely available. 

**4. In brief, outline your approach to creating your project (knowing that you may not
know everything in advance and that these details might change later). Answer
questions like the ones below, but feel free to add more information:**  
**a. What does your database schema look like?**

>This question appears to be answered more in depth in the next phase of the project. For now, the database schema will have a table for:
>- users
>- plants
>- plots
>- lists (of favorited plants)
>- projects
>- user_lists
>- user_plots
>- user_projects
>- plots_plants
>- projects_plots
>- projects_lists

**b. What kinds of issues might you run into with your API?**

>The data sources may not be complete. From a brief investigation, there are null values present for certain plant attributes. All of the APIs listed require keys, so a potential (good) problem would be that too many requests are being made for the free tier. There are many common names for plants, so I’ll have to make sure requests can handle multiple possible naming conventions, or enforce specific ones (perhaps some kind of autocomplete).

**c. Is there any sensitive information you need to secure?**

>Users will be able to create profiles to save their plots. I’m also considering some kind of alert system (email when harvest is coming up, reminders for watering), which may introduce additional security needs. For user passwords I’ll be using flask-bcrypt to encrypt and store only the encrypted password and salt. All forms will be done through WTForms to handle any CSRF concerns.	

**d. What will the user flow look like?**

>Users enter the site to a homepage that will have some already created plots as examples (or as user submitted ones). Paths for registering/logging in will be present. If I decide to go with having some plant news there will be a column for recent stories. Central will be the paths to either search through plants or to create a plot. 
>
>Searching through plants will essentially be a UI for the database which will allow users to search by name, region, growing conditions, etc. (or combinations of these attributes) and will allow users to favorite specific plants to be saved on a list associated with their profile. If not logged in users can still search through plants, and can favorite them for the session, but the list will not persist. Lists can be used to generate a report on all those plants that will show requested attributes. Reports can be exported (likely as pdfs, or maybe emails).
>
>Creating a plot will bring users to a grid system in which they can select plants (either through search, or a favorites list) and place them in the plots. This will likely start as a fairly simple system, where users can set a scale, draw basic shapes that fit to the grid, and place plants within grid cells. Plots can also be selected from basic templates, or user submitted designs. Plots can be saved if logged in, otherwise will only persist for the session. Created plots can be exported (possibly as images) and can also be used to generate a report on requested plant attributes.
>
>Plots and lists can be saved to a project, if the user is logged in.

**e. What features make your site more than CRUD? Do you have any stretch goals?**

>The plot planning and report generation are two aspects that go beyond navigating through the plant database. Many of the aspects could be considered stretch goals, in that the basic implementation could be greatly improved. Possible stretch goals include:
>- Plot planning style and functionality could be improved to allow more specific planning as opposed to a basic grid
>- A plant/gardening/farming news/blog section
>- Allowing users to share and post
>- Webscraping to gather a more robust dataset
