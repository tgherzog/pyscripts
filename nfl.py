#!/usr/bin/python -u -W ignore

"""

NFL stats: a program to calculate NFL team standings

Usage:
  nfl.py FILE --compare T1 T2
  nfl.py FILE --update WEEK
  nfl.py FILE --scores T1

"""


import openpyxl
import pprint
import requests
import sys
import re
from docopt import docopt
from pyquery import PyQuery as pq

if __name__ == '__main__':
  config = docopt(__doc__, version="v0.1")
  # print config
  # sys.exit(0)


def safeInt(i):
    
    try:
        i = int(i)
    except ValueError:
        pass

    return i


def getrecord(teams,id,versus=None,withStrength=True):

  record = {'overall': [0,0,0], 'div': [0,0,0], 'conf': [0,0,0], 'vs': [0,0,0], 'common': [0,0,0], 'victory': [0,0,0], 'schedule': [0,0,0]}

  if teams.get(id) == None or teams[id].get('record') == None:
    raise Exception('undefined team record: ' + id)

  if versus != None and teams[versus]['record'] != None:
    # find common opponents
    common = set([t['op'] for t in teams[id]['record']]) & set([t['op'] for t in teams[versus]['record']])
    record['common_opponents'] = ','.join(common)
  else:
    common = None

  for op in teams[id]['record']:
    win = loss = tie = 0
    if op['us'] == '--' or op['them'] == '--':
      continue

    if op['us'] > op['them']:
      win += 1
    elif op['us'] < op['them']:
      loss += 1
    else:
      tie += 1

    record['overall'][0] += win
    record['overall'][1] += loss
    record['overall'][2] += tie

    if teams[op['op']]['div'] == teams[id]['div']:
      record['div'][0] += win
      record['div'][1] += loss
      record['div'][2] += tie
    
    if teams[op['op']]['conf'] == teams[id]['conf']:
      record['conf'][0] += win
      record['conf'][1] += loss
      record['conf'][2] += tie

    if op['op'] == versus:
      record['vs'][0] += win
      record['vs'][1] += loss
      record['vs'][2] += tie
    elif common != None and op['op'] in common:
      record['common'][0] += win
      record['common'][1] += loss
      record['common'][2] += tie

    if withStrength:
      try:
          t2 = getrecord(teams, op['op'], withStrength=False)

          record['schedule'][0] += t2['overall'][0]
          record['schedule'][1] += t2['overall'][1]
          record['schedule'][2] += t2['overall'][2]

          if win == 1:
              record['victory'][0] += t2['overall'][0]
              record['victory'][1] += t2['overall'][1]
              record['victory'][2] += t2['overall'][2]

      except:
          if record.get('missing_records') == None:
              record['missing_records'] = set([])

          record['missing_records'].update([ op['op'] ])


  return record

def getpct(rec):

  games = rec[0] + rec[1] + rec[2]
  wins  = rec[0] + float(rec[2])/2
  if games == 0:
    return 0

  return wins/games

def getrec(rec):

    if rec == None:
        return '?-?-?'

    return "%d-%d-%d" % (rec[0], rec[1], rec[2])

def addscore(teams,team1,team2,us,them):

    if teams.get(team1) == None:
        print "warning: unrecognized team score: {0}".format(team1)
        return

    if teams[team1].get('record') == None:
        teams[team1]['record'] = []

    teams[team1]['record'].append({'op': team2, 'us': us, 'them': them})

teams = {}
wb = openpyxl.load_workbook(config['FILE'])
for row in wb['Divisions']:
  team = row[0].value
  conf = row[2].value
  div  = row[3].value
  if team != None and conf != None and div != None:
    div = conf + '-' + div
    teams[team] = {'name': row[1].value, 'div': div, 'conf': conf}

for row in wb['Scores']:
    if row[0].row == 1 or row[0].value == None:
        continue

    addscore(teams,row[1].value,row[3].value, row[2].value, row[4].value)
    addscore(teams,row[3].value,row[1].value, row[4].value, row[2].value)
        


if config['--compare'] == True:
  try:
    if teams.get(config['T1']) == None:
      raise Exception('undefined team: ' + config['T1'])
    
    if teams.get(config['T2']) == None:
      raise Exception('undefined team: ' + config['T2'])

    if teams[config['T1']].get('record') == None:
      raise Exception('undefined team record: ' + config['T1'])
    
    if teams[config['T2']].get('record') == None:
      raise Exception('undefined team record: ' + config['T2'])

    if teams[config['T1']]['conf'] != teams[config['T2']]['conf']:
      print "Warning: %s and %s are in different conferences" % (config['T1'], config['T2'])

    r1 = getrecord(teams, config['T1'], config['T2'])
    r2 = getrecord(teams, config['T2'], config['T1'])
    
    #report
    print "                           %12s %12s" % (config['T1'], config['T2'])
    step = 1
    print "%d. Overall:                %12s %12s" % (step, getrec(r1['overall']), getrec(r2['overall']))
    step += 1

    print "%d. Head to Head:           %12s %12s" % (step, getrec(r1['vs']), getrec(r2['vs']))
    step += 1

    # step one: compare overall
    if teams[config['T1']]['div'] == teams[config['T2']]['div']:
        print "%d. Division:               %12s %12s" % (step, getrec(r1['div']), getrec(r2['div']))
        step += 1
        print "%d. Common Teams:           %12s %12s" % (step, getrec(r1['common']), getrec(r2['common']))
        step += 1
        print "    (%s)" % r2['common_opponents']
        print "%d. Conference:             %12s %12s" % (step, getrec(r1['conf']), getrec(r2['conf']))
        step += 1
    else:
        print "%d. Conference:             %12s %12s" % (step, getrec(r1['conf']), getrec(r2['conf']))
        step += 1
        print "%d. Common Teams:           %12s %12s" % (step, getrec(r1['common']), getrec(r2['common']))
        step += 1
        print "    (%s)" % r2['common_opponents']
    
    if r1.get('missing_records') != None or r2.get('missing_records') != None:
        print "Can't compute strength of victory or schedule. Missing " + ",".join(r1['missing_records'] | r2['missing_records'])
    else:
        print "%d. Strength of Victory:    %12s %12s" % (step, getrec(r1['victory']), getrec(r2['victory']))
        step += 1
        print "%d. Strength of Schedule:   %12s %12s" % (step, getrec(r1['schedule']), getrec(r2['schedule']))
        step += 1

  except Exception as e:
      print "Error: %s" % (e)

if config['--update'] == True:
    # name lookup
    tids = {elem['name']:id for id,elem in teams.iteritems()}
    ws = wb['Scores']
    row = 2

    for week in range(1,int(config['WEEK'])+1):
        print "Processing week {0}".format(week)
        url = 'http://www.nfl.com/scores/2015/REG{0}'.format(week)
        d = pq(url)
        for elem in d('div.scorebox-wrapper'):
            i = pq(elem)
            (aname,ascore) = (i('.away-team .team-name a').text(), i('.away-team .total-score').text())
            (bname,bscore) = (i('.home-team .team-name a').text(), i('.home-team .total-score').text())

            if tids.get(aname) != None:
                aname = tids[aname]

            if tids.get(bname) != None:
                bname = tids[bname]

            ws.cell(row=row, column=1, value=week)
            ws.cell(row=row, column=2, value=aname)
            ws.cell(row=row, column=3, value=safeInt(ascore))
            ws.cell(row=row, column=4, value=bname)
            ws.cell(row=row, column=5, value=safeInt(bscore))
            row += 1

    while row < ws.max_row:
        for c in range(1,6):
            ws.cell(row=row, column=c, value=None)

    wb.save(config['FILE'])

if config['--scores'] == True:
    try:
        team = config['T1']
        if teams.get(team) == None:
          raise Exception('undefined team: ' + config['T1'])

        if teams[team].get('record') == None:
          raise Exception('undefined team record: ' + config['T1'])

        win = loss = tie = 0
        for game in teams[team]['record']:
            if game['us'] > game['them']:
                wins = '*'
                win += 1
            elif game['us'] == game['them']:
                wins = 't'
                tie += 1
            else:
                wins = ' '
                loss += 1

            print "{0:<20} {1:8} {2:8} {3}".format(game['op'], game['us'], game['them'], wins)

        # print "Record: {0}-{1}-{2}".format(win, loss, tie)
    except Exception as e:
        raise
