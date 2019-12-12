from sanic import Sanic
from sanic.response import html, redirect, text
import analyzor
import asyncio
import socketio
import os
import glob
import util

sio = socketio.AsyncServer(async_mode='sanic')
app = Sanic()
sio.attach(app)

@app.route('/')
async def main(request):
    with open('templates/index.html') as f:
        return html(f.read())

@app.route('/flush')
async def flush(request):
    files = glob.glob("cache/league/*")
    files += glob.glob("cache/masterys/*")
    files += glob.glob("cache/matches/*")
    files += glob.glob("cache/matchlists/*")
    files += glob.glob("cache/players/*")
    for f in files:
        os.remove(f)
    return text("Deleted.")

@app.route('/team')
async def getTeam(request):
    if "p1" not in request.args or "p2" not in request.args or "p3" not in request.args or "p4" not in request.args or "p5" not in request.args:
        return redirect("/")
    playerOBJs = util.loadPlayersFromCache(request.args["p1"][0], request.args["p2"][0], request.args["p3"][0], request.args["p4"][0], request.args["p5"][0])
    if playerOBJs == -1:
        return redirect("/")
    else:
        mightBeHTML = util.exportStringHTML(playerOBJs)
        return html(mightBeHTML)


@sio.event
async def analyzeStart(sid, message):
    asyncio.create_task(analyzor.analyzeWrap(message, sid, sio))

if __name__ == '__main__':
    app.run()