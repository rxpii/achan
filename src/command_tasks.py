import os
import asyncio

import tasks
import chan_fetch

BATCH_SIZE = int(os.getenv('BATCH_SIZE'))
POST_DELAY = int(os.getenv('POST_DELAY'))

async def dump_thread(ctx, board, thread_id, limit=20, offset=0,
        results_cache=None):
    # grab all the images in the thread
    img_urls = await chan_fetch.get_thread_images_urls(
            board, thread_id, results_cache=results_cache)
    img_urls_length = len(img_urls)

    if not img_urls:
        await ctx.send(f'Invalid board or thread id.')
        return None

    end = min(offset + limit, img_urls_length)
    img_urls_to_post = img_urls[offset:end]

    # post them, batch by batch
    await tasks.post_imgs(ctx, img_urls_to_post,
            batch_size=BATCH_SIZE, post_delay=POST_DELAY)

    # return the index of the next image, as well as the total
    # number of images
    return end, img_urls_length, end - offset
