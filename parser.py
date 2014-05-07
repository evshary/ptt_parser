#!/usr/bin/python

from HTMLParser import HTMLParser
import urllib2

class MyHTMLParser(HTMLParser):
	def handle_starttag(self, tag, attrs):
		print "Start Tag:", tag
	def handle_endtag(self, tag):
		print "End Tag:", tag
	def handle_data(self, data):
		print "Data:", data

def main():
	req = urllib2.Request("http://www.google.com")
	response = urllib2.urlopen(req)
	htmlSrc = response.read()
	parser = MyHTMLParser()
	parser.feed(htmlSrc)
	parser.close()

if __name__ == '__main__':
	main()
