#!/usr/bin/env python3
# Sound Voltex Song Data Collector
# Scrapes RemyWiki for compiling information about Sound Voltex songs

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

# parse json for the list of song pageids
# for all additional page ids, we're going to use python's append() to add on to this list
song_page_ids = extract_values(json_data, 'pageid')

print(songs)

print(json_data['continue']['cmcontinue'])

# if 'cmcontinue' exists in our json data, that means there are more songs we need to fetch
# the api does this to break up big lists into bite-sized sections that you download one at
# a time, to save on bandwidth
try:
	while json_data['continue']['cmcontinue']:
		cmcontinue = json_data['continue']['cmcontinue']
		# cmcontinue value found, that means there are more songs we haven't gotten yet
		print("cmcontinue: " + cmcontinue)
		# generate a new request, this time including our cmcontinue value
		page = requests.get("https://remywiki.com/api.php" \
					+ "?action=query" \
					+ "&format=json" \
					+ "&list=categorymembers" \
					+ "&cmtitle=" + sdvx_song_page
					+ "&cmcontinue=" + cmcontinue)
		# parse page data as json
		json_data = json.loads(page.content)
		# append new song pageids to list
		song_page_ids.append(extract_values(json_data, 'pageid'))
		# sleep so we send requests slowly!
		time.sleep(1)
except:
	print("No \'cmcontinue\' value found, exiting loop.")
	#get cmcontinue value
	#run same string with cmcontinue value to get additional songs

#########
# Get song data
#########

# https://remywiki.com/api.php?action=query&format=json&prop=revisions&rvprop=content&rvslots=main&titles=%22Coconatsu%22%20wa%20yume%20no%20katachi