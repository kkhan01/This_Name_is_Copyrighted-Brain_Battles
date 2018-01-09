from __future__ import print_function
from flask import Flask, render_template, request, session, redirect, url_for, flash
import sys
import os
import database
import sqlite3   #enable control of an sqlite database
f="data/database.db"

db = sqlite3.connect(f, check_same_thread=False) #open if f exists, otherwise create
c = db.cursor()    #facilitate db ops

#==========================================================
#sql code

#checks if username is in db
def user_exist(username):
    command = 'SELECT * FROM accounts'
    possibility = c.execute(command)
    for i in possibility:
        if(i[0] == username):
            return True
    return False

#gets a username's pass
def get_pass(username):
    command = 'SELECT * FROM accounts'
    possibility = c.execute(command)
    for i in possibility:
        if(i[0] == username):
            return i[1]
    return False

#adds a new user
def create_user(username, password):
    if(user_exist(username)):
        return False
    command = 'INSERT INTO accounts(username, password) VALUES("%s", "%s")'%(username, password)
    c.execute(command)
    db.commit() #save changes
    return True

#get list of users with matching string within
def search_user(username):
    command = 'SELECT * FROM accounts'
    possibility = c.execute(command)
    array = []
    for i in possibility:
        if(username in i[0]):
            array.append(i[0])
        else:
            pass        
    return array

#==========================================================
#flask code
app = Flask(__name__)

app.secret_key = 'keysmithsmakekeys'

#PRINTS STUFF!!!!
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    return

@app.route('/')                                                                 
def root():
    if 'user' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'user' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

#will say what's wrong
def authenticate(user, passw):
    #check if username & pass are in the database
    if user_exist(user):
        if get_pass(user) == passw:
            return 'good'
        else:
            return 'password'
    else:
        return 'username and password'
        
@app.route('/create', methods=['POST', 'GET'])
def create():
    return render_template('create.html')

@app.route('/creation', methods=['POST', 'GET'])
def creation():
    if 'uname' in request.form:
            user = request.form['uname']
            passw = request.form['upass']
            passw2 = request.form['upass2']
            eprint("u: %s\np: %s\np2: %s" % (user,passw,passw2))
            if(passw != passw2):
                flash ('Sorry, but your passwords were different. Please try again')
                #THIS REDIRECTION ISNT WORKING IDK WHY
                redirect (url_for('create'))
            else:
                #check if unique name 
                if user_exist(user):
                    flash ('Sorry, but this user exists, please choose a different username')
                    redirect (url_for('create'))
                else:
                    #add to database
                    create_user(user, passw)
                    flash ('New user successfully created!')
                    redirect (url_for('login'))
    return redirect (url_for('login'))

@app.route('/logout', methods=['POST', 'GET'])
def logout():
   session.pop('user')
   return redirect(url_for('login'))

#temp welcoming page
@app.route('/home', methods=['POST', 'GET'])
def home():
    if 'user' not in session:
		#fixed if statement here
        if 'uname' in request.form:
            user = request.form['uname']
            passw = request.form['upass']
        
            result = authenticate(user, passw)
        
            if result == 'good':
                session['user'] = user
            else:
                flash ('Sorry, but your '+ result + ' is wrong. Please try again')
        return redirect(url_for('login'))

    else:
        return render_template('dummy.html', name = session['user'])

@app.route('/search', methods=['POST', 'GET'])
def search():
    s = request.form['searchtext']
    return render_template('search.html', s_text = s, results = search_user(s))

@app.route('/simon')
def simon():
    return render_template('simon.html')

@app.route('/react')
def react():
    return render_template('react.html')

@app.route('/wordsearch')
def wordsearch():
    return render_template('wordsearch.html')

@app.route('/rename')
def rename():
    image = request.form['image']
    path = "/static/img/temp/"
    newpath = "/static/img/profile/"
    base, ext = os.path.splitext(image)
    if(ext != ".png" or ext != ".jpg" or ext != ".jpeg" or ext != ".gif"):
        #delete file and flash invalid
        flash ('Invalid file! Please upload a valid image.')
        os.remove((os.path.join(path, image)))
    else:
        #rename and flash changed?
        eprint (base + "   "+ ext)
        #os.rename(os.path.join(newpath, image), os.path.join(path, session['user']+ext))
    return redirect(url_for(profile))

@app.route('/profile', methods=['POST', 'GET'])
def profile():
    username = 'hello'
    isuser = False
    if request.method == 'POST':
        username = request.form['user']
        isuser = True
    else:
        username = session['user']
    simon = database.get_user_highscore('simon', username)
    search = database.get_user_highscore('search', username)
    react = database.get_user_highscore('react', username)
    teams = find_teams(username)
    return render_template('profile.html', user = username, iu = isuser, simon = simon, search = search, react = react, teams = teams)


if __name__ == '__main__':
    app.debug = True
    app.run()

#==========================================================
db.commit() #save changes
db.close() #close database
