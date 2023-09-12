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

    #posts = Post.select().order_by(Post.indexed_at.desc()).order_by(Post.cid.desc()).limit(limit)
    
    posts = Post.select().order_by(Post.indexed_at.desc()).order_by(Post.cid.desc())
    
    for post in posts:
        pisspost = {}
        pisspost['uri'] = post.uri
        
        likes = len(Likes.select().where(Likes.post_uri == post.uri))

        delta = datetime.date(datetime.now()) - datetime.date(post.indexed_at)

        #score = ((post.likes + 2*(post.reposts)) * (1 + 0.5 * int(post.image == True)) *  (1.5 - (0.5/7)*delta.days))

        score = ((likes) * (1 + 0.5 * int(post.image == True)) *  (1.5 - (0.5/7)*delta.days))

        #print(round(score, 2))

        #print(post.uri)

        pisspost['score'] = round(score, 2)
        pisspost['indexed_at'] = post.indexed_at
        pisspost['cid'] = post.cid
        pissPosts.append(pisspost)

    sorted_pissPost = sorted(pissPosts, key=lambda x: x['score'], reverse=True)

    if cursor:
        cursor_parts = cursor.split('::')
        if len(cursor_parts) != 2:
            raise ValueError('Malformed cursor')

        score, cid = cursor_parts
        #indexed_at = datetime.fromtimestamp(int(indexed_at) / 1000)
        sorted_pissPost = sorted_pissPost[:next((index for (index, d) in enumerate(sorted_pissPost) if d["cid"] == cid), None)]
        #print(sorted_pissPost)

    sorted_pissPost = sorted_pissPost[:limit]
    feed = [{'post': pisspost['uri']} for pisspost in sorted_pissPost]

    cursor = None
    last_post = sorted_pissPost[limit-1] if sorted_pissPost else None
    #print(last_post['indexed_at'].timestamp())
    if last_post:
        score = last_post['score']
        cid = last_post['cid']
        cursor = f'{int(score)}::{cid}'

    return {
        'cursor': cursor,
        'feed': feed
    }
