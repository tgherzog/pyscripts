#!/usr/bin/python

"""

Diagnose and clean the strong-pm.json file

Usage:
  strongpmfix.py [--info] FILE

Options:
  --info, -i     print information (don't fix)
"""

import json
import sys
from docopt import docopt

options = docopt(__doc__)

with open(options['FILE']) as json_file:
  data = json.load(json_file)
  if options['--info']:
      print "%-20s %10s %10s" % ('Variable', 'Next ID', 'Size')
      for elem in ['ServiceProcess', 'AgentTrace']:
          print "%-20s %10d %10d" % (elem, data['ids'][elem], len(data['models'][elem].keys()))

  else:
      data['ids']['ServiceProcess'] = 1
      data['ids']['AgentTrace'] = 1
      data['models']['ServiceProcess'] = {}
      data['models']['AgentTrace'] = {}

      print json.dumps(data, indent=4)
