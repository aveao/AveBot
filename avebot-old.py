import asyncio
import datetime
import os
import re
import socket
import subprocess
import time
import traceback
import inspect
import locale

from pathlib import Path
from decimal import *
from dateutil import parser

import random
import aiohttp 

import discord
from discord.ext import commands

import configparser



import logging
import logging.handlers
import sys

# TODO: COGS https://gist.github.com/leovoel/46cd89ed6a8f41fd09c5

session = aiohttp.ClientSession()

config_file_name = "avebot.ini"
log_file_name = "avebot.log"

perm_names = {'0': 'Banned', '1': 'Regular User', '2': 'Privileged User', '8': 'Mod', '9': 'Owner'}

config = configparser.ConfigParser()

if not Path(config_file_name).is_file():
    logging.warning("No config file ({}) found, please create one from avebot.ini.example file.".format(config_file_name))
    exit(3)

description = 'AveBot Rewrite\nGit Hash: {}\nLast Commit: {}' \
    .format(get_git_revision_short_hash(), get_git_commit_text())
bot = commands.Bot(command_prefix=prefix, description=description)


def save_config():
    with open(config_file_name, 'w') as configfile:
        config.write(configfile)


@bot.command(pass_context=True)
async def addpriv(contx):
    """Adds a privileged user (Mod/Owner only)"""
    if check_level(contx.message.author.id) in ["8", "9"]:
        privtoadd = contx.message.mentions
        for dtag in privtoadd:
            if not (check_level(contx.message.author.id) == "8" and check_level(dtag.id) in ["8", "9"]):
                config['permissions'][dtag.id] = "2"
                em = discord.Embed(title='Added {} ({}) as privileged user.'.format(str(dtag), dtag.id),
                                   description='Welcome to the team!', colour=0x64dd17)
                await bot.send_message(contx.message.channel, embed=em)
        save_config()


@bot.command(pass_context=True)
async def rmpriv(contx):
    """Removes a privileged user (Mod/Owner only)"""
    if check_level(contx.message.author.id) in ["8", "9"]:
        privtorm = contx.message.mentions
        for dtag in privtorm:
            if not (check_level(contx.message.author.id) == "8" and check_level(dtag.id) in ["8", "9"]):
                config['permissions'][dtag.id] = "1"
                em = discord.Embed(
                    title='Removed {} ({}) as privileged user.'.format(str(dtag), dtag.id), colour=0x64dd17)
                await bot.send_message(contx.message.channel, embed=em)
        save_config()


@bot.command(pass_context=True)
async def addmod(contx):
    """Adds a mod (Owner only)"""
    if check_level(contx.message.author.id) in ["9"]:
        modstoadd = contx.message.mentions
        for dtag in modstoadd:
            config['permissions'][dtag.id] = "8"
            em = discord.Embed(title='Added {} ({}) as mod.'.format(str(dtag), dtag.id),
                               description='Welcome to the team!', colour=0x64dd17)
            await bot.send_message(contx.message.channel, embed=em)
        save_config()


@bot.command(pass_context=True)
async def rmmod(contx):
    """Removes a mod (Owner only)"""
    if check_level(contx.message.author.id) in ["9"]:
        modstorm = contx.message.mentions
        for dtag in modstorm:
            config['permissions'][dtag.id] = "1"
            em = discord.Embed(title='Removed {} ({}) as mod.'.format(str(dtag), dtag.id), colour=0x64dd17)
            await bot.send_message(contx.message.channel, embed=em)
        save_config()


@bot.command(pass_context=True)
async def ban(contx):
    """Bans a user (Mod/Owner only)"""
    if check_level(contx.message.author.id) in ["8", "9"]:
        toban = contx.message.mentions
        for dtag in toban:
            if not (check_level(contx.message.author.id) == "8" and check_level(dtag.id) in ["8", "9"]):
                config['permissions'][dtag.id] = "0"
                em = discord.Embed(title='Banned {} ({}).'.format(str(dtag), dtag.id), colour=0x64dd17)
                await bot.send_message(contx.message.channel, embed=em)
        save_config()


@bot.command(pass_context=True)
async def unban(contx):
    """Unbans a user (Mod/Owner only)"""
    if check_level(contx.message.author.id) in ["8", "9"]:
        tounban = contx.message.mentions
        for dtag in tounban:
            if not (check_level(contx.message.author.id) == "8" and check_level(dtag.id) in ["8", "9"]):
                config['permissions'][dtag.id] = "1"
                em = discord.Embed(
                    title='Unbanned {} ({}).'.format(str(dtag), dtag.id), colour=0x64dd17)
                await bot.send_message(contx.message.channel, embed=em)
        save_config()


new_message = 0
new_command = 0

@bot.event
async def on_message(message):
    try:
        if message.author.bot:
            return

        global new_message
        global new_command
        new_message += 1
        if message.content.startswith(prefix):  # TODO: OK this is not reliable at all, find a better way to check this.
            new_command += 1

        if check_level(str(message.author.id)) != "0":  # Banned users simply do not get a response
            if message.content.lower().startswith(config["advanced"]["voting-prefix"].lower()):
                await bot.add_reaction(message, config["advanced"]["voting-emoji-y"])
                await bot.add_reaction(message, config["advanced"]["voting-emoji-n"])

            if message.content.startswith('abddg!'):  # implementing this here because ext.commands handle the bang name ugh
                toduck = message.content.replace("+", "%2B").replace("abddg!", "!").replace(" ", "+")
                j = await aiojson(
                    "https://api.duckduckgo.com/?q={}&format=json&pretty=0&no_redirect=1".format(toduck))
                resolvedto = j["Redirect"]
                if resolvedto:
                    unfurld = await unfurl_b(resolvedto)
                    await bot.send_message(message.channel, "Bang resolved to: {}".format(unfurld))
            if message.content.lower() == "{}help".format(prefix):
                help_text = open("help.md", "r").read()
                em = discord.Embed(title="Welcome to AveBot Rewrite",
                                   description=help_text,
                                   colour=0xDEADBF)
                await bot.send_message(message.channel, embed=em)
            else:
                await bot.process_commands(message)
    except Exception:
        await catch_error(traceback.format_exc())


logging.info("AveBot started. Git hash: " + get_git_revision_short_hash())
if not os.path.isdir("files"):
    os.makedirs("files")

bot.loop.create_task(update_stats())
bot.run(config['base']['token'])
