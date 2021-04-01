
'''
Script that iterates the API databases to check if the indicator endpoints are internally consistent.
See https://gist.github.com/tgherzog/f213ff55b254a940d3e18e038da01495 for sample reports

Usage:
  apitest1.py [--deep] [ID]

Options:

  --deep:               Deep test (compare indicator lists not just counts)
'''

from docopt import docopt
import wbgapi as wb
import requests
from urllib.parse import urlencode
from itertools import zip_longest as zip_all
import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.WARNING)

config = docopt(__doc__)

root_api = 'https://api.worldbank.org/v2'

sources = {row['id']: row for row in wb.source.list()}
if config['ID']:
    rows = [config['ID']]
else:
    rows = sources.keys()

for id in rows:
    source = sources[id]

    try:
        url = '/indicators?{}'.format( urlencode({'format': 'json', 'per_page': 1, 'source': source['id']}))
        old_count = requests.get(root_api + url).json()[0]['total']

        concept = wb.source.concepts(source['id'])['series']['key']
        url = '/sources/{}/{}?{}'.format(source['id'], concept, urlencode({'format': 'json', 'per_page': 1}))
        new_count = requests.get(root_api + url).json()['total']

        old_series = set()
        series_counts = {}
        for row in wb.fetch('indicators', {'source': source['id']}):
            old_series.add(row['id'])
            series_counts[row['id']] = series_counts.get(row['id'], 0) + 1

        series_counts = {k:v for k,v in series_counts.items() if v > 1}
        new_series = set([row['id'] for row in wb.series.list(db=source['id'])])

    except:
        logging.warning('Unexpected API response for {} ({})'.format(url, source['name']))
        old_count = new_count = old_series = new_series = series_counts = None

    if old_count is not None:
        if config['--deep']:
            if old_series != new_series:
                print('{:60} {:10} {:6} {:6}'.format(source['name'], source['lastupdated'], old_count, new_count))
                print('{:5} {:35} {:35}'.format('', 'Kruft', 'Missing'))
                for elem in zip_all(old_series - new_series, new_series - old_series):
                  print('{:5} {:35} {:35}'.format('', elem[0] or '', elem[1] or ''))

        elif old_count != new_count or len(series_counts):
            print('{:60} {:10} {:6} {:6}'.format(source['name'], source['lastupdated'], old_count, new_count))

        if len(series_counts):
            for k,v in series_counts.items():
              print('{:5} {} listed {} times in master indicator table'.format('', k, v))
