from datetime import datetime
from typing import Optional
from operator import itemgetter

from server import config
from server.database import Post, Likes

uri = config.PISS_ALGO_URI


def handler(cursor: Optional[str], limit: int) -> dict:
    #   Algorithm:
    #   post_score = ((likes + 2(reposts)) * %150*hasimage) * %(1.5 - (0.5/7)*age_in_days))
    #

    pissPosts = []

    posts = Post.select().order_by(Post.indexed_at.desc()).order_by(Post.cid.desc()).limit(limit)

    for post in posts:
        pisspost = {}
        pisspost['uri'] = post.uri
        
        likes = len(Likes.select().where(Likes.post_uri == post.uri))

        delta = datetime.date(datetime.now()) - datetime.date(post.indexed_at)

        #score = ((post.likes + 2*(post.reposts)) * (1 + 0.5 * int(post.image == True)) *  (1.5 - (0.5/7)*delta.days))

        score = ((likes) * (1 + 0.5 * int(post.image == True)) *  (1.5 - (0.5/7)*delta.days))

        print(round(score, 2))

        pisspost['score'] = round(score, 2)
        pissPosts.append(pisspost)

    if cursor:
        cursor_parts = cursor.split('::')
        if len(cursor_parts) != 2:
            raise ValueError('Malformed cursor')

        indexed_at, cid = cursor_parts
        indexed_at = datetime.fromtimestamp(int(indexed_at) / 1000)
        posts = posts.where(Post.indexed_at <= indexed_at).where(Post.cid < cid)


    sorted_pissPost = sorted(pissPosts, key=lambda x: x['score'], reverse=True)

    feed = [{'post': pisspost['uri']} for pisspost in sorted_pissPost]

    cursor = None
    last_post = posts[-1] if posts else None
    if last_post:
        cursor = f'{int(last_post.indexed_at.timestamp() * 1000)}::{last_post.cid}'

    return {
        'cursor': cursor,
        'feed': feed
    }
