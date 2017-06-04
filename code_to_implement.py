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
