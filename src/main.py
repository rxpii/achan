import os
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands

import chan_fetch
import tasks

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD')
GUILD_ID = int(os.getenv('GUILD_ID'))
POST_DELAY = int(os.getenv('POST_DELAY'))
BATCH_SIZE = int(os.getenv('BATCH_SIZE'))
IMGS_LIMIT = int(os.getenv('IMGS_LIMIT'))

# initialize
enabled_channels = {GUILD_ID: set()}
bot = commands.Bot(command_prefix='chn ')

# util
def current_enabled_channels():
    return enabled_channels[GUILD_ID]

def is_channel_enabled(channel):
    return channel in current_enabled_channels()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    # set of enabled channels to listen for commands in
    # should hold a list of channel ids
    bot.enabled_channels = {GUILD_ID: {}}

@bot.command(name='thread', help='Dump images from a thread.')
async def thread(ctx, board: str=None, thread_id: int=None, limit: int=None):
    channel = ctx.channel

    if not is_channel_enabled(channel):
        return

    if board == None:
        await ctx.send(f'No board selected.')
        return

    if thread_id == None:
        await ctx.send(f'No thread id passed.')
        return

    # grab all the images in the thread
    img_urls = await chan_fetch.get_thread_images_urls(
            board, thread_id, limit=IMGS_LIMIT)

    if not img_urls:
        await ctx.send(f'Invalid board or thread id.')
        return

    # post them, batch by batch
    await tasks.post_imgs(ctx, img_urls,
            batch_size=BATCH_SIZE, post_delay=POST_DELAY)

@bot.command(name='enable', help='Enable a-chan in this channel!')
async def enable(ctx):
    channel = ctx.channel
    current_enabled_channels().add(channel)
    await ctx.send(f"Enabled in channel '{channel}'")

@bot.command(name='disable', help='Disable a-chan in this channel.')
async def enable(ctx):
    channel = ctx.channel
    current_enabled_channels().discard(ctx.channel)
    await ctx.send(f"Disabled in channel '{channel}'")

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

bot.run(TOKEN)
