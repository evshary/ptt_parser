#!/usr/bin/python
# -*- coding: utf-8 -*-

from HTMLParser import HTMLParser
import urllib2
import pdb
import MySQLdb

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
		self.users = {}
		self.name_flag = 0
		self.year_flag = 0
		self.meta_flag = 0

	def handle_starttag(self, tag, attrs):
		if tag == "span" and ("class","f3 hl push-userid") in attrs:
			self.name_flag = 1
	
	def handle_endtag(self, tag):
		#push-userid flag should be unset
		if tag == "span" and self.name_flag == 1:
			self.name_flag = 0

	def handle_data(self, data):
		#Get the time
		if self.year_flag == 1:
			self.meta_flag = 0
			if "2014" not in data:
				self.year_flag = -1
			else:
				self.year_flag = 0
		data = data.strip()
		#If the article is not in 2014, neglect it
		if self.year_flag != -1 and data != '':
			#Get the pushers
			if self.name_flag == 1:
				try:
					self.users[data][1] += 1
				except:
					self.users[data] = [0,1]
			#Get the author
			elif self.name_flag == 2:
				data = data.split(" ")[0]
				try:
					self.users[data][0] += 1
				except:
					self.users[data] = [1,0]
				self.name_flag = 0
	
			if data == u"作者" and self.meta_flag == 1:
				self.name_flag = 2
			elif data == u"時間" and self.meta_flag == 1:
				self.year_flag = 1
	
def main():
	global BaseURL
	file_handle = open("board.txt", "r")
	for board in file_handle:
		board = board.strip()
		board_users = {}
		page = "/bbs/"+board+"/index.html"
		ArticleParser = MyArticleParser()
		while True:
			links = []
			count_2013 = 0
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
				#try to access the article
				while True:
					bbsURL = BaseURL+article
					print bbsURL
					try:
						htmlSrc = urllib2.urlopen(urllib2.Request(bbsURL)).read()
						htmlSrc = htmlSrc.decode('utf-8')
						ArticleParser.meta_flag = 1
						ArticleParser.feed(htmlSrc)
						break
					except:
						if try_count > 5:
							with open("log.txt", "a") as logfile:
								logfile.write(bbsURL+"\n")
							break
						else:
							try_count += 1
						continue
				if ArticleParser.year_flag == -1:
					if count_2013 != 19:
						ArticleParser.year_flag = 0
						count_2013 += 1
					else:
						break
			if ArticleParser.year_flag == -1:
				break
		board_users = ArticleParser.users
		ArticleParser.close()
			
		#write into db
		with open("db_info", "r") as db_info:
			db_host = db_info.readline().strip()
			db_user = db_info.readline().strip()
			db_pass = db_info.readline().strip()
			db_name = db_info.readline().strip()
		db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_name)
		cursor = db.cursor()
		cursor.execute("CREATE TABLE `"+board+"` (user VARCHAR(20), article_count INT(5), push_count INT(5));")
		db.commit()
		for user_name in board_users:
			(article_count,push_count) = board_users[user_name]
			try:
				sql = u"INSERT INTO `"+board+"` (user, article_count, push_count) values (%s,"+str(article_count)+","+str(push_count)+");"	
				cursor.execute(sql, user_name)
			except:
				continue
				#pdb.set_trace()
				#with open("error.txt", "w") as error_log:
				#	error_log.write(sql % user_name)
		db.commit()
		cursor.close()
		db.close()
	file_handle.close()

if __name__ == '__main__':
	main()
