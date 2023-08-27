from atproto import AsyncClient
from atproto import Client
import json


def get_furries():

    # Get secrets
    with open('./secrets/secret.json') as file_object:
        secrets = json.load(file_object)
        
    #Log into bsky as me
    client = Client()
    client.login(secrets["Username"], secrets["Password"])

    #Get initial follower count from furlist
    actor = 'furryli.st'
    followsCount = client.bsky.actor.get_profile({'actor' : actor}).followsCount
    #print(followsCount)
    
    #Initially populate and get firt cursor
    followsList = []
    follows = client.bsky.graph.get_follows({'actor' : actor, 'limit' : 100})
    
    #Add only handles to the list
    for f in follows.follows:
        followsList.append(f.handle)

    followsCursor = follows.cursor

    #Using cursor, get the rest of the followers handles
    while len(followsList) <= followsCount:
        follows = client.bsky.graph.get_follows({'actor' : actor, 'cursor' : followsCursor, 'limit' : 100})
        #followsList.append(follows.follows)
        followsCursor = follows.cursor

        for f in follows.follows:
            followsList.append(f.handle)

        #print(str(len(followsList)) + "/" + str(followsCount))

    return followsList

def write_furry_file(furryList):
    with open('furries.txt', 'w') as f:
        f.write('\n'.join(furryList))

# FOR DEBUG PURPOSE ONLY
if __name__ == '__main__':
    # FOR DEBUG PURPOSE ONLY
    furries = get_furries()
    print(len(furries))
    write_furry_file(furries)