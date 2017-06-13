import urllib2
import re
from bs4 import BeautifulSoup

#todo: store this in db
print 'Initializing...'
searchString = 'Doctor Who (2005)'
lastSeason = 10
lastEpisode = 8

#functions
def returnHTML(url):
	hdr = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'User-Agent' : "Python Urllib2"}
	req = urllib2.Request(url, headers=hdr)
	try:
		response = urllib2.urlopen(req)
	except urllib2.HTTPError, e:
		print e.fp.read()
	html = response.read()
	return html

def dataPrep(html, htmlclass, regex):
	soup = BeautifulSoup(html, 'html.parser')
	list = soup.find_all('a', class_=htmlclass)
	urlPattern = re.compile(regex, re.I)
	return list, urlPattern
	
#data processing
print 'Retrieving the showlist'
showlistHTML = returnHTML('https://eztv.ag/showlist/')
showList, urlPatternShow = dataPrep(showlistHTML, 'thread_link', '\<a(.*?) href=\"(.*?)\"\>(.*?)\<')
for i in range(len(showList)):
	showUrl = (urlPatternShow.search(str(showList[i]))).group(2)
	showName = (urlPatternShow.search(str(showList[i]))).group(3)
	if searchString.lower() in showName.lower():
		tempShowUrl = showUrl
		tempShowName = showName

print "Found: " + tempShowName + " (" + tempShowUrl + ")"

seriesPageHTLM = returnHTML('https://eztv.ag' + tempShowUrl)

#adding leading zeros
lastSeason = str(lastSeason) if lastSeason > 9 else "0" + str(lastSeason)
lastEpisode = str(lastEpisode + 1) if lastEpisode > 9 else "0" + str(lastEpisode + 1)
newEpisode = "S" + lastSeason + "E" + lastEpisode
print "Looking for episode " + newEpisode

episodeList, urlPatternEp = dataPrep(seriesPageHTLM, 'epinfo', '\<a(.*?) href=\"(.*?)\"(.*?)\>')
for i in range(len(episodeList)):
	episodeName = (urlPatternEp.search(str(episodeList[i]))).group(3)
	if newEpisode.lower() in episodeName.lower():
		print episodeName.lower()
