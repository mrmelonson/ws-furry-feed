import os
import json

with open('./server/secrets/static.json') as file_object:
    static_values = json.load(file_object)

SERVICE_DID = os.environ.get('SERVICE_DID', None)
#HOSTNAME = os.environ.get('HOSTNAME', None)

HOSTNAME = static_values["HOSTNAME"]

if HOSTNAME is None:
    raise RuntimeError('You should set "HOSTNAME" environment variable first.')

if SERVICE_DID is None:
    SERVICE_DID = f'did:web:{HOSTNAME}'


#PISS_ALGO_URI = os.environ.get('PISS_ALGO_URI')
PISS_ALGO_URI = static_values["PISS_URI"]

if PISS_ALGO_URI is None:
    raise RuntimeError('Publish your feed first (run publish_feed.py) to obtain Feed URI. '
                       'Set this URI to "PISS_ALGO_URI" environment variable.')
