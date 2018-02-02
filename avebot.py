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

import psycopg2
from pathlib import Path

"""AveBot is a bot that does some neat and some dumb stuff."""

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
config.read("avebot.ini")

postgres_connection = psycopg2.connect(config['base']['postgres-connection-string'])

def get_prefix(bot, message):
    prefixes = [config['base']['prefix']]

    return commands.when_mentioned_or(*prefixes)(bot, message)

initial_extensions = ['cogs.common', 'cogs.permissionmanage', 'cogs.basic', 'cogs.admin', 'cogs.nsfw', 'cogs.technical',
'cogs.finance', 'cogs.imagemanip', 'cogs.fun', 'cogs.emojis', 'cogs.linguistics', 'cogs.stockstream', 'cogs.jose']

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
bot.postgres_connection = postgres_connection

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

    bot.bot_info = await bot.application_info()
    bot.start_time = int(time.time())
    bot.main_channel = bot.get_channel(int(config['base']['main-channel']))
    bot.support_channel = bot.get_channel(int(config['base']['support-channel']))

    await bot.main_channel.send(embed=em, file=discord.File(log_file_name))

@bot.event
async def on_command(ctx):
    log_text = f"{ctx.message.author} ({ctx.message.author.id}): \"{ctx.message.content}\" "
    if ctx.guild: # was too long for tertiary if
        log_text += f"on \"{ctx.channel.name}\" ({ctx.channel.id}) at \"{ctx.guild.name}\" ({ctx.guild.id})" 
    else: 
        log_text += f"on DMs ({ctx.channel.id})"
    log.info(log_text)


@bot.event
async def on_error(event_method, *args, **kwargs):
    log.error(f"Error on {event_method}: {sys.exc_info()}")


@bot.event
async def on_command_error(ctx, error):
    log.error(f"Error with \"{ctx.message.content}\" from \"{ctx.message.author}\" ({ctx.message.author.id}): {error}")


@bot.event
async def on_guild_join(guild):
    em = discord.Embed(title='Joined server')
    em.add_field(name="Name", value=guild.name)
    em.add_field(name="ID", value=guild.id)
    em.add_field(name="User Count", value=guild.member_count)
    em.add_field(name="Region", value=guild.region)
    em.add_field(name="Owner", value=guild.owner)
    em.add_field(name="Verification Level", value=guild.verification_level)
    em.add_field(name="Created at", value=guild.created_at)
    em.set_thumbnail(url=guild.icon_url)

    await bot.main_channel.send(embed=em, file=discord.File(log_file_name))
    await guild.owner.send("Hello and welcome to AveBot!\n"
        "If you don't know why you're getting this message, it's because someone added AveBot to your server\n"
        "Due to Discord API ToS, I am required to inform you that **I log command usages and errors**.\n"
        "**I don't log *anything* else**.\nLogging code can be found at <https://github.com/aveao/AveBot/blob/"
        "fea15e7973fb55fc0b2471254182a591370491d2/avebot.py#L99-L119>, please feel free to check it out "
        "if you have any concerns.\n\nIf you do not agree to be logged, stop using AveBot and remove it from your "
        "server as soon as possible.")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_perm = await bot.get_permission(message.author.id)
    if user_perm == 0:
        return

    ctx = await bot.get_context(message)
    await bot.invoke(ctx)

if not Path("avebot.ini").is_file():
    log.warning("No config file (avebot.ini) found, please create one from avebot.ini.example file.")
    exit(3)

bot.run(config['base']['token'], bot=True, reconnect=True)