#!/usr/bin/python

"""

Prints shapefile information

Usage:
  shpinfo.py FILE [--fields FIELD_LIST] [--max-width MAX]

Options:
  --fields FIELD_LIST     Print specified fields (comma-separated field offsets). If no fields are specified, print header information and quit

  --max-width MAX         Maximum field width


"""

import sys
import os
import shapefile
from docopt import docopt

if __name__ != '__main__':
  sys.exit(0)

config = docopt(__doc__, version="version " + "0.1")

  
reader = shapefile.Reader(config['FILE'])
fields = [x for x in reader.fields]
fields.pop(0) # pop the DELETE field

if config['--fields'] == None:
    n = 0
    for row in fields:
        print "%3d %-20s %-2s %3d %3d" % (n, row[0], row[1], row[2], row[3])
        n += 1

    sys.exit(0)


fld_list = config['--fields'].split(',')

for row in reader.iterRecords():
    for f in fld_list:
      f = int(f)
      type = fields[f][1]
      wid  = fields[f][2]
      if config['--max-width'] and wid > int(config['--max-width']):
        wid = int(config['--max-width'])

      if type == 'C':
        fmt = "%-{0}s".format(wid)
      elif type == 'N':
        fmt = "%{0}d".format(wid)
      elif type == 'F':
        fmt = "%{0}.{1}f".format(wid, fields[f][3])
      else:
        continue

      print fmt % (row[f]),

    print ""
