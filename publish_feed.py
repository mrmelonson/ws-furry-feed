#!/usr/bin/env python3
# YOU MUST INSTALL ATPROTO SDK
# pip3 install atproto

from datetime import datetime

from atproto.xrpc_client.models import ids

from atproto import Client, models
import json

with open('./server/secrets/secret.json') as file_object:
        secrets = json.load(file_object)

# YOUR bluesky handle
# Ex: user.bsky.social
HANDLE: str = secrets["Username"]

# YOUR bluesky password, or preferably an App Password (found in your client settings)
# Ex: abcd-1234-efgh-5678
PASSWORD: str = secrets["Password"]

# The hostname of the server where feed server will be hosted
# Ex: feed.bsky.dev
HOSTNAME: str = 'feed.zelenyy.info'

# A short name for the record that will show in urls
# Lowercase with no spaces.
# Ex: whats-hot
RECORD_NAME: str = 'FURRY-WS-FEED'

# A display name for your feed
# Ex: What's Hot
DISPLAY_NAME: str = 'Furry watersports posts'

# (Optional) A description of your feed
# Ex: Top trending content from the whole network
DESCRIPTION: str = 'Top watersports content from furries. List of furries gathered from @furryli.st'

# (Optional) The path to an image to be used as your feed's avatar
# Ex: ./path/to/avatar.jpeg
AVATAR_PATH: str = ''

# (Optional). Only use this if you want a service did different from did:web
SERVICE_DID: str = ''


# -------------------------------------
# NO NEED TO TOUCH ANYTHING BELOW HERE
# -------------------------------------


def main():
    client = Client()
    client.login(HANDLE, PASSWORD)

    feed_did = SERVICE_DID
    if not feed_did:
        feed_did = f'did:web:{HOSTNAME}'

    avatar_blob = None
    if AVATAR_PATH:
        with open(AVATAR_PATH, 'rb') as f:
            avatar_data = f.read()
            avatar_blob = client.com.atproto.repo.upload_blob(avatar_data).blob

    response = client.com.atproto.repo.put_record(models.ComAtprotoRepoPutRecord.Data(
        repo=client.me.did,
        collection=ids.AppBskyFeedGenerator,
        rkey=RECORD_NAME,
        record=models.AppBskyFeedGenerator.Main(
            did=feed_did,
            displayName=DISPLAY_NAME,
            description=DESCRIPTION,
            avatar=avatar_blob,
            createdAt=datetime.now().isoformat(),
        )
    ))

    print('Successfully published!')
    print('Feed URI (put in "PISS_ALGO_URI" env var):', response.uri)


if __name__ == '__main__':
    main()
