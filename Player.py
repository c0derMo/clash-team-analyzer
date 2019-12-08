import time

class Player():

    def setSummonerInfo(self, sinfo):
        self.summonerInfo = sinfo

    def setMasteryInfo(self, minfo):
        self.masteryInfo = minfo
    
    def setMatchlist(self, mlist):
        self.matchlist = mlist
        self.unanalyzedMatches = []
        self.analyzedMatches = []
        for match in mlist["matches"]:
            self.unanalyzedMatches.append(match["gameId"])
    
    def setMatchInfo(self, matchId, mInfo):
        self.unanalyzedMatches.remove(matchId)
        self.analyzedMatches.append(mInfo)
    
    def setLeagueInfo(self, linfo):
        self.leagueInfo = linfo

    def getEncryptedSummonerId(self):
        return self.summonerInfo["id"]
    
    def getSummonerName(self):
        return self.summonerInfo["name"]
    
    def getTop5Mastery(self):
        return [self.masteryInfo[0], self.masteryInfo[1], self.masteryInfo[2], self.masteryInfo[3], self.masteryInfo[4]]
    
    def getLastModify(self):
        return time.strftime('%d/%m/%Y %H:%M:%S', time.gmtime(self.summonerInfo["revisionDate"]/1000.))
    
    def getEncryptedAccountId(self):
        return self.summonerInfo["accountId"]
    
    def getToplanePercent(self):
        topmatches = 0
        for match in self.matchlist["matches"]:
            if match["lane"] == "TOP":
                topmatches += 1
        return (topmatches / self.matchlist["matches"].__len__()) * 100
    
    def getMidlanePercent(self):
        topmatches = 0
        for match in self.matchlist["matches"]:
            if match["lane"] == "MID":
                topmatches += 1
        return (topmatches / self.matchlist["matches"].__len__()) * 100
        
    def getAdcPercent(self):
        topmatches = 0
        for match in self.matchlist["matches"]:
            if match["lane"] == "BOTTOM" and match["role"] == "DUO_CARRY":
                topmatches += 1
        return (topmatches / self.matchlist["matches"].__len__()) * 100
    
    def getSupportPercent(self):
        topmatches = 0
        for match in self.matchlist["matches"]:
            if match["lane"] == "BOTTOM" and match["role"] == "DUO_SUPPORT":
                topmatches += 1
        return (topmatches / self.matchlist["matches"].__len__()) * 100
    
    def getJunglePercent(self):
        topmatches = 0
        for match in self.matchlist["matches"]:
            if match["lane"] == "JUNGLE":
                topmatches += 1
        return (topmatches / self.matchlist["matches"].__len__()) * 100
    
    def getAnalyzedMatches(self):
        return self.analyzedMatches.__len__()

    def getMaxMatches(self):
        return self.matchlist["matches"].__len__()

    def getMostPlayedChampions(self):
        champs = {}
        for match in self.matchlist["matches"]:
            if match["champion"] in champs:
                champs[match["champion"]] += 1
            else:
                champs[match["champion"]] = 1
        top1 = {"champ": 0, "amount": 0}
        top2 = {"champ": 0, "amount": 0}
        top3 = {"champ": 0, "amount": 0}
        top4 = {"champ": 0, "amount": 0}
        top5 = {"champ": 0, "amount": 0}
        for champ in champs:
            if champs[champ] > top1["amount"]:
                top1["champ"] = champ
                top1["amount"] = champs[champ]
            elif champs[champ] > top2["amount"]:
                top2["champ"] = champ
                top2["amount"] = champs[champ]
            elif champs[champ] > top3["amount"]:
                top3["champ"] = champ
                top3["amount"] = champs[champ]
            elif champs[champ] > top4["amount"]:
                top4["champ"] = champ
                top4["amount"] = champs[champ]
            elif champs[champ] > top5["amount"]:
                top5["champ"] = champ
                top5["amount"] = champs[champ]
        return [top1, top2, top3, top4, top5]
    
    def getMatchToAnalyze(self):
        if self.unanalyzedMatches.__len__() > 0:
            return self.unanalyzedMatches[0]
        else:
            return -1
    
    def getAvgKDA(self):
        pID = 0
        kills = 0
        deaths = 0
        assists = 0

        if self.analyzedMatches.__len__() == 0:
            return 0, 0, 0

        for match in self.analyzedMatches:
            for participantIdentitiy in match["participantIdentities"]:
                if participantIdentitiy["player"]["summonerName"] == self.summonerInfo["name"]:
                    pID = participantIdentitiy["participantId"]
                    break
            for stats in match["participants"]:
                if stats["participantId"] == pID:
                    kills += stats["stats"]["kills"]
                    deaths += stats["stats"]["deaths"]
                    assists += stats["stats"]["assists"]
                break
        
        kills = kills/self.getAnalyzedMatches()
        deaths = deaths/self.getAnalyzedMatches()
        assists = assists/self.getAnalyzedMatches()

        return kills, deaths, assists
    
    def getFirstBloodPercent(self):
        pID = 0
        fb = 0

        if self.getAnalyzedMatches() == 0:
            return 0

        for match in self.analyzedMatches:
            for participantIdentitiy in match["participantIdentities"]:
                if participantIdentitiy["player"]["summonerName"] == self.summonerInfo["name"]:
                    pID = participantIdentitiy["participantId"]
                    break
            for stats in match["participants"]:
                if stats["participantId"] == pID:
                    if stats["stats"]["firstBloodKill"]:
                        fb += 1
        
        fb = fb/self.getAnalyzedMatches()

        return fb*100
    
    def getWinRate(self):
        pID = 0
        wins = 0

        if self.getAnalyzedMatches() == 0:
            return 0

        for match in self.analyzedMatches:
            for participantIdentitiy in match["participantIdentities"]:
                if participantIdentitiy["player"]["summonerName"] == self.summonerInfo["name"]:
                    pID = participantIdentitiy["participantId"]
                    break
            for stats in match["participants"]:
                if stats["participantId"] == pID:
                    if stats["stats"]["win"]:
                        wins += 1
        
        wins = wins/self.getAnalyzedMatches()

        return wins*100
    
    def getSoloDuoRank(self):
        for queue in self.leagueInfo:
            if queue["queueType"] == "RANKED_SOLO_5x5":
                return queue["tier"] + " " + queue["rank"], queue["leaguePoints"]
        return "UNRANKED", 0
    
    def getFlexRank(self):
        for queue in self.leagueInfo:
            if queue["queueType"] == "RANKED_FLEX_SR":
                return queue["tier"] + " " + queue["rank"], queue["leaguePoints"]
        return "UNRANKED", 0
    
    def getSoloDuoWR(self):
        for queue in self.leagueInfo:
            if queue["queueType"] == "RANKED_SOLO_5x5":
                return round((queue["wins"]/queue["wins"]+queue["losses"])*100)
        return 0
    
    def getFlexWR(self):
        for queue in self.leagueInfo:
            if queue["queueType"] == "RANKED_FLEX_SR":
                return round((queue["wins"]/queue["wins"]+queue["losses"])*100)
        return 0