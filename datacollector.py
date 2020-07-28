#!/usr/bin/env python3
# Sound Voltex Song Data Collector
# Scrapes Remiwiki for compiling information about Sound Voltex songs

import requests
import json

#########
# Get list of songs
#########

page = requests.get("https://remywiki.com/api.php?action=query&format=json&list=categorymembers&cmtitle=Category:SOUND_VOLTEX_Songs")
print(page.status_code)
print(page.content)

#json_data = json.loads(response_message)

# parse json for song list

#print(json_data['categorymembers'])

# get cmcontinue value

# run same string with cmcontinue value to get additional songs

#########
# Get song data
#########

# https://remywiki.com/api.php?action=query&format=json&prop=revisions&rvprop=content&rvslots=main&titles=%22Coconatsu%22%20wa%20yume%20no%20katachi