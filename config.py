# THIS IS THE INTERFACE-FILE TO THE CONFIG-FILE
# DO NOT EDIT THIS!
# EDIT config.json

import json

cfg = {}
fileRead = False

def loadDefaultConfig():
    cfg["keyType"] = "dev"
    cfg["rateLimits"] = {}
    cfg["rateLimits"]["perSecond"] = 20
    cfg["rateLimits"]["per2Minutes"] = 100
    cfg["matchesToAnalyze"] = 20
    cfg["hostname"] = "127.0.0.1"
    cfg["port"] = 8000

def readConfig():
    global cfg
    global fileRead
    with open("config.json") as f:
        cfg = json.loads(f.read())
        fileRead = True

def getAPIType():
    if not fileRead:
        readConfig()
    return cfg["keyType"]

def getRateLimitPerSecond():
    if not fileRead:
        readConfig()
    return cfg["rateLimits"]["perSecond"]

def getRateLimitPer2Minutes():
    if not fileRead:
        readConfig()
    return cfg["rateLimits"]["per2Minutes"]

def getRateLimitPer10Seconds():
    if not fileRead:
        readConfig()
    return cfg["rateLimits"]["per10Seconds"]

def getRateLimitPer10Minutes():
    if not fileRead:
        readConfig()
    return cfg["rateLimits"]["per10Minutes"]

def getMatchCountToAnalyze():
    if not fileRead:
        readConfig()
    return cfg["matchesToAnalyze"]

def getHostname():
    if not fileRead:
        readConfig()
    return cfg["hostname"]

def getPort():
    if not fileRead:
        readConfig()
    return cfg["port"]