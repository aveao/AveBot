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

        result = ', '.join(str(random.randint(1, limit)+modification) for r in range(rolls))
        await ctx.send(f"{result} (Modifier: {modifier if modifier else "0"})")

    @commands.command()
    async def xkcd(self, ctx, xkcdcount: int):
        """Returns info about the specified xkcd comic."""
        j = await self.bot.aiojson("https://xkcd.com/{}/info.0.json".format(str(xkcdcount)))
        resolvedto = j["img"]
        if resolvedto:
            messagecont = "**XKCD {0}:** `{1}`, published on {2}-{3}-{4} (DMY)\n**Image:** {5}\n**Alt text:** `{6}`\n" \
                          "Explain xkcd: <http://www.explainxkcd.com/wiki/index.php/{0}>" \
                .format(str(j["num"]), j["safe_title"], j["day"], j["month"], j["year"], resolvedto, j["alt"])
            await ctx.send(messagecont)


    @commands.command()
    async def xkcdlatest(self, ctx):
        """Returns info about the latest xkcd comic."""
        j = await self.bot.aiojson("https://xkcd.com/info.0.json")
        resolvedto = j["img"]
        if resolvedto:
            messagecont = "**XKCD {0}:** `{1}`, published on {2}-{3}-{4} (DMY)\n**Image:** {5}\n**Alt text:** `{6}`\n" \
                          "Explain xkcd: <http://www.explainxkcd.com/wiki/index.php/{0}>" \
                .format(str(j["num"]), j["safe_title"], j["day"], j["month"], j["year"], resolvedto, j["alt"])
            await ctx.send(messagecont)

def setup(bot):
    bot.add_cog(Fun(bot))