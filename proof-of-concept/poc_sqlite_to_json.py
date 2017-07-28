import sqlite3, json
from sqlobject import *

class Movie(SQLObject):
#	fid = IntCol()
	title = StringCol()
	cover = StringCol()
	description = StringCol()
	year = IntCol()
	rating = IntCol()
	url = StringCol()

# connect to sqlite.db and return json
def db2json():
	connection = connectionForURI('sqlite:example.db')
	sqlhub.processConnection = connection
	
	# create table if there is none
	try:
		Movie.createTable()
	except (dberrors.OperationalError) as e:
		print(e)
	
	# form json
	all_movies = Movie.select().orderBy(Movie.q.title)
	movies_as_dict = []
	for movie in all_movies:
		movie_as_dict = {
			'id' : movie.fid,
			'title' : movie.title,
			'cover' : movie.cover,
			'description' : movie.description,
			'year' : movie.year,
			'url' : movie.url,
			'rating' : movie.rating}
		movies_as_dict.append(movie_as_dict)
		
	sqlhub.processConnection.close()
	return json.dumps(movies_as_dict)

def json2db(jsondata, url):
	db = sqlite3.connect("example.db")
	c = db.cursor()
	c.execute("insert into movies(title,cover,description,year,rating,url) values(" + jsondata["title"] + "," + jsondata["poster"]["large"] + "," + jsondata["description"] + "," + jsondata["year"] + "," + jsondata["rating"] + "," + url + ")")
	return c.lastrowid