import urllib2
import re
from bs4 import BeautifulSoup

#todo: store this in db
searchString = 'Doctor Who (2005)'
lastSeason = 10
lastEpisode = 8

def returnHTML(url):
	hdr = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'User-Agent' : "Python Urllib2"}
	req = urllib2.Request(url, headers=hdr)

	try:
		response = urllib2.urlopen(req)
	except urllib2.HTTPError, e:
		print e.fp.read()

	html = response.read()
	return html



showlistHTML = returnHTML('https://eztv.ag/showlist/')
soup = BeautifulSoup(showlistHTML, 'html.parser')
showList = soup.find_all("a", class_="thread_link")
urlPattern = re.compile('\<a(.*?) href=\"(.*?)\"\>(.*?)\<', re.I)

for i in range(len(showList)):
	showUrl = (urlPattern.search(str(showList[i]))).group(2)
	showName = (urlPattern.search(str(showList[i]))).group(3)
	if searchString.lower() in showName.lower():
		tempShowUrl = showUrl
		tempShowName = showName

print tempShowName + " (" + tempShowUrl + ")"

seriesPageHTLM = returnHTML('https://eztv.ag' + tempShowUrl)
#file = open('test.html','w')
#file.write(seriesPage)
#file.close()
soup2 = BeautifulSoup(seriesPageHTLM, 'html.parser')
episodeList = soup.find_all("a", class_="epinfo")
urlPattern2 = re.compile('\<a(.*?) href=\"(.*?)\"(.*?)\>', re.I)

newEpisode = "S" + str(lastSeason) + "E" + str(lastEpisode + 1)
for i in range(len(episodeList)):
	episodeName = (urlPattern2.search(str(episodeList[i]))).group(3)
	if newEpisode.lower() in episodeName.lower():
		episodeUrl = (urlPattern2.search(str(episodeList[i]))).group(2)
