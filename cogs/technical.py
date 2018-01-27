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
        try:
            heat_json = await self.bot.aiojson(self.bot.config['homeheat']['dataurl'])
            
            aveheat_data_timestamp = datetime.datetime.utcfromtimestamp(int(heat_json["timestamp"]))

            em = discord.Embed(title="Heat Inside Ave's House", timestamp=aveheat_data_timestamp)

            charturl = f"{self.bot.config['homeheat']['charturl']}?t={time.time()}"

            em.set_image(url=charturl)
            em.set_footer(text="Chart data is UTC")
            
            em.add_field(name="Inside", value=f"{heat_json['inside']}°C")
            em.add_field(name="Outside", value=f"{heat_json['outside']}°C")
            
            await ctx.send(embed=em)
        except:
            self.bot.log.error(traceback.format_exc())


    @commands.command()
    async def render(self, ctx, page_link: str):
        """Returns an image of the site."""
        if ctx.guild and not ctx.channel.is_nsfw():
            await ctx.send("This command can only be ran on nsfw channels "
            "(because I don't want people to do `ab!render http://yourfaveadultsite.example` and get the bot kicked)")
            return
        link = f"http://http2pic.haschek.at/api.php?url={page_link}"
        em = discord.Embed(title=f'Page render for {page_link}, as requested by {ctx.message.author}')
        em.set_image(url=link)
        em.set_footer(text='Powered by http2pic.haschek.at.')
        await ctx.send(embed=em)


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


    @commands.is_owner()
    @commands.command(pass_context=True)
    async def get(self, ctx, link: str, direct=True):
        """Gets a file from the internet (owner only for limited time)."""
        mention = ctx.message.author.mention
        filename = ("files/" + link.split('/')[-1]) if direct else "files/directfile"
        await self.bot.download_file(link, filename)
        file_size = Path(filename).stat().st_size
        if file_size < 1024 * 1024 * 8:  # Limit of discord is 8MiB
            await ctx.send(file=discord.File(filename),
              content=f"{mention}: Here's the file you requested.")
        else:
            await ctx.send(f"{mention}: File is too big for discord"
              f"(Limit is 8MiB, file is {file_size / (1024 * 1024)}MiB).")
        os.remove(filename)  # Remove file when we're done with it (kinda risky TBH)

def setup(bot):
    bot.add_cog(Technical(bot))