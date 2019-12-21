from sanic import Sanic
from sanic.response import html, redirect, text, raw
from sanic.log import logger
import analyzor
import asyncio
import socketio
import os
import glob
import util
import time
from sanic_jinja2 import SanicJinja2
import config

sio = socketio.AsyncServer(async_mode='sanic')
app = Sanic()
sio.attach(app)
jinja = SanicJinja2(app)


lastClearMatches = 0
lastClearEverything = 0

app.static("/assets", "./assets")

async def clearDB():
    global lastClearMatches, lastClearEverything
    currentTime = time.time()
    if currentTime - lastClearEverything > 7200:
        logger.info("Clearing cache of league, masterys, matchlists and players...")
        files = glob.glob("cache/league/*")
        files += glob.glob("cache/masterys/*")
        files += glob.glob("cache/matchlists/*")
        files += glob.glob("cache/players/*")
        for f in files:
            os.remove(f)
        lastClearEverything = currentTime
    if currentTime - lastClearMatches > 86400:
        logger.info("Clearing cache of matches...")
        files = glob.glob("cache/matches/*")
        for f in files:
            os.remove(f)
        lastClearMatches = currentTime

@app.route('/')
async def main(request):
    asyncio.create_task(util.addPageAnalytic("/"))
    asyncio.create_task(clearDB())
    if hasValidKey:
        fn ="index.html"
    else:
        fn = "indexdemo.html"
    with open('templates/' + fn) as f:
        return html(f.read())

@app.route('/team')
async def getTeam(request):
    asyncio.create_task(util.addPageAnalytic("/team"))
    asyncio.create_task(clearDB())
    if "p1" not in request.args or "p2" not in request.args or "p3" not in request.args or "p4" not in request.args or "p5" not in request.args:
        return redirect("/")
    playerOBJs = util.loadPlayersFromCache(request.args["p1"][0], request.args["p2"][0], request.args["p3"][0], request.args["p4"][0], request.args["p5"][0])
    if playerOBJs == -1:
        return redirect("/")
    else:
        mightBeHTML = util.exportStringHTML(playerOBJs)
        return html(mightBeHTML)

@app.route('/demodata')
async def getDemoData(request):
    asyncio.create_task(util.addPageAnalytic("/demodata"))
    asyncio.create_task(clearDB())
    with open('templates/demodata.html', encoding="utf-8") as f:
        return html(f.read())

@app.route('/favicon.ico')
async def getFavicon(request):
    return raw(b"")

@app.route('/statistics')
async def getStatistics(request):
    if "date" not in request.args:
        dataX = util.getStatistics()
    else:
        dataX = util.getStatistics(request.args["date"][0])
    return jinja.render("statistics.html", request, data=dataX)

@sio.event
async def analyzeStart(sid, message):
    asyncio.create_task(util.addStatAnalyze())
    asyncio.create_task(analyzor.analyzeWrap(message, sid, sio, logger))

if __name__ == '__main__':
    hasValidKey = analyzor.hasValidAPIKey()
    if hasValidKey:
        logger.info("We've got a valid API-Key. Full functionality.")
    else:
        logger.warning("! We've got no valid API-Key! Limited functionality. !")

    if not util.getChampInfo():
        logger.error("! We could not get up-to-date champ information from the Data Dragon !")
    
    try:
        config.Config.readConfig()
    except FileNotFoundError:
        logger.error("! No config file was found! Standard development-configuration loaded. !")
        config.Config.loadDefaultConfig()
    finally:
        logger.info("Current configuration:")
        logger.info("Key-Type: " + config.Config.getAPIType())
        if config.Config.getAPIType() == "production":
            logger.info("Ratelimit per 10 seconds: " + str(config.Config.getRateLimitPer10Seconds()))
            logger.info("Ratelimit per 10 minutes: " + str(config.Config.getRateLimitPer10Minutes()))
        elif config.Config.getAPIType() == "dev":
            logger.info("Ratelimit per 1 second: " + str(config.Config.getRateLimitPerSecond()))
            logger.info("Ratelimit per 2 minutes: " + str(config.Config.getRateLimitPer2Minutes()))
        else:
            logger.warning("Couldn't read API-Key-Type! Using development-settings...")
            logger.info("Ratelimit per 1 second: " + str(config.Config.getRateLimitPerSecond()))
            logger.info("Ratelimit per 2 minutes: " + str(config.Config.getRateLimitPer2Minutes()))
        logger.info("Matches to analyze per player: " + str(config.Config.getMatchCountToAnalyze()))

    app.run()