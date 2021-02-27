import os
import pickle
import discord

def current_enabled_channels(enabled_channels, guild):
    return enabled_channels.get(guild.id, None)

def is_channel_enabled(enabled_channels, guild, channel):
    guild_channels = current_enabled_channels(enabled_channels, guild)
    return channel.id in guild_channels if guild_channels else False

def is_administrator(member):
    return isinstance(member, discord.member.Member) \
            and member.guild_permissions.administrator

def write_enabled_channels(data_path, enabled_channels):
    with open(data_path, "wb") as fd:
        pickle.dump(enabled_channels, fd)
    return

def read_enabled_channels(data_path):
    data = None
    with open(data_path, "rb") as fd:
        data = pickle.load(fd)
    return data

def load_enabled_channels(data_path):
    if os.path.isfile(data_path):
        return read_enabled_channels(data_path)
    else:
        return {}

