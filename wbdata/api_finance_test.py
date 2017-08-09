#!/usr/local/bin/python

"""
Queries the World Bank finances API and returns summary data, as reported on the
open data website.

Usage:
  api_finance_test.py CODE

"""

from docopt import docopt
import requests
import re
import sys
from datetime import date, datetime

config = docopt(__doc__, version='version ' + '0.1')


# country code mapping across platforms
code_mapping = {
  'CD': 'Congo, Democratic Republic of',
  'CG': 'Congo, Republic of',
  'EG': 'Egypt, Arab Republic of',
  'IR': 'Iran, Islamic Republic of',
  'KP': 'Korea, Democratic People\'s Republic of',
  'KR': 'Korea, Republic of',
  'LA': 'Lao People\'s Democratic Republic',
  'MK': 'Macedonia, former Yugoslav Republic of',
  'VE': 'Venezuela, Republica Bolivariana de',
  'YE': 'Yemen, Republic of',
}

base = 'https://finances.worldbank.org/api/views/{}/rows.json?meta=false'

tasks = [
  'iufu-v5bc', { 'title': 'Summary of IBRD Loans', 'name_key': 10, 'fields': [
    8, '{d}Disbursed as of', 11, 'Original Principal Amount', 12, 'Cancelled Amount',
     14, 'Disbursed Amount', 13, 'Undisbursed Amount', 15, 'Borrowers Obligation'
  ]},
  '7izs-nyu8', { 'title': 'Summary of IDA Credits', 'name_key': 9, 'fields': [
    8, '{d}Disbursed as of', 10, 'Original Principal Amount', 11, 'Cancelled Amount',
     13, 'Disbursed Amount', 12, 'Undisbursed Amount', 14, 'Borrowers Obligation'
  ]},
  '9dma-g62z', { 'title': 'Summary of IDA Grants', 'name_key': 9, 'fields': [
    8, '{d}Disbursed as of', 10, 'Original Principal Amount', 11, 'Cancelled Amount',
     13, 'Disbursed Amount', 12, 'Undisbursed Amount', 14, 'Borrowers Obligation'
  ]},
  'kx5v-mb5q', { 'title': 'Summary of Contributions to FIFs', 'name_key': 9, 'fields': [
    8, '{d}Disbursed as of', 10, 'Amount (USD)'
  ]},
]

# some but not all finance datasets have ISO codes, so we must search by name
response = requests.get('http://api.worldbank.org/v2/country/' + config['CODE'] + '?format=json')
data = response.json()
if len(data) == 1:
  sys.stderr.write(data[0]['message'][0]['value'] + '\n')
  sys.exit(-1)

iso2 = data[1][0]['iso2Code']
country_name = code_mapping.get(iso2, data[1][0]['name'])

while len(tasks) > 0:
  key = tasks.pop(0)
  setup = tasks.pop(0)
  url = base.format(key)
  response = requests.get(url)
  data = response.json()
  for row in data['data']:
    if row[setup['name_key']] == country_name:
        print setup['title']
        while len(setup['fields']) > 0:
            offset = setup['fields'].pop(0)
            label  = setup['fields'].pop(0)
            value  = row[offset]
            r = re.search('^{(\w)}(.+)', label)
            if r:
                label = r.group(2)
                if r.group(1) == 'd':
                    value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d')
            else:
                # numeric
                value = "{:,.0f}".format(float(value))
              
            
            print "  {:<30s} {:>15s}".format(label + ':', value)

        print ""
        break

