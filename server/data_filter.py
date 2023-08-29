from atproto import models
from atproto import Client
from server.logger import logger
from server.database import db, Post
import json

furfile =  open("./server/furries.txt", "r")
furlist = furfile.read().split("\n")
furfile.close()

filterfile = open("./server/filter.txt", "r")
filterlist = filterfile.read().split("\n")
filterfile.close()

blacklistfile = open("./server/blacklist.txt", "r")
blacklist = blacklistfile.read().split("\n")
blacklistfile.close()

with open('./server/secrets/secret.json') as file_object:
        secrets = json.load(file_object)
client = Client()
client.login(secrets["Username"], secrets["Password"])

def update_all_likes():
    posts = Post.select()
    for post in posts:
        likes_accurate = client.bsky.feed.get_likes({'uri' : post.uri})
        reposts_accurate = len(client.bsky.feed.get_reposted_by({'uri' : post.uri, 'limit' :100})) #only gets a max of 100 reposts
        Post.update(likes=likes_accurate, reposts=reposts_accurate).where(Post.uri == post.uri)


def operations_callback(ops: dict) -> None:
    # Here we can filter, process, run ML classification, etc.
    # After our feed alg we can save posts into our DB
    # Also, we should process deleted posts to remove them from our DB and keep it in sync

    # for example, let's create our custom feed that will contain all posts that contains alf related text

    posts_to_create = []
    for created_post in ops['posts']['created']:
        record = created_post['record']

        # print all texts just as demo that data stream works
        #print(furlist)
        # only furry posts
        if created_post["author"] in furlist:
            if not any(map(record.text.lower().__contains__, blacklist)) and any(map(record.text.lower().__contains__, filterlist)):
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
                    'likes' : 0,
                    'image' : post_with_images,
                    'reposts' : 0
                }
                posts_to_create.append(post_dict)
                update_all_likes()
                

    posts_to_delete = [p['uri'] for p in ops['posts']['deleted']]
    if posts_to_delete:
        Post.delete().where(Post.uri.in_(posts_to_delete))
        #logger.info(f'Deleted from feed: {len(posts_to_delete)}')

    if posts_to_create:
        with db.atomic():
            for post_dict in posts_to_create:
                Post.create(**post_dict)
        logger.info(f'Added to feed: {len(posts_to_create)}')

    for liked_post in ops['likes']['created']:
        record = liked_post['record']
        try:
            liked_post_to_update = Post.get(Post.uri == record.subject.uri)
            Post.update(likes=Post.likes + 1).where(Post.uri == record.subject.uri).execute()
            #print(Post.get(Post.uri == record.subject.uri).likes)
            logger.info(f'Updated post likes (added): {record.subject.uri}')     
        except:
            next

    #figure out how to remove likes from posts
    posts_to_unlike = [p['uri'] for p in ops['likes']['deleted']]
    if posts_to_unlike:
        Post.update(likes=Post.likes -1).where(Post.uri.in_(posts_to_delete))
        #print("removed like")
        #print(liked_post_removed)
        '''
        try:
            liked_post_removed_to_update = Post.get(Post.uri == record.subject.uri)
            Post.update(likes=Post.likes - 1).where(Post.uri == record.subject.uri)
            logger.info(f'Updated post likes (removed): {record.subject.uri}')     
        except:
            next
        '''
        #if liked_posts_to_update:
        #    for uri in liked_posts_to_update:
        #        Post.update(likes=Post.likes + 1).where(Post.uri == uri)
         #       logger.info(f'Updated post likes: {uri}')     



