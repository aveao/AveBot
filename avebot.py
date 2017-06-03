import asyncio
import datetime
import json
import os
import re
import socket
import subprocess
import time
import traceback

import urllib.request
import urllib.error

from pathlib import Path
from decimal import *

import random
import requests

import discord
from discord.ext import commands

# TODO: move to ext.commands
# TODO: add config support
# TODO: move user permissions to config.
# TODO: COGS https://gist.github.com/leovoel/46cd89ed6a8f41fd09c5
# TODO: Take over >help (on on_message, handle it before handling command)

botowner = "137584770145058817"
prefix='>'

def get_git_commit_text():
    return str(subprocess.check_output(['git', 'log', '-1', '--pretty=%B']).strip())[2:-1]


def get_git_revision_short_hash():
    return str(subprocess.check_output(['git', 'log', '-1', '--pretty=%h']).strip())[2:-1]


description = (
    'AveBot Rewrite\nGit Hash: ' + get_git_revision_short_hash() +
    '\nLast Commit: '+ get_git_commit_text())
bot = commands.Bot(command_prefix=prefix, description=description)


def get_ban_list():
    return []


def avelog(content):
    try:
        st = str(datetime.datetime.now()).split('.')[0]
        text = st + ': ' + content
        print(text)
        with open("log.txt", "a") as myfile:
            myfile.write(text + "\n")
        return
    except Exception:
        exit()


@bot.event
async def on_ready():
    st = str(datetime.datetime.now()).split('.')[0]
    avelog('Logged in as')
    avelog(bot.user.name)
    avelog(bot.user.id)
    avelog('------')
    try:
        asyncio.sleep(3)
        await bot.change_presence(game=discord.Game(name='run >help'))
        em = discord.Embed(title='AveBot initialized!',
                           description='Git hash: `' + get_git_revision_short_hash() + '`\nHostname: ' + socket.gethostname() + '\nLocal Time: ' + st + '\nLogs are attached.',
                           colour=0xDEADBF)
        em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
        await bot.send_message(discord.Object(id='305715263951732737'), embed=em)
        await bot.send_file(discord.Object(id='305715263951732737'), "log.txt")
        open('log.txt', 'w').close()  # Clears log
    except Exception:
        avelog(traceback.format_exc())
        exit()


@bot.command()
async def roll(dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await bot.say('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await bot.say(result)


@bot.command()
async def govegan():
    """Links a resource that'll make you reconsider eating meat."""
    await bot.say("https://zhangyijiang.github.io/puppies-and-chocolate/")


@bot.command()
async def servercount():
    """Returns the amount of servers AveBot is in."""
    await bot.say("AveBot is in {} servers.".format(str(len(bot.servers))))


@bot.command()
async def addavebot():
    """Gives a link that can be used to add AveBot."""
    inviteurl = discord.utils.oauth_url("305708836361207810") # TODO: Move to config file
    await bot.say("You can use {} to add AveBot to your server.".format(inviteurl))


@bot.command()
async def copypasta(ticker: str):
    """Generates a copypasta for StockStream using the given ticker."""
    copypasta_list = ["Kreygasm MUST Kreygasm BUY Kreygasm TICKER Kreygasm THIS Kreygasm ROUND Kreygasm",
                      "FutureMan BUY FutureMan TICKER FutureMan FOR FutureMan A FutureMan BRIGHTER FutureMan FUTURE FutureMan",
                      "Clappy Lemme buy a TICKER before I send you a TICKER Clappy",
                      "GivePLZ TRAIN TO PROFIT TOWN TakeNRG BUY TICKER! GivePLZ BUY TICKER TakeNRG",
                      "PogChamp TICKER PogChamp IS PogChamp OUR PogChamp LAST PogChamp HOPE PogChamp",
                      "Kreygasm MUST  Kreygasm BUY  Kreygasm COL  Kreygasm THIS  Kreygasm ROUND  Kreygasm"]
    to_post = random.choice(copypasta_list).replace("TICKER", ticker)
    await bot.say(to_post)


@bot.command()
async def bigly(text_to_bigly: str):
    """Makes a piece of text as big as the hands of the god emperor."""
    letters = re.findall(r'[a-z0-9 ]', text_to_bigly.lower())
    biglytext = ''
    ri = 'regional_indicator_'
    for letter in letters:
        biglytext = biglytext + ":" + ri + str(letter) + ": "
    to_post = biglytext.replace(ri + "0", "zero").replace(ri + "1", "one").replace(
        ri + "2", "two").replace(ri + "3", "three").replace(ri + "4",
        "four").replace(ri + "5", "five").replace(ri + "6", "six").replace(
        ri + "7", "seven").replace(ri + "8","eight").replace(ri + "9", "nine")\
        .replace(":" + ri + " :", "\n")
    await bot.say(to_post)


@bot.command(pass_context=True)
async def howmanymessages(context):
    """Counts how many messages you sent in this channel in last 10000 messages."""
    tmp = await bot.send_message(context.message.channel, 'Calculating messages...')
    counter = 0
    allcounter = 0
    async for log in bot.logs_from(context.message.channel, limit=10000):
        allcounter += 1
        if log.author == context.message.author:
            counter += 1
    percentage_of_messages = str(100 * (counter / allcounter))[:6]
    message_text = context.message.author.mention + ': You have sent ' + str(
        counter) + ' messages out of the last ' + str(
        allcounter) + ' in this channel (%' + percentage_of_messages + ').'
    await bot.edit_message(tmp, message_text)


    @bot.event
async def on_message(message):
    try:
        if message.content.lower().startswith('ok'):
            await bot.add_reaction(message, "🆗")  # OK emoji
        elif message.content.lower().startswith('hot'):
            await bot.add_reaction(message, "🔥")  # fire emoji
        elif message.content.lower().startswith('cool'):
            await bot.add_reaction(message, "❄")  # snowflake emoji
        elif message.content.lower().startswith('vote:'):
            await bot.add_reaction(message, "🇾")  # Y regional indicator emoji
            await bot.add_reaction(message, "🇳")  # N regional indicator emoji

        if "🤔" in message.content:  # thinking emoji
            await bot.add_reaction(message, "🤔")

        if not str(message.author.id) in get_ban_list(): # Banned users simply do not get a response
            if message.channel.is_private:
                avelog(message.author.name + " (" + message.author.id + ") said \"" + message.content + '"" on PMs.')
            else:
                avelog(
                    message.author.name + " (" + message.author.id + ") said \"" + message.content + '" on "' + message.channel.name + '" at "' + message.server.name + '".')

            await bot.process_commands(message)
    except Exception:
        avelog(traceback.format_exc())
        em = discord.Embed(title="An error happened", description="It was logged and will be reviewed by developers.",
                           colour=0xcc0000)
        em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
        await bot.send_message(message.channel, embed=em)


avelog("AveBot started. Git hash: " + get_git_revision_short_hash())
if not os.path.isdir("files"):
    os.makedirs("files")

try:
    with open("bottoken", "r") as tokfile:
        bot.run(tokfile.read().replace("\n", ""))
except FileNotFoundError:
    avelog("No bottoken file found! Please create one. Join discord.gg/discord-api and check out #faq for more info.")
