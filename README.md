# pyscripts

Variously useful python scripts I've developed along the way as I've been
slowly improving my python knowledge and skills. Collectively this project
demonstrates various things you can do in python.

## Cookbook ##

Notes and short code snippets for common tasks

### Reading from STDIN ###

````
import sys

for line in sys.stdin:
  if line == '':
    break

  line = line.rstrip('\r\n')
  # do something useful

````

### Regex ###

````
import re

m = re.search('(.+)#', string_to_search)
if m is not None:
  matching_string = m.group(1)

````
