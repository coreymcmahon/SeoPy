'''
SeoPy
====
A set of tools for performing some standard SEO tasks, such as keyword research and competitive analysis.
'''

import re
import httplib
import urllib
import time

GOOGLE_SEARCH_URL = "https://encrypted.google.com/search?complete=0&pws=0&q="
TOOLBAR_URL = 'http://toolbarqueries.google.com/search?client=navclient-auto&ch={0}&features=Rank&q=info:{1}'

class SeoPy:	
	''' This class provides the entry-point to the functionality of the library. '''
	
	def execute_http_request (self, endpoint, http_method="GET", http_body="", http_headers=""):
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
		return GoogleResults(self.execute_http_request(url).read())



class GoogleResults:
	''' Class representing a page of Google search results '''
	
	html_document = ""

	def __init__(self, html_document):
		''' Pass in the raw HTML for the results page '''
		self.html_document = html_document
	
	def get_average_pagerank(self):
		''' Get the average PageRank of the 10 results on the first page '''
		checker = PageRankChecker()
		results = self.get_results()
		pageranks = []
		min = 11
		max = -1
		total = 0
		i = 0
		for result in results:
			# TODO: work out why the PR toolbar server is denying us after a certain # of requests
			pagerank = int(checker.get_pr(result[1]))
			time.sleep(4)
			total += pagerank
			if (pagerank < min) :
				min = pagerank
			if (pagerank > max) :
				max = pagerank
			i += 1
			print result[1] + "(" + str(pagerank) + ")\n"
		
		total = total - min - max
		return float(total) / float(i)
		
	
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
			# TODO: line below is failing for certain queries
			url_matches = re.search("/url\?q=(.*?)\&amp;", result)
			url = urllib.unquote(url_matches.group(1))
			rlist.append([title, url])
		return rlist
	
	def get_raw_html(self):
		''' Get the raw HTML for this resultset '''
		return self.html_document


class PageRankChecker:
	''' PageRank checked based on the implementation here: https://github.com/phurix/pagerank/blob/master/pagerank.py '''
	
	prhost='toolbarqueries.google.com'
	prurl='http://%s/tbr?client=navclient-auto&ch=%s&features=Rank&q=info:%s'
	
	def int_str(self, String, Integer, Factor):
		for i in range(len(String)) :
			Integer *= Factor
			Integer &= 0xFFFFFFFF
			Integer += ord(String[i])
		return Integer
	
	def hash_url(self, Str):
		C1 = self.int_str(Str, 0x1505, 0x21)
		C2 = self.int_str(Str, 0, 0x1003F)
		
		C1 >>= 2
		C1 = ((C1 >> 4) & 0x3FFFFC0) | (C1 & 0x3F)
		C1 = ((C1 >> 4) & 0x3FFC00) | (C1 & 0x3FF)
		C1 = ((C1 >> 4) & 0x3C000) | (C1 & 0x3FFF)
		
		T1 = (C1 & 0x3C0) << 4
		T1 |= C1 & 0x3C
		T1 = (T1 << 2) | (C2 & 0xF0F)
		
		T2 = (C1 & 0xFFFFC000) << 4
		T2 |= C1 & 0x3C00
		T2 = (T2 << 0xA) | (C2 & 0xF0F0000)
		
		return (T1 | T2)
	
	def check_hash(self, HashInt):
		HashStr = "%u" % (HashInt)
		Flag = 0
		CheckByte = 0
		
		i = len(HashStr) - 1
		while i >= 0:
			Byte = int(HashStr[i])
			if 1 == (Flag % 2):
				Byte *= 2;
				Byte = Byte / 10 + Byte % 10
			CheckByte += Byte
			Flag += 1
			i -= 1
		
		CheckByte %= 10
		if 0 != CheckByte:
			CheckByte = 10 - CheckByte
			if 1 == Flag % 2:
				if 1 == CheckByte % 2:
					CheckByte += 9
				CheckByte >>= 1
		
		return '7' + str(CheckByte) + HashStr
	
	
	def get_url(self,query):
		hash = self.check_hash(self.hash_url(query))
		url = self.prurl % (self.prhost,hash,query)
		return url
	
	def get_pr(self,url):
		endpoint = self.get_url(url)
		seopy = SeoPy()
		rank = seopy.execute_http_request(endpoint).read()
		print "[" + rank + "]"
		return rank[rank.rfind(":")+1:].replace("\n","")


