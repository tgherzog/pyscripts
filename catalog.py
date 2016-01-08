#!/usr/bin/python

# This is a script for calculating a rough estimate of indicators in
# the open data catalog relevant to "Africa"

# 1. Start by querying the catalog API to get a list of all datasets
# 2. Exclude datasets that don't have MENA or SSA in the economy coverage field
# 3. Exclude datasets with no sourceid (not in the API)
# 4. Call data API to retrieve number of indicators in the dataset

# Obviously very rough, doesn't address datasets not in the API, and may have some double counting

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

