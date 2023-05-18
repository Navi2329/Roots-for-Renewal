from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL

app = Flask(__name__, static_folder='static')


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'lotus@123'
app.config['MYSQL_DB'] = 'authentication'

mysql = MySQL(app)


@app.route('/', methods=['GET', 'POST'])
def hello():
    return render_template('login.html')


@app.route('/form_signup', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['txt']
        email = request.form['email']
        password = request.form['pswd']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        if user:
            return render_template('login.html', login_error="Email already exists.Please login to continue")
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
            return render_template('home.html')
        else:
            return render_template('login.html', login_error="Password and email do not match")

    return render_template('login.html', login_error="")


@app.route('/logout')
def logout():
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
