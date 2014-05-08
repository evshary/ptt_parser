#!/usr/bin/python
# -*- coding: utf-8 -*-

from HTMLParser import HTMLParser
import urllib2
import pdb

BaseURL = "http://www.ptt.cc"

class MyBoardParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.links = []
		self.nextPage = ""
		self.link_flag = 0

	def handle_starttag(self, tag, attrs):
		if tag == "div" and ("class","title") in attrs:
			self.link_flag = 1
		elif tag == "a" and self.link_flag == 1:
			for (variable, value) in attrs:
				if variable == "href":
					self.links.append(value)
			self.link_flag = 0
		elif tag == "a" and self.link_flag == 2:
			for (variable, value) in attrs:
				if variable == "href":
					self.nextPage = value
			self.link_flag = 0
			
	def handle_data(self, data):
		if data == u"最舊":
			self.link_flag = 2

class MyArticleParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.users = {"authors":{},"pushers":{}}
		self.name_flag = 0
		self.year_flag = 0

	def handle_starttag(self, tag, attrs):
		if tag == "span" and ("class","f3 hl push-userid") in attrs:
			self.name_flag = 1
		#elif tag == "span" and ("class","article-meta-value") in attrs:
		#	self.name_flag = 2

	#def handle_endtag(self, tag):
	#	print "End Tag:", tag

	def handle_data(self, data):
		if self.name_flag == 1:
			try:
				self.users["pushers"][data] += 1
			except:
				self.users["pushers"][data] = 1
			self.name_flag = 0
		elif self.name_flag == 2:
			data = data.split(" ")[0]
			try:
				self.users["authors"][data] += 1
			except:
				self.users["authors"][data] = 1
			self.name_flag = 0
		if self.year_flag == 1:
			if "2014" not in data:
				self.year_flag = -1
			else:
				self.year_flag = 0

		if data == u"作者":
			self.name_flag = 2
		elif data == u"時間":
			self.year_flag = 1

def main():
	global BaseURL
	file_handle = open("board.txt", "r")
	for board in file_handle:
		users_name = {}
		page = "/bbs/"+board.strip()+"/index.html"
		ArticleParser = MyArticleParser()
		while True:
			links = []
			#Parse Index
			bbsURL = BaseURL+page
			print bbsURL
			while True:
				try:
					htmlSrc = urllib2.urlopen(urllib2.Request(bbsURL)).read()
					break
				except:
					continue
			htmlSrc = htmlSrc.decode('utf-8')
			BoardParser = MyBoardParser()
			BoardParser.feed(htmlSrc)
			BoardParser.close()
			links =  BoardParser.links
			page = BoardParser.nextPage
			#Parse Article	
			for article in links:
				try_count = 0
				while True:
					try:
						bbsURL = BaseURL+article
						#print bbsURL
						htmlSrc = urllib2.urlopen(urllib2.Request(bbsURL)).read()
						htmlSrc = htmlSrc.decode('utf-8')
						ArticleParser.feed(htmlSrc)
						break
					except:
						if try_count > 5:
							break
						else:
							try_count += 1
						continue
				if ArticleParser.year_flag == -1:
					break
			users_name = ArticleParser.users
			print users_name
			if ArticleParser.year_flag == -1:
				break
		ArticleParser.close()
	file_handle.close()

if __name__ == '__main__':
	main()
