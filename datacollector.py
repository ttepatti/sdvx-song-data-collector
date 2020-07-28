#!/usr/bin/env python3
# Sound Voltex Song Data Collector
# Scrapes RemyWiki for compiling information about Sound Voltex songs

import requests
import json
import csv
import time

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

#########################
#   Get list of songs   #
#########################
def get_song_list():
	# This request is split into multiple lines to make it (hopefully) easier to read
	page = requests.get("https://remywiki.com/api.php" \
						+ "?action=query" \
						+ "&format=json" \
						+ "&list=categorymembers" \
						+ "&cmtitle=" + sdvx_song_page \
						+ "&cmlimit=500")

	# parse the returned page content as json data
	json_data = json.loads(page.content)

	# parse the json for the list of song pageids
	# for all additional page ids, we're going to use python's append() to add on to this list
	song_page_ids = extract_values(json_data, 'pageid')

	#### Now, we check for 'cmcontinue' and fetch any additional songs, appending them
	#### on to our inital list

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
						+ "&cmcontinue=" + cmcontinue \
						+ "&cmlimit=500")
			# parse page data as json
			json_data = json.loads(page.content)
			# append new song pageids to list
			song_page_ids.append(extract_values(json_data, 'pageid'))
			# sleep so we send requests slowly!
			time.sleep(1)
	except Exception as e:
		print(e)
		print("No \'cmcontinue\' value found, exiting loop.")
		#get cmcontinue value
		#run same string with cmcontinue value to get additional songs

	# Save the list of song page IDs to a CSV file for later processing
	with open("song_page_ids.csv", "w") as file:
		writer = csv.writer(file)
		writer.writerow("pageid")
		for pageid in song_page_ids:
			writer.writerow(str(pageid))
		file.close()

########################
#     Get song data    #
########################
def get_song_data(csvname):
	print(csvname)
	# The main goal here is to fetch the following:
	# song title
	# artist name
	# song bpm
	# any dates on the page (we're looking for the date it was added to the game)

	# https://remywiki.com/api.php?action=query&format=json&prop=revisions&rvprop=content&rvslots=main&titles=%22Coconatsu%22%20wa%20yume%20no%20katachi

def main():
	print("Please enter the number of what you'd like to do")
	print("________________________________________________")
	print("1 - Download pageids of all SDVX songs")
	print("2 - Use list of SDVX pageids to get song data")
	print("3 - Exit")
	user_input = input("> ")
	if user_input is "1":
		get_song_list()
	elif user_input is "2":
		print("Please input the name of your song pageid CSV")
		print("(Press enter to use default name: song_page_ids.csv)")
		user_input = input("> ")
		if len(user_input) is 0:
			user_input = "song_page_ids.csv"
		get_song_data(user_input)
	elif user_input is "3":
		exit()
	else:
		print("Invalid input. Exiting...")
		exit()

if __name__ == "__main__":
	main()