import requests
import time
import json
from dotenv import load_dotenv
import os
import Player
import util
import xlsxwriter

load_dotenv()

requestsDuringLastSecond = []
requestsDuringLastTwoMinutes = []

host = "https://euw1.api.riotgames.com"
api_key = os.getenv("API_KEY")

def query(endpoint, additional_arguments=""):
    while(requestsDuringLastSecond.__len__() > 19 or requestsDuringLastTwoMinutes.__len__() > 99):
        for request in requestsDuringLastSecond:
            if time.time()-request > 1:
                requestsDuringLastSecond.remove(request)
        for request in requestsDuringLastTwoMinutes:
            if time.time()-request > 120:
                requestsDuringLastTwoMinutes.remove(request)
    requestsDuringLastSecond.append(time.time())
    requestsDuringLastTwoMinutes.append(time.time())
    response = requests.get(host + endpoint + "?api_key=" + api_key + additional_arguments)
    return response.status_code, json.loads(response.text)

if __name__ == "__main__":
    print("Welcome to c0M's Clash Team Analyzer!")
    print("v0.1")
    print("Please enter the names of all your enemies:")
    players = []
    playerOBJs = []
    # players.append(input("P1>"))
    # players.append(input("P2>"))
    # players.append(input("P3>"))
    # players.append(input("P4>"))
    # players.append(input("P5>"))
    players = ["Senôr Aυtism", "Inselsüchtiger", "Quanox", "Rechtsklickquell", "nvq2015"]
    print("Thanks!")
    print("[....................] Quering summoner information...       ", end="")
    for player in players:
        code, response = query("/lol/summoner/v4/summoners/by-name/" + player)
        if code != 200:
            print("Something went wrong during requesting " + player)
        else:
            plOBJ = Player.Player()
            plOBJ.setSummonerInfo(response)
            playerOBJs.append(plOBJ)
    print("\r[=...................] Quering champion mastery...         ", end="")
    for player in playerOBJs:
        code, response = query("/lol/champion-mastery/v4/champion-masteries/by-summoner/" + player.getEncryptedSummonerId())
        if code != 200:
            print("Something went wrong during requesting mastery for " + player.getSummonerName())
        else:
            player.setMasteryInfo(response)
    
    print("\r[==..................] Quering matchlists...               ", end="")
    for player in playerOBJs:
        code, response = query("/lol/match/v4/matchlists/by-account/" + player.getEncryptedAccountId(), "&endIndex=30")
        if code != 200:
            print("Something went wrong during requesting matchlists for " + player.getSummonerName())
        else:
            player.setMatchlist(response)
    print("\r[====================] Done!                               ")

    util.export(playerOBJs)