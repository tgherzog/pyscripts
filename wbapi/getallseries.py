
'''
Script to export all indicators from all databases to a 3-column CSV file

Usage:
  getallseries.py CSV
  
Options:

  CSV			Name of CSV file
  
'''

import wbgapi as wb
import csv
import logging
from wbgapi import APIError
from docopt import docopt

config = docopt(__doc__)

# I would ordinarily prefer to write the CSV to sys.stdout but on Windows
# that was causing all kinds of line ending and encoding errors, so I had
# to write the interface in a way that I could explicitly open the file stream

with open(config['CSV'], 'w', encoding='utf-8', newline='') as csvfile:
	writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
	writer.writerow(['db', 'cets', 'name'])
	for db in wb.source.list():
		try:
			for elem in wb.series.list(db=db['id']):			
				writer.writerow([db['id'], elem['id'], elem['value']])
		except APIError:
			# some databases such as PEFA_TEST are broken
			logging.warning('Unexpected API response for {} ({})'.format(db['id'], db['name']))
