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
import config
import datetime

load_dotenv()

region_infos = {
    "euw": {
        "host": "https://euw1.api.riotgames.com",
        "requestsDuringLastSecond": [],
        "requestsDuringLastTwoMinutes": [],
        "requestsDuringLast10Seconds": [],
        "requestsDuringLast10Minutes": []
    },
    "na": {
        "host": "https://na1.api.riotgames.com",
        "requestsDuringLastSecond": [],
        "requestsDuringLastTwoMinutes": [],
        "requestsDuringLast10Seconds": [],
        "requestsDuringLast10Minutes": []
    },
    "eune": {
        "host": "https://eun1.api.riotgames.com",
        "requestsDuringLastSecond": [],
        "requestsDuringLastTwoMinutes": [],
        "requestsDuringLast10Seconds": [],
        "requestsDuringLast10Minutes": []
    },
    "br": {
        "host": "https://br1.api.riotgames.com",
        "requestsDuringLastSecond": [],
        "requestsDuringLastTwoMinutes": [],
        "requestsDuringLast10Seconds": [],
        "requestsDuringLast10Minutes": []
    },
    "jp": {
        "host": "https://jp1.api.riotgames.com",
        "requestsDuringLastSecond": [],
        "requestsDuringLastTwoMinutes": [],
        "requestsDuringLast10Seconds": [],
        "requestsDuringLast10Minutes": []
    },
    "kr": {
        "host": "https://kr.api.riotgames.com",
        "requestsDuringLastSecond": [],
        "requestsDuringLastTwoMinutes": [],
        "requestsDuringLast10Seconds": [],
        "requestsDuringLast10Minutes": []
    },
    "lan": {
        "host": "https://la1.api.riotgames.com",
        "requestsDuringLastSecond": [],
        "requestsDuringLastTwoMinutes": [],
        "requestsDuringLast10Seconds": [],
        "requestsDuringLast10Minutes": []
    },
    "las": {
        "host": "https://la2.api.riotgames.com",
        "requestsDuringLastSecond": [],
        "requestsDuringLastTwoMinutes": [],
        "requestsDuringLast10Seconds": [],
        "requestsDuringLast10Minutes": []
    },
    "oce": {
        "host": "https://oc1.api.riotgames.com",
        "requestsDuringLastSecond": [],
        "requestsDuringLastTwoMinutes": [],
        "requestsDuringLast10Seconds": [],
        "requestsDuringLast10Minutes": []
    },
    "tr": {
        "host": "https://tr1.api.riotgames.com",
        "requestsDuringLastSecond": [],
        "requestsDuringLastTwoMinutes": [],
        "requestsDuringLast10Seconds": [],
        "requestsDuringLast10Minutes": []
    },
    "ru": {
        "host": "https://ru.api.riotgames.com",
        "requestsDuringLastSecond": [],
        "requestsDuringLastTwoMinutes": [],
        "requestsDuringLast10Seconds": [],
        "requestsDuringLast10Minutes": []
    },
}

class AnalyzeError(Exception):
    def __init__(self, message, name, query, code, response):
        super().__init__(message)
        self.name = name
        self.query = query
        self.code = code
        self.response = response

api_key = os.getenv("API_KEY")

def hasValidAPIKey():
    if api_key == "":
        return False
    response = requests.get(region_infos["euw"]["host"] + "/lol/status/v3/shard-data?api_key=" + api_key)
    code = response.status_code
    if code > 499:
        return hasValidAPIKey()
    if code == 401 or code == 403:
        return False
    else:
        return True

async def queryDev(endpoint, additional_arguments, region):
    while(region_infos[region]["requestsDuringLastSecond"].__len__() >= config.getRateLimitPerSecond() or region_infos[region]["requestsDuringLastTwoMinutes"].__len__() >= config.getRateLimitPer2Minutes()):
        for request in region_infos[region]["requestsDuringLastSecond"]:
            if time.time()-request > 1:
                region_infos[region]["requestsDuringLastSecond"].remove(request)
        for request in region_infos[region]["requestsDuringLastTwoMinutes"]:
            if time.time()-request > 120:
                region_infos[region]["requestsDuringLastTwoMinutes"].remove(request)
        await asyncio.sleep(1)
    region_infos[region]["requestsDuringLastSecond"].append(time.time())
    region_infos[region]["requestsDuringLastTwoMinutes"].append(time.time())
    response = requests.get(region_infos[region]["host"] + endpoint + "?api_key=" + api_key + additional_arguments)
    asyncio.create_task(util.addCodeAnalytic(response.status_code))
    code = response.status_code
    jdata = json.loads(response.text)
    if code == 429:
        #print("Hit a 429 - why tho?")
        await asyncio.sleep(1)
        code, jdata = await query(endpoint, additional_arguments, region)
    return code, jdata

async def queryProd(endpoint, additional_arguments, region):
    while(region_infos[region]["requestsDuringLast10Seconds"].__len__() >= config.getRateLimitPer10Seconds() or region_infos[region]["requestsDuringLast10Minutes"].__len__() >= config.getRateLimitPer10Minutes()):
        for request in region_infos[region]["requestsDuringLast10Seconds"]:
            if time.time()-request > 10:
                region_infos[region]["requestsDuringLast10Seconds"].remove(request)
        for request in region_infos[region]["requestsDuringLast10Minutes"]:
            if time.time()-request > 600:
                region_infos[region]["requestsDuringLast10Minutes"].remove(request)
        await asyncio.sleep(1)
    region_infos[region]["requestsDuringLast10Minutes"].append(time.time())
    region_infos[region]["requestsDuringLast10Seconds"].append(time.time())
    response = requests.get(region_infos[region]["host"] + endpoint + "?api_key=" + api_key + additional_arguments)
    asyncio.create_task(util.addCodeAnalytic(response.status_code))
    code = response.status_code
    jdata = json.loads(response.text)
    if code == 429:
        #print("Hit a 429 - why tho?")
        await asyncio.sleep(1)
        code, jdata = await query(endpoint, additional_arguments, region)
    return code, jdata

async def query(endpoint, additional_arguments="", region="euw"):
    if config.getAPIType() == "production":
        return await queryProd(endpoint, additional_arguments, region)
    else:
        return await queryDev(endpoint, additional_arguments, region)

async def analyzeWrap(msg, sid, sio, logger):
    try:
        playerNames = msg["players"]
        region = msg["region"]
        await analyze(playerNames, sid, sio, region)
        await sio.emit('analyzeSuccessful', "/team?region=" + region + "&p1=" + playerNames[0] + "&p2=" + playerNames[1] + "&p3=" + playerNames[2] + "&p4=" + playerNames[3] + "&p5=" + playerNames[4], room=sid)
    except AnalyzeError as e:
        await sio.emit('analyzeFailed', str(e), room=sid)
        logger.error("[" + region + "](" + e.name + ") Got an code " + str(e.code) + " when requesting " + e.query)
        await util.addNon200Error(e.code, e.name, e.query, region)
    except Exception as e:
        await sio.emit('analyzeFailed', "Unknown error.", room=sid)
        logger.error(sys.exc_info())

async def analyze(players, sid, sio, region):
    playerOBJs = []
    #starttime = time.time()
    count = 0
    await sio.emit('analyzeUpdate', {'current': count, 'max': 135, 'status': "Quering player info..."}, room=sid)
    for player in players:
        if os.path.isfile("cache/" + region + "/players/" + player + ".player"):
            plOBJ = Player.Player()
            f = open("cache/" + region + "/players/" + player + ".player")
            plOBJ.setSummonerInfo(json.loads(f.read()))
            f.close()
            asyncio.create_task(util.addStatCachedPlayer())
            playerOBJs.append(plOBJ)
        else:
            asyncio.create_task(util.addStatNonCachedPlayer())
            qS = "/lol/summoner/v4/summoners/by-name/" + player
            code, response = await query(qS, "", region)
            if code != 200:
                #print("Something went wrong during requesting " + player)
                raise AnalyzeError("Error when quering player info for " + player, player, qS, code, response)
            else:
                plOBJ = Player.Player()
                plOBJ.setSummonerInfo(response)
                f = open("cache/" + region + "/players/" + player + ".player", "w")
                f.write(json.dumps(response))
                f.close()
                playerOBJs.append(plOBJ)
        count += 1
        await sio.emit('analyzeUpdate', {'current': count, 'max': 135, 'status': "Quering player info..."}, room=sid)
    
    await sio.emit('analyzeUpdate', {'current': count, 'max': 135, 'status': "Quering mastery info..."}, room=sid)
    for player in playerOBJs:
        if not os.path.isfile("cache/" + region + "/masterys/" + player.getEncryptedSummonerId() + ".mastery"):
            qS = "/lol/champion-mastery/v4/champion-masteries/by-summoner/" + player.getEncryptedSummonerId()
            code, response = await query(qS, "", region)
            if code != 200:
                #print("Something went wrong during requesting mastery for " + player.getSummonerName())
                raise AnalyzeError("Error when quering player mastery info for " + player.getSummonerName(), player.getSummonerName(), qS, code, response)
            else:
                f = open("cache/" + region + "/masterys/" + player.getEncryptedSummonerId() + ".mastery", "w")
                f.write(json.dumps(response))
                f.close()
        count += 1
        await sio.emit('analyzeUpdate', {'current': count, 'max': 135, 'status': "Quering mastery info..."}, room=sid)
    
    await sio.emit('analyzeUpdate', {'current': count, 'max': 135, 'status': "Quering matchlists..."}, room=sid)
    for player in playerOBJs:
        matchlist = {}
        matchlist["matches"] = []
        if not os.path.isfile("cache/" + region + "/matchlists/" + player.getEncryptedAccountId() + ".matchlist"):
            for i in range(0, 4):
                begintime = datetime.datetime.now().timestamp()*1000 - 604800000*i
                endtime = datetime.datetime.now().timestamp()*1000 - 604800000*(i+1)
                qS = "/lol/match/v4/matchlists/by-account/" + player.getEncryptedAccountId()
                aP = "&queue=400&queue=420&endTime=" + str(math.floor(begintime)) + "&beginTime=" + str(math.floor(endtime))
                code, response = await query(qS, aP, region)
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
            f = open("cache/" + region + "/matchlists/" + player.getEncryptedAccountId() + ".matchlist", "w")
            f.write(json.dumps(matchlist))
            f.close()
        else:
            f = open("cache/" + region + "/matchlists/" + player.getEncryptedAccountId() + ".matchlist")
            player.setMatchlist(json.loads(f.read()))
            f.close() 
            count += 5
            await sio.emit('analyzeUpdate', {'current': count, 'max': 135, 'status': "Quering matchlists..."}, room=sid)
        
    
    await sio.emit('analyzeUpdate', {'current': count, 'max': 135, 'status': "Quering league info..."}, room=sid)
    for player in playerOBJs:
        if not os.path.isfile("cache/" + region + "/league/" + player.getEncryptedSummonerId() + ".league"):
            qS = "/lol/league/v4/entries/by-summoner/" + player.getEncryptedSummonerId()
            code, response = await query(qS, "", region)
            if code != 200:
                #print("Something went wrong during requesting league info for " + player.getSummonerName())
                raise AnalyzeError("Error when quering league info for " + player.getSummonerName(), player.getSummonerName(), qS, code, response)
            else:
                player.setLeagueInfo(response)
                f = open("cache/" + region + "/league/" + player.getEncryptedSummonerId() + ".league", "w")
                f.write(json.dumps(response))
                f.close()
        count += 1
        await sio.emit('analyzeUpdate', {'current': count, 'max': 135, 'status': "Quering league info..."}, room=sid)

    await sio.emit('analyzeUpdate', {'current': count, 'max': 135, 'status': "Quering match info..."}, room=sid)
    for player in playerOBJs:
        for i in range(0, player.getMaxMatches()):
            mToAnalyze = player.getMatchToAnalyze()
            if not os.path.isfile("cache/" + region + "/matches/" + str(mToAnalyze) + ".match"):
                asyncio.create_task(util.addStatNonCachedMatch())
                qS = "/lol/match/v4/matches/" + str(mToAnalyze)
                code, response = await query(qS, "", region)
                if code != 200:
                    #print("Something went wrong during requesting match for " + player.getSummonerName())
                    raise AnalyzeError("Error when requesting match for " + player.getSummonerName(), player.getSummonerName(), qS, code, response)
                else:
                    player.setMatchInfo(mToAnalyze, response)
                    f = open("cache/" + region + "/matches/" + str(mToAnalyze) + ".match", "w")
                    f.write(json.dumps(response))
                    f.close()
            else:
                asyncio.create_task(util.addStatCachedMatch())
                with open("cache/" + region + "/matches/" + str(mToAnalyze) + ".match") as f:
                    player.setMatchInfo(mToAnalyze, json.loads(f.read()))
                    f.close()
        count += 1
        await sio.emit('analyzeUpdate', {'current': count, 'max': 135, 'status': "Quering match info..."}, room=sid)
