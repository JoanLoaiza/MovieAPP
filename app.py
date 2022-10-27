from sre_constants import SUCCESS
from unicodedata import category
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import static.config as cfg
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'qwerty123'

app.config['MYSQL_HOST'] = 'database-1.coldiu6iwivb.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'pythonlogin'

mysql = MySQL(app)


@app.route('/')
def index():
    session['logged_in'] = False
    session.clear()
    return redirect(url_for('ruta'))


@app.route('/movie')
def ruta():
    return render_template('login.html')


@app.route('/movie/home')
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))


@app.route('/movie/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/movie/register', methods=['GET', 'POST'])
def register():
    msg = ''
    session.clear()
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        
        category = 'danger'
        if account:
            msg = 'El usuario ya existe!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Correo electronico inválido!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'El nombre de usuario solo debe contener numeros y letras!'
        elif not len(password) >= 8:
            msg = 'La contraseña debe tener al menos 8 caracteres!'
        elif not username or not password:
            msg = 'Por favor, completa el formulario!'
        else:
            passw = cfg.get_hashed_password(password)
            now = datetime.now()
            cursor.execute(f'INSERT INTO users(username, password, created_at, email) VALUES ("{username}", "{passw}", "{now}", "{email}")')
            mysql.connection.commit()
            msg = 'Te has registrado con exito!'
            category = 'success'
    return render_template('register.html', msg=msg, category=category)


@app.route('/movie/', methods=['GET', 'POST'])
def login():
    msg = ''
    session.clear()
    try:
        if request.method == 'POST':
            username = request.form['name']
            password = cfg.get_hashed_password(request.form['pass'])
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(f'SELECT * FROM users WHERE username = "{username}" AND password = "{password}"')
            account = cursor.fetchone()
            if account:
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                return redirect(url_for('home'))
            else:
                msg = 'Nombre de usuario/contraseña incorrectas!'
                category = 'danger'
        return render_template('login.html', msg=msg, category=category)
    except Exception as e:
        return render_template('login.html', msg='')

@app.route('/movie/profile')
def profile():
    try:
        if 'loggedin' in session:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(f'SELECT * FROM users WHERE id = {session["id"]}')
            account = cursor.fetchone()
            return render_template('profile.html', account=account)
        return redirect(url_for('home'))
    except Exception as e:
        return render_template('home.html')




if __name__ == '__main__':
    app.run(debug=True)
