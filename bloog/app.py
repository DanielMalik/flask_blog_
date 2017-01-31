from flask import Flask, request, g, redirect, url_for, abort, flash, render_template, make_response, session, escape
import os
import sqlite3
from wtforms import Form, BooleanField, StringField, PasswordField, validators

secret_value = '3i1415'

app = Flask(__name__)
app.config.from_object(__name__)

# in future I will move forms to separate module

class RegistrationForm(Form):
    username = StringField('Name', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=35)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    secret = StringField('Secret', [validators.Length(max=25), validators.Optional()])
    accept_tos = BooleanField('I accept everything', [validators.DataRequired()])

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'nolablog.db'),
    SECRET_KEY='development key',
    USERNAME='daniel',
    PASSWORD='coderslab'
))
app.config.from_envvar('APP_SETTINGS', silent=True)


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():

    init_db()
    print('Initialized the database.')

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def allusers():
    db = get_db()
    all_users = []
    cursor = db.execute('select * from users')
    all_users = cursor.fetchall()
    for row in cursor:
        all_users.append(row[1])
    return all_users

def isuser(user):
    isuser = (user,)
    db = get_db()
    all_users = []
    cursor = db.execute('select * from users where name=?', isuser)
    all_users = cursor.fetchall()
    return all_users


@app.route("/")
def main():
    if 'username' in session:
        username = escape(session['username'])
        return render_template('main.html', user=username)

@app.route('/read')
def show_entries():
    if session.get('logged_in'):
        db = get_db()
        cur = db.execute('select title, text, link from entries order by id desc')
        entries = cur.fetchall()
        user = escape(session['username'])
        return render_template('entries.html', entries=entries, user=user)
    else:
        return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text, link) values (?, ?, ?)',
                 [request.form['title'], request.form['text'], request.form['link']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None
    user = None
    all_users = allusers()

    if request.method == 'GET':

        return render_template('login.html')
    elif request.method == 'POST':
        user = request.form['username']
        print(isuser(user))
        print(isuser(user) == [])
        if isuser(user) == []:
            error = 'Wrong user'
            return render_template('login.html')
        else:
            session['username'] = request.form['username']
            session['logged_in'] = True
            flash('You were logged in')
            user = escape(session['username'])

        return render_template('main.html', user=user, error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    form = RegistrationForm(request.form)

    if request.method =='POST' and form.validate():
        user = request.form['username']
        mail = request.form['email']
        password = request.form['password']
        secret = request.form['secret']
        db = get_db()
        cur = db.execute('select name from users')
        all_users = cur.fetchall()
        if user not in all_users:
            if secret == secret_value:
                admin = 1

                db = get_db()
                db.execute('insert into users (name, mail, password, admin) values (?, ?, ?, ?)',
                           [user, mail, password, admin])
                db.commit()
                return redirect(url_for('login'))
            else:
                no_admin = 0

                db = get_db()
                db.execute('insert into users (name, mail, password, admin) values (?, ?, ?, ?)',
                           [user, mail, password, no_admin])
                db.commit()
                return redirect(url_for('login'))
        else:
            error = "wrong user"
            return render_template('register.html', form=form, errors=error)
    else:
        return render_template('register.html', form=form, errors=error)


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.run()