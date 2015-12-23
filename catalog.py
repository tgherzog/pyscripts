#!/usr/bin/python

import sys
import re
import requests
import string


url = "http://api.worldbank.org/v2/datacatalog?per_page=300&format=json"

response = requests.get(url)
json = response.json()['datacatalog']


nRelevantDatasets = 0
nRelevantAPIIndicators = 0
for dataset in json:
  id = dataset['id']
  name = "???"
  isAfrDataset=False
  sourceid=None
  for field in dataset['metatype']:
    if field['id'] == 'economycoverage':
      economies = string.replace(field['value'], " ", "")
      economies = string.split(economies, ",")
      if 'MNA' in economies or 'SSA' in economies:
        isAfrDataset=True
        nRelevantDatasets += 1
    elif field['id'] == 'apisourceid':
      sourceid = field['value']
    elif field['id'] == 'name':
      name = field['value']

  if isAfrDataset:
    if sourceid is not None and sourceid.isnumeric():
        indicatorsResponse = requests.get("http://api.worldbank.org/sources/{source}/indicators?format=json&per_page=9999".format(source=sourceid))
        try:
            indicatorCount = indicatorsResponse.json()[0]['total']
            nRelevantAPIIndicators += indicatorCount
            print "%3s %-50s %5s" % (id, name, indicatorCount)
        except:
            print "Couldn't fetch indicators for sourceid %s in %s" % (sourceid, id)
    else:
        print "%3s %-50s n/a" % (id, name)

print "Total: %d datasets, %d API indicators" % (nRelevantDatasets, nRelevantAPIIndicators)

