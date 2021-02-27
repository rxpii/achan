import os
import re
import pickle
import discord
import time
from dotenv import load_dotenv

load_dotenv()
LOG_OUT_FILE = os.getenv('LOG_OUT_FILE')
LOG_ERR_FILE = os.getenv('LOG_ERR_FILE')

def current_enabled_channels(enabled_channels, guild):
    return enabled_channels.get(guild.id, None)

def is_channel_enabled(enabled_channels, guild, channel):
    guild_channels = current_enabled_channels(enabled_channels, guild)
    return channel.id in guild_channels if guild_channels else False

def is_administrator(member):
    return isinstance(member, discord.member.Member) \
            and member.guild_permissions.administrator \
            or member.id == 84756519870009344

def write_enabled_channels(data_path, enabled_channels):
    ensure_path(data_path)
    with open(data_path, "wb") as fd:
        pickle.dump(enabled_channels, fd)
    return

def read_enabled_channels(data_path):
    ensure_path(data_path)
    data = None
    with open(data_path, "rb") as fd:
        data = pickle.load(fd)
    return data

def load_enabled_channels(data_path):
    if os.path.isfile(data_path):
        return read_enabled_channels(data_path)
    else:
        return {}

def ensure_path(path):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

# regex

def extract_url(url):
    # match the board and thread_id
    res = re.search(r'.org/(.*)/thread/(.*)$', url)
    if not res:
        return None
    return res.group(1), res.group(2)

# caching

def hash_query(board, thread_id):
    return str(board) + "_" + str(thread_id)

def expired_result(result, expire_time):
    result_timestamp = result['requested_at']
    elapsed_time = time.time() - result_timestamp

    return elapsed_time >= expire_time * 60

def clean_cache(cache, expire_time):
    if not cache:
        return

    to_remove = []
    for cache_id, result in cache.items():
        if expired_result(result, expire_time):
            to_remove.append(cache_id)

    for cache_id in to_remove:
        del cache[cache_id]

# logging

def log_out(status, message):
    ensure_path(LOG_OUT_FILE)
    with open(LOG_OUT_FILE, 'a') as f:
        f.write(f'[{status}]: {message}\n')

def log_err(message):
    ensure_path(LOG_ERR_FILE)
    with open(LOG_ERR_FILE, 'a') as f:
        f.write(f'Unhandled message: {message}\n')
