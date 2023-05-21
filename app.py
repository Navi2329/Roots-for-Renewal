import json
from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__, static_folder='static')
app.secret_key = 'h#3gR52m$Pq56wJ@v^*8x4p$^Sb5&vK9'


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'lotus@123'
app.config['MYSQL_DB'] = 'authentication'

mysql = MySQL(app)


@app.route('/', methods=['GET', 'POST'])
def hello():
    return render_template('Landing_Final.html')


@app.route('/form_signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['txt']
        email = request.form['email']
        password = request.form['pswd']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        if user:
            return render_template('login.html', login_error="Email already exists. Please login to continue")
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                    (username, email, password))
        mysql.connection.commit()
        cur.close()

        return redirect('/form_login')

    return render_template('login.html')


@app.route('/form_login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pswd']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and user[2] == password:
            session['email'] = email  # Store user's email in the session
            return render_template('home.html')
        else:
            if user and user[2] != password:
                return render_template('login.html', login_error="Password and email do not match")
            else:
                return render_template('login.html', login_error="Email Does not exist. Please signup to continue")

    return render_template('login.html', login_error="")


@app.route('/logout')
def logout():
    session.pop('email', None) 
    return redirect('/form_login')

@app.route('/functional')
def index():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT type, variety, place, plant FROM plants")
    rows = cursor.fetchall()
    plantData = {}
    for row in rows:
        type = row[0]
        variety = row[1]
        place = row[2]
        plant = row[3]
        if type not in plantData:
            plantData[type] = {}
        if variety not in plantData[type]:
            plantData[type][variety] = {}
        
        if place not in plantData[type][variety]:
            plantData[type][variety][place] = []
        plantData[type][variety][place].append(plant)
    return render_template('functional.html', plantData=json.dumps(plantData))

@app.route('/save_plant', methods=['POST'])
def save_plant():
    if request.method == 'POST':
        plant_data = request.get_json()
        email = session.get('email')
        if not email:
            return 'User not logged in', 401
        plant_type = plant_data.get('type')
        variety = plant_data.get('variety')
        place = plant_data.get('place')
        plant = plant_data.get('plant')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user_plants (email, type, variety, place, plant) VALUES (%s, %s, %s, %s, %s)",
                    (email, plant_type, variety, place, plant))
        mysql.connection.commit()
        cur.close()
        return 'Plant data saved successfully'
    return 'Invalid request method', 400

if __name__ == '__main__':
    app.run(debug=True)
