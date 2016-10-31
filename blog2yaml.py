#!/usr/bin/python

"""

Read the RSS feed of a World Bank blog and return a YAML object, suitable for updating the open data site

Usage:
  blog2yaml.py [--count=<n>] [URL]

Options:
  --count=<n>:     number of posts to report [default: 4]

  
"""

import sys
import untangle
import yaml
import re
from docopt import docopt

options = docopt(__doc__)

# parameter sanity check
options['--count'] = int(options['--count'])
# print options

if options['URL'] is None:
  # read stdin
  input = "".join(sys.stdin.readlines())
else:
  input = options['URL']


obj = untangle.parse(input)
items = obj.rss.channel.item
if len(items) > options['--count']:
  items = items[0:options['--count']]

data = []
for elem in items:
  title = elem.title.cdata
  auth  = elem.dc_creator.cdata.encode('ascii', errors='replace')
  link  = elem.link.cdata.encode('ascii', errors='replace')
  date  = elem.pubDate.cdata.encode('ascii', errors='replace')

  # transformations and reformatting
  # replace John Smith with J. Smith
  m = re.search('^(\w+)\s+(\w+)$', auth)
  if m is not None:
    auth = m.group(1)[0:1] + '. ' + m.group(2)

  # Replace ISO-style date with 'mmm dd, yyyy'
  m = re.search('^(\w+), (\d+) (\w+) (\d+) ', date)
  if m is not None:
    date = m.group(3) + ' ' + m.group(2) + ', ' + m.group(4)

  data.append({'title': title, 'author': auth, 'date': date, 'url': link})

print "TABLE_DATA:"

# safe_dump avoids the distracting string type declarations in the output
print yaml.safe_dump(data, default_flow_style=False, allow_unicode=True)
