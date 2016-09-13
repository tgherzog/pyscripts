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

### Reading the command line ###

**Note:** in most cases it's easier to process the command line with the [docopt][docopt] library.
````
import sys

first,second = sys.argv[1:3]

````


### Regex ###

````
import re

m = re.search('(.+)#', string_to_search)
if m is not None:
  matching_string = m.group(1)

````


[docopt]: http://docopt.org
