import nltk
import sys
import random
import re
import StringIO
import urllib
import urllib2
import lxml.html as lh
from lxml import etree

class MarkovGenerator(object):
    def __init__(self, data_file, order=3):
        self.cache = {}
        self.data_file = data_file
	self.order = order
        self.words = self.file_to_words()
        self.num_words = len(self.words)
        self.make_cache()
    def file_to_words(self):
        self.data_file.seek(0)
        data = self.data_file.read()
        words = data.split()
        return words
    def triples(self):
        for i in range(len(self.words) - (self.order - 1)):
	    ret = []
	    for j in range(self.order):
		ret.append(self.words[i+j])
	    yield ret
    def make_cache(self):
        for triple in self.triples():
            key = tuple(triple[:-1])
            if key in self.cache:
                self.cache[key].append(triple[-1])
            else:
                self.cache[key] = [triple[-1]]
    def generate_text(self, size=25):
        seed = random.randint(0, self.num_words-self.order)
	key = []
	for j in range(self.order):
	    key.append(self.words[seed + j])
        gen_words = []
        for i in xrange(size):
            gen_words.append(key[0])
	    key = key[1:]
	    key.append(random.choice(self.cache[tuple(key)]))
        return ' '.join(gen_words)

def get_from_files(filenames):
    titles = []
    for filename in filenames:
	parsed = lh.parse(open(filename, 'r'))
	path = "/html/body/div[@class='gs_r']/div[@class='gs_rt']/h3/a"
	titles += [elem.text_content() for elem in parsed.xpath(path)]
    return titles

def scrape_from_google(author):
    titles = []
    for i in xrange(5):
	url = "http://scholar.google.com/scholar?hl=en&num=100&q=" + author
	headers = {'User-Agent' : "Mozilla/5.0"}
	request = urllib2.Request(url, None, headers)
	html = urllib2.urlopen(request).read()
	parsed = lh.parse(StringIO.StringIO(html))
	path = "/html/body/div[@class='gs_r']/div[@class='gs_rt']/h3/a"
	titles += [elem.text_content() for elem in parsed.xpath(path)]
    return titles

def scrape_from_homepage(url):
    html = urllib.urlopen(url).read()    
    text = nltk.clean_html(html)
    text = " ".join(text.split("\n"))
    titles = re.findall('"([^"]*)"', text)
    return titles

if __name__ == "__main__":
    
    #titles = scrape_from_homepage("http://polymer.bu.edu/~hes/econophysics/")
    
    #titles = get_from_files(['1', '2', '3'])
    
    author_name = sys.argv[1].replace(" ", "+")
    titles = scrape_from_google(author_name)
    
    for i in range(len(titles)):
        titles[i] = titles[i].replace("\n", " ")
        titles[i] = titles[i].replace(",", ".")
        if titles[i][-1] != ".":
            titles[i] += "."
    titles = "\n".join(titles)
    m = MarkovGenerator(StringIO.StringIO(titles), 4)
    text = m.generate_text(60)
    print ".\n".join(text.split(". "))
