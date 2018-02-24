from decimal import *
import discord
from discord.ext import commands


class Jose:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def joseprob(self, ctx, jccount: float, amount: float):
        """Calculates probability of a jose steal."""
        prob = (1 + (Decimal(jccount) / Decimal(amount))) * Decimal(0.42)
        prob = round(prob, 2)
        await ctx.send(f"Probability: `{prob}`")

    @commands.command()
    async def josemax(self, ctx, jccount: float):
        """Gives the maximum JCs that'll give 50% chance"""
        maxfifty = (Decimal(jccount) / Decimal(4.58)) * Decimal(0.42)
        maxfifty = round(maxfifty, 2)
        await ctx.send(f"Maximum amount that gives 5 probability: `{maxfifty}`")


def setup(bot):
    bot.add_cog(Jose(bot))
