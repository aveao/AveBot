import discord
from discord.ext import commands

import logging
import logging.handlers

import sys
import traceback

import configparser

"""AveBot is a bot that does some neat and some dumb stuff."""

config_file_name = "avebot.ini"
log_file_name = "avebot.log"

max_file_size = 1000 * 1000 * 8 # Limit of discord (non-nitro) is 8MB (not MiB)
backup_count = 10000 # random big number
file_handler = logging.handlers.RotatingFileHandler(filename=log_file_name, maxBytes=max_file_size, backupCount=backup_count)
stdout_handler = logging.StreamHandler(sys.stdout)

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
'cogs.finance', 'cogs.imagemanip', 'cogs.fun', 'cogs.linguistics', 'cogs.stockstream']

bot = commands.Bot(command_prefix=get_prefix, description=config['base']['description'], pm_help=None)

bot.log = log
bot.config = config

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            log.error(f'Failed to load extension {extension}.', file=sys.stderr)
            log.error(traceback.print_exc())


@bot.event
async def on_ready():
    """http://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_ready"""
    log.info(f'\nLogged in as: {bot.user.name} - {bot.user.id}\ndpy version: {discord.__version__}\n')

    # Changes our bots Playing Status. type=1(streaming) for a standard game you could remove type and url.
    await bot.change_presence(game=discord.Game(name='rewriting in dpy rewrite qwq'))
    em = discord.Embed(title='AveBot initialized!')
    channel = bot.get_channel(int(config['base']['main-channel']))
    await channel.send(embed=em, file=discord.File(log_file_name))


bot.run(config['base']['token'], bot=True, reconnect=True)