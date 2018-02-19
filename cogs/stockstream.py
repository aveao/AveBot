import discord
from discord.ext import commands
import secrets


class Stockstream:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def copypasta(self, ctx, ticker: str):
        """Generates a copypasta for StockStream using the given ticker."""
        copypasta_list = ["Kreygasm MUST Kreygasm BUY Kreygasm {} Kreygasm THIS Kreygasm ROUND Kreygasm",
                          "FutureMan BUY FutureMan {} FutureMan FOR FutureMan A FutureMan BRIGHTER FutureMan FUTURE FutureMan",
                          "Clappy Lemme buy a {0} before I send you a {0} Clappy",
                          "GivePLZ TRAIN TO PROFIT TOWN TakeNRG BUY {}! GivePLZ BUY {} TakeNRG",
                          "PogChamp {} PogChamp IS PogChamp OUR PogChamp LAST PogChamp HOPE PogChamp"]
        to_post = f"Copypasta ready: `{secrets.choice(copypasta_list).format(ticker.upper())}`"
        await ctx.send(to_post)

    @commands.command()
    async def copypastasell(self, ctx, ticker: str):
        """Generates a copypasta for StockStream using the given ticker."""
        copypasta_list = ["Kreygasm MUST Kreygasm SELL Kreygasm {} Kreygasm THIS Kreygasm ROUND Kreygasm",
                          "Kreygasm TIME Kreygasm TO Kreygasm CASH Kreygasm IN Kreygasm {} Kreygasm",
                          "FutureMan SELL FutureMan {} FutureMan FOR FutureMan A FutureMan BRIGHTER FutureMan FUTURE FutureMan",
                          "Clappy Lemme sell a {0} before I send you a {0} Clappy",
                          "GivePLZ TRAIN TO PROFIT TOWN TakeNRG SELL {}! GivePLZ SELL {} TakeNRG",
                          "SELLING PogChamp {} PogChamp IS PogChamp OUR PogChamp LAST PogChamp HOPE PogChamp"]
        to_post = f"Copypasta ready: `{secrets.choice(copypasta_list).format(ticker.upper())}`"
        await ctx.send(to_post)


def setup(bot):
    bot.add_cog(Stockstream(bot))
