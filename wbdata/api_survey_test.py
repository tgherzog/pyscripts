#!/usr/local/bin/python
# -*- coding: utf-8 -*-

"""
Queries the World Bank surveys API and returns the most recent surveys for a country
as reported on the open data website.

Usage:
  api_survey_test.py CODE

"""

from docopt import docopt
import requests
import sys
from datetime import date, datetime
from dateutil.parser import parse as date_parser

reload(sys)
sys.setdefaultencoding('utf8')

config = docopt(__doc__, version='version ' + '0.1')


# country code mapping across platforms
code_mapping = {
    'CI': 'Côte d\'Ivoire',
    'ME': 'Serbia and Montenegro',
    'ST': 'São Tomé and Príncipe',
    'SY': 'Syria',
}

base = 'http://microdata.worldbank.org/index.php/api/catalog/search/format/json/?sort_by=proddate&sort_order=desc&country[]={}'

url = 'http://api.worldbank.org/v2/country/{}?format=json'.format(config['CODE'])
response = requests.get(url)
data = response.json()
if len(data) == 1:
  sys.stderr.write(data[0]['message'][0]['value'] + '\n')
  sys.exit(-1)

value = code_mapping.get(data[1][0]['iso2Code'], data[1][0]['name'])
url = base.format(value)

print "Querying {}".format(url)
response = requests.get(url)
data = response.json()
n = 0
for row in data['result']['rows']:
  title      = row['title']
  link       = row['url']
  updated    = date_parser(row['created']).strftime('%Y-%m-%d')
  proddate   = row['year_start']
  author_org = row['authoring_entity']
  print '{}  {}  {:<80s}  {}'.format(updated, proddate, title, author_org, link)
