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

class Observer:
    def __init__(self, ws, amountRequests):
        self.ws = ws
        self.amountRequests = amountRequests
        self.requestsDone = 0
        self.stage = "Player info"
        self.cancelled = False
        self.done = {
            "Player info": 0,
            "Mastery info": 0,
            "Matchlists": 0,
            "League info": 0,
            "Match info": 0
        }
    
    def setCancelled(self, state):
        self.cancelled = state

    async def success(self, stage="", stageDone=False, amount=1):
        self.requestsDone += amount
        if stageDone:
            self.done[stage] += 1
            if self.done[stage] == 5:
                if self.stage == "Player info":
                    self.stage == "Mastery info"
                elif self.stage == "Mastery info":
                    self.stage == "Matchlists"
                elif self.stage == "Matchlists":
                    self.stage == "League info"
                elif self.stage == "League info":
                    self.stage == "Match info"
                elif self.stage == "Match info":
                    pass
        if not self.cancelled:
            await self.ws.send(json.dumps({'event': 'update', 'current': self.requestsDone, 'max': self.amountRequests, 'status': "Querying " + self.stage + "..."}))

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

async def newAnalyzeWrapper(msg, ws, logger):
    observer = Observer(ws, 135)
    playerNames = msg["players"]
    region = msg["region"]
    playerAnalyzes = []
    for p in playerNames:
        playerAnalyzes.append(asyncio.create_task(newAnalyzePlayer(p, region, observer)))
    try:
        await asyncio.gather(*playerAnalyzes)
        await asyncio.sleep(5)
        await ws.send(json.dumps({'event': 'success', 'link': "/team?region=" + region + "&p1=" + playerNames[0] + "&p2=" + playerNames[1] + "&p3=" + playerNames[2] + "&p4=" + playerNames[3] + "&p5=" + playerNames[4]}))
    except AnalyzeError as e:
        for task in playerAnalyzes:
            task.cancel()
        observer.setCancelled(True)
        await ws.send(json.dumps({'event': 'failure', 'error': str(e)}))
        logger.error("[" + region + "](" + e.name + ") Got an code " + str(e.code) + " when requesting " + e.query)
        await util.addNon200Error(e.code, e.name, e.query, region)
    except Exception as e:
        await ws.send(json.dumps({'event': 'failure', 'error': "Unknown error."}))
        logger.error(sys.exc_info())

async def newAnalyzePlayer(player, region, observer):
    if os.path.isfile("cache/" + region + "/players/" + player + ".player"):
        plOBJ = Player.Player()
        f = open("cache/" + region + "/players/" + player + ".player")
        plOBJ.setSummonerInfo(json.loads(f.read()))
        f.close()
        asyncio.create_task(util.addStatCachedPlayer())
    else:
        asyncio.create_task(util.addStatNonCachedPlayer())
        qS = "/lol/summoner/v4/summoners/by-name/" + player
        code, response = await query(qS, "", region)
        if code != 200:
            raise AnalyzeError("Error when quering player info for " + player, player, qS, code, response)
        else:
            plOBJ = Player.Player()
            plOBJ.setSummonerInfo(response)
            f = open("cache/" + region + "/players/" + player + ".player", "w")
            f.write(json.dumps(response))
            f.close()
    asyncio.create_task(observer.success("Player info", True))

    if not os.path.isfile("cache/" + region + "/masterys/" + plOBJ.getEncryptedSummonerId() + ".mastery"):
        qS = "/lol/champion-mastery/v4/champion-masteries/by-summoner/" + plOBJ.getEncryptedSummonerId()
        code, response = await query(qS, "", region)
        if code != 200:
            raise AnalyzeError("Error when quering player mastery info for " + plOBJ.getSummonerName(), player.getSummonerName(), qS, code, response)
        else:
            f = open("cache/" + region + "/masterys/" + plOBJ.getEncryptedSummonerId() + ".mastery", "w")
            f.write(json.dumps(response))
            f.close()
    asyncio.create_task(observer.success("Mastery info", True))

    matchlist = {}
    matchlist["matches"] = []
    if not os.path.isfile("cache/" + region + "/matchlists/" + plOBJ.getEncryptedAccountId() + ".matchlist"):
        tasks = []
        for i in range(0, 4):
            tasks.append(analyzePlayerMatchlist(plOBJ, region, observer, i))
        results = await asyncio.gather(*tasks)
        matchlist["matches"] = [*results[0], *results[1], *results[2], *results[3]]
        plOBJ.setMatchlist(matchlist)
        f = open("cache/" + region + "/matchlists/" + plOBJ.getEncryptedAccountId() + ".matchlist", "w")
        f.write(json.dumps(matchlist))
        f.close()
        asyncio.create_task(observer.success("Matchlists", True, 0))
    else:
        f = open("cache/" + region + "/matchlists/" + plOBJ.getEncryptedAccountId() + ".matchlist")
        plOBJ.setMatchlist(json.loads(f.read()))
        f.close()
        asyncio.create_task(observer.success("Matchlists", True, 5))
    
    if not os.path.isfile("cache/" + region + "/league/" + plOBJ.getEncryptedSummonerId() + ".league"):
        qS = "/lol/league/v4/entries/by-summoner/" + plOBJ.getEncryptedSummonerId()
        code, response = await query(qS, "", region)
        if code != 200:
            raise AnalyzeError("Error when quering league info for " + plOBJ.getSummonerName(), player.getSummonerName(), qS, code, response)
        else:
            plOBJ.setLeagueInfo(response)
            f = open("cache/" + region + "/league/" + plOBJ.getEncryptedSummonerId() + ".league", "w")
            f.write(json.dumps(response))
            f.close()
    asyncio.create_task(observer.success("League info", True))

    tasks = []
    for i in range(0, plOBJ.getMaxMatches()):
        mToAnalyze = plOBJ.getMatchToAnalyze()
        tasks.append(analyzePlayerMatch(plOBJ, region, observer, mToAnalyze))
    await asyncio.gather(*tasks)
    asyncio.create_task(observer.success("Match info", True, 0))
    return

async def analyzePlayerMatchlist(player, region, observer, i):
    matchlist = []
    begintime = datetime.datetime.now().timestamp()*1000 - 604800000*i
    endtime = datetime.datetime.now().timestamp()*1000 - 604800000*(i+1)
    qS = "/lol/match/v4/matchlists/by-account/" + player.getEncryptedAccountId()
    aP = "&queue=400&queue=420&endTime=" + str(math.floor(begintime)) + "&beginTime=" + str(math.floor(endtime))
    code, response = await query(qS, aP, region)
    if code != 200 and code != 404:
        raise AnalyzeError("Error when quering matchlists for " + player.getSummonerName(), player.getSummonerName(), qS + "?" + aP[1:], code, response)
    elif code != 404:
        if(response["matches"].__len__() != 0):
            for match in response["matches"]:
                matchlist.append(match)
    asyncio.create_task(observer.success())
    return matchlist

async def analyzePlayerMatch(player, region, observer, mID):
    if not os.path.isfile("cache/" + region + "/matches/" + str(mID) + ".match"):
        asyncio.create_task(util.addStatNonCachedMatch())
        qS = "/lol/match/v4/matches/" + str(mID)
        code, response = await query(qS, "", region)
        if code != 200:
            raise AnalyzeError("Error when requesting match for " + player.getSummonerName(), player.getSummonerName(), qS, code, response)
        else:
            player.setMatchInfo(mID, response)
            f = open("cache/" + region + "/matches/" + str(mID) + ".match", "w")
            f.write(json.dumps(response))
            f.close()
    else:
        asyncio.create_task(util.addStatCachedMatch())
        with open("cache/" + region + "/matches/" + str(mID) + ".match") as f:
            player.setMatchInfo(mID, json.loads(f.read()))
            f.close()
    asyncio.create_task(observer.success())
    return