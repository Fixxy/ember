import urllib2
import re
from bs4 import BeautifulSoup
#todo: eztv has an API but its limited, so I can theoretically rewrite the whole thing

#todo: store this in db / post from webpage
print 'Initializing...'
searchString = 'Doctor Who (2005)'
lastSeason = 10
lastEpisode = 8
addParam1 = 'hdtv'
addParam2 = '720p'
statReds = ""

#get html from url
def returnHTML(url):
	hdr = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'User-Agent' : "Python Urllib2"}
	req = urllib2.Request(url, headers=hdr)
	try:
		response = urllib2.urlopen(req)
	except urllib2.HTTPError, e:
		print e.fp.read()
	html = response.read()
	return html

#naughty bits
def dataPrep(html, tag, htmlclass, regex):
	soup = BeautifulSoup(html, 'html.parser')
	list = soup.find_all(tag, class_=htmlclass)
	urlPattern = re.compile(regex, re.I)
	return list, urlPattern
	
#more optimizations
def assembleInfo(text, html):
	infoBit = re.findall(text + "\:\<\/b\>(.*?)\<br", html)
	print text + ":" + infoBit[0]
	return

#data processing
print 'Retrieving the showlist'
showlistHTML = returnHTML('https://eztv.ag/showlist/')
showList, urlPatternShow = dataPrep(showlistHTML, 'a', 'thread_link', '\<a(.*?) href=\"(.*?)\"\>(.*?)\<')
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
print "Looking for episode: " + newEpisode

#todo: rewrite this bit
episodeList, urlPatternEp = dataPrep(seriesPageHTLM, 'a', 'epinfo', '\<a(.*?) href=\"(.*?)\"(.*?)\>')
for i in range(len(episodeList)):
	episodeName = (urlPatternEp.search(str(episodeList[i]))).group(3)
	episodeUrl = (urlPatternEp.search(str(episodeList[i]))).group(2)
	if newEpisode.lower() in episodeName.lower():
		if addParam1.lower() in episodeName.lower():
			if addParam2.lower() in episodeName.lower():
				print episodeName
				tempEpisodeUrl = episodeUrl

#basic info
print "----------"
print "Retrieving latest episode's info:"
print "----------"
infoHTML = returnHTML('https://eztv.ag' + tempEpisodeUrl)
soup = BeautifulSoup(infoHTML, 'html.parser')
assembleInfo("Torrent File", infoHTML)
assembleInfo("Torrent Hash", infoHTML)
assembleInfo("Filesize", infoHTML)
assembleInfo("Released", infoHTML)
assembleInfo("File Format", infoHTML)
assembleInfo("Resolution", infoHTML)
assembleInfo("Aspect Ratio", infoHTML)

magnetLink = re.findall("\<a.*href=\"magnet\:(.*?)\"", infoHTML)
print "Magnet Link: magnet" + magnetLink[0]
