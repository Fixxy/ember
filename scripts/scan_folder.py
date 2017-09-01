# pip install requests
from pprint import pprint
from . import sqlite_routine
import os, re, json, PTN, requests, urllib

api_imdb = "http://www.imdb.com/xml/find?json=1&nr=1&tt=on&q="
api_movies = "http://www.theimdbapi.org/api/movie?movie_id="
##api_movies = "https://moviesapi.com/m.php?type=movie&r=json&i="
api_tv_shows = "http://api.tvmaze.com/lookup/shows?imdb="
api_tv_shows_episodes = "http://api.tvmaze.com/shows/"

def cleanData(data):
	tags = ['\n', '\r', '<[^>]+>']
	for tag in tags: data = re.sub(tag, '', data)
	data = re.sub(' +', ' ', data)
	return data

def JSONReponse(url):
	contents = requests.get(url).text
	contents_clean = cleanData(contents)
	return contents_clean

def imdbJSONResponse(path, title, type, season, episode, cache, limit):
	if (title in cache): # if request's already made
		result = cache[title]
	else:
		url = api_imdb + urllib.parse.quote(title)
		json_data = json.loads(JSONReponse(url))
		title_types = ["title_popular", "title_exact", "title_substring", "title_approx"]
		result = []
		for title_type in title_types:
			if (title_type in json_data):
				for item in json_data[title_type]:
					if item["id"] not in result:
						if (len(result) < limit): # add if array size is smaller than 5
							# get movie/tv-show data from APIs
							tt_url = api_movies + item["id"] if (type == "movies") else api_tv_shows + item["id"]
							tt_data = JSONReponse(tt_url)
							if (tt_data and tt_data != ""):
								tt_data_json = json.loads(tt_data)
								tt_data_json["exists"] = sqlite_routine.check_in_db(item["id"], type, str(season), str(episode))
								tt_data_json["path"] = path
								tt_data_json["type"] = type
								tt_data_json["season"] = season
								tt_data_json["episode"] = episode
								# get episodes if getting a tv-show
								if (type == "tv_shows"):
									tt_data_ep = JSONReponse(api_tv_shows_episodes + str(tt_data_json["id"]) + "/episodes")
									tt_data_json["episodes"] = json.loads(tt_data_ep)
								result.append(tt_data_json)
		cache[title] = result
	return result

#def scan(path):
def scan(root, name):
	ext = [".3g2", ".3gp", ".amv", ".asf", ".asx", ".avi", ".drc", ".flv", ".f4v", ".f4p", ".f4a", ".f4b", ".mkv", ".mov", ".qt", ".mp4", ".m4p", ".m4v", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".m2v", ".ogv", ".rm", ".rmvb", ".svi", ".webm", ".wmv"]
	#found = [] # array for all the files found
	cache = {} # cache for imdb json results
	info = [] # item info
	#def generate():
	#	for root, dirs, files in os.walk(path):
	#		for name in files:
	if name.endswith(tuple(ext)):
		file_location = root.split("\\") # ['E:', 'TV-Series', 'Top Gear', 'Season 1']
		foldername = ""
		if (len(file_location)-1 >= 0):
			temp = file_location[len(file_location)-1] # current folder name - either season name or title
			foldername = temp if ("season" not in temp.lower()) else file_location[len(file_location)-2]
		info = PTN.parse(name)
		# Check if title exists, if not - use folder name instead
		if (info["title"] == ""): info["title"] = foldername
		# Add item type - movie or tv-show
		info["type"] = "tv_shows" if ("episode" in info) else "movies"
		# Add file location
		#info["location"] = root
		# Remove extension from title in case it stays there
		for extension in ext: info["title"] = re.sub(extension.lower(), '', info["title"])
		# Quick-fix for movies - add empty episode and season values
		if ("episode" not in info): info["episode"] = ""
		if ("season" not in info): info["season"] = ""
		# Save to the found_on_imdb key
		info["found_on_imdb"] = imdbJSONResponse(root + "\\" + name, info["title"], info["type"], info["season"], info["episode"], cache, 5)
		# Add to the resulting list
		#found.append(info)
	#return json.dumps(found)
	return json.dumps(info) + "\n"
	