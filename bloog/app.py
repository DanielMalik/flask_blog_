from flask import Flask, request, g, redirect, url_for, abort, flash, render_template, make_response, session, escape
import os
import sqlite3



app = Flask(__name__)
app.config.from_object(__name__)

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

@app.route("/")
@app.route("/")
def main():
    if 'username' in session:
        username = escape(session['username'])
        return render_template('main.html', user=username)

@app.route('/read')
def show_entries():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None
    user = None
    if request.method == 'GET':

        return render_template('login.html')
    elif request.method == 'POST':
        if request.form['username'] != 'admin':
            error = 'Wrong user'
        elif request.form['password'] != 'admin':
            error = 'Wrong password'
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

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.run()