#!/usr/bin/python

"""

968test.py: a script for testing http://github.com/wiredcraft/data.worlbank.org/issues/968 - algorithm for related indicators

Usage:
  urltest.py [--limit=LIMIT] CETS_CODE

Options:
  --limit=LIMIT:   Maximum number of matches [default: 8]

"""

from docopt import docopt
import requests
import json
import sys

config = docopt(__doc__, version="v0.1")


# sorts indicators in the priority they should be compared - first by "featured"
def indicator_sort(a, b):
  if a['featured'] != b['featured']:
    return b['featured'] - a['featured']

  a_ = a['name']
  b_ = b['name']
  if a_ < b_:
    return -1
  elif a_ > b_:
    return 1
  else:
    return 0

def load_indicators():

    # first load featured indicators
    response = requests.get('http://api.worldbank.org/v2/source/2/indicators?per_page=10000&format=json&featured=1')
    data = response.json()[1]

    countries = []
    hits = {}
    for elem in data:
      countries.append({'id': elem['id'], 'name': elem['name'], 'featured': 1})
      hits[elem['id']] = True

    # now load all indicators in addition
    response = requests.get('http://api.worldbank.org/v2/source/2/indicators?per_page=10000&format=json')
    data = response.json()[1]

    for elem in data:
      if hits.get(elem['id']) is None:
        countries.append({'id': elem['id'], 'name': elem['name'], 'featured': 0})

    countries.sort(indicator_sort)
    return countries


def match_mode(cets, i):

  s = cets.split('.')
  while len(s) < 3:
    s.append('')

  if i == 0:
    # A.B.C
    return '.'.join([ s[0], s[1], s[2] ])
  elif i == 1:
    # A'.B.C
    return '.'.join([ s[0][0:1], s[1], s[2] ])
  elif i == 2:
    # A.B
    return '.'.join([ s[0], s[1] ])
  elif i == 3:
    # A'.B
    return '.'.join([ s[0][0:1], s[1] ])
  elif i == 4:
    # A
    return '.'.join([ s[0] ])
  else:
    # A'
    return '.'.join([ s[0][0:1] ])



# Load an indicator array - previously saved from API call
indicators = load_indicators()
cets = config['CETS_CODE']
matches = {}

for i in range(0,6):
  partA = match_mode(cets, i).upper()

  if i == 0:
    pattern = "A.B.C"
  elif i == 1:
    pattern = "A'.B.C"
  elif i == 2:
    pattern = "A.B"
  elif i == 3:
    pattern = "A'.B"
  elif i == 4:
    pattern = "A"
  else:
    pattern = "A'"

  for ind in indicators:
    if cets == ind['id'] or matches.get(ind['id']):
      continue

    partB = match_mode(ind['id'], i).upper()
    if partA is not "" and partA == partB:
      print "%-8s  %-20s  %s" % (pattern, ind['id'], ind['name'])
      matches[ ind['id'] ] = True

  if len(matches) >= int(config['--limit']):
    break
