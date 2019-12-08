import json
import xlsxwriter
import time
import math

champS = '{"1":"Annie","2":"Olaf","3":"Galio","4":"TwistedFate","5":"XinZhao","6":"Urgot","7":"Leblanc","8":"Vladimir","9":"Fiddlesticks","10":"Kayle","11":"MasterYi","12":"Alistar","13":"Ryze","14":"Sion","15":"Sivir","16":"Soraka","17":"Teemo","18":"Tristana","19":"Warwick","20":"Nunu","21":"MissFortune","22":"Ashe","23":"Tryndamere","24":"Jax","25":"Morgana","26":"Zilean","27":"Singed","28":"Evelynn","29":"Twitch","30":"Karthus","31":"Chogath","32":"Amumu","33":"Rammus","34":"Anivia","35":"Shaco","36":"DrMundo","37":"Sona","38":"Kassadin","39":"Irelia","40":"Janna","41":"Gangplank","42":"Corki","43":"Karma","44":"Taric","45":"Veigar","48":"Trundle","50":"Swain","51":"Caitlyn","53":"Blitzcrank","54":"Malphite","55":"Katarina","56":"Nocturne","57":"Maokai","58":"Renekton","59":"JarvanIV","60":"Elise","61":"Orianna","62":"MonkeyKing","63":"Brand","64":"LeeSin","67":"Vayne","68":"Rumble","69":"Cassiopeia","72":"Skarner","74":"Heimerdinger","75":"Nasus","76":"Nidalee","77":"Udyr","78":"Poppy","79":"Gragas","80":"Pantheon","81":"Ezreal","82":"Mordekaiser","83":"Yorick","84":"Akali","85":"Kennen","86":"Garen","89":"Leona","90":"Malzahar","91":"Talon","92":"Riven","96":"KogMaw","98":"Shen","99":"Lux","101":"Xerath","102":"Shyvana","103":"Ahri","104":"Graves","105":"Fizz","106":"Volibear","107":"Rengar","110":"Varus","111":"Nautilus","112":"Viktor","113":"Sejuani","114":"Fiora","115":"Ziggs","117":"Lulu","119":"Draven","120":"Hecarim","121":"Khazix","122":"Darius","126":"Jayce","127":"Lissandra","131":"Diana","133":"Quinn","134":"Syndra","136":"AurelionSol","141":"Kayn","142":"Zoe","143":"Zyra","145":"Kaisa","150":"Gnar","154":"Zac","157":"Yasuo","161":"Velkoz","163":"Taliyah","164":"Camille","201":"Braum","202":"Jhin","203":"Kindred","222":"Jinx","223":"TahmKench","235":"Senna","236":"Lucian","238":"Zed","240":"Kled","245":"Ekko","246":"Qiyana","254":"Vi","266":"Aatrox","267":"Nami","268":"Azir","350":"Yuumi","412":"Thresh","420":"Illaoi","421":"RekSai","427":"Ivern","429":"Kalista","432":"Bard","497":"Rakan","498":"Xayah","516":"Ornn","517":"Sylas","518":"Neeko","555":"Pyke"}'
champJSON = json.loads(champS)

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

    worksheet.write(2, 0, "Last modified:")
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
    worksheet.write(26, 0, "FirstBlood%")
    worksheet.write(28, 0, "Solo/Duo Rank")
    worksheet.write(29, 0, "Flex Rank")

    col = 1

    for player in players:
        worksheet.write(0, col, player.getSummonerName())
        worksheet.write(2, col, player.getLastModify())

        row = 4
        for champ in player.getTop5Mastery():
            worksheet.write(row, col, getChampionName(champ["championId"]))
            worksheet.write(row, col+1, str(champ["championPoints"]))
            worksheet.write(row, col+2, "Lvl " + str(champ["championLevel"]))
            row += 1
        
        worksheet.write(10, col, player.getAnalyzedMatches())
        worksheet.write(12, col, round(player.getToplanePercent()))
        worksheet.write(13, col, round(player.getJunglePercent()))
        worksheet.write(14, col, round(player.getMidlanePercent()))
        worksheet.write(15, col, round(player.getAdcPercent()))
        worksheet.write(16, col, round(player.getSupportPercent()))

        row = 18
        for champ in player.getMostPlayedChampions():
            worksheet.write(row, col, getChampionName(champ["champ"]))
            worksheet.write(row, col+1, str(champ["amount"]) + " times played")
            row += 1

        k, d, a = player.getAvgKDA()
        worksheet.write(24, col, str(round(k)) + "/" + str(round(d)) + "/" + str(round(a)))
        worksheet.write(25, col, round(player.getWinRate()))
        worksheet.write(26, col, round(player.getFirstBloodPercent()))

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