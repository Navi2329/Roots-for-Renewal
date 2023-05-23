import json
from flask import Flask, jsonify, render_template, request, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__, static_folder='static')
app.secret_key = 'h#3gR52m$Pq56wJ@v^*8x4p$^Sb5&vK9'


app.config['MYSQL_HOST'] = 'sql12.freesqldatabase.com'
app.config['MYSQL_USER'] = 'sql12620127'
app.config['MYSQL_PASSWORD'] = 'Xp1Cy885lX'
app.config['MYSQL_DB'] = 'sql12620127'

mysql = MySQL(app)


@app.route('/', methods=['GET', 'POST'])
def hello():
    return render_template('landing_Final.html')


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
            session['email'] = email  
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
        cur.execute("SELECT * FROM user_plants WHERE email = %s AND type = %s AND variety = %s AND place = %s AND plant = %s",
                    (email, plant_type, variety, place, plant))
        existing_plant = cur.fetchone()

        if existing_plant:
            return 'The selected plant already exists in your history.', 409
        cur.execute("SELECT info FROM plants where plant=%s", (plant,))
        info = cur.fetchone()[0]
        cur.execute("SELECT img FROM plants where plant=%s", (plant,))
        img = cur.fetchone()[0]
        cur.execute("INSERT INTO user_plants (email, type, variety, place, plant,info,img) VALUES (%s, %s, %s, %s, %s,%s,%s)",
                    (email, plant_type, variety, place, plant,info,img))
        mysql.connection.commit()
        cur.close()
        return 'Plant data saved successfully'
    return 'Invalid request method', 400


@app.route("/history")
def history():
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT id,type,variety,place,plant,info,img FROM user_plants WHERE email = %s", (session.get('email'),))
    plants = []
    for row in cursor.fetchall():
        plants.append({
            "id": row[0],
            'type': row[1],
            'variety': row[2],
            'place': row[3],
            'plant': row[4],
            'info': row[5],
            'img': row[6],
        })
    cursor.close()
    return render_template("history.html", plants=plants)

@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/delete/<int:plant_id>', methods=['POST'])
def delete(plant_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM user_plants WHERE id = %s", (plant_id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Success'})


if __name__ == '__main__':
    app.run(debug=True)
