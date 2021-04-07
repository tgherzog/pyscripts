
'''
Determines the "master" database for each indicator in the API

Usage:
    buildseriestable.py CSV FILE
    buildseriestable.py --api FILE

Options:
    CSV				CSV input file
	FILE            CSV output file
	--api           Read from the API instead
'''

import pandas as pd
import wbgapi as wb
from wbgapi import APIError
from docopt import docopt
import logging

config = docopt(__doc__)

if config['--api']:
	df = pd.DataFrame()
	for db in wb.source.list():
		try:
			s = wb.series.Series(db=db['id'])
			x = pd.DataFrame({'id': db['id'], 'cets': s.index, 'name': s.values})
			df = pd.concat([df, x])
		except APIError:
			logging.warning('Unexpected API response for {} ({})'.format(db['id'], db['name']))
	
else:
	df = pd.read_csv(config['CSV'])

# from the indicator list build a dictionary of CETS codes and the databases in which they occur
occurrences = {}
for (idx,data) in df.iterrows():
	cets = data['cets']
	id = data['db']
	if occurrences.get(cets):
		occurrences[cets].append(id)
	else:
		occurrences[cets] = [id]

# fetch the list of databases and apply priority weighting
db = pd.DataFrame()
db.index.rename('id', inplace=True)
for elem in wb.source.list():
	db.loc[int(elem['id']), ['code', 'name']] = [elem['code'], elem['name']]
	
db['priority'] = 0

# adjust priorities as follows:
db.loc[ 2, 'priority'] = 5 # WDI above all
db.loc[63, 'priority'] = 4 # then HCI
db.loc[16, 'priority'] = 3 # HNP above education and gender
# everything else in database order (by ID)
db.loc[11, 'priority'] = -1  # Africa development indicators behind everything else
db.loc[57, 'priority'] = -5  # WDI archives is dead last

db_priority = db.reset_index().sort_values(['priority', 'id'], ascending=[False, True])

# next line adds a column set to the highest priority database (first row in db_priority) for each indicator
df['master_db'] = df['cets'].apply(lambda cets: db_priority[db_priority.id.isin(occurrences[cets])].iloc[0]['id'])

# and save
df.to_csv(config['FILE'], index=False)