import MySQLdb
from flask import Flask, render_template, redirect, request, url_for, session
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__, template_folder='templates')
app.secret_key = "Hello"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Cmpe133!'
app.config['MYSQL_DB'] = 'onefit'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


@app.route('/')
def frontpage():
    return render_template("frontpage.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    # ---------------------------------------------------------
    if request.method == 'GET':
        return render_template("register.html", message="", email="", name="")
    # ---------------------------------------------------------
    else:
        user_role = 0  # default user role
        # Get all the values from the registration form
        name = request.form['name']
        formcategory = request.form.get('gendercategory')
        formdate = request.form['bday']
        bday = datetime.strptime(formdate, '%Y-%m-%d').date()
        print(bday.year)
        print(bday.month)
        print(bday.day)
        print(datetime.today().year)
        print(datetime.today().month)
        print(datetime.today().day)

        if datetime.today().month > bday.month:
            age = datetime.today().year - bday.year
        elif datetime.today().month == bday.month:
            if datetime.today().day >= bday.day:
                age = datetime.today().year - bday.year
        else:
            age = datetime.today().year - bday.year - 1
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        nutritionistEmail = request.form['nutritionistEmail']
        # hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
        # Error check for empty fields
        if password.decode('utf-8') == "" or email == "" or name == "" or formcategory == "10" or formdate == "":
            return render_template("register.html", message="Please fill in all required fields", email=email, name=name)
        # Check gender type
        if formcategory == "1":
            gender = "Female"
        else:
            gender = "Male"
        # Error check for incorrect format - only one email required
        if(email.casefold() != "n/a" and nutritionistEmail.casefold() != "n/a") or \
                (email.casefold() == "n/a" and nutritionistEmail.casefold() == "n/a"):
            return render_template("register.html", message="Please enter one email and enter N/A for the other",
                                   email=email, name=name)
        cur = mysql.connection.cursor()
        # If email is N/A, then the user will be registered under the nutritionist role
        if email.casefold() == "n/a":
            # Error check for incorrect email format
            if "@" not in nutritionistEmail:
                return render_template("register.html", message="Incorrect email format", email=email, name=name)
            cur.execute("SELECT * FROM users WHERE email = %s", (nutritionistEmail,))
            nEmailResponse = cur.fetchall()
            # Error check for an already registered email
            if len(nEmailResponse) > 0:
                return render_template("register.html", message="Email is already in use", email=email, name=name)
            user_role = 1  # nutritionist
            # Insert new entry into users table
            cur.execute("INSERT INTO users(user_role, name, email, pass) VALUES(%s, %s, %s, %s)",
                        (user_role, name, nutritionistEmail, password,))
        # If nutritionist email is N/A, then the user will be registered under the user role
        if nutritionistEmail.casefold() == "n/a":
            # Error check for incorrect email format
            if "@" not in email:
                return render_template("register.html", message="Incorrect email format", email=email, name=name)
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            emailResponse = cur.fetchall()
            # Error check for an already registered email
            if len(emailResponse) > 0:
                return render_template("register.html", message="Email is already in use", email=email, name=name)
            # Insert new entry into users table
            cur.execute("INSERT INTO users(user_role, name, email, pass, gender, age) VALUES(%s, %s, %s, %s, %s, %s)",
                        (user_role, name, email, password, gender, age))
        mysql.connection.commit()
        cur.close()
        return render_template("register.html", message="Registration successful", email=email, name=name)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        # Get all the values from the login form
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        # Error check for empty fields
        if password.decode('utf-8') == "" or email == "":
            return render_template("login.html", message="Please fill in the fields")
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Find matching email in users table and error check for nonexistent email
        emailResult = cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        if emailResult > 0:
            user = cur.fetchone()
        else:
            return render_template("login.html", message="Email does not exist")
        cur.close()
        # Check password match
        if user['pass'].encode('utf-8') == password:
            # Start user session
            session['user_id'] = user['user_id']
            # Redirect to user homepage if user role is user
            if user['user_role'] == 0:
                return redirect(url_for("userHomepage"))
            # Redirect to nutritionist homepage if user role is nutritionist
            if user['user_role'] == 1:
                return redirect(url_for("nutritionistHomepage"))
        else:
            return render_template("login.html", message="Password incorrect")
    else:
        return render_template("login.html", message="")


@app.route('/userHomepage')
def userHomepage():
    #display some daily data for user
    return render_template("userHomepage.html")


@app.route('/nutritionistHomepage')
def nutritionistHomepage():
    #display some daily data for nutritionist
    return render_template("nutritionistHomepage.html")


@app.route('/health', methods=["GET", "POST"])
def health():
    #health stuff (form info insert into databse & retrieve data)
    if request.method == 'POST':
        height = request.form['height']
        weight = request.form['weight']
        date = datetime.now()
        bmi = (int(weight)*703)/(int(height)**2)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO fitness(user_id, date, bmi, height, weight) VALUES(%s, %s, %s, %s, %s)",
            (session['user_id'], date.strftime("%m/%d/%y"), bmi, height, weight,))
        mysql.connection.commit()
        cur.close()
        return render_template("health.html", message="Saved Successfully")
    else:
        return render_template("health.html", message="")


@app.route('/exercise')
def exercise():
    #exercise stuff (form info insert into databse & retrieve data)
    return render_template("exercise.html")


@app.route('/nutrition', methods=["GET", "POST"])
def nutrition():
    date = datetime.now()
    calorieInMessage, waterMessage = "", ""
    calorieIntakeData, waterIntakeData = {}, {}
    if request.method == 'POST':
        # Handle the calorie intake form
        if 'calorieIn' in request.form:
            calorieinamount = request.form.get('calorieInAmount')
            # Error check for empty field
            if calorieinamount == "":
                return render_template("nutrition.html", calorieInMessage="Please fill in this field")
            cur = mysql.connection.cursor()
            # Check if there is an entry in the fitness table for today's date
            cur.execute("SELECT * FROM fitness WHERE date=%s AND user_id=%s",
                        (date.strftime("%m/%d/%y"), session['user_id'],))
            dayResponse = cur.fetchall()
            # If there is already an entry for today's date, update the calorie intake value for that entry
            if len(dayResponse) != 0:
                cur.execute("UPDATE fitness SET caloriesIntake=%s WHERE date=%s AND user_id=%s",
                            (calorieinamount, date.strftime("%m/%d/%y"), session['user_id'],))
            else:
                cur.execute("INSERT INTO fitness(user_id, date, caloriesIntake) VALUES(%s, %s, %s)",
                            (session['user_id'], date.strftime("%m/%d/%y"), calorieinamount,))
            mysql.connection.commit()
            cur.close()
            calorieInMessage = "Successfully Saved"
        # Handle the water intake form
        if 'water' in request.form:
            wateramount = request.form['waterAmount']
            # Error check for empty field
            if wateramount == "":
                return render_template("nutrition.html", waterMessage="Please fill in this field")
            cur = mysql.connection.cursor()
            # Check if there is an entry in the fitness table for today's date
            cur.execute("SELECT * FROM fitness WHERE date=%s AND user_id=%s",
                        (date.strftime("%m/%d/%y"), session['user_id'],))
            dayResponse = cur.fetchall()
            # If there is already an entry for today's date, update the water intake value for that entry
            if len(dayResponse) != 0:
                cur.execute("UPDATE fitness SET waterIntake=%s WHERE date=%s AND user_id=%s",
                            (wateramount, date.strftime("%m/%d/%y"), session['user_id'],))
            else:
                cur.execute("INSERT INTO fitness(user_id, date, waterIntake) VALUES(%s, %s, %s)",
                            (session['user_id'], date.strftime("%m/%d/%y"), wateramount,))
            mysql.connection.commit()
            cur.close()
            waterMessage = "Successfully Saved"
    curr = mysql.connection.cursor()
    # Get all the saved calorie intake data from the fitness table
    calorieResult = curr.execute("SELECT * FROM fitness WHERE user_id=%s AND caloriesIntake IS NOT NULL",
                                 (session['user_id'],))
    if calorieResult > 0:
        calorieIntakeData = curr.fetchall()
    # Get all the saved water intake data from the fitness table
    waterResult = curr.execute("SELECT * from fitness WHERE user_id=%s AND waterIntake IS NOT NULL", (session['user_id'],))
    if waterResult > 0:
        waterIntakeData = curr.fetchall()
    curr.close()
    return render_template("nutrition.html", calorieInMessage=calorieInMessage, waterMessage=waterMessage,
                           calorieIntakeData=calorieIntakeData, waterIntakeData=waterIntakeData)


@app.route('/goals', methods=["GET", "POST"])
def goals():
    category = ""
    message = ""
    date = datetime.now()
    achievedGoals, currentGoals, currentWeightGoals, currentCalorieGoals = {}, {}, {}, {}
    if request.method == 'POST':
        # Handle the create new goal form
        if 'newGoal' in request.form:
            goalamount = request.form['amount']
            formcategory = request.form.get('goalcategory')
            # Error check for empty fields
            if goalamount == "" or formcategory == "10":
                return render_template("goals.html", message="Please fill in all fields")
            # Determine the new goal's category from the value of the selected dropdown item
            if formcategory == "1":
                category = "Weight"
            if formcategory == "2":
                category = "Net Calories"
            cur = mysql.connection.cursor()
            # Check if there is an entry in the goals table for today's date
            cur.execute("SELECT * FROM goals WHERE category=%s AND date=%s AND user_id=%s AND completion IS NULL",
                        (category, date.strftime("%m/%d/%y"), session['user_id'],))
            dayResponse = cur.fetchall()
            # If there is already an entry for today's date, update the goal amount value for that entry
            if len(dayResponse) != 0:
                cur.execute("UPDATE goals SET amount=%s WHERE category=%s AND date=%s AND user_id=%s AND completion "
                            "IS NULL", (goalamount, category, date.strftime("%m/%d/%y"), session['user_id'],))
            else:
                cur.execute("INSERT INTO goals(user_id, date, category, amount) VALUES(%s, %s, %s, %s)",
                            (session['user_id'], date.strftime("%m/%d/%y"), category, goalamount,))
            mysql.connection.commit()
            cur.close()
            message = "Successfully Saved"
        # Handle the remove goal form for current goals
        if 'removeGoal' in request.form:
            selectcategory = ""
            formselectcategory = request.form.get('category')
            # Determine the goal category from the value of the selected display dropdown item
            if formselectcategory == "1":
                selectcategory = "Weight"
            if formselectcategory == "2":
                selectcategory = "Net Calories"
            curd = mysql.connection.cursor()
            # Delete the current goal specified by the date value returned from the form
            curd.execute("DELETE FROM goals WHERE category=%s AND date=%s AND completion IS NULL",
                         (selectcategory, request.form['goal_delete'],))
            mysql.connection.commit()
            curd.close()
    cure = mysql.connection.cursor()
    ####################################################################
    # This part might have to be implemented in other methods
    # Get the saved fitness data for today
    dayRecord = cure.execute("SELECT * FROM fitness WHERE user_id=%s AND date=%s",
                          (session['user_id'], date.strftime("%m/%d/%y"),))
    if dayRecord > 0:
        todaysrecord = cure.fetchone()
        # Check the goals table for a weight goal with an amount that matches the weight entered for the day
        gweight = cure.execute("SELECT * FROM goals WHERE category=%s AND amount=%s AND user_id=%s "
                               "AND completion IS NULL", ("Weight", todaysrecord['weight'], session['user_id'],))
        # If there is a match, then the goal is achieved. Update that weight goal with today as the completion date
        if gweight > 0:
            cure.execute("UPDATE goals SET completion=%s WHERE category=%s AND amount=%s AND user_id=%s "
                         "AND completion IS NULL", (date.strftime("%m/%d/%y"), "Weight", todaysrecord['weight'],
                                                    session['user_id'],))
        # Check that there are non null values for the calorie intake and burn for today's fitness entry
        if todaysrecord['caloriesIntake'] is not None and todaysrecord['caloriesBurned'] is not None:
            # Check the goals table for a net calories goal with an amount that matches the net calories for the day
            gcalorie = cure.execute("SELECT * FROM goals WHERE category=%s AND amount=%s AND user_id=%s "
                                    "AND completion IS NULL", ("Net Calories",
                                    todaysrecord['caloriesIntake']-todaysrecord['caloriesBurned'], session['user_id'],))
            # If there is a match, update that net calories goal with today as the completion date
            if gcalorie > 0:
                cure.execute("UPDATE goals SET completion=%s WHERE category=%s AND amount=%s AND user_id=%s "
                             "AND completion IS NULL", (date.strftime("%m/%d/%y"), "Net Calories",
                             todaysrecord['caloriesIntake']-todaysrecord['caloriesBurned'], session['user_id'],))
    ##################################################################
    # Get all the achieved goals from the goals table
    goalResult = cure.execute("SELECT * FROM goals WHERE user_id=%s AND completion IS NOT NULL", (session['user_id'],))
    if goalResult > 0:
        achievedGoals = cure.fetchall()
    mysql.connection.commit()
    cure.close()
    ####################
    curc = mysql.connection.cursor()
    # Get all the current goals from the goals table
    currentResult = curc.execute("SELECT * from goals WHERE user_id=%s AND completion IS NULL", (session['user_id'],))
    if currentResult > 0:
        currentGoals = curc.fetchall()
    # Get all the current weight goals from the goals table
    weightResult = curc.execute("SELECT * from goals WHERE category=%s AND user_id=%s AND completion IS NULL",
                                ("Weight", session['user_id'],))
    if weightResult > 0:
        currentWeightGoals = curc.fetchall()
    # Get all the current net calories goals from the goals table
    netcaloriesResult = curc.execute("SELECT * from goals WHERE category=%s AND user_id=%s AND completion IS NULL",
                                ("Net Calories", session['user_id'],))
    if netcaloriesResult > 0:
        currentCalorieGoals = curc.fetchall()
    curc.close()
    return render_template("goals.html", message=message, achievedGoals=achievedGoals, currentGoals=currentGoals,
                           currentWeightGoals=currentWeightGoals, currentCalorieGoals=currentCalorieGoals)


@app.route('/userAccount')
def userAccount():
    #get user account data, save revision & connection to nutritionist
    return render_template("userAccount.html")


@app.route('/clients', methods=["GET", "POST"])
def clients():
    noneMessage, message = "", ""
    # Preset default values in case there is no corresponding value saved anywhere in the db
    connectedUsers, viewedUser, heightUser, weightUser, bmiUser, bmrUser, calorieinUser, wgoalUser, cgoalUser = \
        {}, {'name': None, 'user_id':None, 'feedback': None}, {'height': None}, {'weight': None}, {'BMI': None}, \
        {'BMR': None}, {'caloriesIntake': None}, {'amount': None}, {'amount': None}
    cur = mysql.connection.cursor()
    # Find the users connected to the nutritionist in the users table
    cur.execute("SELECT * FROM users WHERE user_id=%s", (session['user_id'],))
    nutritionist = cur.fetchone()
    connectResult = cur.execute("SELECT * FROM users WHERE nutritionist=%s", (nutritionist['email'],))
    if connectResult > 0:
        connectedUsers = cur.fetchall()
    else:
        noneMessage = "No Connected Users"
    cur.close()
    if request.method == 'POST':
        # Handle the view info form for selected user
        if 'userInfo' in request.form:
            user = request.form['user']
            curv = mysql.connection.cursor()
            # Get the selected user from the users table
            nresult = curv.execute("SELECT * FROM users WHERE user_id=%s", (user,))
            if nresult > 0:
                viewedUser = curv.fetchone()
            # Get the most recent height of selected user from the fitness table
            hresult = curv.execute("SELECT * FROM fitness WHERE user_id=%s AND height is NOT NULL "
                                   "ORDER BY date DESC LIMIT 1", (user,))
            if hresult > 0:
                heightUser = curv.fetchone()
            # Get the most recent weight of selected user from the fitness table
            wresult = curv.execute("SELECT * FROM fitness WHERE user_id=%s AND weight is NOT NULL "
                                   "ORDER BY date DESC LIMIT 1", (user,))
            if wresult > 0:
                weightUser = curv.fetchone()
            # Get the most recent bmi of selected user from the fitness table
            iresult = curv.execute("SELECT * FROM fitness WHERE user_id=%s AND bmi is NOT NULL "
                                   "ORDER BY date DESC LIMIT 1", (user,))
            if iresult > 0:
                bmiUser = curv.fetchone()
            # Get the most recent bmr of selected user from the fitness table
            rresult = curv.execute("SELECT * FROM fitness WHERE user_id=%s AND bmr is NOT NULL "
                                   "ORDER BY date DESC LIMIT 1", (user,))
            if rresult > 0:
                bmrUser = curv.fetchone()
            # Get the most recent calorie intake of selected user from the fitness table
            cresult = curv.execute("SELECT * FROM fitness WHERE user_id=%s AND caloriesIntake is NOT NULL "
                                   "ORDER BY date DESC LIMIT 1", (user,))
            if cresult > 0:
                calorieinUser = curv.fetchone()
            # Get the most recent weight goal of selected user from the goals table
            wgresult = curv.execute("SELECT * FROM goals WHERE user_id=%s AND category=%s AND completion IS NULL "
                                    "ORDER BY date DESC LIMIT 1", (user, "Weight",))
            if wgresult > 0:
                wgoalUser = curv.fetchone()
            # Get the most recent net calories goal of selected user from the goals table
            cgresult = curv.execute("SELECT * FROM goals WHERE user_id=%s AND category=%s AND completion IS NULL "
                                    "ORDER BY date DESC LIMIT 1", (user, "Net Calories",))
            if cgresult > 0:
                cgoalUser = curv.fetchone()
            curv.close()
        # Handle the feedback form for selected user
        if 'feedback' in request.form:
            feedback = request.form['feedbackDetails']
            # Error check for empty field
            if feedback == "":
                return render_template("clients.html", message="Please enter feedback", connectedUsers=connectedUsers,
                                       viewedUser=viewedUser, heightUser=heightUser, weightUser=weightUser,
                                       bmiUser=bmiUser, bmrUser=bmrUser, calorieinUser=calorieinUser,
                                       wgoalUser=wgoalUser, cgoalUser=cgoalUser)
            userRecommend = request.form['userRecommend']
            curf = mysql.connection.cursor()
            # Update the feedback for the selected user in the users table
            curf.execute("UPDATE users SET feedback=%s WHERE user_id=%s", (feedback, userRecommend,))
            mysql.connection.commit()
            curf.close()
            message = "Successfully Saved"
    return render_template("clients.html", noneMessage=noneMessage, message=message, connectedUsers=connectedUsers,
                           viewedUser=viewedUser, heightUser=heightUser, weightUser=weightUser, bmiUser=bmiUser,
                           bmrUser=bmrUser, calorieinUser=calorieinUser, wgoalUser=wgoalUser, cgoalUser=cgoalUser)


@app.route('/nutritionistAccount')
def nutritionistAccount():
    #get nutritionist account data, save revision
    return render_template("nutritionistAccount.html")


@app.route('/logout')
def logout():
    session.clear()
    return render_template("frontpage.html")


if __name__ == '__main__':
    app.secret_key = "akakakakjajhaaaa"
    app.run(debug=True)
