from dotenv import load_dotenv
import asyncio
import requests
import json
import time
import os
import Player
import util
import math
import sys
import datetime

load_dotenv()

requestsDuringLastSecond = []
requestsDuringLastTwoMinutes = []

host = "https://euw1.api.riotgames.com"
api_key = os.getenv("API_KEY")

def hasValidAPIKey():
    if api_key == "":
        return False
    response = requests.get(host + "/lol/status/v3/shard-data?api_key=" + api_key)
    code = response.status_code
    if code > 499:
        return hasValidKey()
    if code == 401 or code == 403:
        return False
    else:
        return True

async def query(endpoint, additional_arguments=""):
    while(requestsDuringLastSecond.__len__() > 18 or requestsDuringLastTwoMinutes.__len__() > 98):
        for request in requestsDuringLastSecond:
            if time.time()-request > 1:
                requestsDuringLastSecond.remove(request)
        for request in requestsDuringLastTwoMinutes:
            if time.time()-request > 120:
                requestsDuringLastTwoMinutes.remove(request)
        await asyncio.sleep(1)
    requestsDuringLastSecond.append(time.time())
    requestsDuringLastTwoMinutes.append(time.time())
    response = requests.get(host + endpoint + "?api_key=" + api_key + additional_arguments)
    code = response.status_code
    jdata = json.loads(response.text)
    if code == 429:
        #print("Hit a 429 - why tho?")
        code, jdata = await query(endpoint, additional_arguments)
    return code, jdata

class AnalyzeError(Exception):
    def __init__(self, message, name, query, code, response):
        super().__init__(message)
        self.name = name
        self.query = query
        self.code = code
        self.response = response

async def analyzeWrap(players, sid, sio, logger):
    try:
        await analyze(players, sid, sio)
        await sio.emit('analyzeSuccessful', "/team?p1=" + players[0] + "&p2=" + players[1] + "&p3=" + players[2] + "&p4=" + players[3] + "&p5=" + players[4], room=sid)
    except AnalyzeError as e:
        await sio.emit('analyzeFailed', str(e), room=sid)
        logger.error("(" + e.name + ") Got an code " + str(e.code) + " when requesting " + e.query)
    except Exception as e:
        await sio.emit('analyzeFailed', "Unknown error.", room=sid)
        logger.error(sys.exc_info())

async def analyze(players, sid, sio):
    playerOBJs = []
    #starttime = time.time()
    count = 0
    await sio.emit('analyzeUpdate', {'current': count, 'max': 135, 'status': "Quering player info..."}, room=sid)
    for player in players:
        if os.path.isfile("cache/players/" + player + ".player"):
            plOBJ = Player.Player()
            f = open("cache/players/" + player + ".player")
            plOBJ.setSummonerInfo(json.loads(f.read()))
            f.close()
            playerOBJs.append(plOBJ)
        else:
            qS = "/lol/summoner/v4/summoners/by-name/" + player
            code, response = await query(qS)
            if code != 200:
                #print("Something went wrong during requesting " + player)
                raise AnalyzeError("Error when quering player info for " + player, player, qS, code, response)
            else:
                plOBJ = Player.Player()
                plOBJ.setSummonerInfo(response)
                f = open("cache/players/" + player + ".player", "w")
                f.write(json.dumps(response))
                f.close()
                playerOBJs.append(plOBJ)
        count += 1
        await sio.emit('analyzeUpdate', {'current': count, 'max': 135, 'status': "Quering player info..."}, room=sid)
    
    await sio.emit('analyzeUpdate', {'current': count, 'max': 135, 'status': "Quering mastery info..."}, room=sid)
    for player in playerOBJs:
        if not os.path.isfile("cache/masterys/" + player.getEncryptedSummonerId() + ".mastery"):
            qS = "/lol/champion-mastery/v4/champion-masteries/by-summoner/" + player.getEncryptedSummonerId()
            code, response = await query(qS)
            if code != 200:
                #print("Something went wrong during requesting mastery for " + player.getSummonerName())
                raise AnalyzeError("Error when quering player mastery info for " + player.getSummonerName(), player.getSummonerName(), qS, code, response)
            else:
                f = open("cache/masterys/" + player.getEncryptedSummonerId() + ".mastery", "w")
                f.write(json.dumps(response))
                f.close()
        count += 1
        await sio.emit('analyzeUpdate', {'current': count, 'max': 135, 'status': "Quering mastery info..."}, room=sid)
    
    await sio.emit('analyzeUpdate', {'current': count, 'max': 135, 'status': "Quering matchlists..."}, room=sid)
    for player in playerOBJs:
        matchlist = {}
        matchlist["matches"] = []
        if not os.path.isfile("cache/matchlists/" + player.getEncryptedAccountId() + ".matchlist"):
            for i in range(0, 4):
                begintime = datetime.datetime.now().timestamp()*1000 - 604800000*i
                endtime = datetime.datetime.now().timestamp()*1000 - 604800000*(i+1)
                qS = "/lol/match/v4/matchlists/by-account/" + player.getEncryptedAccountId()
                aP = "&queue=400&queue=420&endTime=" + str(math.floor(begintime)) + "&beginTime=" + str(math.floor(endtime))
                code, response = await query(qS, aP)
                if code != 200 and code != 404:
                    #print("Something went wrong during requesting matchlists for " + player.getSummonerName())
                    raise AnalyzeError("Error when quering matchlists for " + player.getSummonerName(), player.getSummonerName(), qS + "?" + aP[1:], code, response)
                elif code != 404:
                    if(response["matches"].__len__() != 0):
                        for match in response["matches"]:
                            matchlist["matches"].append(match)
                count += 1
                await sio.emit('analyzeUpdate', {'current': count, 'max': 135, 'status': "Quering matchlists..."}, room=sid)
            player.setMatchlist(matchlist)
            f = open("cache/matchlists/" + player.getEncryptedAccountId() + ".matchlist", "w")
            f.write(json.dumps(matchlist))
            f.close()
        else:
            f = open("cache/matchlists/" + player.getEncryptedAccountId() + ".matchlist")
            player.setMatchlist(json.loads(f.read()))
            f.close() 
            count += 5
            await sio.emit('analyzeUpdate', {'current': count, 'max': 135, 'status': "Quering matchlists..."}, room=sid)
        
    
    await sio.emit('analyzeUpdate', {'current': count, 'max': 135, 'status': "Quering league info..."}, room=sid)
    for player in playerOBJs:
        if not os.path.isfile("cache/league/" + player.getEncryptedSummonerId() + ".league"):
            qS = "/lol/league/v4/entries/by-summoner/" + player.getEncryptedSummonerId()
            code, response = await query(qS)
            if code != 200:
                #print("Something went wrong during requesting league info for " + player.getSummonerName())
                raise AnalyzeError("Error when quering league info for " + player.getSummonerName(), player.getSummonerName(), qS, code, response)
            else:
                player.setLeagueInfo(response)
                f = open("cache/league/" + player.getEncryptedSummonerId() + ".league", "w")
                f.write(json.dumps(response))
                f.close()
        count += 1
        await sio.emit('analyzeUpdate', {'current': count, 'max': 135, 'status': "Quering league info..."}, room=sid)

    await sio.emit('analyzeUpdate', {'current': count, 'max': 135, 'status': "Quering match info..."}, room=sid)
    for player in playerOBJs:
        for i in range(0, player.getMaxMatches()):
            mToAnalyze = player.getMatchToAnalyze()
            if not os.path.isfile("cache/matches/" + str(mToAnalyze) + ".match"):
                qS = "/lol/match/v4/matches/" + str(mToAnalyze)
                code, response = await query(qS)
                if code != 200:
                    #print("Something went wrong during requesting match for " + player.getSummonerName())
                    raise AnalyzeError("Error when requesting match for " + player.getSummonerName(), player.getSummonerName(), qS, code, response)
                else:
                    player.setMatchInfo(mToAnalyze, response)
                    f = open("cache/matches/" + str(mToAnalyze) + ".match", "w")
                    f.write(json.dumps(response))
                    f.close()
            else:
                with open("cache/matches/" + str(mToAnalyze) + ".match") as f:
                    player.setMatchInfo(mToAnalyze, json.loads(f.read()))
                    f.close()
        count += 1
        await sio.emit('analyzeUpdate', {'current': count, 'max': 135, 'status': "Quering match info..."}, room=sid)