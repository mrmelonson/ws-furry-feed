from atproto import models

from server.logger import logger
from server.database import db, Post

furfile =  open("./server/furries.txt", "r")
furlist = furfile.read().split("\n")
furfile.close()

filterfile = open("./server/filter.txt", "r")
filterlist = filterfile.read().split("\n")
filterfile.close()

blacklistfile = open("./server/blacklist.txt", "r")
blacklist = blacklistfile.read().split("\n")
blacklistfile.close()

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
                }
                posts_to_create.append(post_dict)

    posts_to_delete = [p['uri'] for p in ops['posts']['deleted']]
    if posts_to_delete:
        Post.delete().where(Post.uri.in_(posts_to_delete))
        logger.info(f'Deleted from feed: {len(posts_to_delete)}')

    if posts_to_create:
        with db.atomic():
            for post_dict in posts_to_create:
                Post.create(**post_dict)
        logger.info(f'Added to feed: {len(posts_to_create)}')
