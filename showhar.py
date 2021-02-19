
'''This module reads har files, which are logs of network activity that can be
exported from the Network pane in Google Chrome's debugger. 
'''

import json
from urllib import parse
import numpy as np
import pandas as pd

def load(path):
    '''Return a data frame of select fields from a .har file
    '''

    data = json.load(open(path, 'r', encoding='utf8'))['log']
    df = pd.DataFrame(columns=['host', 'cache', 'send_cookie_size', 'status', 'status_text', 'rec_error', 'rec_size', 'rec_time']) 
    for row in data['entries']:
        url = row['request']['url']
        p = parse.urlparse(url)
        host = p.netloc
        cached = row.get('_fromCache', 'none')
        cookies = list(filter(lambda x: x['name']=='Cookie', row['request']['headers']))
        hdr_cookie_size = len(cookies[0]['value']) if len(cookies) > 0 else np.nan
        status = row['response']['status']
        status_text = row['response']['statusText']
        
        rec_error = row['response']['_error'] if row['response']['_error'] else np.nan
        rec_size  = row['response']['_transferSize'] if row['response']['_transferSize'] else np.nan

        # this seems to be how time is reported in the inspect panel
        rec_time  = row['time'] - max(row['timings']['_blocked_queueing'], 0)

        df.loc[len(df)] =  [host, cached, hdr_cookie_size, status, status_text, rec_error, rec_size, rec_time]

    df['rec_size'] = df['rec_size'].astype('float64') # not sure why this is necessary, but it is...
    return df
