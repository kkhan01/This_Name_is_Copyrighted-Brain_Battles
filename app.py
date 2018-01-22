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
    return members.split(',')


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
    if game == "simon":
        c.execute('SELECT MAX(score) FROM scores WHERE game="%s" AND username="%s";'%(game, user))
    else:
        c.execute('SELECT MIN(score) FROM scores WHERE game="%s" AND username="%s";'%(game, user))
    result = c.fetchall()
    if result == []:
        return 0
    else:
        return result[0][0]

#returns highest scores of each game dict
def get_team_stats(name):
    scores = {}
    scores['simon'] = []
    scores['react'] = []
    scores['search'] = []
    games = ['simon', 'react', 'search']
    members = get_members(name)
    eprint(members)
    for game in games:
        for member in members:
            high_score = get_user_highscore(game, member)
            scores[game].append([high_score, member])
        sorted(scores[game])
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
    c.execute('SELECT MAX(score) FROM scores WHERE game="%s";'%("simon"))
    result = c.fetchall()
    if result == [] or result[0][0] == None:
         simonscore = 0
    else:
        simonscore = result[0][0]
    c.execute('SELECT username FROM scores WHERE game="%s" AND score="%s";'%("simon", simonscore))
    result = c.fetchall()
    if result == [] or result[0][0] == None:
         simonuser = "N/A"
    else:
        simonuser = result[0][0]
    #eprint("%s$$$$$$$$%d"%(simonuser, simonscore))
    #simon second best
    simonscore1 = 0
    simonuser1 = "N/A"
    if simonscore != 0:
        c.execute('SELECT MAX(score) FROM scores WHERE game="%s" AND score<%d;'%("simon", simonscore))
        result = c.fetchall()
        if result == [] or result[0][0] == None:
            simonscore1 = 0
        else:
            simonscore1 = result[0][0]
    c.execute('SELECT username FROM scores WHERE game="%s" AND score="%s";'%("simon", simonscore1))
    result = c.fetchall()
    if result == [] or result[0][0] == None:
         simonuser1 = "N/A"
    else:
        simonuser1 = result[0][0]
    #eprint("%s$$$$$$$$%d"%(simonuser1, simonscore1))
    #simon third best
    simonscore2 = 0
    simonuser2 = "N/A"
    if simonscore1 != 0:
        c.execute('SELECT MAX(score) FROM scores WHERE game="%s" AND score<%d;'%("simon", simonscore1))
        result = c.fetchall()
        if result == [] or result[0][0] == None:
            simonscore2 = 0
        else:
            simonscore2 = result[0][0]
    c.execute('SELECT username FROM scores WHERE game="%s" AND score="%s";'%("simon", simonscore2))
    result = c.fetchall()
    if result == [] or result[0][0] == None:
         simonuser2 = "N/A"
    else:
        simonuser2 = result[0][0]
    #eprint("%s$$$$$$$$%d"%(simonuser2, simonscore2))

    
    #react
    reactscore = 0
    reactuser = "N/A"
    c.execute('SELECT MIN(score) FROM scores WHERE game="%s";'%("react"))
    result = c.fetchall()
    if result == [] or result[0][0] == None:
         reactscore = 0
    else:
        reactscore = result[0][0]
    c.execute('SELECT username FROM scores WHERE game="%s" AND score="%s";'%("react", reactscore))
    result = c.fetchall()
    if result == [] or result[0][0] == None:
         reactuser = "N/A"
    else:
        reactuser = result[0][0]
    #eprint("%s$$$$$$$$%d"%(reactuser, reactscore))
    #react second best
    reactscore1 = 0
    reactuser1 = "N/A"
    if reactscore != 0:
        c.execute('SELECT MIN(score) FROM scores WHERE game="%s" AND score>%d;'%("react", reactscore))
        result = c.fetchall()
        if result == [] or result[0][0] == None:
            reactscore1 = 0
        else:
            reactscore1 = result[0][0]
    c.execute('SELECT username FROM scores WHERE game="%s" AND score="%s";'%("react", reactscore1))
    result = c.fetchall()
    if result == [] or result[0][0] == None:
         reactuser1 = "N/A"
    else:
        reactuser1 = result[0][0]
    #eprint("%s$$$$$$$$%d"%(reactuser1, reactscore1))
    #react third best
    reactscore2 = 0
    reactuser2 = "N/A"
    if reactscore1 != 0:
        c.execute('SELECT MIN(score) FROM scores WHERE game="%s AND score>%d";'%("react", reactscore1))
        result = c.fetchall()
        if result == [] or result[0][0] == None:
         reactscore2 = 0
        else:
            reactscore2 = result[0][0]
    c.execute('SELECT username FROM scores WHERE game="%s" AND score="%s";'%("react", reactscore2))
    result = c.fetchall()
    if result == [] or result[0][0] == None:
         reactuser2 = "N/A"
    else:
        reactuser2 = result[0][0]
    #eprint("%s$$$$$$$$%d"%(reactuser2, reactscore2))


    #wordsearch
    wsscore = 0
    wsuser = "N/A"
    c.execute('SELECT MIN(score) FROM scores WHERE game="%s";'%("search"))
    result = c.fetchall()
    if result == [] or result[0][0] == None:
         wsscore = 0
    else:
        wsscore = result[0][0]
    c.execute('SELECT username FROM scores WHERE game="%s" AND score="%s";'%("search", wsscore))
    result = c.fetchall()
    if result == [] or result[0][0] == None:
         wsuser = "N/A"
    else:
        wsuser = result[0][0]
    #eprint("%s$$$$$$$$%d"%(wsuser, wsscore))
    #wordsearch second best
    wsscore1 = 0
    wsuser1 = "N/A"
    if wsscore != 0:
        c.execute('SELECT MIN(score) FROM scores WHERE game="%s AND score>%d";'%("search", wsscore))
        result = c.fetchall()
        if result == [] or result[0][0] == None:
            wsscore1 = 0
        else:
            wsscore1 = result[0][0]
    c.execute('SELECT username FROM scores WHERE game="%s" AND score="%s";'%("search", wsscore1))
    result = c.fetchall()
    if result == [] or result[0][0] == None:
         wsuser1 = "N/A"
    else:
        wsuser1 = result[0][0]
    #eprint("%s$$$$$$$$%d"%(wsuser1, wsscore1))
    #wordsearch third best
    wsscore2 = 0
    wsuser2 = "N/A"
    if wsscore1 != 0:
        c.execute('SELECT MIN(score) FROM scores WHERE game="%s" AND score>%d;'%("search", wsscore1))
        result = c.fetchall()
        if result == [] or result[0][0] == None:
            wsscore2 = 0
        else:
            wsscore2 = result[0][0]
    c.execute('SELECT username FROM scores WHERE game="%s" AND score="%s";'%("search", wsscore2))
    result = c.fetchall()
    if result == [] or result[0][0] == None:
         wsuser2 = "N/A"
    else:
        wsuser2 = result[0][0]
    #eprint("%s$$$$$$$$%d"%(wsuser2, wsscore2))

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
        return render_template('dummy.html', name = session['user'], scores = top_scores())

@app.route('/search', methods=['POST', 'GET'])
def search():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        s = request.form['searchtext']
        return render_template('search.html', s_text = s, results = search_user(s))

@app.route('/simon')
def simon():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        username = session['user']
        hs = get_user_highscore('simon', username)
        return render_template('simon.html', hs = hs)

@app.route('/react')
def react():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        username = session['user']
        hs = get_user_highscore('react', username)
        return render_template('react.html', hs = hs)

@app.route('/wordsearch')
def wordsearch():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        username = session['user']
        hs = get_user_highscore('search', username)
        return render_template('wordsearch.html', hs = hs)

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
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
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
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            teamname = request.form['team']
        else:
            teamname = request.args['team']
        members = get_members(teamname) #list of members
        stats = get_team_stats(teamname) #highscore dict game: [score, user] sorted
        return render_template('team.html', name = teamname, members = members, stats = stats)


if __name__ == '__main__':
    app.debug = True
    app.run()

#==========================================================
db.commit() #save changes
db.close() #close database
