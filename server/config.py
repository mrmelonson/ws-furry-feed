import os

SERVICE_DID = os.environ.get('SERVICE_DID', None)
HOSTNAME = "DESKTOP-TSTL4T5" #os.environ.get('HOSTNAME', None)

if HOSTNAME is None:
    raise RuntimeError('You should set "HOSTNAME" environment variable first.')

if SERVICE_DID is None:
    SERVICE_DID = f'did:web:{HOSTNAME}'


WHATS_ALF_URI = 'at://did:plc:x6gdykk7qjiq6u327s34wzhq/app.bsky.feed.generator/ZEL-TEST'#os.environ.get('WHATS_ALF_URI')
if WHATS_ALF_URI is None:
    raise RuntimeError('Publish your feed first (run publish_feed.py) to obtain Feed URI. '
                       'Set this URI to "WHATS_ALF_URI" environment variable.')
