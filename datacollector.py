#!/usr/bin/env python3
# Sound Voltex Song Data Collector
# Scrapes Remiwiki for compiling information about Sound Voltex songs

import requests
import json

# Hardcoded name of SDVX Song List page
# You can change this if the page name changes
sdvx_song_page = "Category:SOUND_VOLTEX_Songs"

# Method for recursively searching a complex JSON tree
# for a specific key that may be nested
# Source: https://hackersandslackers.com/extract-data-from-complex-json-python/
def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results

#########
# Get list of songs
#########

# This is split into multiple lines to make it (hopefully) easier to read
page = requests.get("https://remywiki.com/api.php" \
					+ "?action=query" \
					+ "&format=json" \
					+ "&list=categorymembers" \
					+ "&cmtitle=" + sdvx_song_page)

print("Return status code: " + str(page.status_code))

json_data = json.loads(page.content)

# parse json for song list
songs = extract_values(json_data, 'pageid')

print(songs)

while "cmcontinue" in json_data:
	sleep(1)
	#get cmcontinue value
	#run same string with cmcontinue value to get additional songs

#########
# Get song data
#########

# https://remywiki.com/api.php?action=query&format=json&prop=revisions&rvprop=content&rvslots=main&titles=%22Coconatsu%22%20wa%20yume%20no%20katachi