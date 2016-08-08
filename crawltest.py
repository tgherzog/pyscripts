#!/usr/bin/python

"""

crawltest.py: crawl the datasite (indicators and countries) and report any non-200 errors

Usage:
  crawltest.py [--full]
  crawltest.py [--full] SERVER

Options:
  --full:         Full test (include scripts, stylesheets and images)

"""

import requests
import sys
import re
import urlparse
from docopt import docopt
from pyquery import PyQuery
from progress.bar import Bar

config = docopt(__doc__, version="v0.1")

if config['SERVER'] is None:
  config['SERVER'] = 'http://data.worldbank.org'

default_parts = urlparse.urlparse(config['SERVER'])

def full_url(url):
  global default_parts

  parts = urlparse.urlparse(url)
  if parts.scheme == '':
    parts = parts._replace(scheme=default_parts.scheme)
  if parts.netloc == '':
    parts = parts._replace(netloc=default_parts.netloc)

  return urlparse.urlunparse(parts)

def test_links(response, origUrl):
  global default_parts

  doc = PyQuery(response.text)
  urls = []

  elems = doc('link')
  for elem in elems:
    href = PyQuery(elem).attr('href')
    rel  = PyQuery(elem).attr('ref')
    if type(href) is str and type(rel) is str and rel == 'stylesheet':
      urls.append(full_url(href))

  elems = doc('script')
  for elem in elems:
    href = PyQuery(elem).attr('src')
    if type(href) is str:
      urls.append(full_url(href))

  for url in urls:
    parts = urlparse.urlparse(url)
    if parts.netloc == default_parts.netloc:
        response2 = requests.get(url)
        if response2.status_code != 200:
          print "\r  %d %s (in %s)" % (response2.status_code, path, origUrl) 

# start by getting an indicator list: this comes from the API because it's too difficult
# to get an indicator list from the target site
response = requests.get('http://api.worldbank.org/v2/en/indicator?source=2&per_page=2000&format=json')
indicators = response.json()
indicators = ['/indicator/' + elem['id'] for elem in indicators[1]]

doc = PyQuery(config['SERVER'] + '/country')

links = doc('section.nav-item ul li a')
countries = []
for elem in links:
  href = PyQuery(elem).attr('href')
  parts = urlparse.urlparse(href)
  countries.append(parts.path)

print 'INDICATOR TEST'
bar = Bar('Testing', max=len(indicators), width=50)
for path in indicators:
  url = config['SERVER'] + path
  response = requests.get(config['SERVER'] + path)
  bar.next()
  if response.status_code != 200:
    print "\r %d %s" % (response.status_code, path)
  elif config['--full']:
    test_links(response, url)

print 'COUNTRY TEST'
bar = Bar('Testing', max=len(countries), width=50)
for path in countries:
  url = config['SERVER'] + path
  response = requests.get(url)
  bar.next()
  if response.status_code != 200:
    print "\r  %d %s" % (response.status_code, path)
  elif config['--full']:
    test_links(response, url)

print ""
