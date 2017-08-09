#!/usr/local/bin/python

"""
Queries the World Bank projects API and returns summary data, as reported on the
open data website.

Usage:
  api_project_test.py [--topic | --sector | --theme] [--detail YEAR] CODE

Options:
  --topic, -t           query by topic id
  --sector, -s          query by sector code
  --theme, -m           query by theme id
  --detail YEAR         show details for (fiscal) YEAR

"""

from docopt import docopt
import requests
import sys
from datetime import date, datetime

config = docopt(__doc__, version='version ' + '0.1')


# country code mapping across platforms
code_mapping = {
  'CD': 'ZR',
  'KV': 'XK',
  'TL': 'TP',
  'YE': 'RY',
}

base = 'http://search.worldbank.org/api/v2/projects?format=json&rows=20000&prodline_exact=GU^PE&status_exact=Active^Closed'

value = config['CODE']
if config['--topic']:
    sys.stderr.write('Unsupported\n')
elif config['--sector']:
    key = 'mjsectorcode_exact'
elif config['--theme']:
    key = 'mjthemecode_exact'
else:
    key = 'countrycode_exact'
    if len(value) == 3:
        response = requests.get('http://api.worldbank.org/v2/country/' + value + '?format=json')
        data = response.json()
        if len(data) == 1:
            sys.stderr.write(data[0]['message'][0]['value'] + '\n')
            sys.exit(-1)

        value = data[1][0]['iso2Code']

    value = code_mapping.get(value, value)

url = base + '&fl=countrycode,boardapprovaldate,totalamt&%s=%s&frmYear=1947&toYear=%d' % (key, value, date.today().year)

print "Querying {}".format(url)

response = requests.get(url)
data = response.json()
result = {}
for key,row in data['projects'].iteritems():
    cDate = datetime.strptime(row['boardapprovaldate'], '%Y-%m-%dT%H:%M:%SZ')

    # determine the fiscal year, starting July 1st
    year = cDate.year if cDate.month < 7 else cDate.year+1
    value = int(row['totalamt'].replace(',',''))
    if config['--detail'] is not None:
        if year == int(config['--detail']):
            print "{}  {:>4d}  {}  {:>14,d}".format(row['id'], year, cDate.strftime("%Y-%m-%d"), value)

    elif result.get(year):
        result[year]['count'] += 1
        result[year]['total'] += value
    else:
        result[year] = {'count': 1, 'total': value}

if config['--detail'] is None:
    years = result.keys()
    years.sort()
    for i in years:
        print "{:>4d}    {:>5d}    {:>14,d}".format(i, result[i]['count'], result[i]['total'])
