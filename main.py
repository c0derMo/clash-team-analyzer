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

sio = socketio.AsyncServer(async_mode='sanic')
app = Sanic()
sio.attach(app)

lastClearMatches = 0
lastClearEverything = 0

app.static("/assets", "./assets")

hasValidKey = analyzor.hasValidAPIKey()
if hasValidKey:
    logger.info("We've got a valid API-Key. Full functionality.")
else:
    logger.warn("! We've got no valid API-Key! Limited functionality. !")

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
    asyncio.create_task(clearDB())
    if hasValidKey:
        fn ="index.html"
    else:
        fn = "indexdemo.html"
    with open('templates/' + fn) as f:
        return html(f.read())

@app.route('/team')
async def getTeam(request):
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
    asyncio.create_task(clearDB())
    with open('templates/demodata.html', encoding="utf-8") as f:
        return html(f.read())

@app.route('/favicon.ico')
async def getFavicon(request):
    return raw()

@sio.event
async def analyzeStart(sid, message):
    asyncio.create_task(analyzor.analyzeWrap(message, sid, sio))

if __name__ == '__main__':
    app.run()