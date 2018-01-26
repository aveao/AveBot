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

import PIL.Image
import PIL.ImageFilter
import PIL.ImageOps
import PIL.ImageFont
import PIL.ImageDraw

import logging
import logging.handlers
import sys

# TODO: COGS https://gist.github.com/leovoel/46cd89ed6a8f41fd09c5

session = aiohttp.ClientSession()

config_file_name = "avebot.ini"
log_file_name = "avebot.log"

perm_names = {'0': 'Banned', '1': 'Regular User', '2': 'Privileged User', '8': 'Mod', '9': 'Owner'}

max_file_size = 1000 * 1000 * 8 # Limit of discord (non-nitro) is 8MB (not MiB)
backup_count = 10000 # random big number
file_handler = logging.handlers.RotatingFileHandler(filename=log_file_name, maxBytes=max_file_size, backupCount=backup_count)
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=handlers
)

config = configparser.ConfigParser()

if not Path(config_file_name).is_file():
    logging.warning("No config file ({}) found, please create one from avebot.ini.example file.".format(config_file_name))
    exit(3)

config.read(config_file_name)

prefix = config['base']['prefix']

def get_git_commit_text():
    return call_shell("git log -1 --pretty=%B")

def call_shell(command):
    return bytes.decode(subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)).strip()

def git_pull():
    return call_shell("git pull")

def get_git_revision_short_hash():
    return call_shell("git log -1 --pretty=%h")


description = 'AveBot Rewrite\nGit Hash: {}\nLast Commit: {}' \
    .format(get_git_revision_short_hash(), get_git_commit_text())
bot = commands.Bot(command_prefix=prefix, description=description)


def check_level(discord_id: str):
    #  = banned, 1 = regular user, 2 = privileged, 8 = mod, 9 = owner
    try:
        perm = config['permissions'][discord_id]
        if perm:
            return perm
        else:
            return "1"
    except KeyError:
        return "1"


def save_config():
    with open(config_file_name, 'w') as configfile:
        config.write(configfile)


async def download_file(url, local_filename):  # This function is based on https://stackoverflow.com/a/35435419/3286892 by link2110 (https://stackoverflow.com/users/5890923/link2110), modified by Ave (https://github.com/aveao), licensed CC-BY-SA 3.0
    file_resp = await session.get(url)
    file = await file_resp.read()
    with open(local_filename, "wb") as f:
        f.write(file)


@bot.event
async def on_ready():
    st = str(datetime.datetime.now()).split('.')[0]
    logging.info('Logged in as')
    logging.info(bot.user.name)
    logging.info(bot.user.id)
    logging.info('------')
    try:
        await asyncio.sleep(3)
        await bot.change_presence(game=discord.Game(name='{}help | {}'.format(prefix, get_git_revision_short_hash())))
        em = discord.Embed(title='AveBot initialized!',
                           description='Git hash: `{}`\nLast git message: `{}`\nHostname: `{}`\nLocal Time: `{}`\nLogs are below.'
                           .format(get_git_revision_short_hash(), get_git_commit_text(), socket.gethostname(), st),
                           colour=0xDEADBF)
        await bot.send_message(discord.Object(id=config['base']['main-channel']), embed=em)
        await bot.send_file(discord.Object(id=config['base']['main-channel']), log_file_name)
        #open(log_file_name, 'w').close()  # Clears log
    except Exception:
        logging.error(traceback.format_exc())
        bot.close()
        exit(1)

async def catch_error(text):
    logging.error("Error: " + text)
    em = discord.Embed(title="An error happened", description=text,
                       colour=0xcc0000)
    await bot.send_message(discord.Object(id=config['base']['main-channel']), embed=em)

@bot.command(pass_context=True)
async def roll(contx, dice: str):
    """Rolls a dice in NdN format.
    Example: ab!roll 1d20
    Example with modifier: ab!roll 1d20 + 2"""

    modification = 0
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await catch_error(traceback.format_exc())
        await bot.say('Format has to be in NdN!')
        return

    try:
        modifier = contx.message.content.replace(prefix+"roll "+dice, "").replace(" ", "")
        logging.error("modifier is " + modifier)
        if modifier.startswith("+"):
            modification = int(modifier.replace("+", ""))
        elif modifier.startswith("-"):
            modification = -int(modifier.replace("-", ""))
    except Exception:
        await catch_error(traceback.format_exc())
        await bot.say('Exception during modifier stuff!')
        return

    result = ', '.join(str(random.randint(1, limit)+modification) for r in range(rolls))
    await bot.say("{} (Modifier: {})".format(result, modification))


@bot.command(pass_context=True)
async def info(contx):
    """Returns bot's info."""
    st = str(datetime.datetime.now()).split('.')[0]
    em = discord.Embed(title='AveBot Info',
                       description='You\'re running AveBot Rewrite.\nGit hash: `{}`\nLast git message: `{}`\nHostname: `{}`\nLocal Time: `{}`'
                       .format(get_git_revision_short_hash(), get_git_commit_text(), socket.gethostname(), st),
                       colour=0xDEADBF)
    em.set_author(name='AveBot Rewrite', icon_url='https://s.ave.zone/c7d.png')
    await bot.send_message(contx.message.channel, embed=em)


@bot.command(hidden=True)
async def govegan():
    """Links a resource that'll make you reconsider eating meat."""
    await bot.say("https://zhangyijiang.github.io/puppies-and-chocolate/")


@bot.command()
async def servercount():
    """Returns the amount of servers AveBot is in."""
    await bot.say("AveBot is in {} servers.".format(str(len(bot.servers))))


@bot.command()
async def serverlist():
    """Returns the list of servers AveBot is in."""
    avebot_servers = bot.servers
    text_to_post = "**AveBot is in {} servers:**\n".format(str(len(avebot_servers)))
    total_user_count = 0
    for server in avebot_servers:
        text_to_post += "• **{}** (**{} members**)\n".format(server.name.replace("@", ""), str(server.member_count))
        total_user_count += server.member_count
    text_to_post += "In total, AveBot is servicing **{} users**.".format(str(total_user_count))
    sliced_message = slice_message(text_to_post, 2000)
    for msg in sliced_message:
        await bot.say(msg)


@bot.command(pass_context=True)
async def whoami(contx):
    """Returns your information."""
    await bot.say(
        "You are {} (`{}`) and your permission level is {}.".format(
            contx.message.author.name, contx.message.author.id, perm_names[check_level(contx.message.author.id)]))

async def get_images(contx, caller_command):
    images_to_process = []
    for attach in contx.message.attachments:
        extension = os.path.splitext(attach['filename'])[1]
        filename = "files/powered-by-avebot-bot.ave.zone-{}att{}".format(contx.message.id, extension).split('?')[0]
        await download_file(attach['proxy_url'], filename)
        if extension != ".jpg" or extension != ".jpeg":
            im = PIL.Image.open(filename)
            new_name = filename.replace(extension, ".jpg")
            im.save(new_name, "JPEG")
            filename = new_name
        images_to_process.append(filename)
    stuff_after = contx.message.content.replace(prefix + caller_command, "").replace(" ", "")
    if stuff_after != "" and stuff_after.startswith("http"):
        extension = str(os.path.splitext(stuff_after)[1].split('?')[0])
        filename = "files/powered-by-avebot-bot.ave.zone-{}txt{}".format(contx.message.id, extension)
        await download_file(stuff_after, filename)
        if extension != ".jpg" or extension != ".jpeg":
            im = PIL.Image.open(filename)
            new_name = filename.replace(extension, ".jpg")
            im.save(new_name, "JPEG")
            filename = new_name
        images_to_process.append(filename)
    return images_to_process


async def get_image_links(contx, caller_command):
    image_links = []
    for attach in contx.message.attachments:
        image_links.append(attach['proxy_url'])
    stuff_after = contx.message.content.replace(prefix + caller_command, "").replace(" ", "")
    if stuff_after != "" and stuff_after.startswith("http"):
        image_links.append(stuff_after)
    return image_links

@bot.command(pass_context=True)
async def sbahjify(contx):
    """Makes images hella and sweet.

    Usage: ab!sbahjify <link, if you're not uploading an image to discord>"""
    images_to_process = await get_images(contx, "sbahjify")
    msg_to_send = 'Processing image(s).' if len(
        images_to_process) != 0 else '{}: No images found. Try linking them or uploading them directly through discord.'.format(contx.message.author.mention)
    tmp = await bot.send_message(contx.message.channel, msg_to_send)
    for imgtp in images_to_process:
        logging.info("Processing {} for sbahj".format(imgtp))
        im = PIL.Image.open(imgtp)

        for _ in range(2):
            im = PIL.ImageOps.equalize(im)  # Drab-ify, but embellish otherwise hidden artifacts
            im = PIL.ImageOps.solarize(im, 250)  # Create weird blotchy artifacts, but inverts huge swaths
            im = PIL.ImageOps.posterize(im, 2)  # Flatten colors
            for _ in range(2):
                im = im.filter(PIL.ImageFilter.SHARPEN)
                im = im.filter(PIL.ImageFilter.SMOOTH)
                im = im.filter(PIL.ImageFilter.SHARPEN)
        w, h = im.size
        im = im.resize((w, int(h * 0.7)))
        im = PIL.ImageOps.equalize(im)  # Drab-ify, but embellish otherwise hidden artifacts
        im = im.filter(PIL.ImageFilter.SHARPEN)
        im = im.filter(PIL.ImageFilter.SHARPEN)
        out_filename = "files/sbahjify-{}".format(imgtp.replace("files/", ""))
        im.save(out_filename, quality=0, optimize=False, progressive=False)
        await bot.send_file(contx.message.channel, out_filename,
                            content="{}: Here's your image, hella and sweetened:".format(contx.message.author.mention))
    await asyncio.sleep(5)
    await bot.delete_message(tmp)


@bot.command(pass_context=True)
async def jpegify(contx):
    """Makes images jpeg. Also check out ab!ultrajpegify.

    Usage: ab!jpegify <link, if you're not uploading an image to discord>"""
    images_to_process = await get_images(contx, "jpegify")
    msg_to_send = 'Processing image(s).' if len(
        images_to_process) != 0 else '{}: No images found. Try linking them or uploading them directly through discord.'.format(contx.message.author.mention)
    tmp = await bot.send_message(contx.message.channel, msg_to_send)
    for imgtp in images_to_process:
        logging.info("Processing {} for jpeg".format(imgtp))
        im = PIL.Image.open(imgtp)

        im = im.filter(PIL.ImageFilter.SHARPEN)
        im = im.filter(PIL.ImageFilter.SMOOTH)
        out_filename = "files/jpegify-{}".format(imgtp.replace("files/", ""))
        im.save(out_filename, quality=0, optimize=False, progressive=False)
        await bot.send_file(contx.message.channel, out_filename,
                            content="{}: Here's your image, jpegified: (also try `{}ultrajpegify`!)".format(contx.message.author.mention, prefix))
    await asyncio.sleep(5)
    await bot.delete_message(tmp)


@bot.command(pass_context=True)
async def ultrajpegify(contx):
    """Makes images ultra jpeg.

    Usage: ab!ultrajpegify <link, if you're not uploading an image to discord>"""
    images_to_process = await get_images(contx, "ultrajpegify")
    msg_to_send = 'Processing image(s).' if len(
        images_to_process) != 0 else '{}: No images found. Try linking them or uploading them directly through discord.'.format(contx.message.author.mention)
    tmp = await bot.send_message(contx.message.channel, msg_to_send)
    for imgtp in images_to_process:
        logging.info("Processing {} for new ultrajpeg".format(imgtp))
        im = PIL.Image.open(imgtp)
        out_filename = "files/ultrajpegify-{}".format(imgtp.replace("files/", ""))
        w, h = im.size
        for x in range(0, 25):
            im = im.resize((int(w * 0.9), int(h * 1.1)))
            im.save(out_filename, quality=0, optimize=False, progressive=False)
            im = PIL.Image.open(out_filename)

            im = im.resize((int(w * 1.1), int(h * 0.9)))
            im.save(out_filename, quality=0, optimize=False, progressive=False)
            im = PIL.Image.open(out_filename)
        im = im.resize((w, h))
        im.save(out_filename, quality=0, optimize=False, progressive=False)
        await bot.send_file(contx.message.channel, out_filename,
                            content="{}: Here's your image, ULTRA jpegified:".format(contx.message.author.mention))
    await asyncio.sleep(5)
    await bot.delete_message(tmp)


@bot.command(pass_context=True)
async def mazeify(contx):
    """Makes images maze-like, with sharpen filter and jpeg abuse.

    Usage: ab!mazeify <link, if you're not uploading an image to discord>"""
    images_to_process = await get_images(contx, "mazeify")
    msg_to_send = 'Processing image(s).' if len(
        images_to_process) != 0 else '{}: No images found. Try linking them or uploading them directly through discord.'.format(contx.message.author.mention)
    tmp = await bot.send_message(contx.message.channel, msg_to_send)
    for imgtp in images_to_process:
        logging.info("Processing {} for new mazeify".format(imgtp))
        im = PIL.Image.open(imgtp)
        out_filename = "files/mazeify-{}".format(imgtp.replace("files/", ""))

        for x in range(0, 7):
            im = im.filter(PIL.ImageFilter.SHARPEN)
            im.save(out_filename, quality=0, optimize=False, progressive=False)
            im = PIL.Image.open(out_filename)
        await bot.send_file(contx.message.channel, out_filename,
                            content="{}: Here's your image, mazeified (also try `{}ultramazeify`!):".format(contx.message.author.mention, prefix))
    await asyncio.sleep(5)
    await bot.delete_message(tmp)


@bot.command(pass_context=True)
async def ultramazeify(contx):
    """Makes images ultra maze.

    Usage: ab!ultramazeify <link, if you're not uploading an image to discord>"""
    images_to_process = await get_images(contx, "ultramazeify")
    msg_to_send = 'Processing image(s).' if len(
        images_to_process) != 0 else '{}: No images found. Try linking them or uploading them directly through discord.'.format(contx.message.author.mention)
    tmp = await bot.send_message(contx.message.channel, msg_to_send)
    for imgtp in images_to_process:
        logging.info("Processing {} for new ultramazeify".format(imgtp))
        im = PIL.Image.open(imgtp)
        out_filename = "files/ultramazeify-{}".format(imgtp.replace("files/", ""))

        for x in range(0, 10):
            for y in range(0, 10):
                im = im.filter(PIL.ImageFilter.SHARPEN)
            im.save(out_filename, quality=0, optimize=False, progressive=False)
            im = PIL.Image.open(out_filename)
        await bot.send_file(contx.message.channel, out_filename,
                            content="{}: Here's your image, ULTRA mazeified:".format(contx.message.author.mention))
    await asyncio.sleep(5)
    await bot.delete_message(tmp)


@bot.command(pass_context=True)
async def joelify(contx):
    """A tribute to joel (of vinesauce)."""
    try:
        images_to_process = await get_images(contx, "joelify")
        msg_to_send = 'Processing image(s).' if len(
            images_to_process) != 0 else '{}: No images found. Try linking them or uploading them directly through discord.'.format(contx.message.author.mention)
        tmp = await bot.send_message(contx.message.channel, msg_to_send)
        for imgtp in images_to_process:
            logging.info("Processing {} for joelification".format(imgtp))
            im = PIL.Image.open(imgtp)

            w, h = im.size
            for i in range(0, 100):
                w_val = (random.randint(1, 20) / 10)
                h_val = (random.randint(1, 20) / 10)
                im = im.resize((int(w * w_val), int(h * h_val)))
                im = im.resize((w, h))

            out_filename = "files/joelify-{}".format(imgtp.replace("files/", ""))
            im.save(out_filename, quality=50, optimize=False, progressive=False)
            await bot.send_file(contx.message.channel, out_filename,
                                content="{}: Here's your image, joelified (also try `{}ultrajoelify`):".format(contx.message.author.mention, prefix))
        await asyncio.sleep(5)
        await bot.delete_message(tmp)
    except Exception:
        await catch_error(traceback.format_exc())


@bot.command(pass_context=True)
async def ultrajoelify(contx):
    """A tribute to joel (of vinesauce)."""
    try:
        images_to_process = await get_images(contx, "ultrajoelify")
        msg_to_send = '{}: Processing image(s), this\'ll take some time (~30 secs).' if len(
            images_to_process) != 0 else '{}: No images found. Try linking them or uploading them directly through discord.'.format(contx.message.author.mention)
        tmp = await bot.send_message(contx.message.channel, msg_to_send)
        for imgtp in images_to_process:
            logging.info("Processing {} for ultra joelification".format(imgtp))
            im = PIL.Image.open(imgtp)

            w, h = im.size
            for i in range(0, 500):
                w_val = (random.randint(1, 20) / 10)
                h_val = (random.randint(1, 20) / 10)
                im = im.resize((int(w * w_val), int(h * h_val)))
                im = im.resize((w, h))

            out_filename = "files/joel{}".format(imgtp.replace("files/", ""))
            im.save(out_filename, quality=50, optimize=False, progressive=False)
            await bot.send_file(contx.message.channel, out_filename,
                                content="{}: Here's your image, ultra joelified:".format(contx.message.author.mention))
        await asyncio.sleep(5)
        await bot.delete_message(tmp)
    except Exception:
        await catch_error(traceback.format_exc())

@bot.command(pass_context=True, aliases=['giffy', 'gif', 'gifit', 'owo'])
async def gifify(ctx, *, text: str):
    """Gives a gif image of the text supplied. Use _ to insert space."""
    fontname = "MuktaMalar-Medium.ttf"

    tsplit = text.split(" ")
    tcount = len(tsplit)
    tcurrent = 0
    filenames = ""

    for word in tsplit:
        word = word.replace("_", " ")
        tcurrent += 1
        imgsize = 128

        im=PIL.Image.new("RGB", (imgsize, imgsize), color="#343A3B")

        fsize = imgsize
        f = PIL.ImageFont.truetype(fontname, fsize)

        if f.getsize(word)[0] > imgsize:
            fsize = int(fsize/(f.getsize(word)[0] / imgsize))
        f = PIL.ImageFont.truetype(fontname, fsize)

        txt=PIL.Image.new('L', f.getsize(word))
        d = PIL.ImageDraw.Draw(txt)
        d.text((0, 0), word, font=f, fill=255)
        w=txt.rotate(0, expand=1)

        horipos = int((imgsize-f.getsize(word)[0])/2)
        vertpos = int(64-((f.getsize(word)[1]/1.5)))

        im.paste(PIL.ImageOps.colorize(w, (0,0,0), (255,255,255)), (horipos, vertpos), w)
        out_filename = "gifify/{}-{}.jpg".format(ctx.message.id, tcurrent)
        filenames += "{} ".format(out_filename)
        im.save(out_filename, quality=100, optimize=True)
    gif_filename = "gifify/{}.gif".format(ctx.message.id)
    call_shell("convert -delay 15 {}gifify/empty.jpg {}".format(filenames, gif_filename))
    await bot.send_file(ctx.message.channel, gif_filename, content="{} here you go:".format(ctx.message.author.mention))

@bot.command()
async def unfurl(link: str):
    """Finds where a URL redirects to."""
    resolved = await unfurl_b(link)
    await bot.say("<{}> Unfurls to <{}>".format(link, resolved))


@bot.command(aliases=['addavebot'])
async def invite():
    """Gives a link that can be used to add AveBot."""
    inviteurl = discord.utils.oauth_url(bot.user.id)
    await bot.say("You can use the following link to add AveBot to your server:\n<{}>".format(inviteurl))


@bot.command(pass_context=True, aliases=['contact'])
async def feedback(contx, *, contact_text: str):
    """Contacts developers with a message."""
    em = discord.Embed(description=contact_text,
                       colour=0xDEADBF)
    em.set_author(name="{} ({}) on \"{}\" at \"{}\"".format(str(contx.message.author), contx.message.author.id,
                                                            contx.message.channel.name,
                                                            contx.message.server.name),
                  icon_url=contx.message.author.avatar_url)
    await bot.send_message(discord.Object(id=config['base']['support-channel']), embed=em)

    em = discord.Embed(title='Feedback sent!',
                       description='Your message has been delivered to the developers.',
                       colour=0xDEADBF)
    await bot.send_message(contx.message.channel, embed=em)


@bot.command(pass_context=True)
async def sinfo(contx):
    """Shows info about the current server."""
    the_server = contx.message.server
    em = discord.Embed(title='Server info of {} ({})'.format(the_server.name, the_server.id),
                       description='Count of users: **{}**\nRegion: **{}**\nOwner: **{}**\nVerification Level: **{}**\nCreated at: **{}**'.format(
                           str(the_server.member_count), str(the_server.region), str(the_server.owner),
                           str(the_server.verification_level), str(the_server.created_at)),
                       colour=0xDEADBF)
    # em.set_image(url=the_server.icon_url)
    em.set_thumbnail(url=the_server.icon_url)
    await bot.send_message(contx.message.channel, embed=em)


@bot.command(pass_context=True)
async def uinfo(contx):
    """Shows info about the user."""
    to_post = contx.message.mentions
    if len(to_post) == 0:  # if no one is mentioned, return current user
        to_post.append(contx.message.author)
    no_play_text = "No game is being played."
    for the_user in to_post:
        the_member = contx.message.server.get_member_named(str(the_user))
        played_game_text = no_play_text if the_member.game is None else the_member.game.name
        if played_game_text != no_play_text and the_member.game.type == 1:
            played_game_text += "**\nStreaming at: **{}".format(the_member.game.url)
        em = discord.Embed(title='User info of {} ({})'.format(str(the_user), the_user.id),
                           description='Registered at: **{}**\nJoined this server at: **{}**\nStatus: **{}**\nGame: **{}**\nIs bot: **{}**'.format(
                               str(the_user.created_at), str(the_member.joined_at), str(the_member.status),
                               played_game_text, (":white_check_mark:" if the_user.bot else ":x:")),
                           colour=0xDEADBF)

        em.set_thumbnail(url=the_user.avatar_url)
        await bot.send_message(contx.message.channel, embed=em)


@bot.command(aliases=['dig'])
async def resolve(domain: str):
    """Resolves a domain to a URL."""
    resolved = repr(socket.gethostbyname_ex(domain))
    await bot.say("Successfully resolved `{}` to `{}`".format(domain, resolved))


@bot.command(name="!")
async def _duckduckgo():
    """Resolves a duckduckgo bang."""
    await bot.say("No bang supplied. Try giving a bang like abddg!wiki.")

@bot.command(aliases=['fucksafemode'], pass_context=True)
async def tumblrgrab(ctx, *, link: str):
    reg = r'([a-z0-9-.]{1,})\/post\/([0-9]{1,})'
    m = re.search(reg, link)
    if m:
        site = m.group(1)
        postid = m.group(2)
        api_key = config['tumblr']['apikey']
        tumblrapicall_link = "https://api.tumblr.com/v2/blog/{}/posts/photo?id={}&api_key={}".format(site, postid, api_key)
        tumblr_json = await aiojson(tumblrapicall_link)
        tumblr_is_nsfw = ("x_tumblr_content_rating" in tumblr_json["meta"])
        logging.info(tumblr_is_nsfw)

        tumblr_image_base = "\n<{}> (NSFW!)" if tumblr_is_nsfw else "\n{}"

        tumblr_json_images = tumblr_json["response"]["posts"][0]["photos"]
        logging.info("tumblr json images: {}".format(repr(tumblr_json_images)))
        tumblr_text = "{}, here are your requested image(s):".format(ctx.message.author.mention)
        for image in tumblr_json_images:
            current_count = len(tumblr_text)+1
            total_count = len(tumblr_json_images)
            tumblr_text += tumblr_image_base.format(image["original_size"]["url"])
        logging.info(tumblr_text)
        await bot.send_message(ctx.message.channel, tumblr_text)
    else:
        await bot.send_message(ctx.message.channel, "No tumblr link detected")


@bot.command(aliases=["unixtime"])
async def epoch():
    """Returns the Unix Time / Epoch."""
    await bot.say("Current epoch time is: **{}**.".format(str(int(time.time()))))


@bot.command(pass_context=True)
async def ping(contx):
    """Calculates the ping between the bot and the discord server."""
    before = time.monotonic()
    tmp = await bot.send_message(contx.message.channel, 'Calculating...')
    after = time.monotonic()
    ping_ms = (after - before) * 1000
    message_text = ':ping_pong: Ping is {}ms'.format(str(ping_ms)[:6])
    await bot.edit_message(tmp, message_text)


@bot.command(name='exit', pass_context=True)
async def _exit(contx):
    """Quits the bot (Owner only)."""
    if check_level(contx.message.author.id) == "9":
        await bot.say("Exiting AveBot, goodbye!")
        await bot.logout()


@bot.command(pass_context=True)
async def pull(contx):
    """Does a git pull (Owner only)."""
    if check_level(contx.message.author.id) == "9":
        tmp = await bot.send_message(contx.message.channel, 'Pulling...')
        git_output = git_pull()
        await bot.edit_message(tmp, "Pull complete. Output: ```{}```".format(git_output))
        # await bot.logout()


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
async def fetchlog(contx):
    """Returns log"""
    if check_level(contx.message.author.id) in ["9"]:
        await bot.send_file(contx.message.channel, log_file_name, content="Here's the current log file:")


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


@bot.command(name='eval', pass_context=True)
async def _eval(ctx, *, code: str):
    """Evaluates some code (Owner only)"""
    if check_level(ctx.message.author.id) in ["9"]:
        try:
            code = code.strip('` ')

            env = {
                'bot': bot,
                'ctx': ctx,
                'message': ctx.message,
                'server': ctx.message.server,
                'channel': ctx.message.channel,
                'author': ctx.message.author
            }
            env.update(globals())

            logging.info("running:" + repr(code))
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result

            result = "Success! {}".format(repr(result))
            for msg in slice_message(result, 1994):
                await bot.send_message(ctx.message.channel, "```{}```".format(msg))
        except:
            await bot.send_message(ctx.message.channel, "Error! ```{}```".format(traceback.format_exc()))
    else:
        logging.info("no perms for eval")


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


@bot.command(pass_context=True)
async def say(contx, *, the_text: str):
    """Says something (Mod/Owner only)."""
    if check_level(contx.message.author.id) in ["8", "9"]:
        await bot.say(the_text)


@bot.command(pass_context=True)
async def material(contx, filename: str):
    """Gets a file from material.io's icons gallery (Privileged/Mod/Admin only)."""
    if check_level(contx.message.author.id) in ["2", "8", "9"]:
        if not filename.startswith('ic_'):
            filename = "ic_" + filename
        if not filename.endswith('.svg'):
            filename = filename + "_white_48px.svg"
        link = "https://storage.googleapis.com/material-icons/external-assets/v4/icons/svg/" + filename
        filename = "files/" + filename
        if not Path(filename).is_file():  # caching
            await download_file(link, filename)
        await bot.send_file(contx.message.channel, filename,
                            content="Here's the file you requested.")


@bot.command(pass_context=True)
async def get(contx, link: str):
    """Gets a file from the internet (Privileged/Mod/Admin only)."""
    if check_level(contx.message.author.id) in ["2", "8", "9"]:
        filename = "files/" + link.split('/')[-1]
        await download_file(link, filename)
        file_size = Path(filename).stat().st_size
        if file_size < 1024 * 1024 * 7:  # Limit of discord is 7MiB
            await bot.send_file(contx.message.channel, filename,
                                content="{}: Here's the file you requested.".format(contx.message.author.mention))
        else:
            bot.say(
                "{}: File is too big for discord (Limit is 7MiB, file is {}MiB).".format(contx.message.author.mention,
                                                                                         (file_size / (1024 * 1024))))
        os.remove(filename)  # Remove file when we're done with it (kinda risky TBH )


@bot.command(pass_context=True)
async def dget(contx, link: str):
    """Directly gets (doesn't care about name) a file from the internet (Privileged/Mod/Admin only)."""
    if check_level(contx.message.author.id) in ["2", "8", "9"]:
        filename = "files/requestedfile"
        await download_file(link, filename)
        file_size = Path(filename).stat().st_size
        if file_size < 1024 * 1024 * 7:  # Limit of discord is 7MiB
            await bot.send_file(contx.message.channel, filename,
                                content="{}: Here's the file you requested.".format(contx.message.author.mention))
        else:
            bot.say(
                "{}: File is too big for discord (Limit is 7MiB, file is {}MiB).".format(contx.message.author.mention,
                                                                                         (file_size / (1024 * 1024))))
        os.remove(filename)  # Remove file when we're done with it (kinda risky TBH )


@bot.command()
async def xkcd(xkcdcount: int):
    """Returns info about the specified xkcd comic."""
    j = await aiojson("https://xkcd.com/{}/info.0.json".format(str(xkcdcount)))
    resolvedto = j["img"]
    if resolvedto:
        messagecont = "**XKCD {0}:** `{1}`, published on {2}-{3}-{4} (DMY)\n**Image:** {5}\n**Alt text:** `{6}`\n" \
                      "Explain xkcd: <http://www.explainxkcd.com/wiki/index.php/{0}>" \
            .format(str(j["num"]), j["safe_title"], j["day"], j["month"], j["year"], resolvedto, j["alt"])
        await bot.say(messagecont)


@bot.command()
async def xkcdlatest():
    """Returns info about the latest xkcd comic."""
    j = await aiojson("https://xkcd.com/info.0.json")
    resolvedto = j["img"]
    if resolvedto:
        messagecont = "**XKCD {0}:** `{1}`, published on {2}-{3}-{4} (DMY)\n**Image:** {5}\n**Alt text:** `{6}`\n" \
                      "Explain xkcd: <http://www.explainxkcd.com/wiki/index.php/{0}>" \
            .format(str(j["num"]), j["safe_title"], j["day"], j["month"], j["year"], resolvedto, j["alt"])
        await bot.say(messagecont)


@bot.command()
async def copypasta(ticker: str):
    """Generates a copypasta for StockStream using the given ticker."""
    copypasta_list = ["Kreygasm MUST Kreygasm BUY Kreygasm {} Kreygasm THIS Kreygasm ROUND Kreygasm",
                      "FutureMan BUY FutureMan {} FutureMan FOR FutureMan A FutureMan BRIGHTER FutureMan FUTURE FutureMan",
                      "Clappy Lemme buy a {0} before I send you a {0} Clappy",
                      "GivePLZ TRAIN TO PROFIT TOWN TakeNRG BUY {}! GivePLZ BUY {} TakeNRG",
                      "PogChamp {} PogChamp IS PogChamp OUR PogChamp LAST PogChamp HOPE PogChamp"]
    to_post = "Copypasta ready: `{}`".format(random.choice(copypasta_list).format(ticker.upper()))
    await bot.say(to_post)


@bot.command()
async def copypastasell(ticker: str):
    """Generates a copypasta for StockStream using the given ticker."""
    copypasta_list = ["Kreygasm MUST Kreygasm SELL Kreygasm {} Kreygasm THIS Kreygasm ROUND Kreygasm",
                      "Kreygasm TIME Kreygasm TO Kreygasm CASH Kreygasm IN Kreygasm {} Kreygasm",
                      "FutureMan SELL FutureMan {} FutureMan FOR FutureMan A FutureMan BRIGHTER FutureMan FUTURE FutureMan",
                      "Clappy Lemme sell a {0} before I send you a {0} Clappy",
                      "GivePLZ TRAIN TO PROFIT TOWN TakeNRG SELL {}! GivePLZ SELL {} TakeNRG",
                      "SELLING PogChamp {} PogChamp IS PogChamp OUR PogChamp LAST PogChamp HOPE PogChamp"]
    to_post = "Copypasta ready: `{}`".format(random.choice(copypasta_list).format(ticker.upper()))
    await bot.say(to_post)


async def get_change_color(ticker: str):
    symbols = await aiojson("https://api.robinhood.com/quotes/?symbols={}".format(ticker.upper()))
    if symbols == None:
        return 0x000000  # black

    symbols_results = symbols["results"][0]

    current_price = (
        symbols_results["last_trade_price"] if symbols_results["last_extended_hours_trade_price"] is None else symbols_results[
            "last_extended_hours_trade_price"])
    diff = str(Decimal(current_price) - Decimal(symbols_results["previous_close"]))
    percentage = (100 * Decimal(diff) / Decimal(current_price))
    return _get_change_color(percentage)
    

def _get_change_color(change_percentage):
    change_percentage = str(change_percentage).split('.')[0] # before the dot
    if change_percentage.startswith('-'):
        int_perc = int(change_percentage) * -1  # make it positive
        colors = [0xFFEBEE, 0xFFCDD2, 0xEF9A9A, 0xE57373, 0xEF5350, 0xF44336, 0xE53935, 0xD32F2F, 0xC62828, 0xB71C1C,
                  0xD50000]
        return colors[10 if int_perc > 10 else int_perc]
    else:
        int_perc = int(change_percentage) + 1
        colors = [0xF1F8E9, 0xDCEDC8, 0xC5E1A5, 0xAED581, 0x9CCC65, 0x8BC34A, 0x7CB342, 0x689F38, 0x558B2F, 0x33691E,
                  0x1B5E20]
        return colors[10 if int_perc > 10 else int_perc]


@bot.command(pass_context=True, aliases=['stockchart', 'chart'])
async def c(contx, ticker: str):
    """Returns stock chart of the given ticker."""
    image_link = "https://finviz.com/chart.ashx?t={}&ty=c&ta=1&p=d&s=l".format(ticker.upper())
    title_link = "https://finviz.com/quote.ashx?t={}".format(ticker.upper())
    change_color = await get_change_color(ticker)
    em = discord.Embed(title='Chart for {}'.format(ticker.upper()),
                       colour=change_color,
                       url=title_link)
    em.set_image(url=image_link)
    em.set_footer(text='Powered by finviz.com'.format(ticker.upper()))
    await bot.send_message(contx.message.channel, embed=em)


async def aioget(url):
    try:
        data = await session.get(url)
        if data.status == 200:
            return await data.text()
        else:
            logging.error("HTTP Error {} while getting {}".format(data.status, url))
    except:
        logging.error("Error while getting {} on aioget: {}".format(url, traceback.format_exc()))


async def aiojson(url):
    try:
        data = await session.get(url)
        if data.status == 200:
            return await data.json(content_type=data.headers['Content-Type'])
        else:
            logging.error("HTTP Error {} while getting {}".format(data.status, url))
    except:
        logging.error("Error while getting {} on aiojson: {}".format(url, traceback.format_exc()))

def format_currency(amount, locale_to_use):
    try:
        locale.setlocale(locale.LC_ALL, locale_to_use)
        amount = Decimal(amount)
        return locale.currency(amount, grouping=True)
    except:
        logging.error("Error while converting {} on format_currency: {}".format(amount, traceback.format_exc()))


@bot.command(pass_context=True, aliases=['aveishot', 'home'])
async def aveheat(contx):
    """Returns heat info from ave's home."""
    try:
        heat_json = await aiojson(config['homeheat']['dataurl'])
        
        btc_data_timestamp = datetime.datetime.utcfromtimestamp(int(heat_json["timestamp"]))

        em = discord.Embed(title="Heat Inside Ave's House", timestamp=btc_data_timestamp)

        em.set_image(url=config['homeheat']['charturl'])
        em.set_footer(text="Chart data is UTC")
        
        em.add_field(name="Inside", value=f"{heat_json['inside']}°C")
        em.add_field(name="Outside", value=f"{heat_json['outside']}°C")
        
        await bot.send_message(contx.message.channel, embed=em)
    except:
        logging.error(traceback.format_exc())


@bot.command(pass_context=True)
async def btc(contx):
    """Returns bitcoin chart and price info."""
    try:
        currency_locale = "en_US.UTF-8"
        btc_bitstamp_json = await aiojson("https://www.bitstamp.net/api/ticker")

        btc_currentprice_rate = Decimal(btc_bitstamp_json["last"])
        btc_currentprice_string = format_currency(btc_currentprice_rate, currency_locale)

        btc_lastopen_rate = Decimal(btc_bitstamp_json["open"])
        btc_lastopen_string = format_currency(btc_lastopen_rate, currency_locale)

        btc_high_string = format_currency(btc_bitstamp_json["high"], currency_locale)
        btc_low_string = format_currency(btc_bitstamp_json["low"], currency_locale)
        btc_bid_string = format_currency(btc_bitstamp_json["bid"], currency_locale)
        btc_ask_string = format_currency(btc_bitstamp_json["ask"], currency_locale)
        btc_volume_string = str(btc_bitstamp_json["volume"])

        btc_diff = btc_currentprice_rate - btc_lastopen_rate
        btc_change_percentage = (100 * Decimal(btc_diff) / Decimal(btc_currentprice_rate))
        btc_change_percentage_string = "{}%".format(str(btc_change_percentage)[:6])

        btc_change_color = _get_change_color(btc_change_percentage)
        
        btc_data_timestamp = datetime.datetime.utcfromtimestamp(int(btc_bitstamp_json["timestamp"]))

        link = "https://bitcoincharts.com/charts/chart.png?width=600&m=bitstampUSD&r=30&c=0&e=&t=S&m1=10&m2=25&x=0&v=1&cv=0&ps=0&l=0&p=0"
        em = discord.Embed(color=btc_change_color, timestamp=btc_data_timestamp)

        em.set_author(name="30 Day BTC Chart and Info", icon_url="https://bitcoin.org/img/icons/opengraph.png")
        em.set_image(url=link)
        em.set_footer(text="Chart supplied by bitcoincharts.com under CC-BY-SA 3.0, price info supplied by BitStamp.")
        
        em.add_field(name="Current Price", value=btc_currentprice_string)
        em.add_field(name="Opening Price", value=btc_lastopen_string)
        
        em.add_field(name="Change", value=btc_change_percentage_string)
        em.add_field(name="Volume", value=btc_volume_string)
        
        em.add_field(name="High", value=btc_high_string)
        em.add_field(name="Low", value=btc_low_string)
        
        em.add_field(name="Bid", value=btc_bid_string)
        em.add_field(name="Ask", value=btc_ask_string)
        
        await bot.send_message(contx.message.channel, embed=em)
    except:
        logging.error(traceback.format_exc())

@bot.command(pass_context=True)
async def render(contx, page_link: str):
    """Returns an image of the site."""
    if check_level(contx.message.author.id) in ["2", "8", "9"]:
        link = "http://http2pic.haschek.at/api.php?url={}".format(page_link)
        em = discord.Embed(title='Page render for {}, as requested by {}'.format(page_link, str(contx.message.author)))
        em.set_image(url=link)
        em.set_footer(text='Powered by http2pic.haschek.at. If you want a domain banned (nsfw site etc) please PM ao#5755.')
        await bot.send_message(contx.message.channel, embed=em)


@bot.command()
async def bigly(*, text_to_bigly: str):
    """Makes a piece of text as big as the hands of the god emperor."""
    letters = re.findall(r'[a-z0-9 ]', text_to_bigly.lower())
    biglytext = ''
    ri = 'regional_indicator_'
    for letter in letters:
        biglytext = biglytext + ":" + ri + str(letter) + ":\u200b"
    to_post = biglytext.replace(ri + "0", "zero").replace(ri + "1", "one").replace(
        ri + "2", "two").replace(ri + "3", "three").replace(ri + "4",
                                                            "four").replace(ri + "5", "five").replace(ri + "6",
                                                                                                      "six").replace(
        ri + "7", "seven").replace(ri + "8", "eight").replace(ri + "9", "nine") \
        .replace(":" + ri + " :", "\n").replace("\n :", "\n:").replace("\n :", "\n:")  # Worst fucking hack ever.
    await bot.say(to_post)


@bot.command(pass_context=True)
async def howmanymessages(contx):
    """Counts how many messages you sent in this channel in last 10000 messages."""
    tmp = await bot.send_message(contx.message.channel, 'Calculating messages...')
    counter = 0
    allcounter = 0
    async for hmlog in bot.logs_from(contx.message.channel, limit=10000):
        allcounter += 1
        if hmlog.author == contx.message.author:
            counter += 1
    percentage_of_messages = str(100 * (counter / allcounter))[:6]
    message_text = '{}: You have sent {} messages out of the last {} in this channel (%{}).' \
        .format(contx.message.author.mention, str(counter), str(allcounter), percentage_of_messages)
    await bot.edit_message(tmp, message_text)


@bot.command(pass_context=True)
async def log(contx, count: int):
    """Returns a file out of the last N messages submitted in this channel."""
    if check_level(contx.message.author.id) in ["9"]:
        log_text = "===start of log, exported by avebot===\n"
        async for mlog in bot.logs_from(contx.message.channel, limit=count):
            log_text += "[{}]<{}>{}\n".format(str(mlog.timestamp), str(mlog.author), mlog.clean_content)

        mlog_file_name = "files/{}.log".format(contx.message.channel.id)
        file = open(mlog_file_name, "w")
        file.write(log_text)
        file.write("===end of log, exported by avebot===")
        file.close()
        await bot.send_file(contx.message.channel, mlog_file_name,
                            content="{}: Here's the log file you requested.".format(contx.message.author.mention))


@bot.command(pass_context=True)
async def sh(contx, *, command: str):
    """Runs a command on shell (owner only)."""
    if check_level(contx.message.author.id) in ["9"]:
        command = command.strip('`')
        tmp = await bot.send_message(contx.message.channel, 'Running `{}`...'.format(command))
        shell_output = call_shell(command)
        await bot.edit_message(tmp, "Command `{}` completed. Output: ```{}```".format(command, shell_output))


@bot.command()
async def similar(*, word: str):
    output = await aiojson(
        "https://api.datamuse.com/words?ml={}".format(word.replace(" ", "+")))
    await bot.say(
        "**Similar Word:** `{}`\n(more on <http://www.onelook.com/thesaurus/?s={}&loc=cbsim>)".format(output[0]["word"], word.replace(" ", "_")))


@bot.command()
async def typo(*, word: str):
    output = await aiojson(
        "https://api.datamuse.com/words?sp={}".format(word.replace(" ", "+")))
    await bot.say("**Typo Fixed:** `{}`\n(more on <http://www.onelook.com/?w={}&ls=a>)".format(output[0]["word"],
                                                                                               word.replace(" ", "_")))


@bot.command()
async def soundslike(*, word: str):
    output = await aiojson(
        "https://api.datamuse.com/words?sl={}".format(word.replace(" ", "+")))
    await bot.say("**Sounds like:** `{}`\n(more on <http://www.onelook.com/?w={}&ls=a>)".format(output[0]["word"],
                                                                                                word.replace(" ", "_")))


@bot.command()
async def rhyme(*, word: str):
    output = await aiojson(
        "https://api.datamuse.com/words?rel_rhy={}".format(word.replace(" ", "+")))
    await bot.say(
        "**Rhymes with:** `{}`\n(more on <http://www.rhymezone.com/r/rhyme.cgi?Word={}&typeofrhyme=adv&org1=syl&org2=l&org3=y>)".format(
            output[0]["word"], word.replace(" ", "_")))


@bot.command(pass_context=True)
async def howold(contx):
    uri_base = config['howold']['uribase']
    subscription_key = config['howold']['subkey']
    urls = await get_image_links(contx, "howold")
    headers = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': subscription_key,
    }
    params = {
        'returnFaceId': 'false',
        'returnFaceLandmarks': 'false',
        'returnFaceAttributes': 'age,gender',
    }
    for url in urls:
        body = {'url': url}
        response = await session.post(uri_base + '/face/v1.0/detect', json=body, data=None, headers=headers, params=params)
        logging.info("Howold response: {}".format(response.text))
        parsed = await response.json()
        try:
            age = parsed[0]["faceAttributes"]["age"]
            gender = parsed[0]["faceAttributes"]["gender"]
            await bot.say("Age: **{}**\nGender: **{}**\n(it's hella inaccurate I know blame microsoft not me)".format(age, gender))
        except:
            logging.warning("howold failed: {}".format(traceback.format_exc()))
            await bot.say("No face detected.")


@bot.command(pass_context=True, aliases=['stock'])
async def s(contx, ticker: str):
    """Returns stock info about the given ticker."""
    currency_locale = "en_US.UTF-8"
    symbols = await aiojson(
        "https://api.robinhood.com/quotes/?symbols={}".format(ticker.upper()))
    if symbols == None:
        error_text = "Stock not found. This stock is probably not tradeable on robinhood."
        em = discord.Embed(title="Error",
                           description=error_text,
                           colour=0xab000d)
        await bot.send_message(contx.message.channel, embed=em)
        return
    symbols_result = symbols["results"][0]
    instrument = await aiojson(symbols_result["instrument"])
    fundamentals = await aiojson(
        "https://api.robinhood.com/fundamentals/{}/".format(ticker.upper()))

    current_price = Decimal(
        symbols_result["last_trade_price"] if symbols_result["last_extended_hours_trade_price"] is None else symbols_result[
            "last_extended_hours_trade_price"])
    diff = Decimal(Decimal(current_price) - Decimal(symbols_result["previous_close"]))
    percentage = str(100 * diff / current_price)[:6]

    if not percentage.startswith("-"):
        percentage = "+" + percentage

    current_price_string = format_currency(current_price, currency_locale)
    diff_string = format_currency(diff, currency_locale)
    bid_price_string = format_currency(Decimal(symbols_result["bid_price"]), currency_locale)
    ask_price_string = format_currency(Decimal(symbols_result["ask_price"]), currency_locale)
    tradeable_string = (":white_check_mark:" if instrument["tradeable"] else ":x:")

    update_timestamp = parser.parse(symbols_result["updated_at"])

    symbol = symbols_result["symbol"]
    change_color = await get_change_color(symbol)

    embed = discord.Embed(title="{}'s stocks info".format(symbol), color=change_color, timestamp=update_timestamp)

    embed.add_field(name="Name", value=instrument["name"])
    embed.add_field(name="Current Price", value=current_price_string)
    embed.add_field(name="Change from yesterday", value="{} ({}%)".format(diff_string, percentage))
    embed.add_field(name="Bid size", value="{} ({})".format(symbols_result["bid_size"], bid_price_string), inline=True)
    embed.add_field(name="Ask size", value="{} ({})".format(symbols_result["ask_size"], ask_price_string), inline=True)
    embed.add_field(name="Current Volume", value=fundamentals["volume"], inline=True)
    embed.add_field(name="Average Volume", value=fundamentals["average_volume"], inline=True)
    embed.add_field(name="Tradeable on Robinhood", value=tradeable_string, inline=True)
    embed.add_field(name="Country", value=":flag_{}:".format(instrument["country"].lower()), inline=True)

    await bot.send_message(contx.message.channel, embed=embed)


async def unfurl_b(link):
    max_depth = int(config["advanced"]["unfurl-depth"])
    current_depth = 0
    prev_link = ""
    last_link = link
    try:
        while (prev_link != last_link) and (current_depth < max_depth):
            prev_link = last_link
            last_link_aio = await session.request('head', prev_link, allow_redirects=True)
            last_link = last_link_aio.url
            current_depth += 1
        return last_link
    except Exception:
        return prev_link

def slice_message(text, size):
    reply_list = []
    while len(text) > size:
        reply_list.append(text[:size])
        text = text[size:]
    reply_list.append(text)
    return reply_list


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

            if message.content.startswith(prefix):
                if message.channel.is_private:
                    logging.info(
                        "{} ({}) said \"{}\" on PMs ({}).".format(message.author.name, message.author.id, message.content, message.channel.id))
                else:
                    logging.info("{} ({}) said \"{}\" on \"{}\" ({}) at \"{}\" ({})."
                           .format(message.author.name, message.author.id, message.content, message.channel.name, message.channel.id, message.server.name, message.server.id))
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

async def update_stats():
    await bot.wait_until_ready()
    while not bot.is_closed:
        if config['stats']['url'] and config['stats']['key']:
            server_count = len(bot.servers)
            user_count = 0
            for server in bot.servers:
                user_count += server.member_count

            global new_message
            global new_command
            url_to_call = "{}?key={}&user_count={}&server_count={}&new_total_messages={}&new_addressed_messages={}".format(config['stats']['url'], config['stats']['key'], user_count, server_count, new_message, new_command)
            new_message = 0
            new_command = 0
            await aioget(url_to_call)
        await asyncio.sleep(3)

logging.info("AveBot started. Git hash: " + get_git_revision_short_hash())
if not os.path.isdir("files"):
    os.makedirs("files")

bot.loop.create_task(update_stats())
bot.run(config['base']['token'])
