#!/usr/local/bin/python -u

"""
NFL stats: a program to calculate NFL team standings

Script is now designed as a module. To get started, use the command line options or load
interactively and try:

from nfl import NFL
nfl = NFL()
nfl.load('NFLData.xlsx')

nfl('MIN')                       # info and standings for vikings
nfl('NFC')                       # or the NFC conference
nfl.wlt(['MIN', 'GB'])           # win/loss/tie info
nfl.tiebreakers(['DAL', 'PHI'])  # tiebreaker calculations

# and lots more, and yet lots of room for enhancements/improvements ;)

Usage:
    nfl.py update FILE WEEK
    nfl.py team TEAM [--file FILE]
    nfl.py tiebreakers TEAMS... [--file FILE]

Commands:
    update          Update the database FILE, scraping data up to and including WEEK

    team            Report TEAM stats and schedule (division or conference work too)

    tiebreakers     Report tiebreaker analysis for the specified TEAMS

Options:
    --file FILE     Use FILE as database path [default: NFLData.xlsx]

"""


import openpyxl
import pprint
import requests
import sys
import re
import logging
import time
from docopt import docopt
from pyquery import PyQuery
import urllib
from datetime import datetime
import numpy as np
import pandas as pd

class NFLTeam():
    def __init__(self, code, host):

        elem = host.teams_[code]
        self.code = code
        self.name = elem['name']
        self.div  = elem['div']
        self.conf = elem['conf']
        self.host = host

    @property
    def division(self):
        '''Return array of teams in this team's division
        '''
        return self.host.divs_[self.div]

    @property
    def conference(self):
        '''Return array of teams in this team's conference
        '''
        return self.host.confs_[self.conf]

    @property
    def schedule(self):
        '''Return the team's schedule
        '''

        return self.host.schedule(self.code)

    def __repr__(self):
        return '{}: {} ({})\n'.format(self.code, self.name, self.div) + self.host.team_stats(self.code).__repr__()


class NFLDivision():
    def __init__(self, code, host):

        self.code = code
        self.host = host
        self.teams = host.divs_[code]

    def standings(self, rank=False):
        ''' Return division standings

            rank: if True, add 'rank' column based on in-division tiebreaker rules (longer)
                  if False, sort results by game wlt
        '''

        o = self.host.wlt(self.teams)
        d = self.host.wlt(self.teams, within=self.teams)
        z = pd.concat([o, d], keys=['overall', 'division'], axis=1)

        # use division tiebreakers to calculate precise division rank
        if rank:
            t = self.host.tiebreakers(self.teams, ascending=True).xs('pct', axis=1, level=1).transpose()
            t = t.sort_values(list(t.columns), ascending=False)
            t['div_rank'] = range(1, len(t)+1)
            z[('division','rank')] = t['div_rank']
            return z.sort_values(('division','rank'))

        return z

    def __repr__(self):
        z = self.host._stats()
        z = z[z['div']==self.code][['overall','division']]
        return '{}\n'.format(self.code) + z.__repr__()

class NFLConference():
    def __init__(self, code, host):

        self.code = code
        self.host = host
        self.teams = host.confs_[code]

    @property
    def divisions(self):
        return set(map(lambda x: '-'.join([self.code, x]), ['North', 'East', 'South', 'West']))


    def standings(self, rank=False):

        c = None
        for elem in self.divisions:
            z = self.host(elem).standings(rank)
            if type(c) is pd.DataFrame:
                c = pd.concat([c, z])
            else:
                c = z

        z = self.host.wlt(self.teams, within=self.teams)
        c = pd.concat([c['overall'], c['division'], z], keys=['overall', 'division', 'conference'], axis=1)
        c['div'] = c.index.map(lambda x: self.host.teams_[x]['div'].split('-')[1])
        if rank:
            return c.sort_values(['div', ('division','rank')])

        return c.sort_values(['div',('overall','pct')], ascending=[True, False])

    def __repr__(self):
        z = self.host._stats()
        return '{}\n'.format(self.code) + z[z['conf']==self.code][['div', 'overall', 'division', 'conference']].__repr__()

class NFL():

    def __init__(self):
        self.teams_  = {}
        self.divs_   = {}
        self.confs_  = {}
        self.games_  = []
        self.path   = None
        self.max_week = 0
        self.stats = pd.DataFrame()

    def __call__(self, i):

        if i in self.confs_:
            return NFLConference(i, self)

        if i in self.divs_:
            return NFLDivision(i, self)

        if i in self.teams_:
            return NFLTeam(i, self)

    def load(self, path='NFLData.xlsx'):
        ''' Loads data from the specified excel file

            path:   path to Excel file
        '''

        # in case of reload
        self.path   = path
        self.games_ = []
        self.teams_ = {}
        self.divs_  = {}
        self.confs_ = {}
        self.max_week = 0                  

        wb = openpyxl.load_workbook(path, read_only=True)
        for row in wb['Divisions']:
            team = row[0].value
            conf = row[2].value
            div = row[3].value
            if team and conf and div:
                div = '-'.join([conf, div])
                self.teams_[team] = {'name': row[1].value, 'div': div, 'conf': conf}
                if self.divs_.get(div) is None:
                    self.divs_[div] = set()

                self.divs_[div].add(team)

                if self.confs_.get(conf) is None:
                    self.confs_[conf] = set()

                self.confs_[conf].add(team)


        for row in wb['Scores']:
            if row[0].row > 1 and row[0].value:
                # at/ht = away team/home team - same for scores
                game = {'wk': row[0].value, 'at': row[1].value, 'as': row[2].value, 'ht': row[3].value, 'hs': row[4].value}
                game['p'] = game['as'] is not None and game['hs'] is not None
                self.games_.append(game)
                self.max_week = max(self.max_week, game['wk'])

        self.stats = None
        return self

    def _stats(self):

        if self.stats is not None:
            return self.stats

        stat_cols = [('name',''),('div',''),('conf','')]
        stat_cols += list(pd.MultiIndex.from_product([['overall','division','conference', 'vic_stren', 'sch_stren'],['win','loss','tie','pct']]))
        stat_cols += list(pd.MultiIndex.from_product([['misc'],['rank-conf','rank-overall', 'pts-scored', 'pts-allowed']]))
        stats = pd.DataFrame(columns=pd.MultiIndex.from_tuples(stat_cols))

        sched = {k:[] for k in self.teams_.keys()}

        def tally(hcode, acode, hscore, ascore, cat):

            if hscore > ascore:
                stats.loc[hcode, (cat,'win')] += 1
                stats.loc[acode, (cat,'loss')] += 1
                if cat == 'overall':
                    sched[hcode] += [(acode,1)]
                    sched[acode] += [(hcode,0)]
            elif hscore < ascore:
                stats.loc[hcode, (cat,'loss')] += 1
                stats.loc[acode, (cat,'win')] += 1
                if cat == 'overall':
                    sched[hcode] += [(acode,0)]
                    sched[acode] += [(hcode,1)]
            elif hscore == ascore:
                stats.loc[hcode, (cat,'tie')] += 1
                stats.loc[acode, (cat,'tie')] += 1
                if cat == 'overall':
                    sched[hcode] += [(acode,0)]
                    sched[acode] += [(hcode,0)]                   

        for k,team in self.teams_.items():
            stats.loc[k, ['name', 'div', 'conf']] = (team['name'], team['div'], team['conf'])
            stats.loc[k, ['overall','division','conference', 'vic_stren', 'sch_stren', 'misc']] = 0

        for game in self.games_:
            if game['p']:
                tally(game['ht'], game['at'], game['hs'], game['as'], 'overall')
                stats.loc[game['ht'], ('misc', 'pts-scored')] += game['hs']
                stats.loc[game['at'], ('misc', 'pts-scored')] += game['as']
                stats.loc[game['ht'], ('misc', 'pts-allowed')] += game['as']
                stats.loc[game['at'], ('misc', 'pts-allowed')] += game['hs']

                if self.teams_[game['ht']]['div'] == self.teams_[game['at']]['div']:
                    tally(game['ht'], game['at'], game['hs'], game['as'], 'division')
                    tally(game['ht'], game['at'], game['hs'], game['as'], 'conference')
                elif self.teams_[game['ht']]['conf'] == self.teams_[game['at']]['conf']:
                    tally(game['ht'], game['at'], game['hs'], game['as'], 'conference')

        # strength of victory/schedule
        for (k,row) in stats.iterrows():
            for (op,win) in sched[k]:
                stats.loc[k, 'sch_stren'] = (stats.loc[k, 'sch_stren'] + stats.loc[op, 'overall']).values
                if win == 1:
                    stats.loc[k, 'vic_stren'] = (stats.loc[k, 'vic_stren'] + stats.loc[op, 'overall']).values

        # temporary table for calculating ranks - easier syntax
        t = pd.concat([stats['conf'], stats['misc'][['pts-scored','pts-allowed']]], axis=1)
        stats[('misc','rank-overall')] = (t['pts-scored'].rank() + t['pts-allowed'].rank(ascending=False)).rank()

        t['conf-off-rank'] = t.groupby('conf')['pts-scored'].rank()
        t['conf-def-rank'] = t.groupby('conf')['pts-allowed'].rank(ascending=False)
        t['conf-rank'] = t['conf-off-rank'] + t['conf-def-rank']
        stats[('misc', 'rank-conf')] = t.groupby('conf')['conf-rank'].rank()

        for i in ['overall','division','conference', 'sch_stren', 'vic_stren']:
            stats[(i,'pct')] = (stats[(i,'win')] + stats[(i,'tie')]*0.5) / stats[i].sum(axis=1)

        stats.sort_values(['div',('overall','pct')], ascending=(True,False), inplace=True)
        self.stats = stats
        return self.stats


    def reload(self):
        ''' Reloads the previous Excel file
        '''

        if self.path:
            self.load(self.path)

        return self

    def update(self, path, week, year=None):
        ''' Updates the Scores sheet of the specified Excel file by scraping the URL shown in code.
            The file must already exist and have a valid "Divisions" sheet with team names consistent
            with those on the source website.

            path:   path to Excel workbook

            week:   week number (1-based) of last week to load

            year:   season to load; else infer the latest season from the current date
        '''

        if not year:
            dt = datetime.now()
            year = dt.year if dt.month >= 8 else dt.year-1

        self.load(path)
        tids = {v['name']:k for k,v in self.teams_.items()}
        wb = openpyxl.load_workbook(path, read_only=False)
        ws = wb['Scores']
        row = 2

        def safeInt(i):
            try:
                i = int(i)
            except ValueError:
                pass

            return i

        for w in range(1, week+1):
            url = 'https://www.pro-football-reference.com/years/{}/week_{}.htm'.format(year, w)
            try:
                time.sleep(1) # avoid throttling
                d = PyQuery(url=url)('div.game_summaries div.game_summary table.teams')
            except urllib.error.HTTPError as err:
                logging.error('Bad URL: {}'.format(url))
                raise

            logging.info('Processing {}/{}: ({}) - {} games'.format(w, year, url, len(d)))
            for elem in d:
                ateam = PyQuery(PyQuery(elem)('tr:nth-child(2)'))
                bteam = PyQuery(PyQuery(elem)('tr:nth-child(3)'))
                (aname,ascore) = (ateam('td:nth-child(1)').text(), ateam('td:nth-child(2)').text())
                (bname,bscore) = (bteam('td:nth-child(1)').text(), bteam('td:nth-child(2)').text())

                try:
                    aname = tids[aname]
                    bname = tids[bname]
                except KeyError as k:
                    logging.error('{}: unrecognized team name: check the Divisions table'.format(k))
                    raise

                ws.cell(row=row, column=1, value=w)
                ws.cell(row=row, column=2, value=aname)
                ws.cell(row=row, column=3, value=safeInt(ascore))
                ws.cell(row=row, column=4, value=bname)
                ws.cell(row=row, column=5, value=safeInt(bscore))
                row += 1

        # empty the remaining cells
        for row in range(row,ws.max_row):
            for c in range(1,6):
                ws.cell(row=row, column=c, value=None)

        wb.save(path)
        return self

    def set(self, wk, **kwargs):
        ''' Set the final score(s) for games in a given week. You can use this to create
            hypothetical outcomes and analyze the effect on team rankings. Scores
            are specified by team code and applied to the specified week's schedule.
            If the score is specified for only one team in a game, the score of the other
            team is assumed to be zero if not previously set.

            wk:         week number
            **kwargs    dict of team codes and final scores

            # typical example
            set(7, MIN=17, GB=10)

            The above will set the score for the MIN/GB game in week 7 if
            MIN and GB play each other in that week. Otherwise, it will
            set each team's score respectively and default their opponent's scores
            to 0. Scores for bye teams in that week are ignored.
        '''

        # sanity checks
        bogus = set(kwargs.keys()) - set(self.teams_.keys())
        if len(bogus) > 0:
            raise KeyError('Invalid team codes: {}'.format(','.join(bogus)))       

        for elem in self.games_:
            if wk == elem['wk']:
                t = False
                if elem['ht'] in kwargs:
                    elem['hs'] = kwargs[elem['ht']]
                    t = True

                if elem['at'] in kwargs:
                    elem['as'] = kwargs[elem['at']]
                    t = True

                # sanity checks
                if t:
                    elem['hs'] = elem['hs'] or 0
                    elem['as'] = elem['as'] or 0
                    elem['p'] = True

            elif wk < elem['wk']:
                # assuming elements are sorted by week, we can stop at this point
                break

        self.stats = None # signal to rebuild stats
        return self

    def clear(week, teams=None):
        '''Clear scores for a given week or weeks

        week:   can be an integer, range or list-like. Pass None to clear all (for whatever reason)
        '''

        if type(week) is int:
            week = [week]

        for elem in self.games_:
            if week is None or elem['wk'] in week:
                elem['p'] = False
                elem['hs'] = elem['as'] = None

        self.stats = None
        return self


    def games(self, teams=None, limit=None, allGames=False):
        ''' generator to iterate over score data

            teams:      code or list-like of teams to fetch

            limit:      range or list-like of weeks to fetch. Integers are converted
                        to the top limit of a range

            Example:

                for score in scores('MIN', limit=10) # fetch Vikings record up to but not including week 10
        '''

        if type(limit) is int:
            limit = range(1, limit)

        teams = self._teams(teams)

        for elem in self.games_:
            if limit is None or elem['wk'] in limit:
                if teams is None or elem['at'] in teams or elem['ht'] in teams:
                    if elem['p'] or allGames:
                        yield elem


    def scores(self, teams=None, limit=None):
        ''' Returns interated game data structured by teams

            Result is  dict keyed by team code each of game results as follows:

            [wlt, us, them, op, home, week]

            wlt:  'win' 'loss' or 'tie'
            us:   our final score
            them: their final score
            op:   opponent (team code)
            home: True for home games
            week: week number
        '''

        if teams is None:
            z = {i:[] for i in self.teams_.keys()}
        else:
            teams = self._teams(teams)
            z = {i:[] for i in teams}

        for game in self.games(teams, limit):
            if teams is None or game['at'] in teams:
                z[game['at']].append([NFL.result(game['as'], game['hs']), game['as'], game['hs'], game['ht'], False, game['wk']])

            if teams is None or game['ht'] in teams:
                z[game['ht']].append([NFL.result(game['hs'], game['as']), game['hs'], game['as'], game['at'], True, game['wk']])

        return z


    def schedule(self, which):

        if type(which) is int:
            df = pd.DataFrame(columns=['ht', 'at', 'hscore', 'ascore'])
            for game in self.games(teams=None, limit=range(which,which+1), allGames=True):
                df.loc[len(df)] = [game['ht'], game['at'], game['hs'], game['as']]
        else:
            # pre-populate the index so the schedule includes the bye week
            df = pd.DataFrame(columns=['opp', 'at_home', 'score', 'opp_score', 'wlt'], index=range(1, self.max_week+1))
            df.index.name = 'week'
            for game in self.games(teams=which, allGames=True):
                if game['ht'] == which:
                    df.loc[game['wk']] = [game['at'], 1, game['hs'], game['as'], NFL.result(game['hs'],game['as'])]
                else:
                    df.loc[game['wk']] = [game['ht'], 0, game['as'], game['hs'], NFL.result(game['as'], game['hs'])]

        return df

    def opponents(self, teams, limit=None):
        ''' Returns the set of common opponents of one or more teams

            The teams argument can be a single team or a list.
        '''

        if teams is None:
            raise ValueError("teams cannot be None here")

        teams = self._teams(teams)

        ops = {t:set() for t in teams}

        for game in self.games(teams, limit):
            if game['ht'] in ops:
                ops[game['ht']].add(game['at'])

            if game['at'] in ops:
                ops[game['at']].add(game['ht'])

        # Resulting set is common (intersection) of opponents excluding the teams themselves
        z = None
        for s in ops.values():
            if z is None:
                z = s
            else:
                z &= s

        z -= set(teams)
        return z


    def wlt(self, teams=None, within=None, limit=None, points=False):
        ''' Return the wlt stats of one or more teams

            teams:  team code or list of team codes

            within: list of team codes that defines the wlt universe

            points: include points scored and allowed
        '''

        teams = self._teams(teams)

        cols = ['win','loss','tie', 'pct']
        if points:
            cols += ['scored','allowed']
        df = pd.DataFrame(columns=cols)
        df.columns.name = 'outcome'
        df.index.name = 'team'
        for t,scores in self.scores(teams, limit).items():
            df.loc[t] = 0
            for score in scores:
                if within is None or score[3] in within:
                    df.loc[t, score[0]] += 1
                    if 'scored' in df:
                        df.loc[t, 'scored'] += score[1]

                    if 'allowed' in df:
                        df.loc[t, 'allowed'] += score[2]

        df['pct'] = (df['win'] + df['tie'] * 0.5) / df.drop(columns=['scored','allowed'], errors='ignore').sum(axis=1)
        return df.sort_values('pct', ascending=False)

    def team_stats(self, team):
        '''Return stats for a single team
        '''

        return self._stats().loc[team][['overall','division','conference']].unstack()


    def tiebreakers(self, teams):
       '''Return tiebreaker analysis for specified teams

        Each row in the returned dataframe is the results of a step in the NFL's tiebreaker procedure
        currently defined here: https://www.nfl.com/standings/tie-breaking-procedures

        Rows are in order of precedence and depend on whether the teams are in the same division or not

        rank (conference or overall) statistics are always in increasing order, e.g. 1 is the worst
        ranked team

        Example:

        z = nfl.tiebreakers(nfl('NFC-North').teams)

        # sort division according to tiebreaker rules, highest ranked team in column 1
        z = z.xs('pct', level=1, axis=1).sort_values(list(z.index), axis=1, ascending=False)
        '''

        teams = self._teams(teams)
        df = pd.DataFrame(columns=pd.MultiIndex.from_product([teams, ['win','loss','tie', 'pct']], names=['team','outcome']))
        common_opponents = self.opponents(teams)
        divisions = set()
        stats = self._stats()

        # determine which divisions are in the specified list. If more than one then adjust the tiebreaker order
        for t in teams:
            divisions.add(self.teams_[t]['div'])

        # set rules to default values here so they appear in the correct order
        df.loc['overall'] = np.nan
        df.loc['head-to-head'] = np.nan
        if len(divisions) > 1:
            df.loc['conference'] = np.nan
            df.loc['common-games'] = np.nan
        else:
            df.loc['division'] = np.nan
            df.loc['common-games'] = np.nan
            df.loc['conference'] = np.nan
        
        df.loc['victory-strength'] = np.nan
        df.loc['schedule-strength'] = np.nan
        df.loc['conference-rank'] = np.nan
        df.loc['overall-rank'] = np.nan
        df.loc['common-netpoints'] = np.nan
        df.loc['overall-netpoints'] = np.nan

        h2h = self.wlt(teams, within=teams)
        co  = self.wlt(teams, within=common_opponents, points=True)

        for team in teams:
            df.loc['overall', team] = stats.loc[team,'overall'].values
            df.loc['head-to-head', team] = h2h.loc[team].values
            df.loc['common-games', team] = co.loc[team].drop(['scored','allowed']).values
            df.loc['conference', team] = stats.loc[team,'conference'].values
            df.loc['victory-strength', team] = stats.loc[team,'vic_stren'].values
            df.loc['schedule-strength', team] = stats.loc[team,'sch_stren'].values
            if 'division' in df.index:
                df.loc['division', team] = stats.loc[team,'division'].values

            df.loc['conference-rank', (team,'pct')] = stats.loc[team, ('misc', 'rank-conf')]
            df.loc['overall-rank', (team,'pct')] = stats.loc[team, ('misc', 'rank-overall')]
            df.loc['common-netpoints', (team,'pct')] = co.loc[team, 'scored'] - co.loc[team, 'allowed']
            df.loc['overall-netpoints', (team,'pct')] = stats.loc[team, ('misc', 'pts-scored')] - stats.loc[team, ('misc', 'pts-allowed')]

        return df

    @staticmethod
    def result(a, b):
        
        if a is None or b is None:
            return ''
        elif a > b:
            return 'win'
        elif a < b:
            return 'loss'

        return 'tie'

    def _teams(self, teams):
        ''' Transforms teams into an array of actual team codes, or None
        '''

        if teams is None:
            return None

        if type(teams) in [list, set]:
            # already a list
            return teams

        if teams in self.divs_:
            # division code
            return self.divs_[teams]

        if teams in self.confs_:
            # conference code
            return self.confs_[teams]

        # single team code
        return [teams]


if __name__ == '__main__':
    config = docopt(__doc__)
    # print(config)
    # sys.exit(0)

    if config['update']:
        logging.basicConfig(level=logging.INFO)

        NFL().update(config['FILE'], week=int(config['WEEK']))

    if config['team']:
        nfl = NFL()
        nfl.load(config['--file'])
        team = nfl(config['TEAM'])
        print(team)
        if type(team) is NFLTeam:
            print(team.schedule)

    if config['tiebreakers']:
        nfl = NFL()
        print(nfl.load(config['--file']).tiebreakers(config['TEAMS']))


