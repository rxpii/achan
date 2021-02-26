import os
import json
import requests
import asyncio
from dotenv import load_dotenv

load_dotenv()
THREAD_ENDPOINT = os.getenv('THREAD_ENDPOINT')
IMG_ENDPOINT = os.getenv('IMG_ENDPOINT')

async def get_thread_images_urls(board, thread_id, limit=200):
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

    # limit the number of image urls if required
    if limit:
        img_urls = img_urls[:limit]

    return img_urls
