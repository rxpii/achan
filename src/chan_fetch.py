import os
import json
import requests
import asyncio
import time
from dotenv import load_dotenv

from util import *

load_dotenv()
THREAD_ENDPOINT = os.getenv('THREAD_ENDPOINT')
IMG_ENDPOINT = os.getenv('IMG_ENDPOINT')
RESULTS_CACHE_EXPIRE_TIME_MINS = int(os.getenv('RESULTS_CACHE_EXPIRE_TIME_MINS', 5))

async def get_thread_images_urls(board, thread_id, results_cache=None):
    # periodically clean up the cache
    clean_cache(results_cache, RESULTS_CACHE_EXPIRE_TIME_MINS)

    query_id = hash_query(board, thread_id)

    # check if the query results are in the cache
    if not results_cache is None:
        if query_id in results_cache:
            return results_cache[query_id]['img_urls']

    headers = {'Content-Type': 'application/json'}
    res = requests.get(THREAD_ENDPOINT.format(board, thread_id), headers=headers)

    # abort if errors
    if not res.ok:
        return None

    json_data = res.json()

    # parse the image urls from the posts that have them
    imgs = [str(post['tim']) + post['ext'] for post in json_data['posts'] if 'filename' in post and 'ext' in post]
    img_endpoint = IMG_ENDPOINT.format(board)
    img_urls = [img_endpoint + img for img in imgs]

    # cache the result
    if not results_cache is None:
        results_cache[query_id] = {
                'img_urls': img_urls,
                'requested_at': time.time(),
                }

    return img_urls
