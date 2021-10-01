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
        mysql.connection.commit()
        cur.execute("SELECT * FROM fitnessplanner WHERE email = %s", (email,))
        response = cur.fetchall()
        # print(cur.fetchall())
        if len(response) != 0:
            return render_template("register.html", message="Email is already in use", email=email, name=name)
        cur.execute("INSERT INTO fitnessplanner(namw, email, pass, nutritionistEmail) VALUES(%s, %s, %s, %s)", (name, email, password, nutritionistEmail,))
        # cur = mysql.connection.cursor()
        session['name'] = name
        session['email'] = email
        session['nutritionistEmail'] = nutritionistEmail

        return render_template("register.html", message="Registration successful", email=email,
                               name=name)


if __name__ == '__main__':
    app.secret_key = "akakakakjajhaaaa"
    app.run(debug=True)