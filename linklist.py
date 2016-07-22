#!/usr/bin/python

"""
Crawls a site and reports a list of all links

Usage:
  linklist.py [--depth=NUM] URL

Options:
  --depth:          maximum recursive depth, 0 disables recursive scanning  (default: 0)

"""

from docopt import docopt
import requests
import re
import urlparse
from BeautifulSoup import BeautifulSoup

config = docopt(__doc__, version="version " + "0.1")

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
    
def harvest(url):
    global links, images, task_list, base_url_parts, config, depth


    task_list[task_key(url)] = True

    print "Scanning %s (level %d)" % (url, depth)

    response = requests.get(url)
    soup = BeautifulSoup(response.text)

    # harvest images
    for img in soup.findAll('img'):
      src = img.get('src')
      if src is not None:
        if images.get(src) is None:
            images[src] = 1
        else:
            images[src] = images[src] + 1

    # harvest links
    for link in soup.findAll('a'):
      href = link.get('href')
      if href is not None:
        parts = urlparse.urlparse(href)
        if parts.scheme == '':
            parts = parts._replace(scheme=base_url_parts.scheme)

        if parts.netloc == '':
            parts = parts._replace(netloc=base_url_parts.netloc)

        if len(parts.path) > 0 and parts.path[0] != '/':
            parts = parts._replace(path=base_url_parts.scheme + '/' + parts.path)

        parts = parts._replace(scheme=parts.scheme.lower())
        parts = parts._replace(netloc=parts.netloc.lower())

        full_link = urlparse.urlunparse(parts)
        if links.get(full_link) is None:
          links[full_link] = 1
        else:
          links[full_link] = links[full_link] + 1

        if config.get('--depth') and depth < config['--depth']:
            if parts.scheme == 'http' or parts.scheme == 'https':
                if parts.netloc == base_url_parts.netloc and task_list.get(task_key(full_link)) is None:
                    depth = depth + 1
                    harvest(full_link)
                    depth = depth - 1


harvest(base_url)

print "Links:"
for url,count in links.iteritems():
  print "  %4d %s" % (count, url)
