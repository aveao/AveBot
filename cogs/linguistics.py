import discord
from discord.ext import commands
import time
import datetime
import traceback


class Linguistics:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def define(self, ctx, *, word: str):
        """Defines the specified word"""
        url = f"https://od-api.oxforddictionaries.com:443/api/v1/entries/en/{word.lower()}"
        auth_headers = {'Accept': "application/json",
                        'app_id': self.bot.config["oxforddict"]["appid"],
                        'app_key': self.bot.config["oxforddict"]["appkey"]}
        ret = await self.bot.aiosession.get(url, headers = auth_headers)
        if ret.status == 404:
            return await ctx.send(f"{ctx.author.mention}: Word"
                                  f" `{word}` not found on oxford dictionary.")
        elif ret.status == 500:
            return await ctx.send(f"{ctx.author.mention}: Error on oxford's "
                                  f"end while processing the word.")
        rett = await ret.text()
        self.bot.log.info(f"oxford output: {rett}")
        retj = await ret.json(content_type=ret.headers['Content-Type'])
        out_text = f"Definitions for word `{word}`:"
        for lexicalEntry in retj["results"]["lexicalEntries"]:
            for definition in lexicalEntry["entries"]["senses"]["definitions"]:
                out_text += f"\n- {definition}"
        out_text += "\n\nBased on Oxford Dictionaries API"
        await ctx.send(out_text)

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
