import MySQLdb
from flask import Flask, render_template, redirect, flash, request, url_for, session
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__, template_folder='templates')
app.secret_key = "Hello"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'rootpassword'
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
        userEmail = request.form['email']
        password = request.form['password'].encode('utf-8')
        nutritionistEmail = request.form['nutritionistEmail']
        # hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
        # Error check for empty fields
        if password.decode('utf-8') == "" or userEmail == "" or nutritionistEmail == "" or name == "" or formcategory == "10" or formdate == "":
            return render_template("register.html", message="Please fill in all required fields", email=userEmail, name=name)
        bday = datetime.strptime(formdate, '%Y-%m-%d').date()
        # Check if the birth date entered is valid
        if bday > datetime.today().date():
            return render_template("register.html", message="Invalid Birth Date", email=userEmail, name=name)
        # Calculate user age
        if datetime.today().month > bday.month:
            age = datetime.today().year - bday.year
        elif datetime.today().month == bday.month:
            if datetime.today().day >= bday.day:
                age = datetime.today().year - bday.year
        else:
            age = datetime.today().year - bday.year - 1
        # Check gender type
        if formcategory == "1":
            gender = "Female"
        else:
            gender = "Male"
        # Error check for incorrect format - only one email required
        if (userEmail.casefold() != "n/a" and nutritionistEmail.casefold() != "n/a") or \
                (userEmail.casefold() == "n/a" and nutritionistEmail.casefold() == "n/a"):
            return render_template("register.html", message="Please enter one email and enter N/A for the other",
                                   email=userEmail, name=name)
        cur = mysql.connection.cursor()
        # If email is N/A, then the user will be registered under the nutritionist role
        if userEmail.casefold() == "n/a":
            user_role = 1  # nutritionist
            email = nutritionistEmail
        # If nutritionist email is N/A, then the user will be registered under the user role
        if nutritionistEmail.casefold() == "n/a":
            email = userEmail
        # Error check for incorrect email format
        if "@" not in email:
            return render_template("register.html", message="Incorrect email format", email=email, name=name)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        nEmailResponse = cur.fetchall()
        # Error check for an already registered email
        if len(nEmailResponse) > 0:
            return render_template("register.html", message="Email is already in use", email=email, name=name)
        # Insert new entry into users table
        cur.execute("INSERT INTO users(user_role, name, email, pass, gender, age) VALUES(%s, %s, %s, %s, %s, %s)",
                    (user_role, name, email, password, gender, age,))
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
        cur = mysql.connection.cursor()
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
    return render_template("userHomepage.html")


@app.route('/nutritionistHomepage')
def nutritionistHomepage():
    return render_template("nutritionistHomepage.html")


@app.route('/health', methods=["GET", "POST"])
def health():
    message = ""
    bmi, bmr, weight, height, weightData = None, None, None, None, {}
    if request.method == 'POST':
        # Get users registered age and gender
        cure = mysql.connection.cursor()
        cure.execute("SELECT * FROM users where user_id=%s", (session['user_id'],))
        user = cure.fetchone()
        userage = user['age']
        userGen = user['gender']
        cure.close()
        # Get all the values from the health form
        height = request.form['height']
        weight = request.form['weight']
        date = datetime.now()
        # Error check for empty fields
        if height == "" or weight == "":
            message = "Please fill the fields"
            return render_template("health.html", message=message, bmi=bmi, bmr=bmr, userage=userage, weight=weight,
                                   height=height, weightData=weightData)
        # Calculate BMI and BMR
        bmi = (int(weight) * 703) / (int(height) ** 2)
        # Harris-Benedict Forumula for BMR
        if userGen == 'Male':
            bmr = 655 + (4.35 * int(weight)) + (4.7 * int(height)) - (6.8 * int(userage)) - 161
        else:
            bmr = 66 + (6.23 * int(weight)) + (12.7 * int(height)) - (5 * int(userage)) + 5
        bmi = round(bmi, 1)
        bmr = round(bmr, 2)
        cur = mysql.connection.cursor()
        # Check if there is an entry in the fitness table for today's date
        cur.execute("SELECT * FROM fitness WHERE date=%s AND user_id=%s", (date.strftime("%m/%d/%y"), session['user_id'],))
        dayResponse = cur.fetchall()
        # If there is already an entry for today's date in fitness table, update the health values for that entry
        if len(dayResponse) != 0:
            cur.execute("UPDATE fitness SET height=%s, weight=%s, bmi=%s, bmr=%s WHERE date=%s AND user_id=%s",
                        (height, weight, bmi, bmr, date.strftime("%m/%d/%y"), session['user_id'],))
        else:
            cur.execute("INSERT INTO fitness(user_id, date, bmi, bmr, height, weight) VALUES(%s, %s, %s, %s, %s, %s)",
                        (session['user_id'], date.strftime("%m/%d/%y"), bmi, bmr, height, weight,))
        mysql.connection.commit()
        cur.close()
        message = "Saved Successfully"
    cure = mysql.connection.cursor()
    cure.execute("SELECT * FROM users where user_id=%s", (session['user_id'],))
    user = cure.fetchone()
    userage = user['age']
    cure.close()
    curv = mysql.connection.cursor()
    # Get the most recent heath entry of the user from the fitness table
    hresult = curv.execute("SELECT * FROM fitness WHERE user_id=%s AND height is NOT NULL "
                           "ORDER BY date DESC LIMIT 1", (session['user_id'],))
    if hresult > 0:
        health = curv.fetchone()
        bmi = health['BMI']
        bmr = health['BMR']
        weight = health['weight']
        height = health['height']
    # Get all the saved weight data from the fitness table
    weightResult = curv.execute("SELECT * from fitness WHERE user_id=%s AND weight IS NOT NULL", (session['user_id'],))
    if weightResult > 0:
        weightData = curv.fetchall()
    curv.close()
    return render_template("health.html", message=message, bmi=bmi, bmr=bmr, userage=userage, weight=weight,
                           height=height, weightData=weightData)


@app.route('/exercise',  methods=["GET", "POST"])
def exercise():
    category = ""
    date = datetime.now()
    calorieBurn, calorieburnGoal, mileRecord, weightliftRecord, cardioRecord = 0, 0, {}, {}, {}
    curv = mysql.connection.cursor()
    # Check if there is an entry in the exercise table for today's date
    result = curv.execute("SELECT * FROM exercise WHERE date=%s AND user_id=%s",
                          (date.strftime("%m/%d/%y"), session['user_id'],))
    # If there is no entry, set today's workout categories to default 0
    if result == 0:
        curv.execute("INSERT INTO exercise(user_id, date, category, exerciseAmount) "
                     "VALUES(%s, %s, %s, %s)", (session['user_id'], date.strftime("%m/%d/%y"), "miles run", 0,))
        curv.execute("INSERT INTO exercise(user_id, date, category, exerciseAmount) "
                     "VALUES(%s, %s, %s, %s)", (session['user_id'], date.strftime("%m/%d/%y"), "weight lifted", 0,))
        curv.execute("INSERT INTO exercise(user_id, date, category, exerciseAmount) "
                     "VALUES(%s, %s, %s, %s)", (session['user_id'], date.strftime("%m/%d/%y"), "cardio", 0,))
        mysql.connection.commit()
    curv.close()
    # Handle exercise form
    if request.method == 'POST':
        # Get values of the form
        exerciseamount = request.form['amount']
        calorieburn = request.form['calorieburn']
        goalamount = request.form['calorieburngoal']
        formcategory = request.form.get('exercisecategory')
        # The user does not have to enter the goal caloric burn amount if it already exists for the day
        if goalamount == "":
            cur = mysql.connection.cursor()
            result = cur.execute("SELECT * FROM fitness WHERE user_id=%s AND burnGoalAmount IS NOT NULL "
                                 "ORDER BY date DESC LIMIT 1", (session['user_id'],))
            if result > 0:
                recent = cur.fetchone()
                goalamount = recent['burnGoalAmount']
            else:
                flash('calorie burn goal not inputted')
                return redirect(url_for('exercise'))
        # Error check for empty select, amount, and caloric burn fields
        if formcategory == "10":
            flash('no selected exercise')
            return redirect(url_for('exercise'))
        if exerciseamount == "":
            flash('exercise amount not inputted')
            return redirect(url_for('exercise'))
        if calorieburn == "":
            flash('calories burned not inputted')
            return redirect(url_for('exercise'))
        # Determine the exercise category from the value of the selected dropdown item
        if formcategory == "1":
            category = "miles run"
        if formcategory == "2":
            category = "weight lifted"
        if formcategory == "3":
            category = "cardio"
        cur = mysql.connection.cursor()
        # Check if there is an entry in the fitness table for today's date
        dayresult = cur.execute("SELECT * FROM fitness WHERE date=%s AND user_id=%s",
                                (date.strftime("%m/%d/%y"), session['user_id'],))
        # If there is already an entry for today's date, update the calorie data for that entry
        if dayresult > 0:
            dayResponse = cur.fetchone()
            # If there is an existing calorie burn value, add the inputted calories to the old value
            if dayResponse['caloriesBurned'] is not None:
                calorieburn = int(calorieburn) + dayResponse['caloriesBurned']
                cur.execute("UPDATE fitness SET caloriesBurned=%s, burnGoalAmount=%s WHERE date=%s AND user_id=%s",
                            (calorieburn, goalamount, date.strftime("%m/%d/%y"), session['user_id'],))
            else:
                cur.execute("UPDATE fitness SET caloriesBurned=%s, burnGoalAmount=%s WHERE date=%s AND user_id=%s",
                            (calorieburn, goalamount, date.strftime("%m/%d/%y"), session['user_id'],))
        else:
            cur.execute("INSERT INTO fitness(user_id, date, caloriesBurned, burnGoalAmount) VALUES(%s, %s, %s, %s)",
                        (session['user_id'], date.strftime("%m/%d/%y"), calorieburn, goalamount,))
        mysql.connection.commit()
        cur.close()
        ####################
        cure = mysql.connection.cursor()
        # Update the exercise category and amount data for the day in the exercise table
        cure.execute("SELECT * FROM exercise WHERE category=%s AND date=%s AND user_id=%s",
                     (category, date.strftime("%m/%d/%y"), session['user_id'],))
        dayexerciseResponse = cure.fetchone()
        # Add the exercise amount to the existing value
        exerciseamount = int(exerciseamount) + dayexerciseResponse['exerciseAmount']
        cure.execute("UPDATE exercise SET exerciseAmount=%s WHERE category=%s AND date=%s AND user_id=%s",
                     (exerciseamount, category, date.strftime("%m/%d/%y"), session['user_id'],))
        mysql.connection.commit()
        cure.close()
    curc = mysql.connection.cursor()
    # Get the most recent exercise calorie burn and goal input from the fitness table
    exerciseresult = curc.execute("SELECT * FROM fitness WHERE user_id=%s AND caloriesBurned IS NOT NULL "
                                  "AND burnGoalAmount IS NOT NULL ORDER BY date DESC LIMIT 1", (session['user_id'],))
    if exerciseresult > 0:
        recentexercise = curc.fetchone()
        calorieBurn = recentexercise['caloriesBurned']
        calorieburnGoal = recentexercise['burnGoalAmount']
    # Get all the miles run data from the exercise table
    mileResult = curc.execute("SELECT * from exercise WHERE category=%s AND user_id=%s", ("miles run", session['user_id'],))
    if mileResult > 0:
        mileRecord = curc.fetchall()
    # Get all the weightlifting data from the exercise table
    weightResult = curc.execute("SELECT * from exercise WHERE category=%s AND user_id=%s", ("weight lifted", session['user_id'],))
    if weightResult > 0:
        weightliftRecord = curc.fetchall()
    # Get all the cardio data from the exercise table
    cardioResult = curc.execute("SELECT * from exercise WHERE category=%s AND user_id=%s", ("cardio", session['user_id'],))
    if cardioResult > 0:
        cardioRecord = curc.fetchall()
    curc.close()
    return render_template("exercise.html", calorieBurn=calorieBurn, calorieburnGoal=calorieburnGoal,
                           mileRecord=mileRecord, weightliftRecord=weightliftRecord, cardioRecord=cardioRecord)


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
            cur.execute("SELECT * FROM fitness WHERE date=%s AND user_id=%s", (date.strftime("%m/%d/%y"), session['user_id'],))
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
            cur.execute("SELECT * FROM fitness WHERE date=%s AND user_id=%s", (date.strftime("%m/%d/%y"), session['user_id'],))
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
    cur = mysql.connection.cursor()
    # Get all the saved calorie intake data from the fitness table
    calorieResult = cur.execute("SELECT * FROM fitness WHERE user_id=%s AND caloriesIntake IS NOT NULL", (session['user_id'],))
    if calorieResult > 0:
        calorieIntakeData = cur.fetchall()
    # Get all the saved water intake data from the fitness table
    waterResult = cur.execute("SELECT * from fitness WHERE user_id=%s AND waterIntake IS NOT NULL", (session['user_id'],))
    if waterResult > 0:
        waterIntakeData = cur.fetchall()
    cur.close()
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
                                                               todaysrecord['caloriesIntake'] - todaysrecord[
                                                                   'caloriesBurned'], session['user_id'],))
            # If there is a match, update that net calories goal with today as the completion date
            if gcalorie > 0:
                cure.execute("UPDATE goals SET completion=%s WHERE category=%s AND amount=%s AND user_id=%s "
                             "AND completion IS NULL", (date.strftime("%m/%d/%y"), "Net Calories",
                                                        todaysrecord['caloriesIntake'] - todaysrecord['caloriesBurned'],
                                                        session['user_id'],))
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


@app.route('/userAccount', methods=["GET", "POST"])
def userAccount():
    message = ""
    usernutritionist, nutritionists = {'name': None}, {}
    if request.method == 'POST':
        # Handle the update user information form
        if 'updateInfo' in request.form:
            # Get the values of the change information form
            ncategory = request.form.get('infocategory')
            infoUpdate = request.form['updatedInfo']
            cur = mysql.connection.cursor()
            # Get the current user
            cur.execute("SELECT * FROM users where user_id=%s", (session['user_id'],))
            user = cur.fetchone()
            # Check if there are missing fields
            if ncategory == "10" or len(infoUpdate) == 0:
                message = "Fields not filled out"
            # Check if the category is email and update user email in users table
            if ncategory == "1" and len(infoUpdate) > 0:
                # Error check for incorrectly formatted email
                if "@" not in infoUpdate:
                    message = "Incorrect email format"
                else:
                    cur.execute("SELECT * FROM users WHERE email = %s", (infoUpdate,))
                    nEmailResponse = cur.fetchall()
                    # Error check for an already registered email
                    if len(nEmailResponse) > 0:
                        message = "Email is already in use"
                    else:
                        cur.execute("UPDATE users SET email=%s WHERE user_id=%s", (infoUpdate, (session['user_id'],)))
                        message = "Successfully Saved"
            # Check if the category is password and update user password in users table
            if ncategory == "2" and len(infoUpdate) > 0:
                # Error check for same password
                if user['pass'] == infoUpdate:
                    message = "Same Password"
                else:
                    cur.execute("UPDATE users SET pass=%s WHERE user_id=%s", (infoUpdate, (session['user_id'],)))
                    message = "Successfully Saved"
            # Check if the category is nutritionist email and update user's nutritionist in users table
            if ncategory == "3" and len(infoUpdate) > 0:
                # Check if the nutritionist requested exists
                resultN = cur.execute("SELECT * FROM users where user_role=%s AND email=%s", (1, infoUpdate))
                foundnutritionist = cur.fetchone()
                if resultN == 0:
                    message = "Nutritionist does not exist"
                else:
                    # Error check for same nutritionist email
                    if user['nutritionist'] == foundnutritionist['user_id']:
                        message = "Same Nutritionist"
                    else:
                        cur.execute("UPDATE users SET nutritionist=%s WHERE user_id=%s", (foundnutritionist['user_id'],
                                                                                          (session['user_id'],)))
                        message = "Successfully Saved"
            mysql.connection.commit()
            cur.close()
        # Handle the remove nutritionist form
        if 'removeNutritionist' in request.form:
            formcategory = request.form.get('category')
            curd = mysql.connection.cursor()
            curd.execute("SELECT * FROM users where user_id=%s", (session['user_id'],))
            user = curd.fetchone()
            # Item to remove - 1 is nutritionist
            if formcategory == "1":
                # Update the user info to have no nutritionist in the users table
                curd.execute("UPDATE users SET nutritionist=%s WHERE nutritionist=%s", (None, user['nutritionist'],))
            # Item to remove - 2 is nutritionist feedback
            if formcategory == "2":
                # Update the user info to have no nutritionist feedback in the users table
                curd.execute("UPDATE users SET feedback=%s WHERE feedback=%s",
                             (None, user['feedback'],))
            mysql.connection.commit()
            curd.close()
    cure = mysql.connection.cursor()
    cure.execute("SELECT * FROM users where user_id=%s", (session['user_id'],))
    user = cure.fetchone()
    # Get the user's nutritionist information
    if user['nutritionist'] is not None:
        cure.execute("SELECT * FROM users where user_id=%s", (user['nutritionist'],))
        usernutritionist = cure.fetchone()
    # Get the available registered nutritionists the user can connect with
    nresult = cure.execute("SELECT * FROM users where user_role=%s", (1,))
    if nresult > 0:
        nutritionists = cure.fetchall()
    cure.close()
    return render_template("userAccount.html", message=message, user=user, usernutritionist=usernutritionist, nutritionists=nutritionists)


@app.route('/clients', methods=["GET", "POST"])
def clients():
    noneMessage, message = "", ""
    # Preset default values in case there is no corresponding value saved anywhere in the db
    connectedUsers, viewedUser, healthUser, calorieinUser, wgoalUser, cgoalUser = \
        {}, {'name': None, 'user_id': None, 'feedback': None}, {'height': None, 'weight': None, 'BMI': None, 'BMR': None}, \
        {'caloriesIntake': None}, {'amount': None}, {'amount': None}
    cur = mysql.connection.cursor()
    # Find the users connected to the nutritionist in the users table
    connectResult = cur.execute("SELECT * FROM users WHERE nutritionist=%s", (session['user_id'],))
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
            # Get the most recent health info of selected user from the fitness table
            hresult = curv.execute("SELECT * FROM fitness WHERE user_id=%s AND height is NOT NULL "
                                   "ORDER BY date DESC LIMIT 1", (user,))
            if hresult > 0:
                healthUser = curv.fetchone()
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
                                       viewedUser=viewedUser, healthUser=healthUser, calorieinUser=calorieinUser,
                                       wgoalUser=wgoalUser, cgoalUser=cgoalUser)
            userRecommend = request.form['userRecommend']
            curf = mysql.connection.cursor()
            # Update the feedback for the selected user in the users table
            curf.execute("UPDATE users SET feedback=%s WHERE user_id=%s", (feedback, userRecommend,))
            mysql.connection.commit()
            curf.close()
            message = "Successfully Saved"
    return render_template("clients.html", noneMessage=noneMessage, message=message, connectedUsers=connectedUsers, viewedUser=viewedUser,
                           healthUser=healthUser, calorieinUser=calorieinUser, wgoalUser=wgoalUser, cgoalUser=cgoalUser)


@app.route('/nutritionistAccount', methods=["GET", "POST"])
def nutritionistAccount():
    message = ""
    if request.method == 'POST':
        # Get the values of the change information form
        ncategory = request.form.get('infocategorynutrition')
        infoUpdateN = request.form['updatedInfoNutrition']
        cur = mysql.connection.cursor()
        # Get the current user
        cur.execute("SELECT * FROM users where user_id=%s", (session['user_id'],))
        user = cur.fetchone()
        # Check if there are missing fields
        if ncategory == "10" or len(infoUpdateN) == 0:
            message = "Fields not filled out"
        # Check if the category is email and update users email in users table
        if ncategory == "1" and len(infoUpdateN) > 0:
            # Error check for incorrectly formatted email
            if "@" not in infoUpdateN:
                message = "Incorrect email format"
            else:
                cur.execute("SELECT * FROM users WHERE email = %s", (infoUpdateN,))
                nEmailResponse = cur.fetchall()
                # Error check for an already registered email
                if len(nEmailResponse) > 0:
                    message = "Email is already in use"
                else:
                    cur.execute("UPDATE users SET email=%s WHERE user_id=%s", (infoUpdateN, (session['user_id'],)))
                    message = "Successfully Saved"
        # Check if the category is password and update user password in users table
        if ncategory == "2" and len(infoUpdateN) > 0:
            # Error check for same password
            if user['pass'] == infoUpdateN:
                message = "Same Password"
            else:
                cur.execute("UPDATE users SET pass=%s WHERE user_id=%s", (infoUpdateN, (session['user_id'],)))
                message = "Successfully Saved"
        mysql.connection.commit()
        cur.close()
    cure = mysql.connection.cursor()
    cure.execute("SELECT * FROM users where user_id=%s", (session['user_id'],))
    user = cure.fetchone()
    cure.close()
    return render_template("nutritionistAccount.html", message=message, user=user)


@app.route('/logout')
def logout():
    session.clear()
    return render_template("frontpage.html")


if __name__ == '__main__':
    app.secret_key = "akakakakjajhaaaa"
    app.run(debug=True)
