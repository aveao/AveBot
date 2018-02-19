from decimal import *
import time
import datetime
import traceback
import locale
import discord
from discord.ext import commands
from dateutil import parser
import colour


def hex_to_int(color_hex: str):
    """Turns a given hex color into an integer"""
    return int("0x" + color_hex[1:], 16)

def get_change_color(change_percentage, color_range: int = 10):
    """Gets a change color between red-white-green for the given change percentage"""
    change_percentage = str(change_percentage).split('.')[0]  # before the dot
    red = colour.Color("#D50000")
    white = colour.Color("#FFFFFF")
    green = colour.Color("#1B5E20")

    int_perc = int(change_percentage)

    if int_perc is 0:
        return hex_to_int("#ffffff")
    elif change_percentage.startswith('-'):
        colors = list(red.range_to(white, color_range))
        int_perc = int_perc * -1  # make it positive
        int_perc = color_range - int_perc
        int_perc = int_perc if int_perc > 0 else 0 # limit
        return hex_to_int(colors[int_perc].hex_l)
    else:
        int_perc -= 1
        colors = list(white.range_to(green, color_range))
        int_perc = int_perc if int_perc < (color_range - 1) else (color_range - 1) # limit
        return hex_to_int(colors[int_perc].hex_l)


class Finance:
    def __init__(self, bot):
        self.bot = bot
        self.legal_notice = "Data is not guaranteed to be accurate, "\
                            "I am not responsible for your losses."


    def format_currency(self, amount, locale_to_use: str = "en_US.UTF-8"):
        """Formats a currency for the given locale (default: en_US.UTF-8)"""
        try:
            locale.setlocale(locale.LC_ALL, locale_to_use)
            amount = Decimal(amount)
            return locale.currency(amount, grouping=True)
        except:
            self.bot.log.error(f"Error while converting {amount} on "
                               f"format_currency: {traceback.format_exc()}")

    async def get_stock_change_color(self, ticker: str):
        symbols = await self.bot.aiojson("https://api.robinhood.com/quotes/"\
                                        f"?symbols={ticker.upper()}")
        if not symbols:
            return 0x000000 # black

        symbols_results = symbols["results"][0]

        current_price = (symbols_results["last_trade_price"] if
                         "last_extended_hours_trade_price" in symbols_results
                         else symbols_results["last_extended_hours_trade_price"])

        diff = str(Decimal(current_price) -
                   Decimal(symbols_results["previous_close"]))
        percentage = (100 * Decimal(diff) / Decimal(current_price))
        return get_change_color(percentage, 10)

    async def get_crypto_name(self, ticker: str, include_ticker=True):
        """Fetches the name of the given cryptocurrency from Cryptopia API"""
        ticker = ticker.upper()
        json_data = await self.bot.aiojson("https://www.cryptopia.co.nz/api/GetCurrencies")
        if not ("Success" in json_data and json_data["Success"]):
            return ticker if include_ticker else None
        name_list = [data["Name"]
                     for data in json_data["Data"] if data["Symbol"] == ticker]
        if not name_list:
            return ticker if include_ticker else None
        return f"{name_list[0]} ({ticker})" if include_ticker else name_list[0]

    async def get_conversion_rate(self, from_symbol: str, to_symbol: str):
        json_res = await self.bot.aiojson("https://api.fixer.io/latest"\
                                          f"?base={from_symbol.upper()}"\
                                          f"&symbols={to_symbol.upper()}")
        if "rates" in json_res and json_res["rates"]:
            return json_res["rates"][to_symbol.upper()]
        return None

    @commands.command(aliases=['stockchart', 'c'])
    async def chart(self, ctx, ticker: str):
        """Returns stock chart of the given ticker.

        Usage example: ab!c seb"""
        image_link = f"https://finviz.com/chart.ashx?t={ticker.upper()}"\
                     f"&ty=c&ta=1&p=d&s=l&cacheinval={int(time.time())}"
        title_link = f"https://finviz.com/quote.ashx?t={ticker.upper()}"
        change_color = await self.get_stock_change_color(ticker)
        embed = discord.Embed(title=f'Chart for {ticker.upper()}',
                              colour=change_color,
                              url=title_link)
        embed.set_image(url=image_link)
        embed.set_footer(text='Powered by finviz.com')
        await ctx.send(embed=embed)

    # TODO: Find a way to reduce code repetition in following messages
    @commands.command(aliases=['howmuch', 'convert', 'conversion', 'conversionrate'])
    async def currency(self, ctx, from_symbol: str, to_symbol: str):
        """Gives the conversion rate for given symbols.

        Usage example: ab!currency BRL TRY"""
        rate = await self.get_conversion_rate(from_symbol, to_symbol)
        if rate:
            await ctx.send(f"{ctx.author.mention}: "\
                           f"1{from_symbol.upper()} = {rate}{to_symbol.upper()}."\
                           "\n(Powered by fixer.io, data is renewed daily. "\
                           f"{self.legal_notice})")
        else:
            await ctx.send("One of the symbols is not recognized.")

    @commands.command(aliases=['currencyconvert', 'currencyconversion'])
    async def money(self, ctx, amount: float, from_symbol: str, to_symbol: str):
        """Gives a currency conversion for given amount of money.

        Usage example: ab!money 100 BRL TRY"""
        rate = await self.get_conversion_rate(from_symbol, to_symbol)
        if rate:
            result_amount = rate * amount
            await ctx.send(f"{ctx.author.mention}: "\
                           f"{amount}{from_symbol.upper()} = {result_amount}{to_symbol.upper()}."\
                           "\n(Powered by fixer.io, data is renewed daily. "\
                           f"{self.legal_notice})")
        else:
            await ctx.send("One of the symbols is not recognized.")


    @commands.command(aliases=['s'])
    async def stock(self, ctx, ticker: str):
        """Returns stock info about the given ticker.

        Usage example: ab!s seb"""
        symbols = await self.bot.aiojson("https://api.robinhood.com/quotes/"\
                                        f"?symbols={ticker.upper()}")
        if not symbols:
            await ctx.send("Stock not found. This stock is probably not tradeable on robinhood.")
            return
        symbols_result = symbols["results"][0]
        instrument = await self.bot.aiojson(symbols_result["instrument"])
        fundamentals = await self.bot.aiojson(
            f"https://api.robinhood.com/fundamentals/{ticker.upper()}/")

        current_price = (symbols_result["last_trade_price"] if
                         "last_extended_hours_trade_price" in symbols_result
                         else symbols_result["last_extended_hours_trade_price"])
        diff = Decimal(Decimal(current_price) -
                       Decimal(symbols_result["previous_close"]))
        percentage = str(100 * diff / current_price)[:6]

        if not percentage.startswith("-"):
            percentage = "+" + percentage

        current_price_string = self.format_currency(current_price)
        diff_string = self.format_currency(diff)
        bid_price_string = self.format_currency(Decimal(symbols_result["bid_price"]))
        ask_price_string = self.format_currency(Decimal(symbols_result["ask_price"]))
        tradeable_string = (
            ":white_check_mark:" if instrument["tradeable"] else ":x:")

        update_timestamp = parser.parse(symbols_result["updated_at"])

        symbol = symbols_result["symbol"]
        change_color = await self.get_stock_change_color(symbol)

        embed = discord.Embed(title=f"{symbol}'s stocks info",
                              color=change_color,
                              timestamp=update_timestamp)

        embed.add_field(name="Name", value=instrument["name"])
        embed.add_field(name="Current Price", value=current_price_string)
        embed.add_field(name="Change from yesterday", value=f"{diff_string} ({percentage}%)")
        embed.add_field(name="Bid size", value=f"{symbols_result['bid_size']} ({bid_price_string})")
        embed.add_field(name="Ask size", value=f"{symbols_result['ask_size']} ({ask_price_string})")
        embed.add_field(name="Current Volume", value=fundamentals["volume"])
        embed.add_field(name="Average Volume", value=fundamentals["average_volume"])
        embed.add_field(name="Tradeable on Robinhood", value=tradeable_string)
        embed.add_field(name="Country", value=f":flag_{instrument['country'].lower()}:")

        await ctx.send(embed=embed)

    @commands.command()
    async def btc(self, ctx):
        """Returns 30 day bitcoin chart and price info."""
        try:
            btc_bitstamp_json = await self.bot.aiojson("https://www.bitstamp.net/api/ticker")

            btc_currentprice_rate = Decimal(btc_bitstamp_json["last"])
            btc_currentprice_string = self.format_currency(btc_currentprice_rate)

            btc_lastopen_rate = Decimal(btc_bitstamp_json["open"])
            btc_lastopen_string = self.format_currency(btc_lastopen_rate)

            btc_high_string = self.format_currency(btc_bitstamp_json["high"])
            btc_low_string = self.format_currency(btc_bitstamp_json["low"])
            btc_bid_string = self.format_currency(btc_bitstamp_json["bid"])
            btc_ask_string = self.format_currency(btc_bitstamp_json["ask"])
            btc_volume_string = str(btc_bitstamp_json["volume"]) + " BTC"

            btc_diff = btc_currentprice_rate - btc_lastopen_rate
            btc_change_percentage = (
                100 * Decimal(btc_diff) / Decimal(btc_currentprice_rate))
            btc_change_percentage_string = f"{str(btc_change_percentage)[:6]}%"

            btc_change_color = get_change_color(btc_change_percentage, 20)

            btc_data_timestamp = datetime.datetime.utcfromtimestamp(
                int(btc_bitstamp_json["timestamp"]))

            link = "https://bitcoincharts.com/charts/chart.png?width=600&m=bitstampUSD&r=30"\
                  f"&t=S&v=1&cacheinval={int(time.time())}"
            embed = discord.Embed(color=btc_change_color,
                                  timestamp=btc_data_timestamp)

            embed.set_author(name="30 Day BTC Chart and Info",
                             icon_url="https://bitcoin.org/img/icons/opengraph.png")
            embed.set_image(url=link)
            embed.set_footer(text="Chart supplied by bitcoincharts.com under CC-BY-SA 3.0, "\
                                  "price info supplied by BitStamp. " + self.legal_notice)

            embed.add_field(name="Current Price", value=btc_currentprice_string)
            embed.add_field(name="Opening Price", value=btc_lastopen_string)

            embed.add_field(name="Change", value=btc_change_percentage_string)
            embed.add_field(name="Volume", value=btc_volume_string)

            embed.add_field(name="High", value=btc_high_string)
            embed.add_field(name="Low", value=btc_low_string)

            embed.add_field(name="Bid", value=btc_bid_string)
            embed.add_field(name="Ask", value=btc_ask_string)

            await ctx.send(embed=embed)
        except:
            await ctx.send("Error while fetching BTC data.")
            self.bot.log.error(traceback.format_exc())

    @commands.command(aliases=["cryptocoin", "cryptoprice", "cc"])
    async def crypto(self, ctx, ticker: str):
        """Returns price info about the specified cryptocoin."""
        ticker = ticker.upper()
        api_endpoint = "https://min-api.cryptocompare.com/data/pricemultifull"\
                       f"?tsyms=USD&fsyms={ticker}"
        api_json = await self.bot.aiojson(api_endpoint)
        if "Message" in api_json:
            await ctx.send(f"Error from API: `{api_json['Message']}`")
            return

        raw_data = api_json["RAW"][ticker]["USD"]
        stylized_data = api_json["DISPLAY"][ticker]["USD"]

        change_color = get_change_color(raw_data["CHANGEPCTDAY"], 20)

        data_timestamp = datetime.datetime.utcfromtimestamp(
            raw_data["LASTUPDATE"])

        coin_name = await self.get_crypto_name(ticker)

        embed = discord.Embed(color=change_color, timestamp=data_timestamp)

        embed.set_author(name=f"Price info for {coin_name} from {stylized_data['MARKET']}")
        embed.set_footer(text="Price info supplied by CryptoCompare. " + self.legal_notice)

        embed.add_field(name="Current Price", value=stylized_data["PRICE"])
        embed.add_field(name="Opening Price", value=stylized_data["OPENDAY"])

        embed.add_field(name="Change", value=f"{stylized_data['CHANGEDAY']} "\
                                             f"({stylized_data['CHANGEPCTDAY']}%)")
        embed.add_field(name="Volume", value=stylized_data["VOLUMEDAY"])

        embed.add_field(name="High", value=stylized_data["HIGHDAY"])
        embed.add_field(name="Low", value=stylized_data["LOWDAY"])

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Finance(bot))
