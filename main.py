import requests
import time
import json
from dotenv import load_dotenv
import os
import Player
import util
import xlsxwriter
import math
import datetime

load_dotenv()

requestsDuringLastSecond = []
requestsDuringLastTwoMinutes = []

loadedGames = {}

host = "https://euw1.api.riotgames.com"
api_key = os.getenv("API_KEY")

def query(endpoint, additional_arguments=""):
    while(requestsDuringLastSecond.__len__() > 18 or requestsDuringLastTwoMinutes.__len__() > 98):
        for request in requestsDuringLastSecond:
            if time.time()-request > 1:
                requestsDuringLastSecond.remove(request)
        for request in requestsDuringLastTwoMinutes:
            if time.time()-request > 120:
                requestsDuringLastTwoMinutes.remove(request)
        time.sleep(1)
    requestsDuringLastSecond.append(time.time())
    requestsDuringLastTwoMinutes.append(time.time())
    response = requests.get(host + endpoint + "?api_key=" + api_key + additional_arguments)
    code = response.status_code
    jdata = json.loads(response.text)
    if code == 429:
        code, jdata = query(endpoint, additional_arguments)
    return code, jdata

if __name__ == "__main__":
    print("Welcome to c0M's Clash Team Analyzer!")
    print("v0.2")
    print("Please enter the names of all your enemies:")
    players = []
    playerOBJs = []
    players.append(input("P1>"))
    players.append(input("P2>"))
    players.append(input("P3>"))
    players.append(input("P4>"))
    players.append(input("P5>"))
    #players = ["Senôr Aυtism", "Inselsüchtiger", "Quanox", "Rechtsklickquell", "nvq2015"]
    print("Thanks!")
    starttime = time.time()
    util.displayLoadingbar(0, 5, "Quering summoner info...")
    count = 0
    for player in players:
        code, response = query("/lol/summoner/v4/summoners/by-name/" + player)
        if code != 200:
            print("Something went wrong during requesting " + player)
        else:
            plOBJ = Player.Player()
            plOBJ.setSummonerInfo(response)
            playerOBJs.append(plOBJ)
        count += 1
        util.displayLoadingbar(count, 5, "Quering summoner info...")
    
    util.displayLoadingbar(0, 5, "Quering mastery info...")
    count = 0
    for player in playerOBJs:
        code, response = query("/lol/champion-mastery/v4/champion-masteries/by-summoner/" + player.getEncryptedSummonerId())
        if code != 200:
            print("Something went wrong during requesting mastery for " + player.getSummonerName())
        else:
            player.setMasteryInfo(response)
        count += 1
        util.displayLoadingbar(count, 5, "Quering mastery info...")
    
    count = 0
    util.displayLoadingbar(0, 20, "Quering matchlists...")
    for player in playerOBJs:
        matchlist = {}
        matchlist["matches"] = []
        for i in range(0, 4):
            begintime = datetime.datetime.now().timestamp()*1000 - 604800000*i
            endtime = datetime.datetime.now().timestamp()*1000 - 604800000*(i+1)
            code, response = query("/lol/match/v4/matchlists/by-account/" + player.getEncryptedAccountId(), "&queue=400&queue=420&endTime=" + str(math.floor(begintime)) + "&beginTime=" + str(math.floor(endtime)))
            if code != 200:
                print("Something went wrong during requesting matchlists for " + player.getSummonerName())
                print("/lol/match/v4/matchlists/by-account/" + player.getEncryptedAccountId(), "&queue=400&queue=420&beginTime=" + str(math.floor(begintime)) + "&endTime=" + str(math.floor(endtime)))
            else:
                for match in response["matches"]:
                    matchlist["matches"].append(match)
            count += 1
            util.displayLoadingbar(count, 20, "Quering matchlists...")
        player.setMatchlist(matchlist)
    
    count = 0
    util.displayLoadingbar(0, 5, "Quering league info...")
    for player in playerOBJs:
        code, response = query("/lol/league/v4/entries/by-summoner/" + player.getEncryptedSummonerId())
        if code != 200:
            print("Something went wrong during requesting league info for " + player.getSummonerName())
        else:
            player.setLeagueInfo(response)
        count += 1
        util.displayLoadingbar(count, 5, "Quering league info...")

    maxMatchCount = 0
    totalMatchCount = 0
    for player in playerOBJs:
        if player.getMaxMatches() > maxMatchCount:
            maxMatchCount = player.getMaxMatches()
        totalMatchCount += player.getMaxMatches()
    count = 0
    util.displayLoadingbar(0, totalMatchCount, "Quering matches...")
    for i in range(0, maxMatchCount):
        for player in playerOBJs:
            mToAnalyze = player.getMatchToAnalyze()
            if mToAnalyze != -1:
                if mToAnalyze in loadedGames:
                    player.setMatchInfo(mToAnalyze, loadedGames[mToAnalyze])
                elif os.path.isfile("cache/" + str(mToAnalyze) + ".match"):
                    f = open("cache/" + str(mToAnalyze) + ".match")
                    player.setMatchInfo(mToAnalyze, json.loads(f.read()))
                else:
                    code, response = query("/lol/match/v4/matches/" + str(mToAnalyze))
                    if code != 200:
                        print("Something went wrong during requesting match for " + player.getSummonerName())
                    else:
                        f = open("cache/" + str(mToAnalyze) + ".match", "w")
                        f.write(json.dumps(response))
                        f.close()
                        loadedGames[mToAnalyze] = response
                        player.setMatchInfo(mToAnalyze, response)
            count += 1
            util.displayLoadingbar(count, totalMatchCount, "Quering matches...")
    
    print("Done!")
    timetaken = time.time()-starttime
    print("Analyzed 5 players in " + str(math.floor(timetaken)) + " seconds.")

    util.exportHTML(playerOBJs)