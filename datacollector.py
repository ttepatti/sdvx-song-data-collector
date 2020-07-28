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

# import this for parsing text
import re


#### Hardcoded Variables
# You can change this if the RemyWiki page name changes
sdvx_song_page = "Category:SOUND_VOLTEX_Songs"
# Assemble the pageids file name using the current date
pageids_file_name = "sdvx_songs--" + date.today().strftime("%Y-%m-%d") + ".pageids"
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
#   Get song pageids files in current directory   #
#################################################
def get_pageids_files():
	files = [f for f in listdir(current_path) if isfile(join(current_path, f))]

	pageids_files = []

	for f in files:
		if ".pageids" in f:
			pageids_files.append(f)

	return pageids_files

#########################
#   Get list of songs   #
#########################
def get_song_list():
	# This request is split into multiple lines to make it (hopefully) easier to read
	page = requests.post("https://remywiki.com/api.php",
								data = {
									'action': 'query',
									'format': 'json',
									'list': 'categorymembers',
									'cmtitle': sdvx_song_page,
									'cmlimit': '500'
								})

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
		pagecount = 0;
		while json_data['continue']['cmcontinue']:
			pagecount += 1
			cmcontinue = json_data['continue']['cmcontinue']
			# cmcontinue value found, that means there are more songs we haven't gotten yet
			print("Parsing data page " + str(pagecount) + "...")
			# generate a new request, this time including our cmcontinue value
			page = requests.post("https://remywiki.com/api.php",
								data = {
									'action': 'query',
									'format': 'json',
									'list': 'categorymembers',
									'cmtitle': sdvx_song_page,
									'cmcontinue': cmcontinue,
									'cmlimit': '500'
								})
			# parse page data as json
			json_data = json.loads(page.content)
			# append new song pageids to list
			for id in extract_values(json_data, 'pageid'):
				song_page_ids.append(id)
			# sleep so we send requests slowly!
			time.sleep(1)
	except Exception as e:
		print("Finished downloading all pages!")
		#get cmcontinue value
		#run same string with cmcontinue value to get additional songs

	# Save the list of song page IDs to a CSV file for later processing
	print("Writing pageids file...")
	with open(pageids_file_name, "w") as file:
		for pageid in song_page_ids:
			file.write(str(pageid) + "\n")
		print("Saved pageid output as " + pageids_file_name)
		file.close()

########################
#     Get song data    #
########################
def get_song_data(pageids_file):
	print("Fetching Page IDs from " + pageids_file + "...")

	# store the total number of pages we're requesting
	total_pages = 0
	
	# store how many have been parsed
	total_parsed = 0

	# store the page IDs in a bar-delimiated format (bd)
	# since we can query the API with &pageids=1|2|3|4|5 to get multiple pages
	pageids_bd = ""

	# keep count of page ids, because we can only request 50 per API call
	count = 0

	# assemble the list of page IDs for our API call
	with open(pageids_file, 'r') as file:
		# For stats, get total number of pages we're requesting
		for row in file:
			total_pages += 1

		# reset our position
		file.seek(0)

		# actually assemble rows here
		for row in file:
			# if count is 50, fire off an API request
			if count is 50:
				total_parsed += 50
				print("Parsing page " + str(total_parsed) + " of " + str(total_pages) + " total pages.")
				# assemble an API request with our 50 page IDs
				page = requests.post("https://remywiki.com/api.php",
						data = {
							'action': 'query',
							'format': 'json',
							'prop': 'revisions',
							'rvprop': 'content',
							'rvslots': 'main',
							'pageids': pageids_bd
						})
				parse_song_data(page.content)
				# reset count
				count = 0
				# reste our pageids_bd string
				pageids_bd = ""
				# sleep to be kind to the API
				time.sleep(1)
			else:
				# else, continue on:
				if pageids_bd is "":
					# don't add bar for the first element
					pageids_bd = row.rstrip()
				else:
					pageids_bd = pageids_bd + "|" + row.rstrip()
				count +=1

################################
#  Parse a song data API call  #
################################
def parse_song_data(page_content):
	# this method is run on 50 pages at a time
	# first, convert page content to json
	json_data = json.loads(page_content)
	
	# grab tex content
	text_content = extract_values(json_data, "*")

	# store artists
	artist = []
	for song in text_content:
		artist = re.search('Artist: (.*)<br>', song)
		print(artist.group(1))

	# The main goal here is to fetch the following:
	# song title
	# artist name
	# song bpm
	# any dates on the page (we're looking for the date it was added to the game)

################
#     Main     #
################
def main():
	print("####################################################")
	print("# Please enter the number of what you'd like to do #")
	print("####################################################")
	print("1 - Download pageids of all SDVX songs")
	print("2 - Use list of SDVX pageids to get song data")
	print("3 - Exit")
	print("4 - Test JSON parsing with stored JSON file")
	user_input = input("> ")
	if user_input is "1":
		get_song_list()
	elif user_input is "2":
		print("Please select which pageids file you'd like to use")
		pageids_files = get_pageids_files()
		if len(pageids_files) is 0:
			print("Error: No .pageids files found in current directory.")
			exit()
		else:
			for i in range(len(pageids_files)):
				print(str(i) + " - " + str(pageids_files[i]))
			user_input = input("> ")
			try:
				index = int(user_input)
			except:
				print("Error: Your input wasn't a number!")
				exit()
			get_song_data(pageids_files[index])
	elif user_input is "3":
		exit()
	elif user_input is "4":
		print("running parse_song_data()")
		# test JSON parsing using stored page content
		with open("test.json", "r") as file:
			# our file is one row lol
			for row in file:
				parse_song_data(row)
	else:
		print("Invalid input. Exiting...")
		exit()

if __name__ == "__main__":
	main()