import json
import time
import math
from collections import OrderedDict
import Player
import sys
import requests
import ast
import os
import glob
import datetime

champS = '{"1":"Annie","2":"Olaf","3":"Galio","4":"TwistedFate","5":"XinZhao","6":"Urgot","7":"Leblanc","8":"Vladimir","9":"Fiddlesticks","10":"Kayle","11":"MasterYi","12":"Alistar","13":"Ryze","14":"Sion","15":"Sivir","16":"Soraka","17":"Teemo","18":"Tristana","19":"Warwick","20":"Nunu","21":"MissFortune","22":"Ashe","23":"Tryndamere","24":"Jax","25":"Morgana","26":"Zilean","27":"Singed","28":"Evelynn","29":"Twitch","30":"Karthus","31":"Chogath","32":"Amumu","33":"Rammus","34":"Anivia","35":"Shaco","36":"DrMundo","37":"Sona","38":"Kassadin","39":"Irelia","40":"Janna","41":"Gangplank","42":"Corki","43":"Karma","44":"Taric","45":"Veigar","48":"Trundle","50":"Swain","51":"Caitlyn","53":"Blitzcrank","54":"Malphite","55":"Katarina","56":"Nocturne","57":"Maokai","58":"Renekton","59":"JarvanIV","60":"Elise","61":"Orianna","62":"MonkeyKing","63":"Brand","64":"LeeSin","67":"Vayne","68":"Rumble","69":"Cassiopeia","72":"Skarner","74":"Heimerdinger","75":"Nasus","76":"Nidalee","77":"Udyr","78":"Poppy","79":"Gragas","80":"Pantheon","81":"Ezreal","82":"Mordekaiser","83":"Yorick","84":"Akali","85":"Kennen","86":"Garen","89":"Leona","90":"Malzahar","91":"Talon","92":"Riven","96":"KogMaw","98":"Shen","99":"Lux","101":"Xerath","102":"Shyvana","103":"Ahri","104":"Graves","105":"Fizz","106":"Volibear","107":"Rengar","110":"Varus","111":"Nautilus","112":"Viktor","113":"Sejuani","114":"Fiora","115":"Ziggs","117":"Lulu","119":"Draven","120":"Hecarim","121":"Khazix","122":"Darius","126":"Jayce","127":"Lissandra","131":"Diana","133":"Quinn","134":"Syndra","136":"AurelionSol","141":"Kayn","142":"Zoe","143":"Zyra","145":"Kaisa","150":"Gnar","154":"Zac","157":"Yasuo","161":"Velkoz","163":"Taliyah","164":"Camille","201":"Braum","202":"Jhin","203":"Kindred","222":"Jinx","223":"TahmKench","235":"Senna","236":"Lucian","238":"Zed","240":"Kled","245":"Ekko","246":"Qiyana","254":"Vi","266":"Aatrox","267":"Nami","268":"Azir","350":"Yuumi","412":"Thresh","420":"Illaoi","421":"RekSai","427":"Ivern","429":"Kalista","432":"Bard","497":"Rakan","498":"Xayah","516":"Ornn","517":"Sylas","518":"Neeko","523":"Aphelios","555":"Pyke"}'
champJSON = json.loads(champS)

masteryRow = '<tr><th scope="row">%NR</th><td><img src="http://ddragon.leagueoflegends.com/cdn/9.24.2/img/champion/%CHAMP.png" style="width: 60px; height: 60px;"></td><td>%CHAMP</td><td>%LEVEL</td><td>%POINTS</td></tr>'
mostPlayedRow = '<tr><th scope="row">%NR</th><td><img src="http://ddragon.leagueoflegends.com/cdn/9.24.2/img/champion/%CHAMP.png" style="width: 60px; height: 60px;"></td><td>%CHAMP</td><td>%AMOUNT</td></tr>'

def getChampionName(id):
    return champJSON[str(id)]

def getChampInfo():
    global champJSON
    response = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
    if response.status_code != 200:
        return False
    version = ast.literal_eval(response.text)[0]
    r2 = requests.get("http://ddragon.leagueoflegends.com/cdn/" + str(version) + "/data/en_US/champion.json")
    if r2.status_code != 200:
        return False
    jsData = json.loads(r2.text)
    resultData = {}
    for champ in jsData["data"]:
        resultData[jsData["data"][champ]["key"]] = champ
    champJSON = resultData
    return True

def loadDemoData():
    players = ["Inselsüchtiger", "Quanox", "Senôr Aυtism", "Rechtsklickquell", "nvq2015"]
    playerOBJs = []
    for player in players:
        p1O = Player.Player()
        f = open("demodata/players/" + player + ".player")
        p1O.setSummonerInfo(json.loads(f.read()))
        f.close()
        f = open("demodata/masterys/" + p1O.getEncryptedSummonerId() + ".mastery")
        p1O.setMasteryInfo(json.loads(f.read()))
        f.close()
        f = open("demodata/matchlists/" + p1O.getEncryptedAccountId() + ".matchlist")
        p1O.setMatchlist(json.loads(f.read()))
        f.close()
        f = open("demodata/league/" + p1O.getEncryptedSummonerId() + ".league")
        p1O.setLeagueInfo(json.loads(f.read()))
        f.close()
        playerOBJs.append(p1O)
    for p1O in playerOBJs:
        for i in range(0, p1O.getMaxMatches()):
            mToAnalyze = p1O.getMatchToAnalyze()
            f = open("demodata/matches/" + str(mToAnalyze) + ".match")
            p1O.setMatchInfo(mToAnalyze, json.loads(f.read()))
            f.close()
    return playerOBJs

def loadPlayersFromCache(p1, p2, p3, p4, p5):
    players = [p1, p2, p3, p4, p5]
    playerOBJs = []
    try:
        for player in players:
            p1O = Player.Player()
            f = open("cache/players/" + player + ".player")
            p1O.setSummonerInfo(json.loads(f.read()))
            f.close()
            f = open("cache/masterys/" + p1O.getEncryptedSummonerId() + ".mastery")
            p1O.setMasteryInfo(json.loads(f.read()))
            f.close()
            f = open("cache/matchlists/" + p1O.getEncryptedAccountId() + ".matchlist")
            p1O.setMatchlist(json.loads(f.read()))
            f.close()
            f = open("cache/league/" + p1O.getEncryptedSummonerId() + ".league")
            p1O.setLeagueInfo(json.loads(f.read()))
            f.close()
            playerOBJs.append(p1O)
    except FileNotFoundError:
        return -1
    for p1O in playerOBJs:
        for i in range(0, p1O.getMaxMatches()):
            mToAnalyze = p1O.getMatchToAnalyze()
            try:
                f = open("cache/matches/" + str(mToAnalyze) + ".match")
                p1O.setMatchInfo(mToAnalyze, json.loads(f.read()))
                f.close()
            except FileNotFoundError:
                pass
    return playerOBJs

async def addPageAnalytic(message):
    fn = datetime.datetime.now().strftime("%Y-%m-%d.data")
    f = open("statistics/views/" + fn, "a")
    f.write(datetime.datetime.now().strftime("%H:%M:%S ") + message + "\n")
    f.close()

async def addCodeAnalytic(code):
    fn = datetime.datetime.now().strftime("%Y-%m-%d.data")
    f = open("statistics/returncodes/" + fn, "a")
    f.write(datetime.datetime.now().strftime("%H:%M:%S ") + str(code) + "\n")
    f.close()

async def addStatAnalyze():
    fn = datetime.datetime.now().strftime("%Y-%m-%d.data")
    if not os.path.isfile("statistics/analyze/" + fn):
        f = open("statistics/analyze/" + fn, "w")
        f.write("0\n0\n0\n0\n0\n")
        f.close()
    f = open("statistics/analyze/" + fn)
    lines = f.readlines()
    num = int(lines[0])
    num += 1
    lines[0] = str(num) + "\n"
    f.close()
    f = open("statistics/analyze/" + fn, "w")
    f.writelines(lines)
    f.close()

async def addStatNonCachedPlayer():
    fn = datetime.datetime.now().strftime("%Y-%m-%d.data")
    if not os.path.isfile("statistics/analyze/" + fn):
        f = open("statistics/analyze/" + fn, "w")
        f.write("0\n0\n0\n0\n0\n")
        f.close()
    f = open("statistics/analyze/" + fn)
    lines = f.readlines()
    num = int(lines[1])
    num += 1
    lines[1] = str(num) + "\n"
    f.close()
    f = open("statistics/analyze/" + fn, "w")
    f.writelines(lines)
    f.close()

async def addStatCachedPlayer():
    fn = datetime.datetime.now().strftime("%Y-%m-%d.data")
    if not os.path.isfile("statistics/analyze/" + fn):
        f = open("statistics/analyze/" + fn, "w")
        f.write("0\n0\n0\n0\n0\n")
        f.close()
    f = open("statistics/analyze/" + fn)
    lines = f.readlines()
    num = int(lines[2])
    num += 1
    lines[2] = str(num) + "\n"
    f.close()
    f = open("statistics/analyze/" + fn, "w")
    f.writelines(lines)
    f.close()

async def addStatNonCachedMatch():
    fn = datetime.datetime.now().strftime("%Y-%m-%d.data")
    if not os.path.isfile("statistics/analyze/" + fn):
        f = open("statistics/analyze/" + fn, "w")
        f.write("0\n0\n0\n0\n0\n")
        f.close()
    f = open("statistics/analyze/" + fn)
    lines = f.readlines()
    num = int(lines[3])
    num += 1
    lines[3] = str(num) + "\n"
    f.close()
    f = open("statistics/analyze/" + fn, "w")
    f.writelines(lines)
    f.close()

async def addStatCachedMatch():
    fn = datetime.datetime.now().strftime("%Y-%m-%d.data")
    if not os.path.isfile("statistics/analyze/" + fn):
        f = open("statistics/analyze/" + fn, "w")
        f.write("0\n0\n0\n0\n0\n")
        f.close()
    f = open("statistics/analyze/" + fn)
    lines = f.readlines()
    num = int(lines[4])
    num += 1
    lines[4] = str(num) + "\n"
    f.close()
    f = open("statistics/analyze/" + fn, "w")
    f.writelines(lines)
    f.close()

def getStatistics(date=datetime.datetime.now().strftime("%Y-%m-%d")):
    result = {}
    result["views"] = {}
    result["views"]["/"] = [[0, 0],[1, 0],[2, 0],[3, 0],[4, 0],[5, 0],[6, 0],[7, 0],[8, 0],[9, 0],[10, 0],[11, 0],[12, 0],[13, 0],[14, 0],[15, 0],[16, 0],[17, 0],[18, 0],[19, 0],[20, 0],[21, 0],[22, 0],[23, 0]]
    result["views"]["/team"] = [[0, 0],[1, 0],[2, 0],[3, 0],[4, 0],[5, 0],[6, 0],[7, 0],[8, 0],[9, 0],[10, 0],[11, 0],[12, 0],[13, 0],[14, 0],[15, 0],[16, 0],[17, 0],[18, 0],[19, 0],[20, 0],[21, 0],[22, 0],[23, 0]]
    result["views"]["/demodata"] = [[0, 0],[1, 0],[2, 0],[3, 0],[4, 0],[5, 0],[6, 0],[7, 0],[8, 0],[9, 0],[10, 0],[11, 0],[12, 0],[13, 0],[14, 0],[15, 0],[16, 0],[17, 0],[18, 0],[19, 0],[20, 0],[21, 0],[22, 0],[23, 0]]
    result["codes"] = {}
    result["dates"] = []
    result["date"] = date
    for fn in glob.glob("statistics/views/*.data"):
        result["dates"].append(fn[17:-5])
    result["dates"].sort(reverse=True)
    if os.path.isfile("statistics/views/" + date + ".data"):
        with open("statistics/views/" + date + ".data") as f:
            for line in f.readlines():
                dateCpy = line[:8]
                dateArr = dateCpy.split(":")
                view = line[9:]
                t = round(int(dateArr[0]) + (int(dateArr[1]) / 60) + (int(dateArr[2]) / 3600))
                if view == "/\n":
                    tmp = result["views"]["/"][t][1] + 1
                    result["views"]["/"][t][1] = tmp
                elif view == "/team\n":
                    tmp = result["views"]["/team"][t][1] + 1
                    result["views"]["/team"][t][1] = tmp
                elif view == "/demodata\n":
                    tmp = result["views"]["/demodata"][t][1] + 1
                    result["views"]["/demodata"][t][1] = tmp
    if os.path.isfile("statistics/returncodes/" + date + ".data"):
        with open("statistics/returncodes/" + date + ".data") as f:
            for line in f.readlines():
                code = line[9:-1]
                if code in result["codes"]:
                    result["codes"][code] += 1
                else:
                    result["codes"][code] = 1
    if os.path.isfile("statistics/analyze/" + date + ".data"):
        with open("statistics/analyze/" + date + ".data") as f:
            lines = f.readlines()
            result["analyze"] = {}
            result["analyze"]["analyzeCount"] = int(lines[0])
            result["analyze"]["unCachedPlayer"] = int(lines[1])
            result["analyze"]["cachedPlayer"] = int(lines[2])
            result["analyze"]["unCachedMatch"] = int(lines[3])
            result["analyze"]["cachedMatch"] = int(lines[4])
    else:
        result["analyze"] = {"analyzeCount": 0, "unCachedPlayer": 0, "cachedPlayer": 0, "unCachedMatch": 0, "cachedMatch": 0}
    return result

async def addNon200Error(code, player, request):
    fn = datetime.datetime.now().strftime("%Y-%m-%d.data")
    f = open("statistics/errors/" + fn, "a")
    f.write(datetime.datetime.now().strftime("%H:%M:%S ") + str(code) + " for player " + str(player) + " when requesting " + str(request) + "\n")
    f.close()

def getMatchesPlayedTogether(p1, p2):
    p1MatchIDS = []
    p2MatchIDS = []
    for match in p1.matchlist["matches"]:
        p1MatchIDS.append(match["gameId"])
    for match in p2.matchlist["matches"]:
        p2MatchIDS.append(match["gameId"])
    return str(len(set(p1MatchIDS) & set(p2MatchIDS)))

def getMatchesPlayedAsFullTeam(players):
    p1 = players[0]
    p2 = players[1]
    p3 = players[2]
    p4 = players[3]
    p5 = players[4]
    p1MatchIDS = []
    p2MatchIDS = []
    p3MatchIDS = []
    p4MatchIDS = []
    p5MatchIDS = []
    
    for match in p1.matchlist["matches"]:
        p1MatchIDS.append(match["gameId"])
    for match in p2.matchlist["matches"]:
        p2MatchIDS.append(match["gameId"])
    for match in p3.matchlist["matches"]:
        p3MatchIDS.append(match["gameId"])
    for match in p4.matchlist["matches"]:
        p4MatchIDS.append(match["gameId"])
    for match in p5.matchlist["matches"]:
        p5MatchIDS.append(match["gameId"])

    return len(set(p1MatchIDS) & set(p2MatchIDS) & set(p3MatchIDS) & set(p4MatchIDS) & set(p5MatchIDS))

def createRegionFolderStructure(region):
    os.makedirs("cache/" + region + "/league/", exist_ok=True)
    os.makedirs("cache/" + region + "/masterys/", exist_ok=True)
    os.makedirs("cache/" + region + "/matches/", exist_ok=True)
    os.makedirs("cache/" + region + "/matchlists/", exist_ok=True)
    os.makedirs("cache/" + region + "/players/", exist_ok=True)

def createFolderStructure():
    createRegionFolderStructure("euw")
    createRegionFolderStructure("na")
    createRegionFolderStructure("eune")
    createRegionFolderStructure("br")
    createRegionFolderStructure("jp")
    createRegionFolderStructure("kr")
    createRegionFolderStructure("lan")
    createRegionFolderStructure("las")
    createRegionFolderStructure("oce")
    createRegionFolderStructure("tr")
    createRegionFolderStructure("ru")