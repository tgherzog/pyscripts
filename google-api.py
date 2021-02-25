
'''This is a short demonstration of how to authenticate and query google
   API services from a python script. It's intended to help me capture and
   remember how to use these services.

   Given some credentials, the script gets authorization from google API and
   provides a list of the user's photo albums from photos.google.com.

Usage:
   google-api.py --credentials=JSON_FILE --init [--token=TOKEN]
   google-api.py --credentials=JSON_FILE --resume --token=TOKEN

Options:
   --credentials=JSON_FILE      json file of credentials; you get these from the Google API console
   --init                       initialize a new session; client will ask you to login via your browser
                                and copy the response code to proceed
   --token=TOKEN                path to token for resumed/resuming sessions. Required if --resume
   --resume                     Try to resume a previously saved token; --token parameter required

References:
  https://requests-oauthlib.readthedocs.io/en/latest/examples/real_world_example.html
  https://console.cloud.google.com/ (google API console)
  https://developers.google.com/photos/library/guides/overview (Photos API docs)
'''



import json
import sys
import requests
import logging
from requests_oauthlib import OAuth2Session
from docopt import docopt

try:
    import pasteboard as clipMac
except ImportError:
    clipMac = None

# logging.basicConfig(level=logging.INFO)

config = docopt(__doc__)
credentials = None # get these from the Google API console
token = None       # current token from oauth2: optionally persistent
session = None     # oauth2 savvy session returned from requests

# Before running this code you need to create and publish your application in the Google
# API console. A reasonable step-through is here:
# https://bullyrooks.com/index.php/2021/02/02/backing-up-google-photos-to-your-synology-nas/
# The last step in the Google console is to visit the Credentials tab and download a json
# file with the client information you just created. That file is an input to this
# script

def save_token(refreshed_token):

    global token
    token = refreshed_token

    if config['--token']:
        json.dump(refreshed_token, open(config['--token'], 'w'))
    
credentials = json.load(open(config['--credentials'], 'r'))
credentials = credentials['installed']
token = None
required_scope = ['https://www.googleapis.com/auth/photoslibrary.readonly']

if config['--init']:
    # In this mode the script will initialize a new session from scratch, requiring
    # the user to visit a provided URL in the browser, authenticate, and copy
    # a response code back to the script. If --token is defined then the resulting
    # token is saved for future use

    # auto_refresh_kwargs consists of google-specific parameters
    session = OAuth2Session(credentials['client_id'], scope=required_scope,
                redirect_uri=credentials['redirect_uris'][0], 
                auto_refresh_url=credentials['token_uri'],
                auto_refresh_kwargs = {'client_id': credentials['client_id'], 'client_secret': credentials['client_secret']})

    # access_type and prompt are google-specific parameters
    auth_url,state = session.authorization_url(credentials['auth_uri'], access_type='offline', prompt='select_account')
    if clipMac:
        pb = clipMac.Pasteboard()
        pb.set_contents(auth_url)
        print("The authorization URL has been copied to your clipboard. Paste the URL into your browser's address bar.")
    else:
        print('Please visit this URL to authorize access: {}'.format(auth_url))

    auth_response = input('Enter the response code from Google: ')
    new_token = session.fetch_token(credentials['token_uri'], client_secret=credentials['client_secret'], code=auth_response)
    logging.info('Session started: {}'.format(new_token['access_token']))
    save_token(new_token)

else:
    # in '--resume' mode the provided token is recycled, allowing the user to resume without logging in
    token = json.load(open(config['--token'], 'r'))

    # NB: this code is based on the oauthlib docs which are a bit vague about how the `expires_in` parameter
    # is supposed to work, and I haven't verified the module will smoothly request a new token when necessary.
    # Although the docs suggest that `expires_in` is important, the underlying oauthlib package seems to 
    # more sensibly give preference to `expires_at`. In any event, if this doesn't work there are different implementation
    # options in the docs, and ddh2api is also a possible approach, which seems to do the same thing as the oauthlib
    # module.

    # auto_refresh_kwargs consists of google-specific parameters
    session = OAuth2Session(credentials['client_id'], token=token,
                token_updater=save_token,
                auto_refresh_url=credentials['token_uri'],
                auto_refresh_kwargs = {'client_id': credentials['client_id'], 'client_secret': credentials['client_secret']})

    save_token(session.token)

response = session.get('https://photoslibrary.googleapis.com/v1/albums')
result = response.json()
for row in result['albums']:
    print('{}: {} photos'.format(row['title'], row.get('mediaItemsCount', 0)))
