#!/usr/bin/python -B
"""
Produces a report from a data.json file showing coverage of core indicators

Usage:
  report.py PATH [--national | --subnational] [--missing-only]

Options:
  -n, --national       Display national detail (default)
  -s, --subnational    Display sub-national detail: relatively long
  -m, --missing-only   Only display subnational regions with mis-matched shapefiles

"""

import sys
import json
from pprint import pprint
from docopt import docopt
from os import path
import time
import default

if __name__ != '__main__':
  sys.exit(0)

legend_symbols = {1: '1', 2: '2', 3: 'C', 4: 'a', 5: 'D', 6: 'E', 7: '*'}

indicators = [
  # from sources/5
  'SN.SH.SVR.WAST.ZS',
  'SN.SH.STA.STNT.ZS',
  'SN.SH.STA.OWGH.ZS',
  'SN.SH.STA.MALN.ZS',
  'SN.SH.STA.WAST.ZS',

  '-',

  # from sources/38
  'SI.POV.NAHC',
  'SI.POV.RUHC',
  'SI.POV.URHC',

  '-',

  # from sources/50
  'SP.POP.TOTL.ZS',
  'SP.POP.TOTL',
]


def print_report_header():
    print "Data File:  %s" % config['PATH']
    print "Build Date: %s" % time.ctime( path.getmtime(config['PATH']) )
    print 'Indicator order:'
    for item in indicators:
      print "  " + item

    print '''
Key:
1 = Admin Level 1
2 = Admin Level 2
a = Aggregated Level
C = Both Level 1 & Level 2
D = Both Level 1 & Aggregated
E = Both Level 2 & Aggregated
* = All levels
'''


def name_from_country(item):
  return item['name']

def symbol_from_indicator(k, data):
  if k == '-':
    return ' '

  if k in data and data[k] > 0:
    return legend_symbols[data[k]]

  return '.'

def topo_defs(url, id):
    try:
        topopath = path.dirname(url) + '/topojson/' + id + '.json'
        data = json.load( open(topopath) )
        topo = {str(elem['properties']['ADM1_CODE']):elem['properties']['WB_ADM1_NA'] for elem in data['objects'][id]['geometries']}
        return topo
    except:
        return None


config = docopt(__doc__, version="version " + "0.1")

data = json.load( open(config['PATH']) )

countries = [{'id': k, 'name': v['name']} for k,v in data['countries'].iteritems()]
countries.sort(key=name_from_country)

def country_report():
    # report-specific documentation
    print_report_header()
    print ""

    indicator_counts = {k: 0 for k in indicators if k != '-'}

    data_count = row_count = 0

    for elem in countries:
      series_count = 0
      name = elem['name']
      id   = elem['id']
      counts = {k: 0 for k in indicators if k != '-'}
      if id in data['data']:
        row = data['data'][id]
        for series,values in row['indicators'].iteritems():
          section_matches = 0
          for section_key,section in {1: 'adminlevel1', 2: 'adminlevel2', 4: 'aggregates'}.iteritems():
            if section in values and 'max' in values[section]:
              section_matches += 1
              if series in counts:
                counts[series] |= section_key

          if section_matches > 0 and series in indicator_counts:
            series_count += 1
            indicator_counts[series] += 1

      # $exists = file_exists("shp/topojson/$key.topojson") ? 'Y' : 'N';
      exists_on_disk = ' '

      row_count += 1
      
      grid = ''.join([symbol_from_indicator(x,counts) for x in indicators])
      print "{0:>3}  {1:<40} {2:>12} {3:>4} {4}".format(id, name, grid, series_count, exists_on_disk)
      if series_count > 0:
        data_count += 1

    print "\nTotal countries:     {0:4}".format(row_count)
    print "Countries with data: {0:4}".format(data_count)
    print "By series"
    for ind in indicators:
      if ind != '-':
        print "  {0:<18} {1:>4}".format(ind, indicator_counts[ind])


def region_report():
    # report-specific documentation
    if not config['--missing-only']:
        print_report_header()
        print '''X = indicates mismatch between API regions and shape file regions. For aggregate regions, the missing region
    identifers are listed in ().

    Shape file regions and aggregate regions that do not have corresponding regions in the API are listed
    in separate sections for each country. On the map browser these appear in the region list as "No data"
'''

    for item in countries:
      id = item['id']
      if 'adminlevel1' in data['countries'][id]:
        item['regions'] = {key:item['name'] for key,item in data['countries'][id]['adminlevel1'].iteritems()}
      else:
        item['regions'] = {}

    indicator_counts = {k: 0 for k in indicators if k != '-'}

    for elem in countries:
        topo = topo_defs(config['PATH'], elem['id'])
        if not config['--missing-only']:
            print "\n%s (%s)" % (elem['name'], elem['id'])

        country_id = elem['id']
        aggregates = default.ADMINLEVEL1_AGGREGATES[country_id] if country_id in default.ADMINLEVEL1_AGGREGATES else {}

        for region_id,region_name in elem['regions'].iteritems():
            series_count = 0
            counts = {k: 0 for k in indicators if k != '-'}
            if country_id in data['data'] and 'indicators' in data['data'][country_id]:
                for code,ind in data['data'][country_id]['indicators'].iteritems():
                  if code in counts and 'adminlevel1' in ind and region_id in ind['adminlevel1'] and len(ind['adminlevel1'][region_id]) > 0:
                      counts[code] = 1
                      series_count += 1

            grid = ''.join([symbol_from_indicator(x,counts) for x in indicators])
            name = "%s (%s)" % (region_name, region_id)
            if topo == None:
                topo_exist = '?'
            else:
                topo_exist = ' ' if region_id in topo else 'X'

            if config['--missing-only']:
                if topo_exist == 'X':
                    print "\t".join([elem['id'].encode('utf-8'), elem['name'].encode('utf-8'), region_id.encode('utf-8'), region_name.encode('utf-8')])
            else:
                print "  {0:<50}  {1:>12} {2:>4}  {3}".format(name.encode('ascii', 'replace'), grid, series_count, topo_exist)

        # now append adminlevel2 and aggregates: this is tougher b/c data.json doesn't have a pre-defined list of these admin levels
        custom_codes = None
        aggregate_region_count = 0
        if country_id in data['data'] and 'indicators' in data['data'][country_id]:
          for level_id,level in {2: 'adminlevel2', 4: 'aggregates'}.iteritems():
            custom_codes = set()
            for code,ind in data['data'][country_id]['indicators'].iteritems():
              if level in ind and len(ind[level]) > 0:
                for k,v in ind[level].iteritems():
                  if k != 'max' and k != 'min':
                    custom_codes.add(k)

            if len(custom_codes) > 0 and not config['--missing-only']:
              print ""

            for c in custom_codes:
              series_count = 0
              counts = {k: 0 for k in indicators if k != '-'}
              for code,ind in data['data'][country_id]['indicators'].iteritems():
                if code in counts and level in ind and c in ind[level] and len(ind[level][c]) > 0:
                  counts[code] = level_id
                  series_count += 1

              grid = ''.join([symbol_from_indicator(x,counts) for x in indicators])
              if c in aggregates:
                aggregate_region_count += 1
                name = "%s (%s)" % (c, aggregates[c]['name'])
                if topo == None:
                  topo_exist = '?'
                else:
                  # in this case we also include the missing regions
                  stragglers = set([str(i) for i in aggregates[c]['regions']])
                  stragglers = stragglers - set(topo.keys())
                  if len(stragglers) > 0:
                    topo_exist = 'X (' + ",".join([str(i) for i in stragglers]) + ')'
                  else:
                    topo_exist = ' '
              else:
                name = c
                topo_exist = ' '

              if config['--missing-only']:
                  if topo_exist[0] == 'X':
                      for i in stragglers:
                          print "\t".join([elem['id'], elem['name'], str(i), 'n/a'])
              else:
                  print "  {0:<50}  {1:>12} {2:>4}  {3}".format(name.encode('ascii', 'replace'), grid, series_count, topo_exist)

        if config['--missing-only']:
            continue

        # now print topographies that don't have a data match - these will appear as "no data" on the map
        if topo != None and len( set(topo.keys()) - set(elem['regions'].keys()) ) > 0:
            print "\n  Extra Gaul Regions:"

            for k,v in topo.iteritems():
                if k not in elem['regions']:
                  print "    {0} ({1})".format(v.encode('ascii', 'replace'), k)

        # and aggregate definitions with no data match
        if aggregate_region_count > 0 and custom_codes is not None and len( set(aggregates.keys()) - custom_codes ) > 0:
            print "\n  Extra Aggregate Regions:"

            for k,v in aggregates.iteritems():
              if k not in custom_codes:
                print "    {0} ({1})".format(k, v['name'].encode('ascii', 'replace'))

#topo = topo_defs(config['PATH'], 'AFGH')
#print topo
#if topo != None:
#    print 'yes' if '295' in topo else 'no'
#print default.ADMINLEVEL1_AGGREGATES
#sys.exit(0)

if config['--subnational']:
  region_report()
else:
  country_report()
