#!/usr/local/bin/python

"""
Runs diagnostics on config files, checking to make sure indicators still exist, etc

Usage:
  config_check.py FILE


"""

from docopt import docopt
import yaml
import os
import requests


def check_indicator_groups(path):

    with open(path) as fd:
        setup = yaml.load(fd)

        cets = set()
        for k,v in setup.iteritems():
            for i in v['codes']:
                cets.add(i)

        for i in cets:
            url = 'https://api.worldbank.org/source/{}/indicator/{}?format=json'.format(2, i)
            response = requests.get(url)
            result = response.json()
            if len(result) < 2 or len(result[1]) < 1:
                print '{} doesn\'t exist in the API'.format(i)


config = docopt(__doc__, version='1.0')

filename = os.path.basename(config['FILE'])
if filename == 'indicator_groups.yaml':
    check_indicator_groups(config['FILE'])
