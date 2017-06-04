            elif message.content.startswith('>contact '):
                contactcontent = message.content.replace(">contact ", "")
                em = discord.Embed(title='Contact received!', description='**Message by:** ' + str(
                    message.author) + " (" + message.author.id + ')\n on ' + message.channel.name + ' at ' + message.server.name + '\n**Message content:** ' + contactcontent,
                                   colour=0xDEADBF)
                em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                await client.send_message(discord.Object(id='305857608378613761'), embed=em)
                em = discord.Embed(title='Contact sent!',
                                   description='Your message has been delivered to the developers.',
                                   colour=0xDEADBF)
                em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                await client.send_message(message.channel, embed=em)
            elif message.content.startswith('>ping'):
                em = discord.Embed(title=':ping_pong: Pong', colour=0xDEADBF)
                em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                await client.send_message(message.channel, embed=em)
            elif message.content.startswith('>trumpsim'):
                seed = message.content.split(' ')[1]
                response = requests.get("127.0.0.1:2001/reply?q={}".format(seed)).content
                em = discord.Embed(title="Trump says: '{}'".format(response), colour=0xDEADBF)
                em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                await client.send_message(message.channel, embed=em)
            elif message.content.startswith('>epoch') or message.content.startswith('>unixtime'):
                em = discord.Embed(title="Current epoch time is: **" + str(int(time.time())) + "**.",
                                   colour=0xDEADBF)
                em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                await client.send_message(message.channel, embed=em)
            elif message.content.startswith('>erdogan') or message.content.startswith('>trump'):
                em = discord.Embed(title="DICTATOR DETECTED", colour=0xDEADBF)
                em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                await client.send_message(message.channel, embed=em)
            elif message.content.startswith('>!'):
                toquery = message.content.replace(">!", "!").replace(" ", "+")
                output = urllib.request.urlopen(
                    "https://api.duckduckgo.com/?q=" + toquery + "&format=json&pretty=0&no_redirect=1").read().decode()
                j = json.loads(output)
                resolvedto = j["Redirect"]
                if resolvedto:
                    messagecont = "Bang resolved to: " + resolvedto
                    await client.send_message(message.channel, content=messagecont)
            elif message.content.startswith('>xkcd '):
                toquery = message.content.replace(">xkcd", "").replace(" ", "").replace("xkcd.com/", "").replace(
                    "https://", "").replace("http://", "").replace("www.", "").replace("m.", "").replace("/", "")  # lazy as hell :/
                if toquery:
                    toquery = toquery + "/"
                output = urllib.request.urlopen("https://xkcd.com/" + toquery + "info.0.json").read().decode()
                j = json.loads(output)
                resolvedto = j["img"]
                title = j["safe_title"]
                alt = j["alt"]
                xkcdid = str(j["num"])
                date = j["day"] + "-" + j["month"] + "-" + j["year"] + " (DDMMYYYY)"
                if resolvedto:
                    messagecont = "**XKCD " + xkcdid + ":** `" + title + "`, published on " + date + "\n**Image:** " + resolvedto + "\n**Alt text:** `" + alt + "`\nExplain xkcd: <http://www.explainxkcd.com/wiki/index.php/" + xkcdid + ">"
                    await client.send_message(message.channel, content=messagecont)
            elif message.content.startswith('>similar '):
                toquery = message.content.replace(">similar ", "")
                output = urllib.request.urlopen(
                    "https://api.datamuse.com/words?ml=" + toquery.replace(" ", "+")).read().decode()
                j = json.loads(output)
                em = discord.Embed(title="Similar word: " + j[0]["word"],
                                   description="(more on <http://www.onelook.com/thesaurus/?s=" + toquery.replace(
                                       " ", "_") + "&loc=cbsim>)", colour=0xDEADBF)
                em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                await client.send_message(message.channel, embed=em)
            elif message.content.startswith('>typo '):
                toquery = message.content.replace(">typo ", "")
                output = urllib.request.urlopen(
                    "https://api.datamuse.com/words?sp=" + toquery.replace(" ", "+")).read().decode()
                j = json.loads(output)
                em = discord.Embed(title="Typo fixed: " + j[0]["word"],
                                   description="(more on <http://www.onelook.com/?w=" + toquery.replace(" ",
                                                                                                        "+") + "&ls=a>)",
                                   colour=0xDEADBF)
                em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                await client.send_message(message.channel, embed=em)
            elif message.content.startswith('>soundslike '):
                toquery = message.content.replace(">soundslike ", "")
                output = urllib.request.urlopen(
                    "https://api.datamuse.com/words?sl=" + toquery.replace(" ", "+")).read().decode()
                j = json.loads(output)
                em = discord.Embed(title="Sounds like: " + j[0]["word"],
                                   description="(more on <http://www.onelook.com/?w=" + toquery.replace(" ",
                                                                                                        "+") + "&ls=a>)",
                                   colour=0xDEADBF)
                em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                await client.send_message(message.channel, embed=em)
            elif message.content.startswith('>rhyme '):
                toquery = message.content.replace(">rhyme ", "")
                output = urllib.request.urlopen(
                    "https://api.datamuse.com/words?rel_rhy=" + toquery.replace(" ", "+")).read().decode()
                j = json.loads(output)
                em = discord.Embed(title="Rhymes with: " + j[0]["word"],
                                   description="(more on <http://www.rhymezone.com/r/rhyme.cgi?Word=" + toquery.replace(
                                       " ", "+") + "&typeofrhyme=adv&org1=syl&org2=l&org3=y>)", colour=0xDEADBF)
                em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                await client.send_message(message.channel, embed=em)
            elif message.content.startswith('>chart') or message.content.startswith('>stockchart'):
                toquery = message.content.replace(">chart ", "").replace(">stockchart ", "").upper()
                link = "http://finviz.com/chart.ashx?t=" + toquery + "&ty=c&ta=1&p=d&s=l"
                filename = "files/" + toquery + ".png"
                urllib.request.urlretrieve(link, filename)
                await client.send_file(message.channel, filename,
                                       content="Here's the charts for " + toquery + ". See <http://finviz.com/quote.ashx?t=" + toquery + "> for more info.")
            elif message.content.startswith('>s') or message.content.startswith('>stock'):
                toquery = message.content.replace(">stock ", "").replace(">s ", "").upper()
                try:
                    symbols = urllib.request.urlopen("https://api.robinhood.com/quotes/?symbols=" + toquery).read().decode()
                    symbolsj = json.loads(symbols)["results"][0]
                    instrument = urllib.request.urlopen(symbolsj["instrument"]).read().decode()
                    instrumentj = json.loads(instrument)
                    fundamentals = urllib.request.urlopen("https://api.robinhood.com/fundamentals/" + toquery + "/").read().decode()
                    fundamentalsj = json.loads(fundamentals)                    current_price=(symbolsj["last_trade_price"] if symbolsj["last_extended_hours_trade_price"] is None else symbolsj["last_extended_hours_trade_price"])
                    diff=str(Decimal(current_price)-Decimal(symbolsj["previous_close"]))
                    if not diff.startswith("-"):
                        diff = "+" + diff
                    percentage = str(100 * Decimal(diff)/Decimal(current_price))[:6]
                    if not percentage.startswith("-"):
                        percentage = "+" + percentage                    em = discord.Embed(title=symbolsj["symbol"]+"'s stocks info as of " + symbolsj["updated_at"],
                                       description="Name: **"+instrumentj["name"]+"**\n"+
                                       "Current Price: **" + current_price + " USD**\n"+
                                       "Change from yesterday: **" + diff + " USD**, (**" + percentage + "%**)\n"+
                                       "Bid size: **" + str(symbolsj["bid_size"]) + " ("+symbolsj["bid_price"]+" USD)**, Ask size: **" + str(symbolsj["ask_size"]) + " ("+symbolsj["ask_price"]+" USD)**\n"+
                                       "Current Volume: **" + fundamentalsj["volume"] + "**, Average Volume: **" + fundamentalsj["average_volume"] + "** \n"+
                                       "Tradeable (on robinhood): " + (":white_check_mark:" if instrumentj["tradeable"] else ":x:") + ", :flag_" + instrumentj["country"].lower() + ":",
                                       colour=(0xab000d if diff.startswith("-") else 0x32cb00))
                    em.set_author(name='AveBot - Stocks', icon_url='https://s.ave.zone/c7d.png')
                    await client.send_message(message.channel, embed=em)
                except urllib.error.HTTPError as e:
                    em = discord.Embed(title="HTTP Error",
                                       description=("Stock not found (HTTP 400 returned)." if e.code == 400 else "Error Code: " + str(e.code)+"\nError Reason: "+e.reason),
                                       colour=0xab000d)
                    em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                    await client.send_message(message.channel, embed=em)            if message.author.id == botowner:
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
                            modfile.write(dtag.id + "\n")
                            em = discord.Embed(title='Added ' + str(dtag) + '(' + dtag.id + ') as mod.',
                                               description='Welcome to the team!', colour=0x64dd17)
                            em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                            await client.send_message(message.channel, embed=em)
                elif message.content.startswith('>fetchlog'):
                    await client.send_file(message.channel, "log.txt", content="Here's the current log file:")
            # else:
            #    em = discord.Embed(title="Insufficient Permissions (Owner status needed)", colour=0xcc0000)
            #    em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
            #    await client.send_message(message.channel, embed=em)            if message.author.id in get_mods_list():
                if message.content.startswith('>addpriv '):
                    privstoadd = message.mentions
                    with open("privlist", "a") as privfile:
                        for dtag in privstoadd:
                            privfile.write(dtag.id + "\n")
                            em = discord.Embed(title='Added ' + str(dtag) + '(' + dtag.id + ') as privileged user.',
                                               description='Welcome to the team!', colour=0x64dd17)
                            em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                            await client.send_message(message.channel, embed=em)
                elif message.content.startswith('>ban '):
                    banstohand = message.mentions
                    with open("banlist", "a") as banfile:
                        for dtag in banstohand:
                            banfile.write(dtag.id + "\n")
                            em = discord.Embed(title='Banned ' + str(dtag) + '(' + dtag.id + ').',
                                               description='(People are idiots)', colour=0x64dd17)
                            em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                            await client.send_message(message.channel, embed=em)
                elif message.content.startswith('>say '):
                    tosay = message.content.replace(">say ", "")
                    await client.send_message(message.channel, content=tosay)
            # else:
            #    em = discord.Embed(title="Insufficient Permissions (Mod status needed)", colour=0xcc0000)
            #    em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
            #    await client.send_message(message.channel, embed=em)            if message.author.id in get_privileged_list():
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
                        urllib.request.urlretrieve(link, filename)
                    await client.send_file(message.channel, filename,
                                           content=":thumbsup: Here's the file you requested.")
                elif message.content.startswith('>dget '):
                    link = message.content.split(' ')[1]
                    filename = "files/requestedfile"
                    urllib.request.urlretrieve(link, filename)
                    await client.send_file(message.channel, filename,
                                           content=":thumbsup: Here's the file you requested.")
                elif message.content.startswith('>get '):
                    link = message.content.split(' ')[1]
                    filename = "files/" + link.split('/')[-1]
                    urllib.request.urlretrieve(link, filename)
                    await client.send_file(message.channel, filename,
                                           content=":thumbsup: Here's the file you requested.")                    # else:
                    #    em = discord.Embed(title="Insufficient Permissions (Privileged status needed)", colour=0xcc0000)
                    #    em.set_author(name='AveBot', icon_url='https://s.ave.zone/c7d.png')
                    #    await client.send_message(message.channel, embed=em)        else:
