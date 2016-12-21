#!/usr/bin/python -u

"""

Diagnostic program to test and report country/indicator combinations from subnational API

Usage:
  apitest.py URL [--mrv] [--retry COUNT] [--countries COUNTRY_LIST] [--indicators INDICATOR_LIST]

Options:
  -c, --countries COUNTRY_LIST     List of ISO3 country codes, comma-separated. Will use the list provided by the API if missing

  -i, --indicators INDICATOR_LIST  List of indicator codes, comma-separated. Will use the list provided by the API if missing

  -m, --mrv                        MRV test: make sure MRNEV variant returns data consistent with the ordinary variant

  -r, --retry COUNT                Retry count: 0 if omitted (e.g. --retry=3 makes 3 attempts)

Examples:

  apitest.py http://api.worldbank.org/v2/country/{country}/subnational/indicator/{indicator5}/?source=5&format=json&MRNEV=1&per_page=9999


"""

import sys
import re         # regex
import requests   # HTTP requests
import urlparse
import urllib


from docopt import docopt

def fetch(url, config):

  for i in range(0, int(config['--retry'])):
    try:
      response = requests.get(url)
      return response
    except:
      continue

  return None

def test(url, config):

  if config['--mrv']:
    parts = urlparse.urlparse(url)
    q     = urlparse.parse_qs(parts.query)
    q['format'] = 'json'

    if 'MRNEV' in q:
      del q['MRNEV']

    parts = parts._replace(query=urllib.urlencode(q, doseq=True))
    url = urlparse.urlunparse(parts)

    q['MRNEV'] = 1
    parts = parts._replace(query=urllib.urlencode(q, doseq=True))
    url2 = urlparse.urlunparse(parts)

    resp1 = fetch(url, config)
    if resp1 is None:
      print "NO RESPONSE: " + url
      return

    if resp1.status_code != 200:
      print "{0:<6} {1:<12} {3:<10} {2}".format(resp1.status_code, resp1.reason, url, '--')
      return

    try:
      data1 = resp1.json()
      size1 = data1[0]['total']
    except:
      print "JSON ERROR: " + url
      return

    resp2 = fetch(url2, config)
    if resp2 is None:
      print "NO RESPONSE: " + url2
      return

    if resp2.status_code != 200:
      print "{0:<6} {1:<12} {3:<10} {2}".format(resp2.status_code, resp2.reason, url2, '--')
      return

    try:
      data2 = resp2.json()
      size2 = data2[0]['total']
    except:
      print "JSON ERROR: " + url2

    print "{0:<6} {1:<12} {3:<10} {2}".format(resp2.status_code, resp2.reason, url, 'MATCH' if (size1>0) == (size2>0) else 'NO MATCH')
    return

      
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
  if config['--retry'] is None:
    config['--retry'] = 1

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
# sys.exit(0)

if country_test and indicator_test:
  for c in countries:
    for i in indicators:
      kv = {'country': c, indicator_key: i}
      test( url.format(**kv), config )

elif country_test:
  for c in countries:
    kv = {'country': c}
    test( url.format(**kv), config )

elif indicator_test:
  for i in indicators:
    kv = {indicator_key: i}
    test( url.format(**kv), config )

else:
  test(url, config)
