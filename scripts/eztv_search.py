import urllib.request, urllib.error, json, re
from bs4 import BeautifulSoup

#get html from url
def returnHTML(url):
	hdr = {'Accept': 'text/html', 'User-Agent' : "Fiddler"}
	req = urllib.request.Request(url, headers=hdr)
	try:
		response = urllib.request.urlopen(req)
	except urllib.HTTPError as e:
		print(e)
	html = response.read()
	return html
	
def getTopRes(data):
	cleanString = re.sub('\W+','-', data) #remove special characters
	query = cleanString.replace(' ','-') #replace spaces with '-'
	url = ('https://eztv.ag/search/%s' % query)
	searchResults = returnHTML(url)
	
	list = []
	soup = BeautifulSoup(searchResults, 'html.parser')
	allLinks = soup.find_all('tr', class_='forum_header_border')
	
	#find_all tds
	for link in allLinks:
		title = link.td.find_next('td')
		magnet = title.find_next('td')
		hash = re.search('btih\:(.*?)\&', magnet.a['href']).group(1)
		size = magnet.find_next('td')
		age = size.find_next('td')
		seeds = age.find_next('td')
		if (seeds != '0'):  #only show torrents with seeds
			list.append([title.text.strip(), magnet.a['href'].strip(), seeds.text, hash])
	
	return json.dumps(list)