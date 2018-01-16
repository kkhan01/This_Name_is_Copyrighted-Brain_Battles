from __future__ import print_function
from flask import Flask, render_template, request, session, redirect, url_for, flash
import sys
import os
#import database
import sqlite3   #enable control of an sqlite database
from werkzeug import secure_filename #uploading files

reload(sys)
sys.setdefaultencoding('utf-8')

f="data/database.db"

db = sqlite3.connect(f, check_same_thread=False) #open if f exists, otherwise create
c = db.cursor()    #facilitate db ops

app = Flask(__name__)

app.secret_key = 'keysmithsmakekeys'

#PRINTS STUFF!!!!
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    return

#==========================================================
#uploading prereqs
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

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


c.execute('CREATE TABLE IF NOT EXISTS accounts (username TEXT PRIMARY KEY, password TEXT);')
c.execute('CREATE TABLE IF NOT EXISTS scores (game TEXT, username TEXT, score INTEGER);')
c.execute('CREATE TABLE IF NOT EXISTS teams (teamname TEXT, members TEXT);')

#adds a users new score
@app.route('/addscore', methods=['POST'])
def add_score():
    game = request.form['game']
    score = int(request.form['score'])
    user = session['user']
    #eprint(game+"$$$"+score+"$$$"+user)
    c.execute('INSERT INTO scores VALUES("%s", "%s", %d);'%(game, user, score))
    db.commit()
    return True

#creates a new team
def create_team(name, creator):
    c.execute('INSERT INTO teams VALUES("%s", "%s");'%(name, creator))
    db.commit()

def delete_team(name):
    c.execute('DELETE FROM teams WHERE teamname = "%s";'%name)
    db.commit()

#adds a member to a team 
def add_member(name, member):
    c.execute('SELECT members FROM teams WHERE teamname = "%s";'%name)
    members = c.fetchall()[0][0]
    members = members + "," + member
    c.execute('DELETE FROM teams WHERE teamname = "%s";'%name)
    c.execute('INSERT INTO teams VALUES("%s", "%s");'%(name, members))
    db.commit()

#removes a member from a team
def remove_member(name, member):
    c.execute('SELECT members FROM teams WHERE teamname = "%s";'%name)
    members = c.fetchall()[0][0]
    member = "," + member
    members = members.replace(member, "", 1)
    c.execute('DELETE FROM teams WHERE teamname = "%s";'%name)
    c.execute('INSERT INTO teams VALUES("%s", "%s");'%(name, members))
    db.commit()

#retuns all members of a team
def get_members(name):
    c.execute('SELECT members FROM teams WHERE teamname = "%s";'%name)
    members = c.fetchall()[0][0]
    return members

#returns hightest scores of each game dict
#def get_team_stats(name):
#    scores = {}
#    simon = c.execute('SELECT MAX(score) FROM scores WHERE game = "simon" AND username IN teams.

#finds all the teams a given user is a part of
def find_teams(user):
    c.execute('SELECT teamname FROM teams;')
    teams = c.fetchall()
    #print teams
    teams_in = []
    for team in teams:
        c.execute('SELECT members FROM teams WHERE teamname = "%s";'%team)
        members = c.fetchall()[0][0]
        if members.find(user) != -1:
            teams_in.append(team)
    return teams_in


#gets a user's highscore for a given game
def get_user_highscore(game, user):
    if game != "react":
        c.execute('SELECT MAX(score) FROM scores WHERE game="%s" AND username="%s";'%(game, user))
    else:
        c.execute('SELECT MIN(score) FROM scores WHERE game="%s" AND username="%s";'%(game, user))
    result = c.fetchall()
    if result == []:
        return 0
    else:
        return result[0][0]

#gets the all time highscore for a given game
def get_game_highscore(game):
    c.execute('SELECT MAX(score) FROM  scores WHERE game = "%s";'%game)
    result = c.fetchall()
    if result == []:
        return 0
    else:
        return result[0][0]


#==========================================================
#flask code

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

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

#check if valid ext
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#saves to the root, unsure how to fix that, but renaming will do it!
@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        eprint(1)
        fil = request.files['image']
        if allowed_file(fil.filename):
            eprint(2)
            filn = secure_filename(fil.filename)
            fil.save(filn)
            eprint(3)
            rename(filn)
            eprint(4)
            flash ('Successfully changed profile pictures!')
        else:
            flash ('Invalid file! Please upload a valid image.')
    eprint(5)
    return redirect(url_for('profile'))

def rename(image):
    eprint(11)
    path = "static/img/profile"
    files = os.listdir(path)
    for filen in files:
        base, ext = os.path.splitext(filen)
        if(base == session['user']):
            old = os.path.join("./static/img/profile", filen)
            os.remove(old)
            eprint("REMOVED!")
    eprint(12)
    base, ext = os.path.splitext(str(image))
    eprint(13)
    #eprint (base + "   "+ ext)
    source = os.path.join("./", str(image))
    #eprint(os.path.isfile(image)) 
    eprint(source)
    newfile = session['user'] + ext
    eprint(newfile)
    dest = os.path.join("./static/img/profile", newfile)
    eprint(dest)
    os.rename(source, dest)
    return

@app.route('/profile', methods=['POST', 'GET'])
def profile():
    #which user is it?
    username = 'hello'
    isuser = False
    if request.method == 'POST':
        username = request.form['user']
    else:
        username = session['user']
    #if it's THE user, they get extra settings
    if username == session['user']:
        isuser = True
    pic = 'static/img/generic.png'
    path = "static/img/profile"
    files = os.listdir(path)
    for filen in files:
        base, ext = os.path.splitext(filen)
        if(base == username):
            pic = path + "/" + filen
    eprint(pic)
    simon = get_user_highscore('simon', username)
    search = get_user_highscore('search', username)
    react = get_user_highscore('react', username)
    teams = find_teams(username)
    eprint(isuser)
    return render_template('profile.html', pic = pic, user = username, iu = isuser, simon = simon, search = search, react = react, teams = teams)

@app.route('/team', methods = ["POST", "GET"])
def team():
    if request.method == 'POST':
        teamname = request.form['team']
    else:
        teamname = request.args['team']
    members = get_members(teamname) #list of members
    #dict of highscores key is game, value is list of member and score
    stats = get_team_stats(teamname) 
    return render_template('team.html', name = teamname, members = members, stats = stats)


if __name__ == '__main__':
    app.debug = True
    app.run()

#==========================================================
db.commit() #save changes
db.close() #close database
