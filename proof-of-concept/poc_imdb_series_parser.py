from urllib.request import urlopen
from bs4 import BeautifulSoup

# get the html | a bit different from the other function I wrote
def returnHTML(url):
	raw = urlopen(url).read()
	html = raw.decode('utf8')
	return html
	
def showJSON(showUrl):
	# basic info
	showPage = returnHTML(showUrl)
	soup = BeautifulSoup(showPage, 'html.parser')

	# get original title if exists
	title = ''
	titleRaw = soup.find(itemprop = 'name')
	origTitleRaw = soup.find(class_='originalTitle')
	try:
		title = origTitleRaw.get_text().replace('(original title)',' ').strip()
	except:
		title = titleRaw.get_text().strip()

	# poster and description
	poster = soup.find(class_ = 'poster')
	summary = soup.find(class_ = 'summary_text')

	# total number of seasons
	s = 0;
	epsHTML = returnHTML(showUrl + 'episodes');
	soup = BeautifulSoup(epsHTML, 'html.parser')
	select = soup.find_all('option')

	for sel in select:
		if 'bySeason' in str(sel.parent):
			s += 1
	
	# comb the desert
	jsonOut = []
	episodeList = []
	for i in range(1, s + 1):
		epListHTML = returnHTML(showUrl + 'episodes?season=' + str(i));
		soup = BeautifulSoup(epListHTML, 'html.parser')
		
		e = 1
		epList = soup.find_all(class_ = 'list_item')
		for ep in epList:
			seasonn = ('%02d' % (i,))
			episoden = ('%02d' % (e,))
			eptitle = str(ep.strong.a['title'])
			epimage = str(ep.div.a.div.img['src'])
			eurl = str(ep.div.a['href'])
			epdesc = ep.find(class_ = 'item_description').get_text().strip()
			
			episodeList.append('{"season":%s, "episode":%s, "title":"%s", "image":"%s", "url":"%s", "desc":"%s"}' % (seasonn, episoden, eptitle, epimage, eurl, epdesc))
			e += 1
		
	# todo: rewrite and move this routine somewhere | dirty json generation
	jsonOut = '[{"title":"%s", "poster":"%s", "description":"%s", "episodes":"%s"}]' % (title, poster.a.img['src'], summary.get_text().strip(), str(episodeList).replace('\'',''))
	return jsonOut
	
test = showJSON('http://www.imdb.com/title/tt3487382/')
print(test)