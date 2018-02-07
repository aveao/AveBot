import discord
from discord.ext import commands

import re
import io
import PIL.Image

class Emoji:
    def __init__(self, bot):
        self.bot = bot
        self.raw_emoji_regex = "(<(a|):([a-zA-Z0-9_*/-:]*):([0-9]*)>)"
        self.emoji_regex = "(<(a|):[a-zA-Z0-9_*/-:]*:[0-9]*>)"
        self.bot.extract_emojis = self.extract_emojis
        self.bot.download_and_add_emoji = self.download_and_add_emoji
        self.emoji_guild_id = int(self.bot.config['base']['emoji-guild'])
        self.max_jumbo = 3
        self.max_emoji_size = 256 * 1024
        self.emoji_dim_max = 128


    def extract_emojis(self, text: str, raw=False):
        regex_to_use = self.raw_emoji_regex if raw else self.emoji_regex
        regex_results = re.findall(regex_to_use, text)
        if raw:
            return regex_results
        emojis = list(dict(regex_results).keys())
        return emojis


    async def download_and_add_emoji(self, guild_id: int, emoji_name: str, url: str):
        emoji_guild = self.bot.get_guild(guild_id)
        emoji_bytes = await self.bot.aiogetbytes(url)
        if len(emoji_bytes) > self.max_emoji_size:
            im = PIL.Image.open(io.BytesIO(emoji_bytes))
            w, h = im.size
            if w < self.emoji_dim_max and h < self.emoji_dim_max:
                return None
            elif w > h:
                ratio = w / self.emoji_dim_max
                new_h = int(h / ratio)
                im = im.resize((self.emoji_dim_max, new_h))
            else:
                ratio = h / self.emoji_dim_max
                new_w = int(w / ratio)
                im = im.resize((new_w, self.emoji_dim_max))

            emoji_bytes = io.BytesIO()
            im.save(emoji_bytes, format='PNG')
            emoji_bytes = emoji_bytes.getvalue()
            if len(emoji_bytes) > self.max_emoji_size:
                return None
        added_emoji = await emoji_guild.create_custom_emoji(name=emoji_name, image=emoji_bytes)
        return added_emoji


    @commands.command(aliases=['avemoji', 'avemojiinvite', 'avemojisinvite', 'ainvite'])
    async def avemojis(self, ctx):
        """Gives an invite link to Avemojis. """
        await ctx.send(f"{ctx.message.author.mention}: {self.bot.config["emojis"]["emojiinvite"]}")


    @commands.command(hidden=True)
    async def addemoji(self, ctx, url: str, emoji_name: str):
        author_level = await self.bot.get_permission(ctx.author.id)
        if author_level < 8:
            return
        added_emoji = await self.download_and_add_emoji(self.emoji_guild_id, emoji_name, url)
        result_str = f"Added {str(added_emoji)}" if added_emoji else "This emoji is too big."
        await ctx.send(f"{ctx.message.author.mention}: {result_str}")


    @commands.is_owner()
    @commands.command(hidden=True, aliases=['stealmoji'])
    async def stealemoji(self, ctx, *, emoji_string: str):
        emojis = self.extract_emojis(emoji_string, True)
        for emoji in emojis:
            emoji_format = "gif" if emoji[1] == "a" else "png"
            emoji_name = emoji[2]
            emoji_url = f"https://cdn.discordapp.com/emojis/{emoji[3]}.{emoji_format}?v=1"

            added_emoji = await self.download_and_add_emoji(self.emoji_guild_id, emoji_name, emoji_url)
            result_str = f"Added {str(added_emoji)}" if added_emoji else "This emoji is too big."
            await ctx.send(f"{ctx.message.author.mention}: {result_str}")


    @commands.command(aliases=['emoji', 'einfo', 'emojiinfo', 'jumbo'])
    async def jumbomoji(self, ctx, *, emoji_string: str):
        """Jumboifies an emoji."""
        emojis = self.extract_emojis(emoji_string, True)
        if len(emojis) > self.max_jumbo:
            await ctx.send(f"{ctx.message.author.mention}: that's a little too many emojis. Max is {self.max_jumbo}.")
            return
        elif len(emojis) == 0:
            await ctx.send(f"{ctx.message.author.mention}: you didn't send any emojis.")
            return
        emoji_text = f"{ctx.message.author.mention}: "
        for emoji in emojis:
            emoji_format = "gif" if emoji[1] == "a" else "png"
            emoji_url = f"https://cdn.discordapp.com/emojis/{emoji[3]}.{emoji_format}?v=1"
            emoji_text += f"\n{emoji_url}"
        await ctx.send(emoji_text)
    
def setup(bot):
    bot.add_cog(Emoji(bot))