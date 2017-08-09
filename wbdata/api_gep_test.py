#!/usr/local/bin/python
# -*- coding: utf-8 -*-

"""
Queries the World Bank data API and returns the most recent Prospects (GEP) data for a country
as reported on the open data website.

Usage:
  api_gep_test.py CODE

"""

from docopt import docopt
import requests
import sys
from datetime import date, datetime

config = docopt(__doc__, version='version ' + '0.1')


base = 'http://api.worldbank.org/v2/en/countries/{}/indicators/NYGDPMKTPKDZ?per_page=20000&format=json'

url = 'http://api.worldbank.org/v2/country/{}?format=json'.format(config['CODE'])
response = requests.get(url)
data = response.json()
if len(data) == 1:
  sys.stderr.write(data[0]['message'][0]['value'] + '\n')
  sys.exit(-1)

url = base.format(config['CODE'])
print "Querying {}".format(url)

response = requests.get(url)
data = response.json()
if len(data) == 1:
  sys.stderr.write(data[0]['message'][0]['value'] + '\n')
  sys.exit(-1)
elif type(data[1]) is not list:
  sys.stderr.write('No data for ' + config['CODE'] + '\n')
  sys.exit(-1)

for row in data[1]:
    status = row.get('obs_status', 'A') or 'A'
    value  = '--' if row['value'] is None else "{:8.3f}".format(row['value'])
    print "{}  {}  {:>8}".format(row['date'], status, value)
