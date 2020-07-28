#!/usr/bin/env python3
# Sound Voltex Song Data Collector
# Scrapes RemyWiki for compiling information about Sound Voltex songs

# for connecting to the website
import requests

# for parsing json
import json

# for exporting as CSV
import csv

# for sleep()
import time

# use this for assembling the saved CSV title
from datetime import date

# import these for finding all CSVs
import os
from os import listdir
from os.path import isfile, join


#### Hardcoded Variables
# You can change this if the RemyWiki page name changes
sdvx_song_page = "Category:SOUND_VOLTEX_Songs"
# Assemble the CSV file name using the current date
csv_file_name = "song_page_ids--" + date.today().strftime("%Y-%m-%d") + ".csv"
# Path that the script is being run from
current_path = os.path.dirname(os.path.abspath(__file__))


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

#################################################
#   Get song pageid CSVs in current directory   #
#################################################
def get_pageid_csvs():
	files = [f for f in listdir(current_path) if isfile(join(current_path, f))]

	csv_files = []

	for f in files:
		if ".csv" in f:
			csv_files.append(f)

	return csv_files

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
		print("Finished downloading all pages!")
		#get cmcontinue value
		#run same string with cmcontinue value to get additional songs

	# Save the list of song page IDs to a CSV file for later processing
	print("Writing CSV file...")
	with open(csv_file_name, "w") as file:
		writer = csv.writer(file)
		writer.writerow("pageid")
		for pageid in song_page_ids:
			writer.writerow(str(pageid))
		print("Saved pageid output as " + csv_file_name)
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
	print("####################################################")
	print("# Please enter the number of what you'd like to do #")
	print("####################################################")
	print("1 - Download pageids of all SDVX songs")
	print("2 - Use list of SDVX pageids to get song data")
	print("3 - Exit")
	user_input = input("> ")
	if user_input is "1":
		get_song_list()
	elif user_input is "2":
		print("Please select which CSV file you'd like to use")
		csv_files = get_pageid_csvs()
		if len(csv_files) is 0:
			print("Error: No CSV files found in current directory.")
			exit()
		else:
			for i in range(len(csv_files)):
				print(str(i) + " - " + str(csv_files[i]))
			user_input = input("> ")
			try:
				index = int(user_input)
				get_song_data(csv_files[index])
			except:
				print("Error: Your input wasn't a number!")
				exit()
	elif user_input is "3":
		exit()
	else:
		print("Invalid input. Exiting...")
		exit()

if __name__ == "__main__":
	main()