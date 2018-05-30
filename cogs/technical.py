import discord
from discord.ext import commands
import socket
import time
import datetime
import traceback
import os
from pathlib import Path


class Technical:
    def __init__(self, bot):
        self.bot = bot

    async def unfurl_b(self, link):
        max_depth = int(self.bot.config["advanced"]["unfurl-depth"])
        current_depth = 0
        prev_link = ""
        last_link = link
        try:
            while (prev_link != last_link) and (current_depth < max_depth):
                prev_link = last_link
                last_link_aio = await self.bot.aiosession.request('head', prev_link, allow_redirects=True)
                last_link = last_link_aio.url
                current_depth += 1
            return last_link
        except Exception:
            return prev_link

    @commands.command(aliases=['aveishot', 'home'])
    async def aveheat(self, ctx):
        """Returns heat info from ave's home."""
        heat_json = await self.bot.aiojson(self.bot.config['homeheat']['dataurl'])

        aveheat_data_timestamp = datetime.datetime.utcfromtimestamp(
            int(heat_json["timestamp"]))

        embed = discord.Embed(title="Heat Inside Ave's House",
                              timestamp=aveheat_data_timestamp)

        charturl = f"{self.bot.config['homeheat']['charturl']}?t={int(time.time())}"

        embed.set_image(url=charturl)
        embed.set_footer(text="Chart data is UTC")

        embed.add_field(name="Inside", value=f"{heat_json['inside']}°C")

        await ctx.send(embed=embed)

    @commands.command(aliases=['codetime', 'programmingtime'])
    async def wakatime(self, ctx):
        """Shows wakatime stats of dev."""
        current_time = datetime.datetime.utcnow()

        embed = discord.Embed(
            title="Coding Activity over Last 7 Days", timestamp=current_time)

        charturl = f"{self.bot.config['wakatime']['url']}?t={time.time()}"
        embed.set_image(url=charturl)

        await ctx.send(embed=embed)

    @commands.command()
    async def render(self, ctx, page_link: str):
        """Returns an image of the site."""
        if (ctx.guild and not ctx.channel.is_nsfw()) and not (ctx.message.author == self.bot.bot_info.owner):
            await ctx.send("This command can only be ran on nsfw channels "
                           "(because I don't want people to render nsfw sites and get the bot kicked)")
            return
        link = f"{self.bot.config['render']['splashhost']}/render.png?render_all=1&wait=1&url={page_link}"
        # TODO: The line above is not very safe. Let's improve that later.
        local_filename = f"files/{ctx.message.id}render.png"
        await self.bot.download_file(link, local_filename)
        text = (f"Page render for {page_link}, as requested by {ctx.message.author.mention}:")
        await ctx.send(content=text, file=discord.File(local_filename))

    @commands.command()
    async def unfurl(self, ctx, link: str):
        """Finds where a URL points at."""
        resolved = await self.unfurl_b(link)
        await ctx.send(f"<{link}> Unfurls to <{resolved}>")

    @commands.command(aliases=['dig'])
    async def resolve(self, ctx, domain: str):
        """Resolves a domain to its IP values."""
        resolved = repr(socket.gethostbyname_ex(domain))
        await ctx.send(f"Successfully resolved `{domain}` to `{resolved}`")

    @commands.command(aliases=["unixtime"])
    async def epoch(self, ctx):
        """Returns the Unix Time / Epoch."""
        await ctx.send(f"Current epoch time is: **{int(time.time())}**.")

    @commands.command()
    async def get(self, ctx, link: str, filename=None):
        """Gets a file from the internet (privileged, mod and owner only)."""
        author_level = await self.bot.get_permission(ctx.author.id)
        if author_level < 2:
            return
        mention = ctx.message.author.mention
        url_filename = await self.bot.url_get_filename(link)
        filename = "files/" + (filename if filename else url_filename)
        await self.bot.download_file(link, filename)
        file_size = Path(filename).stat().st_size
        if file_size < 1024 * 1024 * 8:  # Limit of discord is 8MiB
            await ctx.send(file=discord.File(filename),
                           content=f"{mention}: Here's the file you requested.")
        else:
            await ctx.send(f"{mention}: File is too big for discord"
                           f"(Limit is 8MiB, file is {file_size / (1024 * 1024)}MiB).")
        # Remove file when we're done with it (kinda risky TBH)
        os.remove(filename)


def setup(bot):
    bot.add_cog(Technical(bot))
