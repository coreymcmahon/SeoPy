import re
import httplib
import urllib

GOOGLE_SEARCH_URL = "https://encrypted.google.com/search?complete=0&pws=0&q="
TOOLBAR_URL = 'http://toolbarqueries.google.com/search?client=navclient-auto&ch={0}&features=Rank&q=info:{1}'

class SeoPy:
	"""doc"""
	
	def __init__ (self):
		print "hola"
	

	def __execute (self, endpoint, http_method="GET", http_body="", http_headers=""):

		# Trim off everything before // and everything after the first occurence of /
		domain = endpoint[ endpoint.find("//") + 2 :]
		if domain.find("/") != -1 :
			domain = domain[ 0 : domain.find("/") ]
		
		# Get the resource (relative URL)
		resource = endpoint[ endpoint.find(domain) + len(domain) :]

		# Do we want http or https?
		conn = httplib.HTTPConnection(domain)
		if endpoint.find("https") != -1 :
			conn = httplib.HTTPSConnection(domain)

		conn.request(http_method, resource)
		response = conn.getresponse()
		return response
	

	def get_results_for(self,keyword) :
		url = GOOGLE_SEARCH_URL + urllib.quote(keyword)
		return GoogleResults(self.__execute(url).read())



class GoogleResults:

	html_document = ""

	def __init__(self, html_document):
		self.html_document = html_document
	
	def get_average_pagerank(self):
		print "tba"
	
	def get_number_of_results(self):
		results = re.search('([0-9,]*?) result', self.html_document)
		#return results.group(0).replace(" result","").replace(",","")
		return results.group(1).replace(",","")
	
	def get_results(self) :
		results = re.findall('<h3.*?</h3>', self.html_document, re.M)
		
		rlist = []
		for result in results:
			title = re.sub('<[^<]+?>', '', result)
			url_matches = re.search("/url\?q=(.*?)\&amp;", result)
			url = urllib.unquote(url_matches.group(1))
			rlist.append([title, url])
		return rlist
	
	def get_raw_html(self):
		return self.html_document
