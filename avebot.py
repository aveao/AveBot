import discord
from discord.ext import commands

import logging
import logging.handlers

import sys
import traceback

import configparser
import subprocess

import time
import datetime
import socket

"""AveBot is a bot that does some neat and some dumb stuff."""

config_file_name = "avebot.ini"
log_file_name = "avebot.log"

max_file_size = 1000 * 1000 * 8 # Limit of discord (non-nitro) is 8MB (not MiB)
backup_count = 10000 # random big number
file_handler = logging.handlers.RotatingFileHandler(filename=log_file_name, maxBytes=max_file_size, backupCount=backup_count)
stdout_handler = logging.StreamHandler(sys.stdout)

log_format = logging.Formatter('[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s')
file_handler.setFormatter(log_format)
stdout_handler.setFormatter(log_format)

log = logging.getLogger('discord')
log.setLevel(logging.INFO)
log.addHandler(file_handler)
log.addHandler(stdout_handler)

config = configparser.ConfigParser()
config.read(config_file_name)

def get_prefix(bot, message):
    prefixes = [config['base']['prefix']]

    return commands.when_mentioned_or(*prefixes)(bot, message)

initial_extensions = ['cogs.common', 'cogs.basic', 'cogs.admin', 'cogs.nsfw', 'cogs.technical',
'cogs.finance', 'cogs.imagemanip', 'cogs.fun', 'cogs.emojis', 'cogs.linguistics', 'cogs.stockstream']

bot = commands.Bot(command_prefix=get_prefix, description=config['base']['description'], pm_help=None)

def get_git_commit_text():
    return call_shell("git log -1 --pretty=%B")

def call_shell(command):
    return bytes.decode(subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)).strip()

def get_git_revision_short_hash():
    return call_shell("git log -1 --pretty=%h")

bot.log = log
bot.config = config
bot.call_shell = call_shell
bot.get_git_revision_short_hash = get_git_revision_short_hash
bot.get_git_commit_text = get_git_commit_text

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            log.error(f'Failed to load extension {extension}.', file=sys.stderr)
            log.error(traceback.print_exc())


@bot.event
async def on_ready():
    log.info(f'\nLogged in as: {bot.user.name} - {bot.user.id}\ndpy version: {discord.__version__}\n')

    await bot.change_presence(game=discord.Game(name=f'ab!help | {get_git_revision_short_hash()}'))

    local_time = str(datetime.datetime.now()).split('.')[0]
    total_guild_count = len(bot.guilds)
    total_user_count = len(list(bot.get_all_members()))
    total_unique_user_count = len(list(set(bot.get_all_members())))

    em = discord.Embed(title='AveBot initialized!')
    em.add_field(name="Git Hash", value=get_git_revision_short_hash())
    em.add_field(name="Last git message", value=get_git_commit_text())
    em.add_field(name="Hostname", value=socket.gethostname())
    em.add_field(name="Local Time", value=local_time)
    em.add_field(name="Guild count", value=total_guild_count)
    em.add_field(name="Users", value=total_user_count)
    em.add_field(name="Unique users", value=total_unique_user_count)

    bot.start_time = int(time.time())

    channel = bot.get_channel(int(config['base']['main-channel']))
    await channel.send(embed=em, file=discord.File(log_file_name))

@bot.event
async def on_command(ctx):
    log_text = f"{ctx.message.author} ({ctx.message.author.id}): \"{ctx.message.content}\" "
    if ctx.guild: # was too long for tertiary if
        log_text += f"on \"{ctx.channel.name}\" ({ctx.channel.id}) at \"{ctx.guild.name}\" ({ctx.guild.id})" 
    else: 
        log_text += f"on DMs ({ctx.channel.id})"
    log.info(log_text)

@bot.event
async def on_message(message):
    if not message.author.bot:
        await bot.process_commands(message)


bot.run(config['base']['token'], bot=True, reconnect=True)