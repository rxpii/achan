import asyncio

async def post_imgs(ctx, img_urls, batch_size=5, post_delay=1):
    total_img_urls = len(img_urls)
    for i in range(0, total_img_urls, batch_size):
        effective_size = min(i+batch_size, total_img_urls)
        img_batch = img_urls[i: effective_size]
        response = '\n'.join(img_batch)
        await ctx.send(response)
        await asyncio.sleep(post_delay)
