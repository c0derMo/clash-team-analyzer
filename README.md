# Clash-Team-Analyzer
A webapp to analyze League of Legends-Clash-Teams, written in Python.

## Usage / Setup
To use the webhosted version of this project, to to [clash.currymaker.net](http://clash.currymaker.net).

## Features
This project automaticly analyzes teams of 5 people using the supplied summoner-names. It automaticly caches their...
- general summoner info
- matchhistory of the last 30 days
- mastery information
- league / elo information
- detailed information about their last 20 games

Cached details will be deleted after 2 hours, cached games will be deleted after one day.

Using those cached informations, this tool will tell you for each player...
- their most played posision in the last 30 days
- their winrate and average kda of the last 20 games
- ranks & elo
- champion levels and points
- most played champions in the last 30 days

### Planned features:
- List how many games they have played together
- Winrates based on role