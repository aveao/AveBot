import discord
import asyncio
import urllib.request
from pathlib import Path
import socket
import datetime
import traceback
import re
import os
import time
import subprocess
import socket
import json

client = discord.Client()

def get_git_revision_short_hash():
    return str(subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()).replace("b'","").replace("'","")

def avelog( content ):
    try:
        st = str(datetime.datetime.now()).split('.')[0]
        text = st + ': ' + content
        print(text)
        with open("log.txt", "a") as myfile:
            myfile.write(text+"\n")
        return
    except Exception:
        exit()

@client.event
async def on_ready():
    st = str(datetime.datetime.now()).split('.')[0]
    avelog('Logged in as')
    avelog(client.user.name)
    avelog(client.user.id)
    avelog('------')
    try:
        time.sleep(3)
        await client.change_presence(game=discord.Game(name='run >help'))
        em = discord.Embed(title='AveBot initialized!', description='Git hash: `'+get_git_revision_short_hash()+'`\nHostname: '+socket.gethostname()+'\nLocal Time: '+st+'\nLogs are attached.', colour=0xDEADBF)
        em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
        await client.send_message(discord.Object(id='305715263951732737'), embed=em)
        await client.send_file(discord.Object(id='305715263951732737'), "log.txt")
        open('log.txt', 'w').close() # Clears log
    except Exception:
        avelog(traceback.format_exc())
        exit()

@client.event
async def on_message(message):
    try:
        if message.content.startswith('>howmanymessages'):
            client.send_typing(message.channel)
            avelog(str(message.author) + " ran " + message.content)
            counter = 0
            tmp = await client.send_message(message.channel, 'Calculating messages...')
            async for log in client.logs_from(message.channel, limit=100):
                if log.author == message.author:
                    counter += 1    

            await client.edit_message(tmp, 'You have sent {} messages out of the last 100 in this channel.'.format(counter))
        elif message.content.startswith('>get'):
            await client.send_typing(message.channel)
            avelog(str(message.author) + " ran " + message.content)
            link = message.content.split(' ')[1]
            filename = "files/" + link.split('/')[-1]
            urllib.request.urlretrieve(link, filename);
            await client.send_file(message.channel, filename, content=":thumbsup: Here's the file you requested.")
        elif message.content.startswith('>invite'):
            await client.send_typing(message.channel)
            avelog(str(message.author) + " ran " + message.content)
            inviteurl = await client.create_invite(message.channel,max_uses=1)
            em = discord.Embed(title='Invite ready!', description='Here you go: ' + inviteurl.url, colour=0xDEADBF)
            em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
            await client.send_message(message.channel, embed=em)
        elif message.content.startswith('>contact'):
            await client.send_typing(message.channel)
            await client.send_typing(discord.Object(id='305857608378613761'))
            avelog(str(message.author) + " ran " + message.content)
            contactcontent = message.content.replace(">contact ", "")
            em = discord.Embed(title='Contact received!', description='**Message by:** '+str(message.author)+'\n**Message content:** '+contactcontent, colour=0xDEADBF)
            em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
            await client.send_message(discord.Object(id='305857608378613761'), embed=em)
            em = discord.Embed(title='Contact sent!', description='Your message has been delivered to the developers.', colour=0xDEADBF)
            em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
            await client.send_message(message.channel, embed=em)
        elif message.content.startswith('>bigly'):
            await client.send_typing(message.channel)
            avelog(str(message.author) + " ran " + message.content)
            letters = re.findall(r'[a-z0-9]', message.content.replace(">bigly ", "").lower())
            biglytext = ''
            for letter in letters:
                biglytext = biglytext+ ":regional_indicator_"+str(letter)+": "
            em = discord.Embed(title='Biglified', description=biglytext, colour=0xDEADBF)
            em.set_author(name='AveBot', icon_url='https://s.ave.zone/bigly.png')
            await client.send_message(message.channel, embed=em)
        elif message.content.startswith('>help'):
            await client.send_typing(message.channel)
            avelog(str(message.author) + " ran " + message.content)
            em = discord.Embed(title='Hello from AveBot!', description='This bot is developed and owned by ao#4273 and is currently running on `'+socket.gethostname()+'` server.\nGit hash: `'+get_git_revision_short_hash()+'`, repo: https://github.com/ardaozkal/AveBot\n**>help:** displays this \n**>get <url>:** gets a link and uploads it to discord\n**>dget <url>:** like get, but doesn\'t try to determine filename, also no caching\n**>invite:** generates an invite for this channel one use and unlimited duration\n**>material <name>:** gets an icon from material.io\'s free icons list.\n**>howmanymessages:** Checks how many messages you have in this channel, out of the last 100 ones.\n**>:regional_indicator_b: :regional_indicator_i: :regional_indicator_g: :regional_indicator_l: :regional_indicator_y::** Makes text as big as the hands of the god-emperor.\n**>contact <message>:** Send developers a message. Can be an idea or a bug report.\n**>resolve <domain>** / **>dig <domain>:** Resolves a domain to an IP address.\n**>ping:** Checks if bot is running.\n**>epoch** / **>unixtime:** Returns UNIX time since epoch.\n**!<bang> <something>** Resolves a duckduckgo bang. (more info at <https://duckduckgo.com/bang>)', colour=0xDEADBF)
            em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
            await client.send_message(message.channel, embed=em)
        elif message.content.startswith('>resolve') or message.content.startswith('>dig'):
            await client.send_typing(message.channel)
            avelog(str(message.author) + " ran " + message.content)
            resolveto = message.content.replace(">resolve ", "").replace(">dig ", "")
            resolved = repr(socket.gethostbyname_ex(resolveto))
            em = discord.Embed(title='Resolved ' + resolveto, description='Successfully resolved `' + resolveto + '` to `'+resolved+'`.', colour=0xDEADBF)
            em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
            await client.send_message(message.channel, embed=em)
        elif message.content.startswith('>ping'):
            await client.send_typing(message.channel)
            avelog(str(message.author) + " ran " + message.content)
            em = discord.Embed(title=':ping_pong: Pong', colour=0xDEADBF)
            em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
            await client.send_message(message.channel, embed=em)
        elif message.content.startswith('>epoch') or message.content.startswith('>unixtime'):
            await client.send_typing(message.channel)
            avelog(str(message.author) + " ran " + message.content)
            em = discord.Embed(title="Current epoch time is: **" + str(int(time.time()))+"**.", colour=0xDEADBF)
            em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
            await client.send_message(message.channel, embed=em)
        elif message.content.startswith('>dget'):
            await client.send_typing(message.channel)
            avelog(str(message.author) + " ran " + message.content)
            link = message.content.split(' ')[1]
            filename = "files/requestedfile"
            urllib.request.urlretrieve(link, filename);
            await client.send_file(message.channel, filename, content=":thumbsup: Here's the file you requested.")
        elif message.content.startswith('!'):
            await client.send_typing(message.channel)
            avelog(str(message.author) + " ran " + message.content)
            output = urllib.request.urlopen("https://api.duckduckgo.com/?q="+message.content.replace(" ","+")+"&format=json&pretty=0&no_redirect=1").read()
            j = json.loads(output)
            messagecont="Bang resolved to: "+j["Redirect"]
            await client.send_message(message.channel, content=messagecont)
        elif message.content.startswith('>material'):
            await client.send_typing(message.channel)
            avelog(str(message.author) + " ran " + message.content)
            filename = message.content.split(' ')[1]
            if not filename.startswith('ic_'):
                filename = "ic_" + filename
            if not filename.endswith(('.svg', '.png')):
                filename = filename + "_white_48px.svg"
            link = "https://storage.googleapis.com/material-icons/external-assets/v4/icons/svg/" + filename
            filename = "files/" + filename
            my_file = Path(filename)
            if not my_file.is_file():
                urllib.request.urlretrieve(link, filename);
            await client.send_file(message.channel, filename, content=":thumbsup: Here's the file you requested.")
    except Exception:
        avelog(traceback.format_exc())

avelog("AveBot started. Git hash: " + get_git_revision_short_hash())
if not os.path.isdir("files"):
    os.makedirs("files")

if os.path.exists("bottoken"):
    file = open("bottoken", "r") 
    client.run(file.read())
else:
    avelog("No bottoken file found! Please create one. Join discord.gg/discord-api and check out #faq for more info.")