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
        user_role = 0
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        nutritionistEmail = request.form['nutritionistEmail']
        # hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
        if password.decode('utf-8') == "" or email == "" or name == "":
            return render_template("register.html", message="Please fill in all required fields", email=email,
                                   name=name)
        if(email != "N/A" and nutritionistEmail != "N/A") or (email == "N/A" and nutritionistEmail == "N/A"):
            return render_template("register.html", message="Please enter one email and enter N/A for the other",
                                   email=email, name=name)
        cur = mysql.connection.cursor()
        if email == "N/A":
            cur.execute("SELECT * FROM users WHERE email = %s", (nutritionistEmail,))
            response = cur.fetchall()
            # print(cur.fetchall())
            if len(response) > 3:
                return render_template("register.html", message="Email is already in use", email=nutritionistEmail, name=name)
            user_role = 1
            cur.execute("INSERT INTO users(user_role, name, email, pass) VALUES(%s, %s, %s, %s)",
                        (user_role, name, nutritionistEmail, password,))
        if nutritionistEmail == "N/A":
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            response = cur.fetchall()
            # print(cur.fetchall())
            if len(response) > 3:
                return render_template("register.html", message="Email is already in use", email=email, name=name)
            cur.execute("INSERT INTO users(user_role, name, email, pass) VALUES(%s, %s, %s, %s)",
                        (user_role, name, email, password,))
        # cur = mysql.connection.cursor()
        mysql.connection.commit()
        cur.close()
        return render_template("register.html", message="Registration successful", email=email,
                               name=name)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()
        ####################
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM users WHERE pass=%s", (password,))
        n = curl.fetchone()
        curl.close()
        if user['pass'].encode('utf-8') == password:
            session['user_id'] = user['user_id']
            if user['user_role'] == 0:
                # userHomepage()
                return redirect(url_for("userHomepage"))
            if user['user_role'] == 1:
                return redirect(url_for("nutritionistHomepage"))
        else:
            return render_template("login.html", message="Password or email incorrect")
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


@app.route('/nutrition')
def nutrition():
    #nutrition stuff (form info insert into databse & retrieve data)
    return render_template("nutrition.html")


@app.route('/goals', methods=["GET", "POST"])
def goals():
    category = ""
    message = ""
    date = datetime.now()
    achievedGoals, currentGoals, currentWeightGoals, currentCalorieGoals = {}, {}, {}, {}
    if request.method == 'POST':
        ncategory = request.form.get('goalcategory')
        if ncategory == "1":
            category = "Weight"
        if ncategory == "2":
            category = "Net Calories"
        goalamount = request.form['amount']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM goals WHERE category=%s AND date=%s AND user_id=%s AND completion IS NULL",
                    (category, date.strftime("%m/%d/%y"), session['user_id'],))
        response = cur.fetchall()
        if len(response) != 0:
            cur.execute("UPDATE goals SET amount=%s WHERE category=%s AND date=%s AND user_id=%s AND completion IS NULL",
                        (goalamount, category, date.strftime("%m/%d/%y"), session['user_id'],))
        else:
            cur.execute("INSERT INTO goals(user_id, date, category, amount) VALUES(%s, %s, %s, %s)",
                        (session['user_id'], date.strftime("%m/%d/%y"), category, goalamount,))
        mysql.connection.commit()
        cur.close()
        message = "Successfully Saved"
    cure = mysql.connection.cursor()
    record = cure.execute("SELECT * FROM fitness WHERE user_id=%s AND date=%s",
                          (session['user_id'], date.strftime("%m/%d/%y"),))
    if record > 0:
        daysrecord = cure.fetchone()
        gweight = cure.execute("SELECT * FROM goals WHERE category=%s AND amount=%s AND user_id=%s "
                               "AND completion IS NULL", ("Weight", daysrecord['weight'], session['user_id'],))
        if gweight > 0:
            cure.execute("UPDATE goals SET completion=%s WHERE category=%s AND amount=%s AND user_id=%s "
                         "AND completion IS NULL", (date.strftime("%m/%d/%y"), "Weight", daysrecord['weight'],
                                                    session['user_id'],))
        gcalorie = cure.execute("SELECT * FROM goals WHERE category=%s AND amount=%s AND user_id=%s "
                                "AND completion IS NULL", ("Net Calories", daysrecord['caloriesIntake']-daysrecord['caloriesBurned'],
                                                           session['user_id'],))
        if gcalorie > 0:
            cure.execute("UPDATE goals SET completion=%s WHERE category=%s AND amount=%s AND user_id=%s "
                         "AND completion IS NULL", (date.strftime("%m/%d/%y"), "Net Calories",
                                                    daysrecord['caloriesIntake']-daysrecord['caloriesBurned'], session['user_id'],))
    gresultValue = cure.execute("SELECT * FROM goals WHERE user_id=%s AND completion IS NOT NULL", (session['user_id'],))
    if gresultValue > 0:
        achievedGoals = cure.fetchall()
    mysql.connection.commit()
    cure.close()
    curc = mysql.connection.cursor()
    aresultValue = curc.execute("SELECT * from goals WHERE user_id=%s AND completion IS NULL", (session['user_id'],))
    if aresultValue > 0:
        currentGoals = curc.fetchall()
    wresultValue = curc.execute("SELECT * from goals WHERE category=%s AND user_id=%s AND completion IS NULL",
                                ("Weight", session['user_id'],))
    if wresultValue > 0:
        currentWeightGoals = curc.fetchall()
    cresultValue = curc.execute("SELECT * from goals WHERE category=%s AND user_id=%s AND completion IS NULL",
                                ("Net Calories", session['user_id'],))
    if cresultValue > 0:
        currentCalorieGoals = curc.fetchall()
    curc.close()
    return render_template("goals.html", message=message, achievedGoals=achievedGoals, currentGoals=currentGoals,
                           currentWeightGoals=currentWeightGoals, currentCalorieGoals=currentCalorieGoals)


@app.route('/delete_goal', methods=["GET", "POST"])
def delete_goal():
    selectcategory = ""
    nselectcategory = request.form.get('category')
    if nselectcategory == "1":
        selectcategory = "Weight"
    if nselectcategory == "2":
        selectcategory = "Net Calories"
    curd = mysql.connection.cursor()
    curd.execute("DELETE FROM goals WHERE category=%s AND date=%s AND completion IS NULL",
                 (selectcategory, request.form['goal_delete'],))
    mysql.connection.commit()
    curd.close()
    return redirect(url_for("goals"))


@app.route('/userAccount')
def userAccount():
    #get user account data, save revision & connection to nutritionist
    return render_template("userAccount.html")


@app.route('/clients')
def clients():
    #display list clients
    #redirect to a client details page or use drop down menu to view details
    return render_template("clients.html")


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