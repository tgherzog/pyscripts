#!/usr/bin/python

"""
Crawls a site and reports a list of all links

Usage:
  linklist.py [--depth=NUM --print-links --print-images --host=HOST] URL

Options:
  --depth:           maximum recursive depth, 0 disables recursive scanning  [default: 0]
  --print-links:     print hyperlinks only
  --print-images:    print image links only
  --host:            only print links from HOST

"""

from docopt import docopt
import requests
import re
import sys
import urlparse
from BeautifulSoup import BeautifulSoup

config = docopt(__doc__, version="version " + "0.1")

if config['--print-images'] == False and config['--print-links'] == False:
  config['--print-images'] = True
  config['--print-links']  = True

config['--verbose'] = True

base_url = config['URL']
base_url_parts = urlparse.urlparse(base_url, 'http')
m = re.search('(.+)/', base_url_parts.path)
if m is None:
    base_url_parts = base_url_parts._replace(path='')
else:
    base_url_parts = base_url_parts._replace(path=m.group(1))

links = {}
images = {}
task_list = {}
depth = 0

def task_key(url):
    parts = urlparse.urlparse(url)
    parts = parts._replace(scheme='')
    return urlparse.urlunparse(parts).lower()
    
def harvest(url, origUrl, srcUrl):
    global links, images, task_list, base_url_parts, config, depth

    # print >> sys.stderr, "Tasks: ", task_list

    url_ = url
    url = re.sub('#.+', '', url)
    if task_list.get(task_key(url)) == True:
      if config['--verbose']:
      	print >> sys.stderr, "Skipping %s" % (url_)

      return

    task_list[task_key(url)] = True

    if config['--verbose']:
    	print >> sys.stderr, "Scanning %s (level %d)" % (url, depth)

    response = requests.get(url)
    if response.status_code != 200:
      if config['--verbose']:
	print >> sys.stderr, "  Error: %d, Original: %s, From: %s" % (response.status_code, origUrl, srcUrl)

      return

    soup = BeautifulSoup(response.text)

    # harvest images
    for img in soup.findAll('img'):
      src = img.get('src')
      if src is not None:
	parts = urlparse.urlparse(src)
	host = base_url_parts.netloc if parts.netloc == '' else parts.netloc
	if config['--host'] is None or config['--host'].lower() == host:
	  if images.get(src) is None:
	      images[src] = {url: True}
	  else:
	      images[src][url] = True

    # harvest links
    for link in soup.findAll('a'):
      href = link.get('href')
      if href is not None:
        parts = urlparse.urlparse(href)
        if parts.scheme == '':
            parts = parts._replace(scheme=base_url_parts.scheme)

        if parts.netloc == '':
            parts = parts._replace(netloc=base_url_parts.netloc)

        if parts.path == "" or parts.path[0] != '/':
            parts = parts._replace(path=base_url_parts.path + '/' + parts.path)

        parts = parts._replace(scheme=parts.scheme.lower())
        parts = parts._replace(netloc=parts.netloc.lower())

        full_link = urlparse.urlunparse(parts)
	if config['--host'] is None or config['--host'].lower() == parts.netloc:
	  if links.get(full_link) is None:
	    links[full_link] = {url: True}
	  else:
	    links[full_link][url] = True

        if depth < int(config['--depth']):
            if parts.scheme == 'http' or parts.scheme == 'https':
                if parts.netloc == base_url_parts.netloc:
                    depth = depth + 1
                    harvest(full_link, href, url)
                    depth = depth - 1


harvest(base_url, base_url, '(TOP)')

if config['--print-links']:
  for url,sources in links.iteritems():
    # print "  %4d %s" % (count, url)
    print url
    for src,count in sources.iteritems():
      print "  %s" % (src)

if config['--print-images']:
  for url,sources in images.iteritems():
    # print "  %4d %s" % (count, url)
    print url
    for src,count in sources.iteritems():
      print "  %s" % (src)
