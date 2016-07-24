import feedparser
import re
import string
from html.parser import HTMLParser
from nltk.corpus import stopwords


# Strip HTML tags from http://stackoverflow.com/questions/753052/strip-html-
# from-strings-in-python


class HTMLStripper(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.reset()
		self.fed = []
	def handle_data(self, d):
		self.fed.append(d)
	def get_data(self):
		return ' '.join(self.fed)

def strip_tag(html):
	s = HTMLStripper()
	s.feed(html)
	return s.get_data()

def generateWordVector(url):
	"""
	Returns a tuple of blog title and word frequency dictionary.
	url: rss url of blog
	"""
	text = feedparser.parse(url)
	word_frequencies = {}
	
	if 'title' not in text.feed or not text.feed.title:
		raise ValueError('The following website is not correct or has an empty title: {} '.format(url))
	
	for posts in text.entries:
		if 'summary' in posts:
			summary = posts['summary']
		elif 'description' in posts:
			summary = posts['description']
		else:
			continue
		if not summary: continue
		summary = strip_tag(summary)
		summary = summary.lower()
		summary = re.sub(r'[^\w\s\d]','',summary)
		# remove non-alphabetic characters 
		summary = re.findall(r'[^\W\d]+', summary)
		for words in summary:
			if words in cached_stop_words:
				continue
			else:
				word_frequencies.setdefault(words, 0)
				word_frequencies[words] += 1

	return text.feed.title, word_frequencies

blog_word_frequencies = {}
word_freq = {}
cached_stop_words = stopwords.words('english')
cached_stop_words.extend(['also','th','x','go','\u2013'])
cached_stop_words.append('')


for url in open('./data/rssfeedurls.txt'):
	title, word_count = generateWordVector(url)
	word_freq[title] = word_count
	
	for word, count in word_count.items():
		blog_word_frequencies.setdefault(word, 0)
		if count > 1:
			blog_word_frequencies[word] += 1

word_list = []
for words, counts in blog_word_frequencies.items():
	# only use words that appear in at least 3 blogs
	# get rid of irrelevant terms
	if counts >= 4:
		word_list.append(words)

out = open('./data/blogsdata.txt', 'w')
out.write('Blog')
for words in word_list:
	out.write('\t%s' % words)
out.write('\n')
for sites, word_counts in word_freq.items():
	out.write(sites)
	for words in word_list:
		if words in word_counts:
			out.write('\t%d' % word_counts[words])
		else:
			out.write('\t0')
	out.write('\n')



