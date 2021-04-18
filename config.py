# THIS IS THE INTERFACE-FILE TO THE CONFIG-FILE
# DO NOT EDIT THIS!
# EDIT config.json

import json

class Config:
    def loadDefaultConfig(self):
        self.cfg = {}
        self.fileRead = False
        self.cfg["keyType"] = "dev"
        self.cfg["rateLimits"] = {}
        self.cfg["rateLimits"]["perSecond"] = 20
        self.cfg["rateLimits"]["per2Minutes"] = 100
        self.cfg["matchesToAnalyze"] = 20
        self.cfg["hostname"] = "127.0.0.1"
        self.cfg["port"] = 8000

    def readConfig(self):
        with open("config.json") as f:
            self.cfg = json.loads(f.read())
            self.fileRead = True

    def getAPIType(self):
        if not self.fileRead:
            self.readConfig()
        return self.cfg["keyType"]

    def getRateLimitPerSecond(self):
        if not self.fileRead:
            self.readConfig()
        return self.cfg["rateLimits"]["perSecond"]

    def getRateLimitPer2Minutes(self):
        if not self.fileRead:
            self.readConfig()
        return self.cfg["rateLimits"]["per2Minutes"]

    def getRateLimitPer10Seconds(self):
        if not self.fileRead:
            self.readConfig()
        return self.cfg["rateLimits"]["per10Seconds"]

    def getRateLimitPer10Minutes(self):
        if not self.fileRead:
            self.readConfig()
        return self.cfg["rateLimits"]["per10Minutes"]

    def getMatchCountToAnalyze(self):
        if not self.fileRead:
            self.readConfig()
        return self.cfg["matchesToAnalyze"]
    
    def getHostname(self):
        if not self.fileRead:
            self.readConfig()
        return self.cfg["hostname"]
    
    def getPort(self):
        if not self.fileRead:
            self.readConfig()
        return self.cfg["port"]