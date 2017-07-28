# pip install requests
from pprint import pprint
import os, re, json, PTN, requests, urllib

api_imdb = "http://www.imdb.com/xml/find?json=1&nr=1&tt=on&q="
api_movies = "http://www.theimdbapi.org/api/movie?movie_id="
api_tv_shows = "http://api.tvmaze.com/lookup/shows?imdb="

def cleanData(data):
	tags = ['\n', '\r', '<[^>]+>']
	for tag in tags: data = re.sub(tag, '', data)
	data = re.sub(' +', ' ', data)
	return data

def JSONReponse(url):
	contents = requests.get(url).text
	contents_clean = cleanData(contents)
	return contents_clean

def imdbJSONResponse(title, type, cache, limit):
	if (title in cache): # if request already made
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
						if (len(result) < limit): # add if array size smaller than 5
							tt_url = api_movies if (type == "movies") else api_tv_shows
							tt_data = JSONReponse(tt_url + item["id"])
							if (tt_data and tt_data != ""): result.append(json.loads(tt_data))
		cache[title] = result
	return result

def scan(path):
	ext = [".3g2", ".3gp", ".amv", ".asf", ".asx", ".avi", ".drc", ".flv", ".f4v", ".f4p", ".f4a", ".f4b", ".mkv", ".mov", ".qt", ".mp4", ".m4p", ".m4v", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".m2v", ".ogv", ".rm", ".rmvb", ".svi", ".webm", ".wmv"]
	found = [] # array for all the files found
	cache = {} # cache for imdb json results
	for root, dirs, files in os.walk(path):
		for name in files:
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
				# Remove extension from title in case it stays there
				for extension in ext: info["title"] = re.sub(extension.lower(), '', info["title"])
				# Save to the found_on_imdb key
				info["found_on_imdb"] = imdbJSONResponse(info["title"], info["type"], cache, 5)
				# Add to the resulting list
				found.append(info)
	return json.dumps(found)

#print(scan("E:\TV-Series\An Idiot Abroad"))