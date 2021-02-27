import os
import discord
import random
import time
from dotenv import load_dotenv
from discord.ext import commands

import command_tasks
from util import *

# load env config
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CMD_PREFIX = os.getenv('CMD_PREFIX')
IMGS_LIMIT = int(os.getenv('IMGS_LIMIT'))
COMMANDS_CACHE_EXPIRE_TIME_MINS = int(os.getenv('COMMANDS_CACHE_EXPIRE_TIME_MINS'))
ENABLED_DATA_FILE = os.getenv('ENABLED_DATA_FILE')

# initialize

# load pre-existing guild channel configs
enabled_channels = load_enabled_channels(ENABLED_DATA_FILE)
commands_cache = {}
results_cache = {}
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

@bot.command(name='url', help='Dump images from a thread url.')
async def url(ctx, url: str=None,
        limit: int=IMGS_LIMIT, offset: int=None):
    # periodically clean up the cache
    clean_cache(commands_cache, COMMANDS_CACHE_EXPIRE_TIME_MINS)

    author = ctx.message.author
    channel = ctx.channel
    guild = ctx.guild

    if not is_channel_enabled(enabled_channels, guild, channel):
        return

    if url == None:
        await ctx.send(f'No URL passed.')
        return

    extracted_params = extract_url(url)

    if extracted_params == None:
        await ctx.send(f'Malformed URL.')
        return

    board, thread_id = extracted_params

    query_id = hash_query(board, thread_id)

    # if the offset is unset, then check if there's a currently cached
    # next index to use
    # if not, use 0
    if not offset:
        if (author.id in commands_cache
                and commands_cache[author.id]['query_id'] == query_id):
            offset = commands_cache[author.id]['next_img_index']
        else:
            offset = 0

    # post the images
    result = await command_tasks.dump_thread(
            ctx, board, thread_id, limit, offset,
            results_cache)

    # return if we encountered an error
    if not result:
        return

    next_img_index, total_imgs, total_dumped = result
    if total_dumped > 0:
        await ctx.send(f"Dumped {total_dumped} total ({next_img_index}/{total_imgs})")
    else:
        await ctx.send(f"No images dumped.")

    # cache the command, allowing the user to continue off from previous
    # commands
    if next_img_index >= total_imgs:
        if author.id in commands_cache:
            del commands_cache[author.id]
    else:
        commands_cache[author.id] = {
                'board': board,
                'thread_id': thread_id,
                'query_id': query_id,
                'next_img_index': next_img_index,
                'requested_at': time.time(),
                }

    log_out("INFO", f'Executed command [dump] {author} {channel} {guild}: params {board} {thread_id}')

@bot.command(name='dump', help='Dump images from a thread.')
async def dump(ctx, board: str=None, thread_id: int=None,
        limit: int=IMGS_LIMIT, offset: int=None):
    # periodically clean up the cache
    clean_cache(commands_cache, COMMANDS_CACHE_EXPIRE_TIME_MINS)

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

    query_id = hash_query(board, thread_id)

    # if the offset is unset, then check if there's a currently cached
    # next index to use
    # if not, use 0
    if not offset:
        if (author.id in commands_cache
                and commands_cache[author.id]['query_id'] == query_id):
            offset = commands_cache[author.id]['next_img_index']
        else:
            offset = 0

    # post the images
    result = await command_tasks.dump_thread(
            ctx, board, thread_id, limit, offset,
            results_cache)

    # return if we encountered an error
    if not result:
        return

    next_img_index, total_imgs, total_dumped = result
    if total_dumped > 0:
        await ctx.send(f"Dumped {total_dumped} total ({next_img_index}/{total_imgs})")
    else:
        await ctx.send(f"No images dumped.")

    # cache the command, allowing the user to continue off from previous
    # commands
    if next_img_index >= total_imgs:
        if author.id in commands_cache:
            del commands_cache[author.id]
    else:
        commands_cache[author.id] = {
                'board': board,
                'thread_id': thread_id,
                'query_id': query_id,
                'next_img_index': next_img_index,
                'requested_at': time.time(),
                }

    log_out("INFO", f'Executed command [dump] {author} {channel} {guild}: params {board} {thread_id}')

@bot.command(name='cont', help='Continue dumping based on previous command.')
async def cont(ctx, limit: int=IMGS_LIMIT, offset: int=None):
    # periodically clean up the cache
    clean_cache(commands_cache, COMMANDS_CACHE_EXPIRE_TIME_MINS)

    author = ctx.message.author
    channel = ctx.channel
    guild = ctx.guild

    if not is_channel_enabled(enabled_channels, guild, channel):
        return

    if not author.id in commands_cache:
        await ctx.send(f'No previous command found. Try running `dump` first.')
        return

    previous_command = commands_cache[author.id]
    board = previous_command['board']
    thread_id = previous_command['thread_id']

    # if the offset is unset, then check if there's a currently cached
    # next index to use
    # if not, use 0
    if not offset:
        offset = commands_cache[author.id]['next_img_index']

    # post the images
    result = await command_tasks.dump_thread(
            ctx, board, thread_id, limit, offset,
            results_cache)

    # return if we encountered an error
    if not result:
        return

    next_img_index, total_imgs, total_dumped = result
    if total_dumped > 0:
        await ctx.send(f"Dumped {total_dumped} total ({next_img_index}/{total_imgs})")
    else:
        await ctx.send(f"No images dumped.")

    # cache the command, allowing the user to continue off from previous
    # commands
    if next_img_index >= total_imgs:
        if author.id in commands_cache:
            del commands_cache[author.id]
    else:
        commands_cache[author.id]['next_img_index'] = next_img_index
        commands_cache[author.id]['requested_at'] = time.time()

    log_out("INFO", f'Executed command [cont] {author} {channel} {guild}: params {board} {thread_id}')

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
