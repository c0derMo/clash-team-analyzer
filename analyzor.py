from dotenv import load_dotenv
import asyncio
import requests
import json
import time
import os
import Player
import util
import math
import datetime

load_dotenv()

requestsDuringLastSecond = []
requestsDuringLastTwoMinutes = []

host = "https://euw1.api.riotgames.com"
api_key = os.getenv("API_KEY")

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

async def analyzeWrap(players, sid, sio):
    try:
        await analyze(players, sid, sio)
        await sio.emit('analyzeSuccessful', "/team?p1=" + players[0] + "&p2=" + players[1] + "&p3=" + players[2] + "&p4=" + players[3] + "&p5=" + players[4], room=sid)
    except Exception as e:
        await sio.emit('analyzeFailed', str(e), room=sid)

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
            code, response = await query("/lol/summoner/v4/summoners/by-name/" + player)
            if code != 200:
                print("Something went wrong during requesting " + player)
                
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
            code, response = await query("/lol/champion-mastery/v4/champion-masteries/by-summoner/" + player.getEncryptedSummonerId())
            if code != 200:
                print("Something went wrong during requesting mastery for " + player.getSummonerName())
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
                code, response = await query("/lol/match/v4/matchlists/by-account/" + player.getEncryptedAccountId(), "&queue=400&queue=420&endTime=" + str(math.floor(begintime)) + "&beginTime=" + str(math.floor(endtime)))
                if code != 200:
                    print("Something went wrong during requesting matchlists for " + player.getSummonerName())
                    print("/lol/match/v4/matchlists/by-account/" + player.getEncryptedAccountId(), "&queue=400&queue=420&beginTime=" + str(math.floor(begintime)) + "&endTime=" + str(math.floor(endtime)))
                else:
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
            code, response = await query("/lol/league/v4/entries/by-summoner/" + player.getEncryptedSummonerId())
            if code != 200:
                print("Something went wrong during requesting league info for " + player.getSummonerName())
            else:
                player.setLeagueInfo(response)
                f = open("cache/league/" + player.getEncryptedSummonerId() + ".league", "w")
                f.write(json.dumps(response))
                f.close()
        count += 1
        await sio.emit('analyzeUpdate', {'current': count, 'max': 135, 'status': "Quering league info..."}, room=sid)

    maxMatchCount = 0
    for player in playerOBJs:
        if player.getMaxMatches() > maxMatchCount:
            maxMatchCount = player.getMaxMatches()
    await sio.emit('analyzeUpdate', {'current': count, 'max': 135, 'status': "Quering match info..."}, room=sid)
    for i in range(0, maxMatchCount):
        for player in playerOBJs:
            mToAnalyze = player.getMatchToAnalyze()
            if mToAnalyze != -1:
                if not os.path.isfile("cache/matches/" + str(mToAnalyze) + ".match"):
                    code, response = await query("/lol/match/v4/matches/" + str(mToAnalyze))
                    if code != 200:
                        print("Something went wrong during requesting match for " + player.getSummonerName())
                    else:
                        player.setMatchInfo(mToAnalyze, response)
                        f = open("cache/matches/" + str(mToAnalyze) + ".match", "w")
                        f.write(json.dumps(response))
                        f.close()
            count += 1
            await sio.emit('analyzeUpdate', {'current': count, 'max': 135, 'status': "Quering match info..."}, room=sid)