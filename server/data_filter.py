from atproto import models
from atproto import Client
from server.logger import logger
from server.database import db, Post, Likes
import json

import re

from datetime import datetime, timedelta

furfile =  open("./server/furries.txt", "r")
furlist = furfile.read().split("\n")
furfile.close()

filterfile = open("./server/filter.txt", "r")
filterlist = filterfile.read().split("\n")
filterlist_combined = "(" + ")|(".join(filterlist) + ")"
filterfile.close()

blacklistfile = open("./server/blacklist.txt", "r")
blacklist = blacklistfile.read().split("\n")
blacklist_combined = "(" + ")|(".join(blacklist) + ")"
blacklistfile.close()

with open('./server/secrets/secret.json') as file_object:
        secrets = json.load(file_object)
client = Client()
client.login(secrets["Username"], secrets["Password"])

def update_all_likes():
    posts = Post.select()
    for post in posts:
        likes_accurate = client.bsky.feed.get_likes({'uri' : post.uri})
        #print(client.bsky.feed.get_reposted_by({'uri' : post.uri, 'limit' :100}).repostedBy)
        reposts_accurate = len(client.bsky.feed.get_reposted_by({'uri' : post.uri, 'limit' :100}).repostedBy) #only gets a max of 100 reposts
        Post.update(likes=likes_accurate, reposts=reposts_accurate).where(Post.uri == post.uri)

def remove_old_posts():
    days_ago = 10
    
    cutoff_date = datetime.date(datetime.now()) - timedelta(days_ago)
    Post.delete().where(Post.indexed_at < cutoff_date).execute()
    print(cutoff_date)

def operations_callback(ops: dict) -> None:
    # Here we can filter, process, run ML classification, etc.
    # After our feed alg we can save posts into our DB
    # Also, we should process deleted posts to remove them from our DB and keep it in sync

    # for example, let's create our custom feed that will contain all posts that contains alf related text

    # First check if there are posts to add
    # Then check if it matched blacklists, if not then check for filter
    # Create dict with relevent info
    # Add a new record in Post DB

    posts_to_create = []
    for created_post in ops['posts']['created']:
        record = created_post['record']
        if created_post["author"] in furlist:
            if not re.search(blacklist_combined, record.text.lower()) and re.search(filterlist_combined, record.text.lower()):
                post_with_images = isinstance(record.embed, models.AppBskyEmbedImages.Main)
                inlined_text = record.text.replace('\n', ' ')
                logger.info(f'New post (with images: {post_with_images}): {inlined_text}')

                reply_parent = None
                if record.reply and record.reply.parent.uri:
                    reply_parent = record.reply.parent.uri

                reply_root = None
                if record.reply and record.reply.root.uri:
                    reply_root = record.reply.root.uri

                post_dict = {
                    'uri': created_post['uri'],
                    'cid': created_post['cid'],
                    'reply_parent': reply_parent,
                    'reply_root': reply_root,
                    'image' : post_with_images,
                    'reposts' : 0,
                    'text' : inlined_text
                }
                posts_to_create.append(post_dict) # add a post into db
                remove_old_posts() #remove posts from 10 days ago from db

    # Check if there are any posts to delete then get the uri of the post and delete it if it is in the db
    #
    posts_to_delete = [p['uri'] for p in ops['posts']['deleted']]
    if posts_to_delete:
        Post.delete().where(Post.uri.in_(posts_to_delete)).execute()
        #logger.info(f'Deleted from feed: {len(posts_to_delete)}')

    # create new record if there has been a post that matches filter
    if posts_to_create:
        with db.atomic():
            for post_dict in posts_to_create:
                Post.create(**post_dict)
        logger.info(f'Added to feed: {len(posts_to_create)}')

    # If there is a like that matches a post_URI then add it to the likes table
    likes_to_create = []
    for liked_post in ops['likes']['created']:
        record = liked_post['record']
        try:
            if Post.get(Post.uri == record.subject.uri):
                # when a post is liked, create in db
                likes_dict = {
                    'post_uri' : record.subject.uri,
                    'like_uri' : liked_post['uri']
                }
                
                likes_to_create.append(likes_dict)
                logger.info(f'Updated post likes (added): ' + str(liked_post['uri']))     
        except:
            next

    # formally add it to the db
    if likes_to_create:
        with db.atomic():
            for like_dict in likes_to_create:
                Likes.create(**like_dict)
        logger.info(f'Added to feed: {len(posts_to_create)}')


    # if there is a like deleted, check if it is in the likes table and delete if there is
    posts_to_unlike = [p['uri'] for p in ops['likes']['deleted']]
    if posts_to_unlike:
        Likes.delete().where(Likes.like_uri.in_(posts_to_unlike)).execute()




