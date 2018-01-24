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
c.execute('CREATE TABLE IF NOT EXISTS teams (teamname TEXT, creator TEXT,  members TEXT);')

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

def user_exists(name):
    c.execute('SELECT username FROM accounts WHERE username = "%s";'%name)
    user = c.fetchall()
    if user != name:
        return False
    else:
        return True

def get_users():
    c.execute('SELECT username FROM accounts;')
    members = c.fetchall()
    users = []
    for member in members:
        if member[0] != session['user']:
            users.append(member[0])
    return users

#creates a new team
def create_team(name, creator):
    c.execute('INSERT INTO teams VALUES("%s", "%s", "%s");'%(name, creator, creator))
    db.commit()

def delete_team(name):
    c.execute('DELETE FROM teams WHERE teamname = "%s";'%name)
    db.commit()

def team_exist(name):
    c.execute('SELECT teamname FROM teams WHERE teamname = "%s";'%name)
    team = c.fetchall()
    eprint(team)
    eprint('\n\n\n\n')
    if len(team) < 1:
        return False
    else:
        return True
    
#adds a member to a team 
def add_member(name, member):
    c.execute('SELECT members FROM teams WHERE teamname = "%s";'%name)
    members = c.fetchall()[0][0]
    eprint(members)
    eprint('\n\n\n\n')
    members = members + "," + member
    c.execute('SELECT creator FROM teams WHERE teamname = "%s";'%name)
    creator = c.fetchall()[0][0]
    c.execute('DELETE FROM teams WHERE teamname = "%s";'%name)
    c.execute('INSERT INTO teams VALUES("%s", "%s", "%s");'%(name, creator, members))
    db.commit()

#checks for member presence in team 
def is_member(name, member):
    c.execute('SELECT members FROM teams WHERE teamname = "%s";'%name)
    members = c.fetchall()[0][0]
    eprint(members)
    eprint(member)
    eprint('\n\n\n\n')
    return member in members


#removes a member from a team
def remove_member(name, member):
    c.execute('SELECT members FROM teams WHERE teamname = "%s";'%name)
    members = c.fetchall()[0][0]
    member = "," + member
    members = members.replace(member, "", 1)
    c.execute('SELECT creator FROM teams WHERE teamname = "%s";'%name)
    creator = c.fetchall()[0][0]
    c.execute('DELETE FROM teams WHERE teamname = "%s";'%name)
    c.execute('INSERT INTO teams VALUES("%s", "%s", "%s");'%(name, creator, members))
    db.commit()

#retuns all members of a team
def get_members(name):
    c.execute('SELECT members FROM teams WHERE teamname = "%s";'%name)
    members = c.fetchall()[0][0]
    return members.split(',')

def get_creator(name):
    c.execute('SELECT creator FROM teams WHERE teamname = "%s";'%name)
    creator = c.fetchall()[0][0]
    return creator

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
            teams_in.append(team[0])
    return teams_in


#gets a user's highscore for a given game
def get_user_highscore(game, user):
    if game == "simon":
        c.execute('SELECT MAX(score) FROM scores WHERE game="%s" AND username="%s";'%(game, user))
    else:
        c.execute('SELECT MIN(score) FROM scores WHERE game="%s" AND username="%s";'%(game, user))
    result = c.fetchall()
    if result == []:
        return 0
    else:
        return result[0][0]

def getscore(elem):
    eprint(elem[0])
    return elem[0]
#returns highest scores of each game dict
def get_team_stats(name):
    scores = {}
    scores['simon'] = []
    scores['react'] = []
    scores['search'] = []
    games = ['simon', 'react', 'search']
    members = get_members(name)
    #eprint(members)
    for game in games:
        for member in members:
            high_score = get_user_highscore(game, member)
            if high_score is not None:
                scores[game].append([high_score, member])
        eprint(scores[game])
        if game == 'simon':
            scores[game] = sorted(scores[game], key=getscore ,reverse=True)
        else:
            scores[game] = sorted(scores[game], key=getscore,reverse=False)
    return scores


def get_leaderboards():
    scores = {}
    scores['simon'] = []
    scores['react'] = []
    scores['search'] = []
    games = ['simon', 'react', 'search']
    for game in games:
        if game == 'react' or game == 'search':
            c.execute('SELECT MIN(score),username FROM scores WHERE game="%s";'%game)
            scores[game].append(c.fetchall()[0])
        else:
            c.execute('SELECT MAX(score),username FROM scores WHERE game="%s";'%game)
            scores[game].append(c.fetchall()[0])
        if scores[game][0][0] is None:
            del scores[game][0]
            break
        highscore = scores[game][0][0]
        count = 0
        while count < 4:
            if game == 'react' or game == 'search':
                c.execute('SELECT MIN(score),username FROM scores WHERE game="%s" AND score > %d;'%(game, highscore))
                scores[game].append(c.fetchall()[0])
                if scores[game][count+1][0] is None:
                    del scores[game][count+1]
                    break
                highscore = scores[game][count+1][0]
            else:
                c.execute('SELECT MAX(score),username FROM scores WHERE game="%s" AND score <  %d;'%(game, highscore))
                scores[game].append(c.fetchall()[0])
                if scores[game][count+1][0] is None:
                    del scores[game][count+1]
                    break
                highscore = scores[game][count+1][0]
            count = count + 1
    return scores

#top scores of each game of all time
def top_scores():
    #simon
    simonscore = 0
    simonuser = "N/A"
    simonscore1 = 0
    simonuser1 = "N/A"
    simonscore2 = 0
    simonuser2 = "N/A"
    result = c.execute('SELECT DISTINCT * FROM scores WHERE game = "simon" ORDER BY score DESC;')
    counter = 0
    for i in result:
        if(counter == 0):
            simonuser = i[1]
            simonscore = i[2]
        if(counter == 1):
            simonuser1 = i[1]
            simonscore1 = i[2]
        if(counter == 2):
            simonuser2 = i[1]
            simonscore2 = i[2]
        counter += 1
    #react
    reactscore = 0
    reactuser = "N/A"
    reactscore1 = 0
    reactuser1 = "N/A"
    reactscore2 = 0
    reactuser2 = "N/A"
    result = c.execute('SELECT DISTINCT * FROM scores WHERE game = "react" ORDER BY score ASC;')
    counter = 0
    for i in result:
        if(counter == 0):
            reactuser = i[1]
            reactscore = i[2]
        if(counter == 1):
            reactuser1 = i[1]
            reactscore1 = i[2]
        if(counter == 2):
            reactuser2 = i[1]
            reactscore2 = i[2]
        counter += 1
    #search
    wsscore = 0
    wsuser = "N/A"
    wsscore1 = 0
    wsuser1 = "N/A"
    wsscore2 = 0
    wsuser2 = "N/A"
    result = c.execute('SELECT DISTINCT * FROM scores WHERE game = "search" ORDER BY score ASC;')
    counter = 0
    for i in result:
        if(counter == 0):
            wsuser = i[1]
            wsscore = i[2]
        if(counter == 1):
            wsuser1 = i[1]
            wsscore1 = i[2]
        if(counter == 2):
            wsuser2 = i[1]
            wsscore2 = i[2]
        counter += 1
    
    #all scores
    scores = {}
    #simon
    simon = {}
    simon["0"] = [simonuser, simonscore]
    simon["1"] = [simonuser1, simonscore1]
    simon["2"] = [simonuser2, simonscore2]
    scores["simon"] = simon
    #react
    react = {}
    react["0"] = [reactuser, reactscore]
    react["1"] = [reactuser1, reactscore1]
    react["2"] = [reactuser2, reactscore2]
    scores["react"] = react
    #ws
    search = {}
    search["0"] = [wsuser, wsscore]
    search["1"] = [wsuser1, wsscore1]
    search["2"] = [wsuser2, wsscore2]
    scores["search"] = search
    return scores

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

@app.route('/about')
def about():
    if 'user' not in session:
        return redirect(url_for('home'))
    return render_template('about.html', me=session['user'])
    

@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'user' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

#will say what's wrong
def authenticate(user, passw):
    #check if username & pass are in the database
    eprint(user_exist(user))
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

            eprint(user)
            eprint(passw)
            result = authenticate(user, passw)
            eprint(result + '\n\n\n\n')
        
            if result == 'good':
                session['user'] = user
            else:
                flash ('Sorry, but your '+ result + ' is wrong. Please try again')
        return redirect(url_for('login'))

    else:
        return render_template('dummy.html', name = session['user'], scores = top_scores(), me = session['user'])

@app.route('/search', methods=['POST', 'GET'])
def search():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        s = request.form['searchtext']
        return render_template('search.html', s_text = s, results = search_user(s), me = session['user'])

@app.route('/simon')
def simon():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        username = session['user']
        hs = get_user_highscore('simon', username)
        return render_template('simon.html', hs = hs,me = session['user'])

@app.route('/react')
def react():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        username = session['user']
        hs = get_user_highscore('react', username)
        return render_template('react.html', hs = hs, me = session['user'])

@app.route('/wordsearch')
def wordsearch():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        username = session['user']
        hs = get_user_highscore('search', username)
        return render_template('wordsearch.html', hs = hs, me = session['user'])

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
    return redirect(url_for('profile', user=session['user']))

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
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        #which user is it?
        username = 'hello'
        isuser = False
        if request.method == 'POST':
            username = request.form['user']
        else:
            username = request.args['user']
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
        return render_template('profile.html', pic = pic, user = username, iu = isuser, simon = simon, search = search, react = react, teams = teams, me = session['user'])
    
@app.route('/team', methods = ["POST", "GET"])
def team():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            teamname = request.form['team']
        else:
            teamname = request.args['team']
        members = get_members(teamname) #list of members
        creator = get_creator(teamname) #creator of team
        stats = get_team_stats(teamname) #highscore dict game: [score, user] sorted
        return render_template('team.html', name = teamname, members = members, stats = stats, creator = creator, me = session['user'])

@app.route('/createteam', methods = ["POST", "GET"])
def createteam():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        users = get_users()
        return render_template('new_team.html', users = users, me=session['user'])

@app.route('/team_backend', methods = ["POST", "GET"])
def team_backend():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            teamname = request.form['team']
        else:
            teamname = request.args['team']
            eprint(teamname)
        #eprint(team_exist(teamname))
        if team_exist(teamname):
            flash ('Sorry, that team name already exists.')
            return redirect(url_for('createteam'))
        else:
            create_team(teamname, session['user'])


        flash('Team successfully created!')
        return redirect(url_for('profile', user=session['user']))

@app.route('/new_member', methods = ["POST"])
def new_member():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        user = request.form['member']
        team = request.form['team']
        eprint(user);
        eprint(team);
        eprint('\n\n\n\n\n');
        if user_exist(user) and not is_member(team,user):
            add_member(team, user)
            return 'Done!'
        else:
            #flash ('That username does not exist')
            return 'DNE'

@app.route('/delete_member', methods = ["POST"])
def delete_member():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        user = request.form['member']
        team = request.form['team']
        remove_member(team, user)
        return "Done!"

@app.route('/leave_team', methods = ["POST"])
def leave_team():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        user = request.form['member']
        team = request.form['team']
        remove_member(team, user)
        flash ('You have successfully left the team')
        return redirect(url_for('home'))

@app.route('/disband_team', methods = ["POST"])
def disband_team():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        team = request.form['team']
        delete_team(team)
        flash ('You have successfully disbanded your team')
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.debug = True
    app.run()

#==========================================================
db.commit() #save changes
db.close() #close database
