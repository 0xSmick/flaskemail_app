#blog.py - controller

#imports
from flask import Flask, render_template, request, session, flash, redirect, url_for, g
from functools import wraps
import sqlite3

#config
DATABASE = '/Users/sheldon.smickley/scripts/apps/email.db'
USERNAME = "admin"
PASSWORD = "admin"
SECRET_KEY = "\xe8\xc3\xf2\x85\x85d\x06\xeb\xa2\xb9x\xeaW\xba\x05\xb5\xc5\xbf\xbei\xac\xe6\xf0Z"


app = Flask(__name__)

#searches app configs
app.config.from_object(__name__)


def connect_db():
  return sqlite3.connect(app.config['DATABASE'])

#routes
def login_required(test):
  @wraps(test)
  def wrap(*args, **kwargs):
    if 'logged_in' in session:
      return test(*args, **kwargs)
    else:
      flash('You need to login first.')
      return redirect(url_for('login'))
  return wrap

@app.route('/', methods=['GET','POST'])
def login():
  error = None
  if request.method == 'POST':
    if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
      error = 'Invalid Credentials. Please try again.'
    else:
      session['logged_in'] = True
      return redirect(url_for('main'))
  return render_template('login.html', error=error)

@app.route('/add', methods=['POST'])
@login_required
def add():
    company_name = request.form['company_name']
    email = request.form['email']
    url = request.form['url']
    if not company_name or not email or not url:
      flash("All fields are required. Please try again.")
      return redirect(url_for('main'))
    else:
      conn = sqlite3.connect(app.config['DATABASE'])
      c = conn.cursor()
      c.execute('INSERT into emails (company_name, email, url) values (?, ?, ?)',
        [request.form['company_name'], request.form['email'], request.form['url']])
      new_id = c.lastrowid
      conn.commit()
      conn.close()
      flash('New entry was posted')
      return redirect(url_for('main'))

@app.route('/main')
@login_required
def main():
  g.db = connect_db()
  cur = g.db.execute('select * from emails')
  entries = [dict(company_name=row[1], email=row[2], url=row[3]) for row in cur.fetchall()]
  g.db.close()
  return render_template('main.html', entries=entries)

@app.route('/logout')
def logout():
  session.pop('logged_in', None)
  flash('You were logged out')
  return redirect(url_for('login'))



if __name__=="__main__":
	app.run(debug=True)