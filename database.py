import sqlite3

f = "data/database.db"
db = sqlite3.connect(f)
c = db.cursor()
c.execute('CREATE TABLE IF NOT EXISTS accounts (username TEXT PRIMARY KEY, password TEXT);')
c.execute('CREATE TABLE IF NOT EXISTS scores (game TEXT, username TEXT, score INTEGER);')
c.execute('CREATE TABLE IF NOT EXISTS teams (teamname TEXT, members TEXT);')
#db.close()

c.execute('INSERT INTO scores VALUES("simon", "shanny_boy", 22);')

db.close()

#adds a users new score
def add_score(game, user, score):
    #f = "data/database.db"
    #db = sqlite3.connect(f)
    #c = db.cursor()
    c.execute('INSERT INTO scores VALUES("%s", "%s", %d);'%(game, user, score))
    db.close()
    
#creates a new team
def create_team(name, creator):
    f = "data/database.db"
    db = sqlite3.connect(f)
    c = db.cursor()
    members = []
    creator = members.append(creator)
    c.execute('INSERT INTO teams VALUES("%s", "%s");'%(name, creator))
    db.close()

#adds a member to a team 
def add_member(name, member):
    f = "data/database.db"
    db = sqlite3.connect(f)
    c = db.cursor()
    members = c.execute('SELECT members FROM teams WHERE teamname = "%s";'%name)
    members.append(member)
    c.execute('DELETE FROM teams WHERE teamname = "%s";'%name)
    c.execute('INSERT INTO scores VALUES("%s", "%s");'%(name, members))
    db.close()

#removes a member from a team
def remove_member(name, member):
    f = "data/database.db"
    db = sqlite3.connect(f)
    c = db.cursor()
    members = c.execute('SELECT members FROM teams WHERE teamname = "%s";'%name)
    members.remove(member)
    c.execute('DELETE FROM teams WHERE teamname = "%s";'%name)
    c.execute('INSERT INTO scores VALUES("%s", "%s");'%(name, members))
    db.close()

#gets a user's highscore for a given game
def get_user_highscore(game, user):
    f = "data/database.db"
    db = sqlite3.connect(f)
    c = db.cursor()
    c.execute('SELECT MAX(score) FROM scores WHERE game="%s" AND username="%s";'%(game, user))
    result = c.fetchall()
    if result == []:
        db.close()
        return 0
    else:
        db.close()
        return result[0][0]

def get_game_highscore(game):
    f = "data/database.db"
    db = sqlite3.connect(f)
    c = db.cursor()
    c.execute('SELECT MAX(score) FROM  scores WHERE game = "%s";'%game)
    result = c.fetchall()
    if result == []:
        db.close()
        return 0
    else:
        db.close()
        return result[0][0]

#add_score('simon', 'shanny_boy', 22)
              
