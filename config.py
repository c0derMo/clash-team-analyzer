# THIS IS THE INTERFACE-FILE TO THE CONFIG-FILE
# DO NOT EDIT THIS!
# EDIT config.json

import json

fileRead = False
cfg = {}

class Config:
    def loadDefaultConfig():
        global cfg
        global fileRead
        cfg["keyType"] = "dev"
        cfg["rateLimits"]["perSecond"] = 20
        cfg["rateLimits"]["per2Minutes"] = 100
        cfg["matchesToAnalyze"] = 20

    def readConfig():
        global cfg
        global fileRead
        with open("config.json") as f:
            cfg = json.loads(f.read())
            fileRead = True

    def getAPIType():
        global cfg
        global fileRead
        if not fileRead:
            readConfig()
        return cfg["keyType"]

    def getRateLimitPerSecond():
        global cfg
        global fileRead
        if not fileRead:
            readConfig()
        return cfg["rateLimits"]["perSecond"]

    def getRateLimitPer2Minutes():
        global cfg
        global fileRead
        if not fileRead:
            readConfig()
        return cfg["rateLimits"]["per2Minutes"]

    def getRateLimitPer10Seconds():
        global cfg
        global fileRead
        if not fileRead:
            readConfig()
        return cfg["rateLimits"]["per10Seconds"]

    def getRateLimitPer10Minutes():
        global cfg
        global fileRead
        if not fileRead:
            readConfig()
        return cfg["rateLimits"]["per10Minutes"]

    def getMatchCountToAnalyze():
        global cfg
        global fileRead
        if not fileRead:
            readConfig()
        return cfg["matchesToAnalyze"]