'''
SeoPy
====
A set of tools for performing some standard SEO tasks, such as keyword research and competitive analysis.
'''

import re
import httplib
import urllib

GOOGLE_SEARCH_URL = "https://encrypted.google.com/search?complete=0&pws=0&q="
TOOLBAR_URL = 'http://toolbarqueries.google.com/search?client=navclient-auto&ch={0}&features=Rank&q=info:{1}'

class SeoPy:	
	''' This class provides the entry-point to the functionality of the library. '''
	
	def __execute (self, endpoint, http_method="GET", http_body="", http_headers=""):
		''' Internal (private) method for executing HTTP requests '''
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
		''' Get the first 10 results for this search query '''
		url = GOOGLE_SEARCH_URL + urllib.quote(keyword)
		return GoogleResults(self.__execute(url).read())




class GoogleResults:
	''' Class representing a page of Google search results '''
	
	html_document = ""

	def __init__(self, html_document):
		''' Pass in the raw HTML for the results page '''
		self.html_document = html_document
	
	def get_average_pagerank(self):
		''' Get the average PageRank of the 10 results on the first page '''
		print "tba"
	
	def get_number_of_results(self):
		''' Get the total number of results for this query '''
		results = re.search('([0-9,]*?) result', self.html_document)
		return results.group(1).replace(",","")
	
	def get_results(self) :
		''' Get an array of arrays containing the top 10 results, the title of the page and the URL '''
		results = re.findall('<h3.*?</h3>', self.html_document, re.M)
		
		rlist = []
		for result in results:
			title = re.sub('<[^<]+?>', '', result)
			url_matches = re.search("/url\?q=(.*?)\&amp;", result)
			url = urllib.unquote(url_matches.group(1))
			rlist.append([title, url])
		return rlist
	
	def get_raw_html(self):
		''' Get the raw HTML for this resultset '''
		return self.html_document


