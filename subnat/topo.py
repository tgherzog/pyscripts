#!/usr/bin/python
"""
Produces a report from a data.json file showing coverage of core indicators

Usage:
  report.py PATH

"""

import sys
import json
from docopt import docopt
from os import path

if __name__ != '__main__':
  sys.exit(0)

config = docopt(__doc__, version="version " + "0.1")

name = path.basename(config['PATH'])
try:
  if name[-5:] != '.json':
    raise
  id  = name[:-5]
except:
  print "Input file should be a topjson file ending with a .json suffix"
  sys.exit(-1)

data = json.load( open(config['PATH']) )
# features = [{'id': v['WB_ADM1_CO'], 'name': v['WB_ADM1_NA']} for v in data['objects'][id]['geometries']]

for elem in data['objects'][id]['geometries']:
  props = elem['properties']
  # print props
  print "{0:<8} {1}".format(props['ADM1_CODE'], props['WB_ADM1_NA'])

