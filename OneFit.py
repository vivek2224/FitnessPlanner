from flask import Flask, render_template, redirect, request, url_for, session
from flask_mysqldb import MySQL

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
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        nutritionistEmail = request.form['nutritionistEmail']
        # hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
        if password.decode('utf-8') == "" or email == "" or name == "":
            return render_template("register.html", message="Please fill in all required fields", email=email,
                                   name=name)

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM fitnessplanner WHERE email = %s", (email,))
        response = cur.fetchall()
        # print(cur.fetchall())
        if len(response) != 0:
            return render_template("register.html", message="Email is already in use", email=email, name=name)
        cur.execute("INSERT INTO fitnessplanner(namew, email, pass, nutritionistEmail) VALUES(%s, %s, %s, %s)", (name, email, password, nutritionistEmail,))
        # cur = mysql.connection.cursor()
        mysql.connection.commit()
        cur.close()
        session['name'] = name
        session['email'] = email
        session['nutritionistEmail'] = nutritionistEmail

        return render_template("register.html", message="Registration successful", email=email,
                               name=name)


@app.route('/login')
def login():
    #if login successful
    #return redirect('/userHomepage') for user
    #return redirect('/nutritionistHomepage') for nutritionist
    #else
    #some error message
    return render_template("login.html")


@app.route('/userHomepage')
def userHomepage():
    #display some daily data for user
    return render_template("userHomepage.html")


@app.route('/nutritionistHomepage')
def nutritionistHomepage():
    #display some daily data for nutritionist
    return render_template("nutritionistHomepage.html")


@app.route('/health')
def health():
    #health stuff (form info insert into databse & retrieve data)
    return render_template("health.html")


@app.route('/exercise')
def exercise():
    #exercise stuff (form info insert into databse & retrieve data)
    return render_template("exercise.html")


@app.route('/nutrition')
def nutrition():
    #nutrition stuff (form info insert into databse & retrieve data)
    return render_template("nutrition.html")


@app.route('/goals')
def goals():
    #goals stuff (form info insert into databse & retrieve data)
    return render_template("goals.html")


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


if __name__ == '__main__':
    app.secret_key = "akakakakjajhaaaa"
    app.run(debug=True)