import discord
from discord.ext import commands


class Jose:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def joseprob(self, ctx, jccount: float, amount: float):
        """Calculates probability of a jose steal."""
        prob = (1 + (jccount / amount)) * 0.42
        await ctx.send(f"Probability: `{prob:.01f}`")

    @commands.command()
    async def josemax(self, ctx, jccount: float):
        """Gives the maximum JCs that'll give 50% chance"""
        maxfifty = (jccount / 4.58) * 0.42
        await ctx.send(f"Maximum amount that gives 5 probability: `{maxfifty:.01f}`")


def setup(bot):
    bot.add_cog(Jose(bot))
