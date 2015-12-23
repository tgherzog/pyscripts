#!/usr/bin/python -u

"""

Diagnostic program to test and report country/indicator combinations from subnational API

Usage:
  apitest.py URL [--countries COUNTRY_LIST] [--indicators INDICATOR_LIST]

Options:
  -c, --countries COUNTRY_LIST     List of ISO3 country codes, comma-separated. Will use the list provided by the API if missing

  -i, --indicators INDICATOR_LIST  List of indicator codes, comma-separated. Will use the list provided by the API if missing

Examples:

  apitest.py http://api.worldbank.org/v2/country/{country}/subnational/indicator/{indicator5}/?source=5&format=json&MRNEV=1&per_page=9999


"""

import sys
import re         # regex
import requests   # HTTP requests

from docopt import docopt

def test(url):

  try:
    response = requests.get(url)
  except:
    print "NO RESPONSE: " + url
    return

  len  = response.headers.get('content-length') or -1
  code = response.status_code
  msg  = response.reason

  type = response.headers.get('content-type') or ""
  type = type.split(';')[0]

  print "{0:<6} {1:<12} {2:<20} {3:>8} {4}".format(code, msg, type, len, url)


if __name__ == '__main__':
  config = docopt(__doc__, version="version " + "0.1")

  url = config['URL']
  if re.match('https?://\S+', url) == None:
    sys.exit("URL: must begin with http:// or https://");

  country_test=indicator_test=False

  if re.search('{country}', url):
    country_test=True
    if config['--countries']:
      countries = config['--countries'].split(',')
    else:
      countries = []
      list = requests.get('http://api.worldbank.org/v2/subnational/?format=json&per_page=9999')
      for row in list.json()[1]:
        if row.get('id'):
          countries.append(row['id'])

  m = re.search('{indicator(\d+)}', url)
  if m != None:
    indicator_test=True
    indicator_key = 'indicator' + m.group(1)
    if config['--indicators']:
      indicators = config['--indicators'].split(',')
    else:
      indicators = []
      list = requests.get("http://api.worldbank.org/sources/{source}/indicators?format=json&per_page=9999".format(source=m.group(1)))
      for row in list.json()[1]:
        if row.get('id'):
          indicators.append(row['id'])


# print config
# if 'countries' in vars(): print countries
# if 'indicators' in vars(): print indicators

if country_test and indicator_test:
  for c in countries:
    for i in indicators:
      kv = {'country': c, indicator_key: i}
      test( url.format(**kv) )

elif country_test:
  for c in countries:
    kv = {'country': c}
    test( url.format(**kv) )

elif indicator_test:
  for i in indicators:
    kv = {indicator_key: i}
    test( url.format(**kv) )

else:
  test(url)
