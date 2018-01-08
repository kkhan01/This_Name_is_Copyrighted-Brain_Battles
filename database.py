import sqlite3

f = "data/database.db"
db = sqlite3.connect(f)
c = db.cursor()
c.execute('CREATE TABLE IF NOT EXISTS accounts (username TEXT PRIMARY KEY, password TEXT);')
c.execute('CREATE TABLE IF NOT EXISTS scores (game TEXT, username TEXT, score INTEGER);')
c.execute('CREATE TABLE IF NOT EXISTS teams (teamname TEXT, members TEXT);')



#adds a users new score
def add_score(game, user, score):
    c.execute('INSERT INTO scores VALUES("%s", "%s", %d);'%(game, user, score))
    db.commit()
    
#creates a new team
def create_team(name, creator):
    c.execute('INSERT INTO teams VALUES("%s", "%s");'%(name, creator))
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

#finds all the teams a given user is a part of
def find_teams(user):
    c.execute('SELECT teamname FROM teams;')
    teams = c.fetchall()[0][0]
    teams_in = []
    for team in teams:
        c.execute('SELECT members FROM teams WHERE teamname = "%s";'%team)
        members = c.fetchall()[0][0]
        if members.find(user) != -1:
            teams_in.append(team)
    return teams_in


#gets a user's highscore for a given game
def get_user_highscore(game, user):
    c.execute('SELECT MAX(score) FROM scores WHERE game="%s" AND username="%s";'%(game, user))
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

print get_game_highscore('simon')
              
