import json
import xlsxwriter
import time
import math
from collections import OrderedDict
import Player
import sys

champS = '{"1":"Annie","2":"Olaf","3":"Galio","4":"TwistedFate","5":"XinZhao","6":"Urgot","7":"Leblanc","8":"Vladimir","9":"Fiddlesticks","10":"Kayle","11":"MasterYi","12":"Alistar","13":"Ryze","14":"Sion","15":"Sivir","16":"Soraka","17":"Teemo","18":"Tristana","19":"Warwick","20":"Nunu","21":"MissFortune","22":"Ashe","23":"Tryndamere","24":"Jax","25":"Morgana","26":"Zilean","27":"Singed","28":"Evelynn","29":"Twitch","30":"Karthus","31":"Chogath","32":"Amumu","33":"Rammus","34":"Anivia","35":"Shaco","36":"DrMundo","37":"Sona","38":"Kassadin","39":"Irelia","40":"Janna","41":"Gangplank","42":"Corki","43":"Karma","44":"Taric","45":"Veigar","48":"Trundle","50":"Swain","51":"Caitlyn","53":"Blitzcrank","54":"Malphite","55":"Katarina","56":"Nocturne","57":"Maokai","58":"Renekton","59":"JarvanIV","60":"Elise","61":"Orianna","62":"MonkeyKing","63":"Brand","64":"LeeSin","67":"Vayne","68":"Rumble","69":"Cassiopeia","72":"Skarner","74":"Heimerdinger","75":"Nasus","76":"Nidalee","77":"Udyr","78":"Poppy","79":"Gragas","80":"Pantheon","81":"Ezreal","82":"Mordekaiser","83":"Yorick","84":"Akali","85":"Kennen","86":"Garen","89":"Leona","90":"Malzahar","91":"Talon","92":"Riven","96":"KogMaw","98":"Shen","99":"Lux","101":"Xerath","102":"Shyvana","103":"Ahri","104":"Graves","105":"Fizz","106":"Volibear","107":"Rengar","110":"Varus","111":"Nautilus","112":"Viktor","113":"Sejuani","114":"Fiora","115":"Ziggs","117":"Lulu","119":"Draven","120":"Hecarim","121":"Khazix","122":"Darius","126":"Jayce","127":"Lissandra","131":"Diana","133":"Quinn","134":"Syndra","136":"AurelionSol","141":"Kayn","142":"Zoe","143":"Zyra","145":"Kaisa","150":"Gnar","154":"Zac","157":"Yasuo","161":"Velkoz","163":"Taliyah","164":"Camille","201":"Braum","202":"Jhin","203":"Kindred","222":"Jinx","223":"TahmKench","235":"Senna","236":"Lucian","238":"Zed","240":"Kled","245":"Ekko","246":"Qiyana","254":"Vi","266":"Aatrox","267":"Nami","268":"Azir","350":"Yuumi","412":"Thresh","420":"Illaoi","421":"RekSai","427":"Ivern","429":"Kalista","432":"Bard","497":"Rakan","498":"Xayah","516":"Ornn","517":"Sylas","518":"Neeko","523":"Aphelios","555":"Pyke"}'
champJSON = json.loads(champS)

masteryRow = '<tr><th scope="row">%NR</th><td>%CHAMP</td><td>%LEVEL</td><td>%POINTS</td></tr>'
mostPlayedRow = '<tr><th scope="row">%NR</th><td>%CHAMP</td><td>%AMOUNT</td></tr>'

def getChampionName(id):
    return champJSON[str(id)]

def displayLoadingbar(current, max, message, done=False, length=50):
    if done or current == max:
        print("\r[" + "=" * length + "] " + message + " [" + str(current) + "/" + str(max) + "]")
    else:
        print("\r[" + "=" * round((current/max)*length) + "." * round(length-((current/max)*length)) + "] " + message + " [" + str(current) + "/" + str(max) + "]", end="")

def export(players):
    workbook = xlsxwriter.Workbook('result-' + str(math.floor(time.time())) + '.xlsx')
    worksheet = workbook.add_worksheet()

    worksheet.write(2, 0, "Level:")
    worksheet.write(4, 0, "Top 5 Mastery Champions:")
    worksheet.write(10, 0, "Analyzed matches:")
    worksheet.write(12, 0, "Toplane%")
    worksheet.write(13, 0, "Jungle%")
    worksheet.write(14, 0, "Midlane%")
    worksheet.write(15, 0, "ADC%")
    worksheet.write(16, 0, "Support%")
    worksheet.write(18, 0, "Most played champions: ")
    worksheet.write(24, 0, "Average KDA:")
    worksheet.write(25, 0, "Winrate:")
    worksheet.write(28, 0, "Solo/Duo Rank")
    worksheet.write(29, 0, "Flex Rank")

    col = 1

    for player in players:
        worksheet.write(0, col, player.getSummonerName())
        worksheet.write(2, col, player.getSummonerLevel())

        row = 4
        for champ in player.getTop5Mastery():
            worksheet.write(row, col, getChampionName(champ["championId"]))
            worksheet.write(row, col+1, str(champ["championPoints"]))
            worksheet.write(row, col+2, "Lvl " + str(champ["championLevel"]))
            row += 1
        
        worksheet.write(10, col, player.getAnalyzedMatches())
        worksheet.write(12, col, round(player.getToplanePercent(), 1))
        worksheet.write(13, col, round(player.getJunglePercent(), 1))
        worksheet.write(14, col, round(player.getMidlanePercent(), 1))
        worksheet.write(15, col, round(player.getAdcPercent(), 1))
        worksheet.write(16, col, round(player.getSupportPercent(), 1))

        row = 18
        mPC = player.getMostPlayedChampions()
        top1 = {"champ": 0, "amount": 0}
        top2 = {"champ": 0, "amount": 0}
        top3 = {"champ": 0, "amount": 0}
        top4 = {"champ": 0, "amount": 0}
        top5 = {"champ": 0, "amount": 0}
        for champ in mPC:
            if mPC[champ] > top1["amount"]:
                top1["champ"] = champ
                top1["amount"] = mPC[champ]
            elif mPC[champ] > top2["amount"]:
                top2["champ"] = champ
                top2["amount"] = mPC[champ]
            elif mPC[champ] > top3["amount"]:
                top3["champ"] = champ
                top3["amount"] = mPC[champ]
            elif mPC[champ] > top4["amount"]:
                top4["champ"] = champ
                top4["amount"] = mPC[champ]
            elif mPC[champ] > top5["amount"]:
                top5["champ"] = champ
                top5["amount"] = mPC[champ]
        top5Champs = [top1, top2, top3, top4, top5]
        for champ in top5Champs:
            worksheet.write(row, col, getChampionName(champ["champ"]))
            worksheet.write(row, col+1, str(champ["amount"]) + " times played")
            row += 1

        k, d, a = player.getAvgKDA()
        worksheet.write(24, col, str(round(k, 1)) + "/" + str(round(d, 1)) + "/" + str(round(a, 1)))
        worksheet.write(25, col, round(player.getWinRate()))

        solo_rank, solo_points = player.getSoloDuoRank()
        solo_wr = player.getSoloDuoWR()
        flex_rank, flex_points = player.getFlexRank()
        flex_wr = player.getFlexWR()
        worksheet.write(28, col, solo_rank)
        worksheet.write(28, col+1, str(solo_points) + " LP")
        worksheet.write(28, col+2, solo_wr)
        worksheet.write(29, col, flex_rank)
        worksheet.write(29, col+1, str(flex_points) + " LP")
        worksheet.write(29, col+2, flex_wr)

        col += 3

    worksheet.set_column(0, 0, 25)
    worksheet.set_column(1, 1, 19)
    worksheet.set_column(4, 4, 19)
    worksheet.set_column(7, 7, 19)
    worksheet.set_column(10, 10, 19)
    worksheet.set_column(13, 13, 19)

    workbook.close()

def exportHTML(players):
    f = open("template.html")
    newlines = []

    masteryStrings = []
    for player in players:
        index = 1
        masterTmp = ""
        for mastery in player.getMastery():
            tmp = masteryRow
            tmp = tmp.replace("%NR", str(index))
            tmp = tmp.replace("%CHAMP", getChampionName(mastery["championId"]))
            tmp = tmp.replace("%LEVEL", str(mastery["championLevel"]))
            tmp = tmp.replace("%POINTS", str(mastery["championPoints"]))
            masterTmp += tmp
            index += 1
        masteryStrings.append(masterTmp)
    
    mostPlayedStrings = []
    for player in players:
        index = 1
        masterTmp = ""
        sortedChamps = OrderedDict(sorted(player.getMostPlayedChampions().items(), key=lambda item: item[1], reverse=True))
        for key in sortedChamps:
            tmp = mostPlayedRow
            tmp = tmp.replace("%NR", str(index))
            tmp = tmp.replace("%CHAMP", getChampionName(key))
            tmp = tmp.replace("%AMOUNT", str(sortedChamps[key]))
            masterTmp += tmp
            index += 1
        mostPlayedStrings.append(masterTmp)

    for line in f.readlines():
        index = 1
        for player in players:
            line = line.replace("%LEVEL-P" + str(index), str(player.getSummonerLevel()))
            line = line.replace("%WR-P" + str(index), str(round(player.getWinRate(), 1)) + "%")

            k1, d1, a1 = player.getAvgKDA()
            line = line.replace("%KDA-P" + str(index), str(round(k1, 1)) + "/" + str(round(d1, 1)) + "/" + str(round(a1, 1)))
            sd1, sd1p = player.getSoloDuoRank()
            line = line.replace("%SD-P" + str(index), sd1 + " " + str(sd1p) + " LP")
            line = line.replace("%WR-SD-P" + str(index), str(player.getSoloDuoWR()) + "%")
            flex1, flex1p = player.getFlexRank()
            line = line.replace("%FLEX-P" + str(index), flex1 + " " + str(flex1p) + " LP")
            line = line.replace("%WR-FLEX-P" + str(index), str(player.getFlexWR()) + "%")

            line = line.replace("%P" + str(index) + "-MASTERY", masteryStrings[index-1])
            line = line.replace("%P" + str(index) + "-MOSTPLAYED", mostPlayedStrings[index-1])

            line = line.replace("%P" + str(index) + "-TOP", str(round(player.getToplanePercent(), 1)))
            line = line.replace("%P" + str(index) + "-JNG", str(round(player.getJunglePercent(), 1)))
            line = line.replace("%P" + str(index) + "-MID", str(round(player.getMidlanePercent(), 1)))
            line = line.replace("%P" + str(index) + "-ADC", str(round(player.getAdcPercent(), 1)))
            line = line.replace("%P" + str(index) + "-SUP", str(round(player.getSupportPercent(), 1)))

            line = line.replace("%P" + str(index), player.getSummonerName())
            index += 1
        newlines.append(line)
    f = open("result-" + str(math.floor(time.time())) + ".html", "wb")
    for line in newlines:
        f.write(line.encode('utf-8'))
    f.close()

def exportStringHTML(players):
    f = open("template.html")
    result = ""

    masteryStrings = []
    for player in players:
        index = 1
        masterTmp = ""
        for mastery in player.getMastery():
            tmp = masteryRow
            tmp = tmp.replace("%NR", str(index))
            tmp = tmp.replace("%CHAMP", getChampionName(mastery["championId"]))
            tmp = tmp.replace("%LEVEL", str(mastery["championLevel"]))
            tmp = tmp.replace("%POINTS", str(mastery["championPoints"]))
            masterTmp += tmp
            index += 1
        masteryStrings.append(masterTmp)
    
    mostPlayedStrings = []
    for player in players:
        index = 1
        masterTmp = ""
        sortedChamps = OrderedDict(sorted(player.getMostPlayedChampions().items(), key=lambda item: item[1], reverse=True))
        for key in sortedChamps:
            tmp = mostPlayedRow
            tmp = tmp.replace("%NR", str(index))
            tmp = tmp.replace("%CHAMP", getChampionName(key))
            tmp = tmp.replace("%AMOUNT", str(sortedChamps[key]))
            masterTmp += tmp
            index += 1
        mostPlayedStrings.append(masterTmp)

    for line in f.readlines():
        index = 1
        for player in players:
            line = line.replace("%LEVEL-P" + str(index), str(player.getSummonerLevel()))
            line = line.replace("%WR-P" + str(index), str(round(player.getWinRate(), 1)) + "%")

            k1, d1, a1 = player.getAvgKDA()
            line = line.replace("%KDA-P" + str(index), str(round(k1, 1)) + "/" + str(round(d1, 1)) + "/" + str(round(a1, 1)))
            sd1, sd1p = player.getSoloDuoRank()
            line = line.replace("%SD-P" + str(index), sd1 + " " + str(sd1p) + " LP")
            line = line.replace("%WR-SD-P" + str(index), str(player.getSoloDuoWR()) + "%")
            flex1, flex1p = player.getFlexRank()
            line = line.replace("%FLEX-P" + str(index), flex1 + " " + str(flex1p) + " LP")
            line = line.replace("%WR-FLEX-P" + str(index), str(player.getFlexWR()) + "%")

            line = line.replace("%P" + str(index) + "-MASTERY", masteryStrings[index-1])
            line = line.replace("%P" + str(index) + "-MOSTPLAYED", mostPlayedStrings[index-1])

            line = line.replace("%P" + str(index) + "-TOP", str(round(player.getToplanePercent(), 1)))
            line = line.replace("%P" + str(index) + "-JNG", str(round(player.getJunglePercent(), 1)))
            line = line.replace("%P" + str(index) + "-MID", str(round(player.getMidlanePercent(), 1)))
            line = line.replace("%P" + str(index) + "-ADC", str(round(player.getAdcPercent(), 1)))
            line = line.replace("%P" + str(index) + "-SUP", str(round(player.getSupportPercent(), 1)))
            line = line.replace("%P" + str(index) + "-GAMES", str(player.getAnalyzedMatches()))

            line = line.replace("%P" + str(index), player.getSummonerName())
            index += 1
        result += line
    return result

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