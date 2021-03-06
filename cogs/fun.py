import discord
from discord.ext import commands
import time
import datetime
import traceback
import re
import random


class Fun:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def howmanymessages(self, ctx):
        """Counts how many messages you sent in this channel in last 10000 messages."""
        tmp = await ctx.send('Calculating messages...')
        counter = 0
        allcounter = 0
        async for log in ctx.channel.history(limit=10000):
            allcounter += 1
            if log.author == ctx.message.author:
                counter += 1
        percentage_of_messages = str(100 * (counter / allcounter))[:6]
        message_text = f"{ctx.message.author.mention}: You have sent {counter} messages out of the last {allcounter} in this channel (%{percentage_of_messages})."
        await tmp.edit(content=message_text)

    @commands.command()
    async def bigly(self, ctx, *, text_to_bigly: str):
        """Makes a piece of text as big as the hands of the god emperor."""
        letters = re.findall(r'[a-z0-9 ]', text_to_bigly.lower())
        biglytext = ''
        ri = 'regional_indicator_'

        numbers_to_replace = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
                              "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine"}

        for letter in letters:
            biglytext += f":{ri}{letter}:"

        for number, text in numbers_to_replace.items():
            biglytext = biglytext.replace(f"{ri}{number}", text)

        biglytext = biglytext.replace(f":{ri} :", "\n")

        self.bot.log.info(f"biglified {text_to_bigly} to {biglytext}")

        await ctx.send(biglytext)

    @commands.command()
    async def roll(self, ctx, dice: str):
        """Rolls a dice in NdN format.

        Example: ab!roll 1d20
        Example with modifier: ab!roll 1d20 + 2"""

        modification = 0
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            self.bot.log.warning(traceback.format_exc())
            await ctx.send('Format has to be in NdN!')
            return

        try:
            modifier = ctx.message.content.split(dice)[1].replace(" ", "")
            self.bot.log.error("modifier is " + modifier)
            if modifier.startswith("+"):
                modification = int(modifier.replace("+", ""))
            elif modifier.startswith("-"):
                modification = -int(modifier.replace("-", ""))
        except Exception:
            self.bot.log.warning(traceback.format_exc())
            await ctx.send('Exception during modifier parsing!')
            return

        result = ', '.join(str(random.randint(1, limit)+modification)
                           for r in range(rolls))
        await ctx.send(f"{result} (Modifier: {modifier if modifier else '0'})")

    @commands.command(aliases=['xkcdlatest'])
    async def xkcd(self, ctx, xkcdcount=0):
        """Returns info about the specified xkcd comic.

        If no value is supplied, it gives the last one instead."""
        j = await self.bot.aiojson(f"https://xkcd.com/{xkcdcount}/info.0.json")
        resolvedto = "img" in j
        if not resolvedto:
            return

        post_timestamp = datetime.datetime.strptime(f"{j['year']}-{j['month']}-{j['day']}",
                                                    "%Y-%m-%d")

        embed = discord.Embed(title=f"xkcd {j['num']}: {j['safe_title']}",
                              url=f"https://xkcd.com/{j['num']}",
                              timestamp=post_timestamp)

        embed.set_image(url=j["img"])
        embed.set_footer(text=j["alt"])

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))
