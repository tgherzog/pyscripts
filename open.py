#!/usr/bin/python
"""
Opens the URL for a source API call

Usage:
  open.py COUNTRY INDICATOR

"""

from docopt import docopt
from subprocess import call

sources = {
'SN.SH.STA.MALN.ZS': 5,
'SN.SH.STA.OWGH.ZS': 5,
'SN.SH.STA.STNT.ZS': 5,
'SN.SH.STA.WAST.ZS': 5,
'SN.SH.SVR.WAST.ZS': 5,
'SI.POV.NAHC': 38,
'SI.POV.RUHC': 38,
'SI.POV.URHC': 38,
'SP.POP.TOTL': 50,
'SP.POP.TOTL.ZS': 50,
}

if __name__ != '__main__':
  sys.exit(0)

config = docopt(__doc__, version="version " + "0.1")

if config['INDICATOR'] not in sources:
  print "{0}: I don't recognize that indicator" % (config['INDICATOR'])
  sys.exit(-1)

source = sources[config['INDICATOR']]
url = "http://api.worldbank.org/v2/country/{country}/subnational/indicator/{ind}/?source={src}&MRNEV=1&per_page=9999".format(country=config['COUNTRY'], ind=config['INDICATOR'], src=source)

call(["open", "/Applications/Google Chrome.app", url])
