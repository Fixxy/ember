import sqlite3, json, re
from pprint import pprint
from flask import Flask, redirect

dbfile = 'example.db'

def array_sampling(selection, offset=0, limit=None):
	if limit == 0: limit = None
	return selection[offset:(limit + offset if limit is not None else None)]


def remHTML(raw):
	tag = re.compile('<.*?>')
	clean = re.sub(tag, '', raw)
	return clean


def json2db(jsondata, magnet, hash, tv_or_movie, episodes, redirectflag):
	if 'movies' in tv_or_movie:
		db = sqlite3.connect(dbfile)
		c = db.cursor()
		table = 'movies'
		data = json.loads(jsondata)
		imdb_id = data['imdb_id']
		
		# add actors
		cast_list = ''
		for actor in data['cast']:
			if 'name' in actor['link']:
				imdb_actor_id = re.findall("name\/(.*?)\/", actor['link']) # regex the id
				cast_list = cast_list + "," + str(imdb_actor_id[0]) # add to the list
				c.execute('SELECT name FROM actors WHERE imdb_id="' + str(imdb_actor_id[0]) + '";')
				if not c.fetchone():
					c.execute('INSERT INTO actors(imdb_id,name) VALUES("' + str(imdb_actor_id[0]) + '","' + str(actor['name']) + '");')
				else:
					pass
		db.commit()
		
		# Add movie
		# Create new row if it doesn't exist
		c.execute('INSERT INTO ' + table + '(imdb_id,title,description,year,rating,url,length,director,cast,img_big,img_small,magnet,hash) SELECT ?,?,?,?,?,?,?,?,?,?,?,?,? WHERE NOT EXISTS(SELECT 1 FROM ' + table + ' WHERE imdb_id=?)', (data['imdb_id'], data['title'], data['description'], data['year'], data['rating'], data['url']['url'], data['length'], data['director'], cast_list[1:], data['poster']['large'], data['poster']['thumb'], magnet, hash, data['imdb_id']))
		# Try to update row if it already exists
		c.execute('UPDATE ' + table + ' SET title=?, description=?, year=?, rating=?, url=?, length=?, director=?, cast=?, img_big=?, img_small=?, magnet=coalesce(?,magnet), hash=coalesce(?,hash) WHERE imdb_id=?', (data['title'], data['description'], data['year'], data['rating'], data['url']['url'], data['length'], data['director'], cast_list[1:], data['poster']['large'], data['poster']['thumb'], magnet, hash, data['imdb_id']))
		db.commit()
		db.close()
	else: # if it's a tv-show
		db = sqlite3.connect(dbfile)
		c = db.cursor()
		table = 'tv_shows'
		data = json.loads(jsondata)
		episodes = json.loads(episodes)
		imdb_id = data['externals']['imdb']
		summary_s = remHTML(data['summary'].replace('"',''))
		
		# Add a TV-show
		#c.execute('INSERT INTO ' + table + ' (imdb_id,title,description,year,rating,url,img_big,img_small,status) VALUES(?,?,?,?,?,?,?,?,?)', (imdb_id, str(data['name']), summary_s, data['premiered'][:4], str(data['rating']['average']), ('http://www.imdb.com/title/%s/' % (imdb_id)), data['image']['original'], data['image']['medium'], data['status']))
		# Create new row if it doesn't exist
		c.execute('INSERT INTO ' + table + '(imdb_id,title,description,year,rating,url,img_big,img_small,status) SELECT ?,?,?,?,?,?,?,?,? WHERE NOT EXISTS(SELECT 1 FROM ' + table + ' WHERE imdb_id=?)', (imdb_id, str(data['name']), summary_s, data['premiered'][:4], str(data['rating']['average']), ('http://www.imdb.com/title/%s/' % (imdb_id)), data['image']['original'], data['image']['medium'], data['status'], imdb_id))
		# Try to update row if it already exists
		c.execute('UPDATE ' + table + ' SET title=?, description=?, year=?, rating=?, url=?, img_big=?, img_small=?, status=? WHERE imdb_id=?', (str(data['name']), summary_s, data['premiered'][:4], str(data['rating']['average']), ('http://www.imdb.com/title/%s/' % (imdb_id)), data['image']['original'], data['image']['medium'], data['status'], imdb_id))
		
		# add to the watchlist if currently running
		nextEpisode = ''
		try:
			nextEpisode = data['_links']['nextepisode']
		except KeyError:
			pass
		
		if ('Running' in data['status'] and nextEpisode != ''):
			#c.execute('INSERT INTO watchlist (tv_show_id, time, day) VALUES("'
			#	+ imdb_id + '","'
			#	+ data['schedule']['time'] + '","'
			#	+ data['schedule']['days'][0] + '");')
			c.execute('INSERT INTO watchlist(tv_show_id,time,day) SELECT ?,?,? WHERE NOT EXISTS(SELECT 1 FROM watchlist WHERE tv_show_id=?)', (imdb_id, data['schedule']['time'], data['schedule']['days'][0], imdb_id))
		
		for ep in episodes:
			#prechecks, in case summary or image are missing
			if ep['image'] is None:
				image = 'missing.jpg'
			else:
				image = ep['image']['original']
			if ep['summary'] is None:
				summary = 'missing'
			else:
				summary = remHTML(ep['summary'].replace('"',''))
			
			#c.execute('INSERT INTO tv_shows_episodes(tv_show_id,se_num,ep_num,title,description,airdate,screenshot) VALUES("'
			#	+ imdb_id + '",'
			#	+ str(ep['season']) + ','
			#	+ str(ep['number']) + ',"'
			#	+ ep['name'].replace('"','') + '","'
			#	+ summary + '","'
			#	+ ep['airdate'] + '","'
			#	+ image + '");')
			c.execute('INSERT INTO tv_shows_episodes(tv_show_id,se_num,ep_num,title,description,airdate,screenshot) SELECT ?,?,?,?,?,?,?,? WHERE NOT EXISTS(SELECT 1 FROM tv_shows_episodes WHERE tv_show_id=? AND se_num=? AND ep_num=?)', (imdb_id, str(ep['season']), str(ep['number']), ep['name'].replace('"',''), summary, ep['airdate'], image, imdb_id, str(ep['season']), str(ep['number'])))
			c.execute('UPDATE tv_shows_episodes SET se_num=?, ep_num=?, title=?, description=?, airdate=?, screenshot=? WHERE tv_show_id=? AND se_num=? AND ep_num=?', (str(ep['season']), str(ep['number']), ep['name'].replace('"',''), summary, ep['airdate'], image, imdb_id, str(ep['season']), str(ep['number'])))

		db.commit()
		db.close()
		
	if (redirectflag == "1"):
		result = redirect("/item/" + table + "/" + imdb_id, code=302)
	else:
		result = imdb_id
	return result


def db2json(table,imdb_id,offset,limit):
	db = sqlite3.connect(dbfile)
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
		query = 'SELECT * FROM %s WHERE tv_show_id="%s"' % ('tv_shows_episodes', imdb_id)
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
	db = sqlite3.connect(dbfile)
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

	db.close()
	return json.dumps(array_sampling(items,offset,limit))
	return str(query)


def check_in_db(imdb_id, type, season, episode):
	# returns value if movie's in the database - has folder specified
	db = sqlite3.connect(dbfile)
	c = db.cursor()
	query = 'SELECT Count(*) FROM movies WHERE imdb_id="%s" AND folder IS NOT NULL AND folder!=""' % (imdb_id)
	if (type == "tv_shows"):
		query = 'SELECT Count(*) FROM tv_shows_episodes WHERE tv_show_id="%s" AND se_num="%s" AND ep_num="%s" AND folder IS NOT NULL AND folder != ""' % (imdb_id, season, episode)
	c.execute(query)
	row = c.fetchone()
	db.close()
	return row[0]


def number_of_rows_all(table):
	db = sqlite3.connect(dbfile)
	c = db.cursor()
	query = 'SELECT Count(*) FROM ' + str(table)
	c.execute(query)
	row = c.fetchone()
	db.close()
	return row[0]


def set_dir(dir, hash):
	if dir is not None:
		db = sqlite3.connect(dbfile)
		c = db.cursor()
		c.execute('UPDATE movies SET folder = "' + dir + '" WHERE hash="' + str(hash) + '";')
		db.commit()
		db.close()
	return