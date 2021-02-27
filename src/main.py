import os
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands

import chan_fetch
import tasks
from util import *

# load env config
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CMD_PREFIX = os.getenv('CMD_PREFIX')
POST_DELAY = int(os.getenv('POST_DELAY'))
BATCH_SIZE = int(os.getenv('BATCH_SIZE'))
IMGS_LIMIT = int(os.getenv('IMGS_LIMIT'))
ENABLED_DATA_FILE = os.getenv('ENABLED_DATA_FILE')

# initialize

# load pre-existing guild channel configs
enabled_channels = load_enabled_channels(ENABLED_DATA_FILE)
bot = commands.Bot(command_prefix=CMD_PREFIX)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print("Connected to the following guilds:")

    # add new entries for new guilds
    for guild in bot.guilds:
        print(f'Serving: {guild.name} ({guild.id})')
        if not guild.id in enabled_channels:
            enabled_channels[guild.id] = set()

@bot.command(name='thread', help='Dump images from a thread.')
async def thread(ctx, board: str=None, thread_id: int=None, limit: int=IMGS_LIMIT):
    author = ctx.message.author
    channel = ctx.channel
    guild = ctx.guild

    if not is_channel_enabled(enabled_channels, guild, channel):
        return

    if board == None:
        await ctx.send(f'No board selected.')
        return

    if thread_id == None:
        await ctx.send(f'No thread id passed.')
        return

    # grab all the images in the thread
    img_urls = await chan_fetch.get_thread_images_urls(
            board, thread_id, limit=limit)

    if not img_urls:
        await ctx.send(f'Invalid board or thread id.')
        return

    log_out("INFO", f'Executed command [thread] {author} {channel} {guild} imgs: {len(img_urls)}')

    # post them, batch by batch
    await tasks.post_imgs(ctx, img_urls,
            batch_size=BATCH_SIZE, post_delay=POST_DELAY)


@bot.command(name='enable', help='Enable a-chan in this channel!')
async def enable(ctx):
    author = ctx.message.author
    channel = ctx.channel
    guild = ctx.guild

    print("ENABLE", author, channel, guild)

    if not is_administrator(author):
        return

    current_enabled_channels(enabled_channels, guild).add(channel.id)
    write_enabled_channels(ENABLED_DATA_FILE, enabled_channels)

    await ctx.send(f"Enabled in channel '{channel}'")

    log_out("INFO", f'Executed command [enable] {author} {channel} {guild}')

@bot.command(name='disable', help='Disable a-chan in this channel.')
async def disable(ctx):
    author = ctx.message.author
    channel = ctx.channel
    guild = ctx.guild

    print("DISABLE", author, channel, guild)

    if not is_administrator(author):
        return

    current_enabled_channels(enabled_channels, guild).discard(channel.id)
    write_enabled_channels(ENABLED_DATA_FILE, enabled_channels)

    await ctx.send(f"Disabled in channel '{channel}'")

    log_out("INFO", f'Executed command [disable] {author} {channel} {guild}')

@bot.command(name='status', help='Check if a-chan is enabled in this channel.')
async def status(ctx):
    author = ctx.message.author
    channel = ctx.channel
    guild = ctx.guild
    print("STATUS", author, channel, guild)

    if not is_administrator(author):
        return

    status = is_channel_enabled(enabled_channels, guild, channel)
    response = \
            f"Currently {'enabled' if status else 'disabled'} in '{channel}'."
    
    await ctx.send(response)

    log_out("INFO", f'Executed command [status] {author} {channel} {guild}')

@bot.event
async def on_error(event, *args, **kwargs):
    log_err(args[0])

bot.run(DISCORD_TOKEN)
