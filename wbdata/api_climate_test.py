#!/usr/local/bin/python
# -*- coding: utf-8 -*-

"""
Queries the World Bank climate API and returns the most recent climate data for a country
as reported on the open data website.

Usage:
  api_climate_test.py CODE

"""

from docopt import docopt
import requests
import sys
from datetime import date, datetime

config = docopt(__doc__, version='version ' + '0.1')


# country code mapping across platforms
code_mapping = {
    'XK': 'XRK', # note: this is a change from the original mapping, where Kosovo=XK
}

base = 'http://climatedataapi.worldbank.org/climateweb/rest/v1/country/cru/{}/month/{}.json'

url = 'http://api.worldbank.org/v2/country/{}?format=json'.format(config['CODE'])
response = requests.get(url)
data = response.json()
if len(data) == 1:
  sys.stderr.write(data[0]['message'][0]['value'] + '\n')
  sys.exit(-1)

value = code_mapping.get(data[1][0]['iso2Code'], data[1][0]['id'])

url = base.format('(tas|pr)', value)
print "Querying {}".format(url)

url = base.format('tas', value)
response = requests.get(url)
temps = response.json()

url = base.format('pr', value)
response = requests.get(url)
precip = response.json()

if len(temps) == 0 or len(precip) == 0:
  sys.stderr.write('No data\n')
  sys.exit(-1)

data = [[None,None] for i in range(12)]
for elem in temps:
    if elem['month'] < len(data):
        data[elem['month']][0] = elem['data']

for elem in precip:
    if elem['month'] < len(data):
        data[elem['month']][1] = elem['data']

print "{:>5}  {:>10}  {:>10}".format('Month', 'Temp', 'Precip')

month = 0
for elem in data:
    tmp = '--' if elem[0] is None else "{:8.3f}".format(elem[0])
    pre = '--' if elem[1] is None else "{:8.3f}".format(elem[1])
    print "{:>5}  {:>10}  {:>10}".format(month+1, tmp, pre)
    month += 1
