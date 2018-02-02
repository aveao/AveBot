import discord
from discord.ext import commands
import time
import datetime
import traceback
from decimal import *
import locale
from dateutil import parser

def format_currency(amount, locale_to_use):
    try:
        locale.setlocale(locale.LC_ALL, locale_to_use)
        amount = Decimal(amount)
        return locale.currency(amount, grouping=True)
    except:
        self.bot.log.error(f"Error while converting {amount} on format_currency: {traceback.format_exc()}")

def get_change_color(change_percentage): # todo: switch this to a parabola or smth
    change_percentage = str(change_percentage).split('.')[0] # before the dot
    if change_percentage.startswith('-'):
        int_perc = int(change_percentage) * -1  # make it positive
        colors = [0xFFEBEE, 0xFFCDD2, 0xEF9A9A, 0xE57373, 0xEF5350,
        0xF44336, 0xE53935, 0xD32F2F, 0xC62828, 0xB71C1C, 0xD50000]
        return colors[10 if int_perc > 10 else int_perc]
    else:
        int_perc = int(change_percentage) + 1
        colors = [0xF1F8E9, 0xDCEDC8, 0xC5E1A5, 0xAED581, 0x9CCC65,
        0x8BC34A, 0x7CB342, 0x689F38, 0x558B2F, 0x33691E, 0x1B5E20]
        return colors[10 if int_perc > 10 else int_perc]

class Finance:
    def __init__(self, bot):
        self.bot = bot

    async def get_stock_change_color(self, ticker: str):
        symbols = await self.bot.aiojson(f"https://api.robinhood.com/quotes/?symbols={ticker.upper()}")
        if symbols == None:
            return 0x000000 # black

        symbols_results = symbols["results"][0]

        current_price = (
            symbols_results["last_trade_price"] if "last_extended_hours_trade_price" in symbols_results else symbols_results[
                "last_extended_hours_trade_price"])
        diff = str(Decimal(current_price) - Decimal(symbols_results["previous_close"]))
        percentage = (100 * Decimal(diff) / Decimal(current_price))
        return get_change_color(percentage)

    @commands.command(aliases=['stockchart', 'c'])
    async def chart(self, ctx, ticker: str):
        """Returns stock chart of the given ticker.

        Usage example: ab!c seb"""
        image_link = f"https://finviz.com/chart.ashx?t={ticker.upper()}&ty=c&ta=1&p=d&s=l&cacheshit={time.time()}"
        title_link = f"https://finviz.com/quote.ashx?t={ticker.upper()}"
        change_color = await self.get_stock_change_color(ticker)
        em = discord.Embed(title=f'Chart for {ticker.upper()}',
                           colour=change_color,
                           url=title_link)
        em.set_image(url=image_link)
        em.set_footer(text='Powered by finviz.com')
        await ctx.send(embed=em)

    @commands.command(aliases=['s'])
    async def stock(self, ctx, ticker: str):
        """Returns stock info about the given ticker.

        Usage example: ab!s seb"""
        currency_locale = "en_US.UTF-8"
        symbols = await self.bot.aiojson(f"https://api.robinhood.com/quotes/?symbols={ticker.upper()}")
        if symbols == None:
            await ctx.send("Stock not found. This stock is probably not tradeable on robinhood.")
            return
        symbols_result = symbols["results"][0]
        instrument = await self.bot.aiojson(symbols_result["instrument"])
        fundamentals = await self.bot.aiojson(
            f"https://api.robinhood.com/fundamentals/{ticker.upper()}/")

        current_price = Decimal(
            symbols_result["last_trade_price"] if "last_extended_hours_trade_price" in symbols_result else symbols_result[
                "last_extended_hours_trade_price"])
        diff = Decimal(Decimal(current_price) - Decimal(symbols_result["previous_close"]))
        percentage = str(100 * diff / current_price)[:6]

        if not percentage.startswith("-"):
            percentage = "+" + percentage

        current_price_string = format_currency(current_price, currency_locale)
        diff_string = format_currency(diff, currency_locale)
        bid_price_string = format_currency(Decimal(symbols_result["bid_price"]), currency_locale)
        ask_price_string = format_currency(Decimal(symbols_result["ask_price"]), currency_locale)
        tradeable_string = (":white_check_mark:" if instrument["tradeable"] else ":x:")

        update_timestamp = parser.parse(symbols_result["updated_at"])

        symbol = symbols_result["symbol"]
        change_color = await self.get_stock_change_color(symbol)

        em = discord.Embed(title=f"{symbol}'s stocks info", color=change_color, timestamp=update_timestamp)

        em.add_field(name="Name", value=instrument["name"])
        em.add_field(name="Current Price", value=current_price_string)
        em.add_field(name="Change from yesterday", value=f"{diff_string} ({percentage}%)")
        em.add_field(name="Bid size", value=f"{symbols_result['bid_size']} ({bid_price_string})", inline=True)
        em.add_field(name="Ask size", value=f"{symbols_result['ask_size']} ({ask_price_string})", inline=True)
        em.add_field(name="Current Volume", value=fundamentals["volume"], inline=True)
        em.add_field(name="Average Volume", value=fundamentals["average_volume"], inline=True)
        em.add_field(name="Tradeable on Robinhood", value=tradeable_string, inline=True)
        em.add_field(name="Country", value=f":flag_{instrument['country'].lower()}:", inline=True)

        await ctx.send(embed=em)

    @commands.command()
    async def btc(self, ctx):
        """Returns 30 day bitcoin chart and price info."""
        try:
            currency_locale = "en_US.UTF-8"
            btc_bitstamp_json = await self.bot.aiojson("https://www.bitstamp.net/api/ticker")

            btc_currentprice_rate = Decimal(btc_bitstamp_json["last"])
            btc_currentprice_string = format_currency(btc_currentprice_rate, currency_locale)

            btc_lastopen_rate = Decimal(btc_bitstamp_json["open"])
            btc_lastopen_string = format_currency(btc_lastopen_rate, currency_locale)

            btc_high_string = format_currency(btc_bitstamp_json["high"], currency_locale)
            btc_low_string = format_currency(btc_bitstamp_json["low"], currency_locale)
            btc_bid_string = format_currency(btc_bitstamp_json["bid"], currency_locale)
            btc_ask_string = format_currency(btc_bitstamp_json["ask"], currency_locale)
            btc_volume_string = str(btc_bitstamp_json["volume"])

            btc_diff = btc_currentprice_rate - btc_lastopen_rate
            btc_change_percentage = (100 * Decimal(btc_diff) / Decimal(btc_currentprice_rate))
            btc_change_percentage_string = f"{str(btc_change_percentage)[:6]}%"

            btc_change_color = get_change_color(btc_change_percentage)
            
            btc_data_timestamp = datetime.datetime.utcfromtimestamp(int(btc_bitstamp_json["timestamp"]))

            link = f"https://bitcoincharts.com/charts/chart.png?width=600&m=bitstampUSD&r=30&c=0&e=&t=S&m1=10&m2=25&x=0&v=1&cv=0&ps=0&l=0&p=0&cacheshit={time.time()}"
            em = discord.Embed(color=btc_change_color, timestamp=btc_data_timestamp)

            em.set_author(name="30 Day BTC Chart and Info", icon_url="https://bitcoin.org/img/icons/opengraph.png")
            em.set_image(url=link)
            em.set_footer(text="Chart supplied by bitcoincharts.com under CC-BY-SA 3.0, price info supplied by BitStamp.")
            
            em.add_field(name="Current Price", value=btc_currentprice_string)
            em.add_field(name="Opening Price", value=btc_lastopen_string)
            
            em.add_field(name="Change", value=btc_change_percentage_string)
            em.add_field(name="Volume", value=btc_volume_string)
            
            em.add_field(name="High", value=btc_high_string)
            em.add_field(name="Low", value=btc_low_string)
            
            em.add_field(name="Bid", value=btc_bid_string)
            em.add_field(name="Ask", value=btc_ask_string)
            
            await ctx.send(embed=em)
        except:
            await ctx.send("Error while fetching BTC data.")
            self.bot.log.error(traceback.format_exc())


def setup(bot):
    bot.add_cog(Finance(bot))