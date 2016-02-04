#!/usr/bin/python

"""

Report status of datasets in the catalog by comparing the last revision date to the update frequency
to ascertain which datasets are "stale"

Usage:
  catstat.py

"""

import sys
import re
import requests
import datetime
import calendar
from docopt import docopt


url = "http://api.worldbank.org/v2/datacatalog?per_page=800&format=json"


def add_months(src, months):

    month = src.month + months - 1
    year  = int(src.year + month/12)
    month = month % 12 + 1
    day   = min(src.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)

def str_to_month(s):

    try:
        return datetime.datetime.strptime(s, '%B').month

    except:
        return datetime.datetime.strptime(s, '%b').month

def smart_date(s):

    if type(s) != str and type(s) != unicode:
        return None

    s = s.strip().lower()

    if s == 'current':
        return datetime.date.today()

    # dd-mmmm-yyyy
    m = re.search('^(\d+)[,\s\-]+([a-z]+)[,\s\-]+(\d{4})$', s)
    if m != None:
        return datetime.date(int(m.group(3)), str_to_month(m.group(2)), int(m.group(1)))

    # mmmm-yyyy
    m = re.search('^([a-z]+)[,\s\-]+(\d{4})$', s)
    if m != None:
        return add_months(datetime.date(int(m.group(2)), str_to_month(m.group(1)), 1), 1).replace(day=1) - datetime.timedelta(1)

    # yyyy
    m = re.search('^(\d{4})$', s)
    if m != None:
        return datetime.date(int(m.group(1)), 12, 31)

    return None



if __name__ == '__main__':
  config = docopt(__doc__, version="version " + "0.1")

response = requests.get(url)
json = response.json()['datacatalog']

# header
print "%4s  %4s  %-50s  %-12s  %-30s  %-12s   %s" % ('ID', 'API', 'NAME', 'LASTMOD', 'FREQUENCY', 'DUEDATE', 'DAYSLATE')

for dataset in json:
    info = {'id': dataset['id']} 
    for fld in dataset['metatype']:
        key   = fld['id']
        value = fld['value']
        info[key] = value

    # try to create a date structure
    lastRev = smart_date(info.get('lastrevisiondate'))
    freq    = info.get('updatefrequency', '??')
    f = freq.lower()

    # calculate when we would expect the next update, with a bit of slop in some cases
    if lastRev == None:
        duedate = 'n/a'
    elif f == 'daily':
        duedate = lastRev + datetime.timedelta(1)
    elif f == 'weekly':
        duedate = lastRev + datetime.timedelta(7)
    elif f == 'monthly':
        duedate = add_months(lastRev, 1+1).replace(day=1)
    elif f == 'quarterly':
        duedate = add_months(lastRev, 3+1).replace(day=1)
    # elif f == 'annually' or f == 'annual +':
    elif f == 'annually':
        duedate = add_months(lastRev + datetime.timedelta(365), 1).replace(day=1) - datetime.timedelta(1)
    elif f == 'biannually':
        duedate = add_months(lastRev + datetime.timedelta(365 * 2), 1).replace(day=1) - datetime.timedelta(1)
    # elif f == 'triannually' or f == 'no fixed schedule':
    elif f == 'triannually':
        duedate = add_months(lastRev + datetime.timedelta(365 * 3), 1).replace(day=1) - datetime.timedelta(1)
    elif f == 'archived' or f == 'no further updates planned':
        duedate = 'never'
    else:
        duedate = 'indefinite'

    idapi = info['apisourceid'] if info.get('apisourceid') else ''
    if re.search('^\d+$', idapi) == None:
       idapi = ''

    now = datetime.date.today()
    days = "{0:4}".format((now-duedate).days) if type(duedate) == datetime.date and duedate < now else ''

    print "%4d  %4s  %-50s  %-12s  %-30s  %-12s   %s" % (int(info['id']), idapi, info.get('name', '??')[:50].encode('utf-8'), str(info.get('lastrevisiondate')), freq, str(duedate), days)
