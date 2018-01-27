import discord
from discord.ext import commands
import time
import datetime
import traceback


class Linguistics:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def similar(self, ctx, *, word: str):
        """Gets a word similar to the one specified."""
        output = await self.bot.aiojson(f"https://api.datamuse.com/words?ml={word.replace(' ', '+')}")
        await ctx.send(f"**Similar Word:** `{output[0]['word']}`\n"
            f"(more on <http://www.onelook.com/thesaurus/?s={word.replace(' ', '_')}&loc=cbsim>)")


    @commands.command()
    async def typo(self, ctx, *, word: str):
        """Fixes a typo in the given word."""
        output = await self.bot.aiojson(f"https://api.datamuse.com/words?sp={word.replace(' ', '+')}")
        await ctx.send(f"**Typo Fixed:** `{output[0]['word']}`\n"
            f"(more on <http://www.onelook.com/?w={word.replace(' ', '_')}&ls=a>)")

    @commands.command()
    async def soundslike(self, ctx, *, word: str):
        """Gets a similar sounding word to the one specified."""
        output = await self.bot.aiojson(f"https://api.datamuse.com/words?sl={word.replace(' ', '+')}")
        await ctx.send(f"**Sounds like:** `{output[0]['word']}`\n"
            f"(more on <http://www.onelook.com/?w={word.replace(' ', '_')}&ls=a>)")


    @commands.command()
    async def rhyme(self, ctx, *, word: str):
        """Gets a word that rhymes with the one specified."""
        output = await self.bot.aiojson(f"https://api.datamuse.com/words?rel_rhy={word.replace(' ', '+')}")
        await ctx.send(f"**Rhymes with:** `{output[0]['word']}`\n"
            f"(more on <http://www.rhymezone.com/r/rhyme.cgi?Word={word.replace(' ', '_')}&typeofrhyme=adv&org1=syl&org2=l&org3=y>)")

def setup(bot):
    bot.add_cog(Linguistics(bot))