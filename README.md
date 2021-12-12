# FitnessPlanner

***Note:** All team members used Windows system and Chrome browser for this project.*

## Installation Guide
1. Download and install Python onto your computer if it does not already have it. Search ‘python download’ and download Python from python.org. Recommended version to download is Python 3.8.
2. Download and install an IDE that supports Python Flask development. Our team strongly recommends using PyCharm (Community Edition) from jetbrains.com as the IDE. It is the virtual environment that we will refer to in this guide, as all of the team members have used it throughout this entire project.
3. Download and install MySQL Workbench (Community) from mysql.com. A helpful YouTube video to help with the download and installation on Windows is linked: https://www.youtube.com/watch?v=OM4aZJW_Ojs
  - For a Mac, follow YouTube instructions to download MySQL and learn to use the terminal to run scripts: https://www.youtube.com/watch?v=-BDbOOY9jsc 
4. Download/unzip/clone the FitnessPlanner project code onto your computer.
5. In PyCharm, go to File -> New Project and then select the FitnessPlanner folder as the location. Select ‘Create from Existing Sources’ in the pop-up.
6. Once the project is loaded and opened in a PyCharm window, open the OneFit.py file.
7. Add a Python interpreter to the project by clicking <No Interpreter> at the bottom right of the project window, selecting ‘Add Interpreter’, and clicking OK in the pop up window.
8. After the Python interpreter is created, <No Interpreter> should change to show the Python version being used. Click that and select ‘Interpreter Settings’.
9. In ‘Interpreter Settings’, click on the ‘+’ to add packages. Search ‘Flask’ and install the ‘Flask’ package that shows up. Then search for ‘Flask-MySQL’ and ‘Flask-MySQLdb’ and install those packages as well. After installation, close the ‘Available Packages’ window and click OK.
10. Now open up MySQL Workbench. Select and sign into the local instance that was set up during the workbench installation. Copy and paste the script in the onefit-mysql-script.sql into the ‘SQL File 1’ and run it by clicking the lightning bolt icon.
11. Go back to the PyCharm window with the FitnessPlanner project. In the OneFit.py file, be sure to edit the app.config['MYSQL_PASSWORD'] field to be whatever your password is for the MySQL local instance connection.
12. Right click inside the OneFit.py file, and click “Run ‘OneFit’”.
13. Click on the blue underlined http:// link generated in the terminal section at the bottom of the PyCharm window. 
14. The application should open up in a web browser.

## Running the Product
1. After the application opens in the web browser, there will be a navigation bar with options to login to an existing account or register a new account.
2. A new user can be registered and then log in to start inputting their fitness data.
3. Aside from registering a new user, the script (onefit-mysql-script.sql) that was run in the project installation process has sample data to show how the application would look for a user that has been inputting data for a few days. 
4. The sample data can be accessed from the web page by going to the login page from the 'Login' item in the home page navigation bar and entering: 
  - Email: joe@gmail.com 
  - Password: password
5. After logging in, the user homepage will load. The pages that can be accessed through the navigation bar at the top of the page and tested out are:
  - Health:
    - Input height and weight data 
    - View most recent height, weight, BMI, BMR, and age data 
    - Track weight data through a graph
  - Exercise: 
    - Input workout data (running, weightlifting and cardio options), calories burned, and calorie burn goal
    - Track daily caloric burn and workout data with graphs
  - Nutrition: 
    - Input caloric intake and water intake data 
    - Track calorie intake and water intake data with graphs
  - Goals: 
    - Input new goals (weight and net calories intake options)
    - View current goals (by all goals, weight goals, or net calories goals)
    - Remove current goals when viewing current goals by category 
    - View achieved goals 
  - Account:
    - Update or set account information (email, password and nutritionist options)
    - View current account information (name, email, nutritionist, and nutritionist feedback)
    - Remove nutritionist connection and feedback from account 
    - View a list of available nutritionists to connect with
6. For the sample user Joe, who already has some fitness data records in the database, the pages will have pre populated data to show how the layout and the graphs on the pages look like with a few days of data.
7. Once a user is done using the application, they may logout by clicking the 'Logout' item at the right of the navigation bar.
8. Aside from the user role, a new nutritionist can also be registered and then logged in to make themselves available for connection and view the information of any users that have connected with them.
9. There is also sample data for a nutritionist who has some users connected to them already. The sample data can be accessed through the login by entering: 
  - Email: pat@gmail.com 
  - Password: password
10. After logging in, the nutritionist homepage will load. The pages that can be accessed through the navigation bar and tested out are:
  - Clients:
    - View a list of connected users 
    - Select a connected user to view their fitness information 
    - View the selected connected users fitness information 
    - Provide feedback to the connected user
  - Account:
    - Update or set new account information (email and password options)
    - View current account information (name and email)
11. For the sample nutritionist Pat, who already has some connected users and account information in the database, the pages will have pre populated data to show how the layout of the pages look like with data.
12. All pages have error checking and messages that will appear to indicate any errors that may have occurred when submitting any of the forms on any of the pages.
