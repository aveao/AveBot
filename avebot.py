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
botowner = "137584770145058817"

def get_mods_list():
    try:
        with open("modslist", "r") as modfile:
            modfilething = modfile.read().split("\n")
            return modfilething
    except FileNotFoundError:
        avelog("No modslist file found! Please create one or run >addmod")
        return []
    except Exception:
        avelog(traceback.format_exc())

def get_privileged_list():
    try:
        with open("privlist", "r") as privfile:
            privfilething = privfile.read().split("\n")
            return privfilething
    except FileNotFoundError:
        avelog("No privlist file found! Please create one or run >addpriv")
        return []
    except Exception:
        avelog(traceback.format_exc())

def get_ban_list():
    try:
        with open("banlist", "r") as banfile:
            banfilething = banfile.read().split("\n")
            return banfilething
    except FileNotFoundError:
        avelog("No banlist file found! Please create one.")
        return []
    except Exception:
        avelog(traceback.format_exc())

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
        if message.content.lower().startswith('ok'):
            await client.add_reaction(message, "🆗")
        if message.content.startswith('>') or message.content.startswith('!'):
            if (not str(message.author.id) in get_ban_list()):
                if (message.channel.is_private):
                    avelog(message.author.name + " (" + message.author.id + ") ran " + message.content + ' on PMs.')
                else:
                    avelog(message.author.name + " (" + message.author.id + ") ran " + message.content + ' on '+message.channel.name+' at '+message.server.name+'.')
                if message.content.startswith('>howmanymessages'):
                    counter = 0
                    tmp = await client.send_message(message.channel, 'Calculating messages...')
                    async for log in client.logs_from(message.channel, limit=10000):
                        if log.author == message.author:
                            counter += 1    
                    await client.edit_message(tmp, 'You have sent {} messages out of the last 10000 in this channel.'.format(counter))
                elif message.content.startswith('>geninvite'):
                    inviteurl = await client.create_invite(message.channel,max_uses=1)
                    em = discord.Embed(title='Invite ready!', description='Here you go: ' + inviteurl.url + ' \n(Note: This invite is for THIS server/channel, not any other server. Please contact ao#5755 if you suspect that it is being abused and want to learn the identity of the person who abused this function.)', colour=0xDEADBF)
                    em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                    await client.send_message(message.channel, embed=em)
                elif message.content.startswith('>addavebot'):
                    inviteurl = await discord.utils.oauth_url("305708836361207810")
                    em = discord.Embed(title='Invite ready!', description='Here you go: ' + str(inviteurl), colour=0xDEADBF)
                    em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                    await client.send_message(message.channel, embed=em)
                elif message.content.startswith('>whoami'):
                    em = discord.Embed(title=':thinking:', description='You are `' + message.author.name + "` (`" + message.author.id + '`)', colour=0xDEADBF)
                    em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                    await client.send_message(message.channel, embed=em)
                elif message.content.startswith('>contact '):
                    contactcontent = message.content.replace(">contact ", "")
                    em = discord.Embed(title='Contact received!', description='**Message by:** '+str(message.author) + " (" + message.author.id + ')\n on '+message.channel.name+' at '+message.server.name+'\n**Message content:** '+contactcontent, colour=0xDEADBF)
                    em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                    await client.send_message(discord.Object(id='305857608378613761'), embed=em)
                    em = discord.Embed(title='Contact sent!', description='Your message has been delivered to the developers.', colour=0xDEADBF)
                    em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                    await client.send_message(message.channel, embed=em)
                elif message.content.startswith('>bigly '):
                    letters = re.findall(r'[a-z0-9 ]', message.content.replace(">bigly ", "").lower())
                    biglytext = ''
                    ri = 'regional_indicator_'
                    for letter in letters:
                        biglytext = biglytext+ ":"+ri+str(letter)+": "
                    em = discord.Embed(title='Biglified', description=biglytext.replace(ri+"0","zero").replace(ri+"1","one").replace(ri+"2","two").replace(ri+"3","three").replace(ri+"4","four").replace(ri+"5","five").replace(ri+"6","six").replace(ri+"7","seven").replace(ri+"8","eight").replace(ri+"9","nine").replace(":"+ri+" :","\n"), colour=0xDEADBF)
                    em.set_author(name='AveBot', icon_url='https://s.ave.zone/bigly.png')
                    await client.send_message(message.channel, embed=em)
                elif message.content.startswith('>helplong'):
                        await client.send_file(message.channel, "helplong.md", content="Here's the long help file:")
                elif message.content.startswith('>help'):
                    helpfile = open("help.md", "r") 
                    em = discord.Embed(title='Hello from AveBot!', description='This bot is developed and owned by ao#5755 and is currently running on `'+socket.gethostname()+'` server.\nGit hash: `'+get_git_revision_short_hash()+'`, repo: https://github.com/ardaozkal/AveBot\nInvite link is on the github repo.\n'+helpfile.read(), colour=0xDEADBF)
                    em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                    await client.send_message(message.channel, embed=em)
                elif message.content.startswith('>resolve ') or message.content.startswith('>dig '):
                    resolveto = message.content.replace(">resolve ", "").replace(">dig ", "")
                    resolved = repr(socket.gethostbyname_ex(resolveto))
                    em = discord.Embed(title='Resolved ' + resolveto, description='Successfully resolved `' + resolveto + '` to `'+resolved+'`.', colour=0xDEADBF)
                    em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                    await client.send_message(message.channel, embed=em)
                elif message.content.startswith('>ping'):
                    em = discord.Embed(title=':ping_pong: Pong', colour=0xDEADBF)
                    em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                    await client.send_message(message.channel, embed=em)
                elif message.content.startswith('>epoch') or message.content.startswith('>unixtime'):
                    em = discord.Embed(title="Current epoch time is: **" + str(int(time.time()))+"**.", colour=0xDEADBF)
                    em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                    await client.send_message(message.channel, embed=em)
                elif message.content.startswith('>erdogan') or message.content.startswith('>trump'):
                    em = discord.Embed(title="DICTATOR DETECTED", colour=0xDEADBF)
                    em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                    await client.send_message(message.channel, embed=em)
                elif message.content.startswith('!'):
                    output = urllib.request.urlopen("https://api.duckduckgo.com/?q="+message.content.replace(" ","+")+"&format=json&pretty=0&no_redirect=1").read().decode()
                    j = json.loads(output)
                    resolvedto = j["Redirect"]
                    if resolvedto:
                        messagecont="Bang resolved to: "+resolvedto
                        await client.send_message(message.channel, content=messagecont)
                elif message.content.startswith('>xkcd '):
                    toquery = message.content.replace(">xkcd", "").replace(" ", "").replace("xkcd.com/", "").replace("https://", "").replace("http://", "").replace("www.", "").replace("m.", "").replace("/", "") #lazy as hell :/
                    if toquery:
                        toquery = toquery + "/"
                    output = urllib.request.urlopen("https://xkcd.com/"+toquery+"info.0.json").read().decode()
                    j = json.loads(output)
                    resolvedto = j["img"]
                    title = j["safe_title"]
                    alt = j["alt"]
                    xkcdid = str(j["num"])
                    date = j["day"]+"-"+j["month"]+"-"+j["year"]+" (DDMMYYYY)"
                    if resolvedto:
                        messagecont="**XKCD "+xkcdid+":** `"+title+"`, published on "+date+"\n**Image:** " + resolvedto + "\n**Alt text:** `"+alt+"`\nExplain xkcd: <http://www.explainxkcd.com/wiki/index.php/"+xkcdid+">"
                        await client.send_message(message.channel, content=messagecont)
                elif message.content.startswith('>similar '):
                    toquery = message.content.replace(">similar ", "")
                    output = urllib.request.urlopen("https://api.datamuse.com/words?ml="+toquery.replace(" ","+")).read().decode()
                    j = json.loads(output)
                    em = discord.Embed(title="Similar word: " + j[0]["word"], description="(more on <http://www.onelook.com/thesaurus/?s="+toquery.replace(" ","_")+"&loc=cbsim>)", colour=0xDEADBF)
                    em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                    await client.send_message(message.channel, embed=em)
                elif message.content.startswith('>typo '):
                    toquery = message.content.replace(">typo ", "")
                    output = urllib.request.urlopen("https://api.datamuse.com/words?sp="+toquery.replace(" ","+")).read().decode()
                    j = json.loads(output)
                    em = discord.Embed(title="Typo fixed: " + j[0]["word"], description="(more on <http://www.onelook.com/?w="+toquery.replace(" ","+")+"&ls=a>)", colour=0xDEADBF)
                    em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                    await client.send_message(message.channel, embed=em)
                elif message.content.startswith('>soundslike '):
                    toquery = message.content.replace(">soundslike ", "")
                    output = urllib.request.urlopen("https://api.datamuse.com/words?sl="+toquery.replace(" ","+")).read().decode()
                    j = json.loads(output)
                    em = discord.Embed(title="Sounds like: " + j[0]["word"], description="(more on <http://www.onelook.com/?w="+toquery.replace(" ","+")+"&ls=a>)", colour=0xDEADBF)
                    em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                    await client.send_message(message.channel, embed=em)
                elif message.content.startswith('>rhyme '):
                    toquery = message.content.replace(">rhyme ", "")
                    output = urllib.request.urlopen("https://api.datamuse.com/words?rel_rhy="+toquery.replace(" ","+")).read().decode()
                    j = json.loads(output)
                    em = discord.Embed(title="Rhymes with: " + j[0]["word"], description="(more on <http://www.rhymezone.com/r/rhyme.cgi?Word="+toquery.replace(" ","+")+"&typeofrhyme=adv&org1=syl&org2=l&org3=y>)", colour=0xDEADBF)
                    em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                    await client.send_message(message.channel, embed=em)

                if message.author.id == botowner:
                    if message.content.startswith('>exit') or message.content.startswith('>brexit'):
                        em = discord.Embed(title='Exiting AveBot', description='Goodbye!', colour=0x64dd17)
                        em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                        await client.send_message(message.channel, embed=em)
                        exit()
                    elif message.content.startswith('>pull'):
                        em = discord.Embed(title='Pulling and restarting AveBot', description='BBIB!', colour=0x64dd17)
                        em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                        await client.send_message(message.channel, embed=em)
                        exit()
                    elif message.content.startswith('>addmod '):
                        modstoadd = message.mentions
                        with open("modslist", "a") as modfile:
                            for dtag in modstoadd: 
                                modfile.write(dtag.id+"\n")
                                em = discord.Embed(title='Added ' + str(dtag) + '(' + dtag.id + ') as mod.', description='Welcome to the team!', colour=0x64dd17)
                                em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                                await client.send_message(message.channel, embed=em)
                    elif message.content.startswith('>fetchlog'):
                        await client.send_file(message.channel, "log.txt", content="Here's the current log file:")
                else:
                    em = discord.Embed(title="Insufficient Permissions (Owner status needed)", colour=0xcc0000)
                    em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                    await client.send_message(message.channel, embed=em)

                if message.author.id in get_mods_list():   
                    if message.content.startswith('>addpriv '):
                        privstoadd = message.mentions
                        with open("privlist", "a") as privfile:
                            for dtag in privstoadd: 
                                privfile.write(dtag.id+"\n")
                                em = discord.Embed(title='Added ' + str(dtag) + '(' + dtag.id + ') as privileged user.', description='Welcome to the team!', colour=0x64dd17)
                                em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                                await client.send_message(message.channel, embed=em)
                    elif message.content.startswith('>ban '):
                        banstohand = message.mentions
                        with open("banlist", "a") as banfile:
                            for dtag in banstohand: 
                                banfile.write(dtag.id+"\n")
                                em = discord.Embed(title='Banned ' + str(dtag) + '(' + dtag.id + ').', description='(People are idiots)', colour=0x64dd17)
                                em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                                await client.send_message(message.channel, embed=em)
                    elif message.content.startswith('>say '):
                        tosay = message.content.replace(">say ", "")
                        await client.send_message(message.channel, content=tosay)
                else:
                    em = discord.Embed(title="Insufficient Permissions (Mod status needed)", colour=0xcc0000)
                    em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                    await client.send_message(message.channel, embed=em)

                if message.author.id in get_privileged_list():
                    if message.content.startswith('>material '):                        
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
                    elif message.content.startswith('>dget '):
                        link = message.content.split(' ')[1]
                        filename = "files/requestedfile"
                        urllib.request.urlretrieve(link, filename);
                        await client.send_file(message.channel, filename, content=":thumbsup: Here's the file you requested.")
                    elif message.content.startswith('>get '):
                        link = message.content.split(' ')[1]
                        filename = "files/" + link.split('/')[-1]
                        urllib.request.urlretrieve(link, filename);
                        await client.send_file(message.channel, filename, content=":thumbsup: Here's the file you requested.")
                else:
                    em = discord.Embed(title="Insufficient Permissions (Privileged status needed)", colour=0xcc0000)
                    em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                    await client.send_message(message.channel, embed=em)

            else:
                avelog(str(message.author) + " (" + message.author.id + ") ran " + message.content + ' on ' + message.channel.name + ' at ' + message.server.name + ', but is banned.')
                em = discord.Embed(title="*Insert sigh* You are banned from using AveBot.", colour=0xcc0000)
                em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                await client.send_message(message.channel, embed=em)
    except Exception:
        avelog(traceback.format_exc())
        em = discord.Embed(title="An error happened", description="It was logged and will be reviewed by developers.", colour=0xcc0000)
        em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
        await client.send_message(message.channel, embed=em)

avelog("AveBot started. Git hash: " + get_git_revision_short_hash())
if not os.path.isdir("files"):
    os.makedirs("files")

try:
    with open("bottoken", "r") as tokfile:
        client.run(tokfile.read().replace("\n",""))
except FileNotFoundError:
    avelog("No bottoken file found! Please create one. Join discord.gg/discord-api and check out #faq for more info.")