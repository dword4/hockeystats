#!/usr/bin/env python

from sopel import module, tools
import requests
import json
import arrow

@module.commands('teamstats')
def teamStats(bot, trigger):
    """ Gets team stats including games played, wins, losses ot. usage: !teamstats WSH """
    tmpTeam = trigger.group(2)
    teamName = tmpTeam.split()
    try:
        if tmpTeam is not None:
            teamId = getTeamId(teamName[0])
            msg = getTeamStats(teamId)
        else:
            msg = "please search using 3 letter team abbreviation"
    except:
        bot.say("unable to find team id")
    bot.say(msg)

@module.commands('lastgame')
def pGame(bot, trigger):
    """ Gets last game information for a team. usage: !lastgame TOR """
    tmpTeam = trigger.group(2)
    teamName = tmpTeam.split()
    try:
        if tmpTeam is not None:
            teamId = getTeamId(teamName[0])
            msg = prevGame(teamId)
        else:
            msg = "please search using 3 letter team abbreviation"
    except:
        bot.say("unable to find team id")
    bot.say(msg)

@module.commands('nextgame')
def nGame(bot, trigger):
    """ Gets next game information for a team. usage: !nextgame MTL """
    tmpTeam = trigger.group(2)
    teamName = tmpTeam.split()
    try:
        if tmpTeam is not None:
            teamId = getTeamId(teamName[0])
            msg = nextGame(teamId)
        else:
            msg = "please search using 3 letter team abbreviation"
    except:
        bot.say("unable to find team id")
    bot.say(msg)

@module.commands('division')
def divisionStandings(bot, trigger):
    """ Grab standings for a division: Options: Metro(politan), Atlantic, Central, Pacific. usage: !division <full division name> """
    tmpDiv = trigger.group(2)
    divName = tmpDiv.split()
    getStandings()
    try:
        if tmpDiv is not None:
            divId = getDivisionId(divName[0])
            getStandings()
            msg = getDivisionStandings(divId)
        else:
            msg = "Options: Metro(politan), Atlantic, Central, Pacific"
    except:
        msg = "Options: Metro(politan), Atlantic, Central, Pacific"
    bot.say(msg)

# team stats (gp, win, loss, ot)
def getTeamStats(teamid):
    req = "https://statsapi.web.nhl.com/api/v1/teams/"+str(teamid)+"/stats"
    r = requests.get(req)
    
    team_stats_json = r.text
    team_stats = json.loads(team_stats_json)
    
    teamName = team_stats['stats'][0]['splits'][0]['team']['name']
    gamesPlayed = team_stats['stats'][0]['splits'][0]['stat']['gamesPlayed']
    wins = team_stats['stats'][0]['splits'][0]['stat']['wins']
    losses = team_stats['stats'][0]['splits'][0]['stat']['losses']
    ot = team_stats['stats'][0]['splits'][0]['stat']['ot']
    pts = team_stats['stats'][0]['splits'][0]['stat']['pts']

    teamStats = "%s GP %s (%s-%s-%s) %s PTS" % (teamName, gamesPlayed, wins, losses, ot, pts)
    return teamStats

# prev game details
def prevGame(teamid):
    req = "https://statsapi.web.nhl.com/api/v1/teams/"+str(teamid)+"?expand=team.schedule.previous"
    r2 = requests.get(req)

    game_last_json = r2.text
    game_last = json.loads(game_last_json)
    date = game_last['teams'][0]['previousGameSchedule']['dates'][0]['date']
    home_team = game_last['teams'][0]['previousGameSchedule']['dates'][0]['games'][0]['teams']['home']
    away_team = game_last['teams'][0]['previousGameSchedule']['dates'][0]['games'][0]['teams']['away']

    prevGameDetails = date + " | " +away_team['team']['name'] + " @ " +home_team['team']['name'] + " | " + str(away_team['score']) + " - " + str(home_team['score']) + " Final"
    return prevGameDetails

# next game detail
def nextGame(teamid):
    req = "https://statsapi.web.nhl.com/api/v1/teams/"+str(teamid)+"?expand=team.schedule.next"
    r2 = requests.get(req)

    game_last_json = r2.text
    game_last = json.loads(game_last_json)
    date = game_last['teams'][0]['nextGameSchedule']['dates'][0]['date']
    home_team = game_last['teams'][0]['nextGameSchedule']['dates'][0]['games'][0]['teams']['home']
    away_team = game_last['teams'][0]['nextGameSchedule']['dates'][0]['games'][0]['teams']['away']
    game_data = game_last['teams'][0]['nextGameSchedule']['dates'][0]['games'][0]['gameDate']
    a = arrow.get(game_data)
    nextGameDetails = date + " | " +away_team['team']['name'] + " @ " +home_team['team']['name'] + " at " +str(a.to('US/Eastern').time()) + " EST"
    return nextGameDetails

# get the division id
def getDivision(teamid):
    req = "https://statsapi.web.nhl.com/api/v1/teams/15"
    r = requests.get(req)
    team_info_json = r.text
    team_info = json.loads(team_info_json)
    return(team_info['teams'][0]['division']['id'])

# get team ID from abbreviation
def getTeamId(abbreviation):
    teams = {
            "NJD" : 1,
            "NYI" : 2,
            "NYR" : 3,
            "PHI" : 4,
            "PIT" : 5,
            "BOS" : 6, 
            "BUF" : 7,
            "MTL" : 8,
            "OTT" : 9,
            "TOR" : 10,
            "CAR" : 12,
            "FLA" : 13,
            "TBL" : 14,
            "WSH" : 15,
            "CHI" : 16,
            "DET" : 17,
            "NSH" : 18,
            "STL" : 19,
            "CGY" : 20,
            "COL" : 21,
            "EDM" : 22,
            "VAN" : 23,
            "ANA" : 24,
            "DAL" : 25,
            "LAK" : 26,
            "SJS" : 28,
            "CBJ" : 29,
            "MIN" : 30,
            "WPG" : 52,
            "ARI" : 53,
            "VGK" : 54
            }

    team = abbreviation

    if team.upper() in teams:
        return teams[team.upper()] 
    else:
        return false

# get division id value
def getDivisionId(division):
    divisions = {
            "ATLANTIC" : 17,
            "CENTRAL" : 16,
            "METROPOLITAN" : 18,
            "METRO" : 18,
            "PACIFIC" : 15
            }
    if division.upper() in divisions:
        return divisions[division.upper()]
    else:
        return false

# get league wide standings
def getStandings():
    req = "http://statsapi.web.nhl.com/api/v1/standings"
    r = requests.get(req)
    standings_info_json = r.text
    standings_info = json.loads(standings_info_json)
    #print(standings_info['records'][0]['division']['id'])
    #print(standings_info['records'][0]['division']['name'])
    global divisionData
    divisionData = {}
    for n in standings_info['records']:
        divisionId = n['division']['id']
        i = 1
        division_blob = ''
        for nn in range(0,3):
            pts = n['teamRecords'][nn]['points']
            team_name = n['teamRecords'][nn]['team']['name'] 
            division_blob += "%s (%s) %s pts" % (team_name, i, pts)
            if i == 3:
                pass
            else: 
                division_blob += ", "
            i += 1
        divisionData[divisionId] = division_blob

def getDivisionStandings(did):
    # getStandings() needs to be called to make sure data is fresh
    return divisionData[did] 
