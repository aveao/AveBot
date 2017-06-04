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


                if message.author.id == botowner:
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
