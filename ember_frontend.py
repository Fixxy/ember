# pip install Flask // install Flask
# pip install bs4 // install BeautifulSoup
# pip install deluge_client // install Deluge
# pip install requests // install Requests - faster than urllib - used in scan
# set FLASK_APP=ember_frontend.py // set our script as a flask application
# set FLASK_DEBUG=1 // enable the debug mode, don't forget to disable it for the actual production machine
# flask run // open to localhost only
# flask run --host=0.0.0.0 // open to entire network

# Initialisation
import json, math
from scripts import tpb_search, sqlite_routine, deluge_routine, scan_folder
from flask import Flask, request, render_template, json, jsonify
app = Flask(__name__)

# Main page
@app.route('/')
def index():
	latest_tvshows, temp = sqlite_routine.db2json("tv_shows","",0,6)
	latest_movies, temp = sqlite_routine.db2json("movies","",0,6)
	return render_template('index.html', data_tv=latest_tvshows, data_movies=latest_movies)

# Show specific movie
@app.route('/item/<string:table>/<string:imdb_id>', methods=['GET'])
def show_item(table,imdb_id):
	data, epdata = sqlite_routine.db2json(table,imdb_id,0,1)
	return render_template('item.html', table=table, data=data, epdata=epdata)

# Show all movies - first N results
@app.route('/all/<string:table>/<int:page>', methods=['GET'])
def show_all(table,page):
	total_items = sqlite_routine.number_of_rows_all(table)
	items_per_page = 9
	if (page == 0 or page > int(math.ceil(total_items/items_per_page))):
		return render_template('404.html')
	else:
		offset = (page-1)*items_per_page
		data, temp = sqlite_routine.db2json(table,"",offset,items_per_page)
		return render_template('all.html', table=table, data=data, total_items=str(total_items), page=page, items_per_page=items_per_page)

# Search
@app.route('/search-all/<int:page>', methods=['GET','POST'])
def search_items(page):
	#return sqlite_routine.db2json_search(request.form["search-all-field"],0,0)
	data_all = sqlite_routine.db2json_search(request.form["search-all-field"],0,0)
	total_items = len(json.loads(data_all))
	items_per_page = 9
	if (page == 0 or page > int(math.ceil(total_items/items_per_page))):
		return render_template('search-all.html', data_all=None, total_items=None, page=None, items_per_page=None, request=request.form["search-all-field"], noresults=1)
	else:
		return render_template('search-all.html', data_all=data_all, total_items=str(total_items), page=page, items_per_page=items_per_page, request=request.form["search-all-field"], noresults=0)

# Import - show form
@app.route('/new/', methods=['GET'])
def new():
	return render_template('new.html')

# Scan folders for movies and tv-series
@app.route('/scan/', methods=['GET'])
def scan():
	return scan_folder.scan("E:\TV-Series\A Bit Of Fry & Laurie")

# Import - add to database
@app.route('/new/add_to_db/', methods=['POST'])
def add_to_db():
	unit_data = sqlite_routine.json2db( request.form['movie-data'],
										request.form['movie-magnet'],
										request.form['movie-hash'],
										request.form['movie-dir'],
										request.form['tvormovieGroup'],
										request.form['movie-episodes'])
										
	if 'movies' in request.form['tvormovieGroup']:
		path = deluge_routine.dwnTorrent(request.form['movie-magnet'], request.form['movie-hash'], request.form['movie-dir']) # download via deluge
		sqlite_routine.set_dir(request.form['movie-dir'], path, request.form['movie-hash'])
	
	return unit_data

# Import - search on tpb
@app.route('/tpb/<string:imdb_id>/', methods=['GET','POST'])
def tpb(imdb_id):
	data = tpb_search.getTopRes(imdb_id);
	return data
