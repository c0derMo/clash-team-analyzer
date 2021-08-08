# Clash-Team-Analyzer

A webapp to analyze League of Legends-Clash-Teams, written in Python.

> **With the release of the match-v5 API and the deprecation of match-v4, this app is deprecated aswell.**

## Usage / Setup

~~To use the webhosted version of this project, to to clash.currymaker.net.~~

_With the deprecation of this project, there no longer is a webhosted version._

## Features

This project automaticly analyzes teams of 5 people using the supplied summoner-names. It automaticly caches their...

- general summoner info
- matchhistory of the last 30 days
- mastery information
- league / elo information
- detailed information about their last 20 games

Cached details will be deleted after 2 hours, cached games will be deleted after one day.

Using those cached informations, this tool will tell you for each player...

- their most played position in the last 30 days
- their winrate and average kda of the last 20 games
- ranks & elo
- champion levels and points
- most played champions in the last 30 days
- List how many games they have played together

### Planned features:

- Winrates based on role
