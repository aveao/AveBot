from decimal import *
import discord
from discord.ext import commands


class Jose:
    """These are a set of commands for the bot Jose."""

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

    @commands.command()
    async def josehmax(self, ctx, jccount: float, amountofpeople: float = 1):
        """Gives the maximum JCs that'll give 50% chance on a heist"""
        incr = decimal.Decimal('0.3') * amountofpeople
        maxfifty = ((4 / Decimal('0.32')) - incr) * jccount
        maxfifty = round(maxfifty, 2)
        await ctx.send("Maximum amount that gives 5 probability for "
                       f"the heist: `{maxfifty}`")


def setup(bot):
    bot.add_cog(Jose(bot))
