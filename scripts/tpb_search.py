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
	list = []
	url = 'https://thepiratebay.org/s/?q=' + str(data) + '&video=on&category=0&page=0&orderby=7'
	tpbResults = returnHTML(url)
	
	soup = BeautifulSoup(tpbResults, 'html.parser')
	allLinks = soup.find_all('a', class_='detLink')
	for link in allLinks:
		seeds = link.find_next('td').text
		#title = link.text.encode('utf-8').strip() #title
		title = link.text.strip() #title
		magnet = link.find_next('a')['href'] #magnet link
		hash = re.search('btih\:(.*?)\&', magnet).group(1) #hash
		if (seeds != '0'):  #only show torrents with seeds
			list.append([title,magnet,seeds,hash])
	return json.dumps(list)