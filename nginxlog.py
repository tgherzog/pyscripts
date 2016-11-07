#!/usr/bin/python

"""

Process nginx error logs and produce data or graphs. Input files
can be either text or compressed (with .gz suffix)

Usage:
  nginxlog.py [--since=yyyy/mm/dd | --only=yyyy/mm/dd] [--error | --paths | --daily | --hourly] [--data | --graph] [--all --limit=LIMIT] FILE...

Options:
  --error:      report errors by type (implies --data)

  --paths:      report errors by simplified URLs (implies --data)

  --hourly:     report errors by hour

  --daily:      report errors by day (default)

  --since:      limit to data since yyyy/mm/dd

  --only:       single-day report

  --data:       output tab-delimited data

  --graph:      output chart using matplotlib (default)

  --all:        report all errors, not just fatal ones (not compatible with --paths)

  --filter:     just one specified error type: LIMIT is an integer
   
"""

import requests
from urlparse import urlparse
import sys
import re
import subprocess
from docopt import docopt
from datetime import date
import matplotlib.pyplot as plot

def chartlabel(i):
  return '/'.join(i.split('/')[1:3]) if len(i.split('/')) == 3 else i

def simplified_url(row):

  m = re.search('request: "(\w+) (\S+) \S+"', row)
  if m is None:
    return None

  parts = urlparse(m.group(2))
  path = parts.path
  if path == '':
    return None

  if re.search('^/(country|pays|pais)/', path):
    path = '/country/[id]'
  elif re.search('^/(indicator|indicador|indicateur)/', path):
    path = '/indicator/[id]'

  return m.group(1) + ' ' + path

options = docopt(__doc__)
#print options
#sys.exit(0)

# sanity checks on options
if not options['--daily'] and not options['--hourly']:
  options['--daily'] = True

if not options['--data'] and not options['--graph']:
  options['--graph'] = True

if options['--paths']:
  options['--all'] = False

if options['--error'] or options['--paths']:
  options['--graph'] = False
  options['--data'] = True

if options['--since'] is not None:
  i = options['--since'].split('/')
  options['--since'] = date(int(i[0]), int(i[1]), int(i[2]))

if options['--only'] is not None:
  i = options['--only'].split('/')
  options['--only'] = date(int(i[0]), int(i[1]), int(i[2]))
  if options['--daily']:
    options['--daily']  = False
    options['--hourly'] = True

data = {}
messages = {}

for fref in options['FILE']:
  if fref[-3:] == '.gz':
    p = subprocess.Popen(['gunzip', '-c', fref], stdout=subprocess.PIPE)
    fd = p.stdout
  else:
    fd = open(fref, 'r')

  for row in fd:
    # try to make sure we start with a timestamp: some messages may contain odd carriage returns
    if re.match('^\d{4}', row) == None:
      continue

    # row = row.rstrip('\r\n')
    d,t = row.split()[0:2]
    d2 = d.split('/')

    # sanity check
    if not d2[0].isdigit():
      continue

    m = re.search('\((\d+): (.+?)\)', row)
    if m is None:
      continue

    err = int(m.group(1))
    msg = m.group(2)
    if not messages.get(err):
      messages[err] = msg

    if err in [2] and not options['--all']:
      continue

    if options['--limit'] is not None and err != int(options['--limit']):
      continue

    dt = date(int(d2[0]), int(d2[1]), int(d2[2]))
    if options['--since'] is not None and dt < options['--since']:
      continue

    if options['--only'] is not None and dt != options['--only']:
      continue

    # key = d + ' ' + t.split(':')[0]
    if options['--error']:
      key = err
    elif options['--paths']:
      key = simplified_url(row)
    elif options['--daily']:
      key = d
    else:
      key = t.split(':')[0]

    if key is None:
      continue

    if data.get(key):
      data[key] += 1
    else:
      data[key] = 1

keys = data.keys()
keys.sort()

if options['--data']:
  if options['--error']:
      for key in keys:
        print "%s\t%s\t%d" % (key, messages[key], data[key])
  else:
      for key in keys:
        # d,h = key.split()
        print "%s\t%d" % (key, data[key])
else:
  # see http://matplotlib.org/examples/ticks_and_spines/ticklabels_demo_rotation.html
  x = range(0, len(keys))
  y = [data[key] for key in keys]
  plot.plot(x, y)

  x2 = range(0, len(keys), 2)
  y2 = [chartlabel(keys[i]) for i in x2]
  plot.xticks(x2, y2, rotation='vertical')
  plot.axes().xaxis.grid()

  # adjust margins and such
  plot.margins(0.05, 0.1)
  plot.show()
