import sqlite3, json, re
from flask import Flask, redirect

def array_sampling(selection, offset=0, limit=None):
	if limit == 0: limit = None
	return selection[offset:(limit + offset if limit is not None else None)]

def json2db(jsondata, magnet, hash, folder, tv_or_movie, episodes):
	if 'movies' in tv_or_movie:
		db = sqlite3.connect('example.db')
		c = db.cursor()
		table = 'movies'
		imdb_id = data['imdb_id']
		data = json.loads(jsondata)
		
		# add actors
		cast_list = ''
		for actor in data['cast']:
			imdb_actor_id = re.findall("name\/(.*?)\/", actor['link']) # regex the id
			cast_list = cast_list + "," + str(imdb_actor_id[0]) # add to the list
			c.execute('SELECT name FROM actors WHERE imdb_id="' + str(imdb_actor_id[0]) + '";')
			if not c.fetchone():
				c.execute('INSERT INTO actors(imdb_id,name) VALUES("' + str(imdb_actor_id[0]) + '","' + str(actor['name']) + '");')
			else:
				pass
		db.commit()
		
		# add film
		c.execute('INSERT INTO ' + table + '(imdb_id,title,description,year,rating,url,length,director,cast,img_big,img_small,magnet,hash,folder) VALUES("'
			+ data['imdb_id'] + '","'
			+ data['title'] + '","'
			+ data['description'] + '","'
			+ data['year'] + '","'
			+ data['rating'] + '","'
			+ data['url']['url'] + '","'
			+ data['length'] + '","'
			+ data['director'] + '","'
			+ cast_list[1:] + '","'
			+ data['poster']['large'] + '","'
			+ data['poster']['thumb'] + '","'
			+ magnet + '","'
			+ hash + '","'
			+ folder + '");')
		
		db.commit()
		db.close()
	else: # if it's a tv-show
		db = sqlite3.connect('example.db')
		c = db.cursor()
		table = 'tv_shows'
		data = json.loads(jsondata)
		episodes = json.loads(episodes)
		imdb_id = data['externals']['imdb']
		
		# add a tv-show
		c.execute('INSERT INTO ' + table + '(imdb_id,title,description,year,rating,url,img_big,img_small) VALUES("'
			+ imdb_id + '","'
			+ str(data['name']) + '","'
			+ data['summary'] + '","'
			+ data['premiered'][:4] + '","'
			+ str(data['rating']['average']) + '","'
			+ ('http://www.imdb.com/title/%s/' % (imdb_id)) + '","'
			+ data['image']['original'] + '","'
			+ data['image']['medium'] + '");')
			
		for ep in episodes:
			#prechecks, in case summary or image are missing
			if ep['image'] is None:
				image = 'missing.jpg'
			else:
				image = ep['image']['original']
			if ep['summary'] is None:
				summary = 'missing'
			else:
				summary = ep['summary'].replace('"','')
			
			c.execute('INSERT INTO tv_shows_episodes(tv_show_id,se_num,ep_num,title,description,airdate,screenshot) VALUES("'
				+ imdb_id + '",'
				+ str(ep['season']) + ','
				+ str(ep['number']) + ',"'
				+ ep['name'].replace('"','') + '","'
				+ summary + '","'
				+ ep['airdate'] + '","'
				+ image + '");')
		
		db.commit()
		db.close()
		
	return redirect("/item/" + table + "/" + imdb_id, code=302)


def db2json(table,imdb_id,offset,limit):
	db = sqlite3.connect('example.db')
	c = db.cursor()
	
	query = 'SELECT * FROM ' + str(table)
	if (imdb_id != ""):
		query = query + ' WHERE imdb_id="' + str(imdb_id) + '"'
	if (limit > 0):
		query = query + ' LIMIT ' + str(limit)
	if (offset > 0):
		query = query + ' OFFSET ' + str(offset)
	c.execute(query)
	
	rows = [x for x in c]
	cols = [x[0] for x in c.description]
	items = []
	for row in rows:
		item = {}
		for prop, val in zip(cols, row):
			item[prop] = val
		item["table"] = table # add table name to json
		items.append(item)
	
	if 'movies' in table:
		db.close()
		return json.dumps(items),0
	else:
		query = 'SELECT * FROM %s WHERE tv_show_id = "%s"' % ('tv_shows_episodes', imdb_id);
		c.execute(query)
		
		rows = [x for x in c]
		cols = [x[0] for x in c.description]
		eps = []
		for row in rows:
			ep = {}
			for prop, val in zip(cols, row):
				ep[prop] = val
			ep["table"] = table # add table name to json
			eps.append(ep)
		
		db.close()
		return json.dumps(items), json.dumps(eps)


def db2json_search(request,offset,limit):
	db = sqlite3.connect('example.db')
	c = db.cursor()
	tables = ["movies","tv_shows"]
	searchColumns = ["title","description","director","cast"]
	items = []
	requestArray = str(request).split(" ")
	
	for table in tables:
		# Build search query
		query = 'SELECT * FROM ' + table + ' WHERE'
		# for each searchable column
		for i, column in enumerate(searchColumns):
			query = query + (' OR ' if i != 0 else ' ')
			# for each keyword
			####query = query + "("
			for j, requestItem in enumerate(requestArray):
				####query = query + (' AND ' if j != 0 else '') + '"' + column + '" LIKE "%' + requestItem + '%"' 
				query = query + (' OR ' if j != 0 else '') + '"' + column + '" LIKE "%' + requestItem + '%"' 
			####query = query + ")"
		query = query + ';'
		c.execute(query)
		rows = [x for x in c]
		cols = [x[0] for x in c.description]
		for row in rows:
			item = {}
			for prop, val in zip(cols, row):
				item[prop] = val
			item["table"] = table # add table name to json
			items.append(item)

	db.commit()
	db.close()
	return json.dumps(array_sampling(items,offset,limit))
	return str(query)

def number_of_rows_all(table):
	db = sqlite3.connect('example.db')
	c = db.cursor()
	query = 'SELECT Count(*) FROM ' + str(table)
	c.execute(query)
	row = c.fetchone()
	db.commit()
	db.close()
	return row[0]

def set_dir(movie_dir, dir, hash):
	if dir is not None:
		folder = str(movie_dir) + '\\' + dir
		db = sqlite3.connect('example.db')
		c = db.cursor()
		c.execute('UPDATE movies SET folder = "' + folder + '" WHERE hash = "' + str(hash) + '";');
		db.commit()
		db.close()
	return