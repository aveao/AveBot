import discord
from discord.ext import commands

import re


class Emoji:
    def __init__(self, bot):
        self.bot = bot
        self.raw_emoji_regex = "(<(a|):([a-zA-Z0-9_*/-:]*):([0-9]*)>)"
        self.emoji_regex = "(<(a|):[a-zA-Z0-9_*/-:]*:[0-9]*>)"
        self.bot.extract_emojis = self.extract_emojis
        self.bot.download_and_add_emoji = self.download_and_add_emoji
        self.emoji_guild_id = int(self.bot.config['base']['emoji-guild'])
        self.max_jumbo = 3


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
        added_emoji = await emoji_guild.create_custom_emoji(name=emoji_name, image=emoji_bytes)
        return added_emoji


    @commands.is_owner()
    @commands.command(hidden=True)
    async def addemoji(self, ctx, url: str, emoji_name: str):
        added_emoji = await self.download_and_add_emoji(self.emoji_guild_id, emoji_name, url)
        await ctx.send(f"{ctx.message.author.mention}: Added {str(added_emoji)}")


    @commands.is_owner()
    @commands.command(hidden=True, aliases=['stealmoji'])
    async def stealemoji(self, ctx, *, emoji_string: str):
        emojis = self.extract_emojis(emoji_string, True)
        for emoji in emojis:
            emoji_format = "gif" if emoji[1] == "a" else "png"
            emoji_name = emoji[2]
            emoji_url = f"https://cdn.discordapp.com/emojis/{emoji[3]}.{emoji_format}?v=1"

            added_emoji = await self.download_and_add_emoji(self.emoji_guild_id, emoji_name, emoji_url)
            await ctx.send(f"{ctx.message.author.mention}: Added {str(added_emoji)}")


    @commands.command(aliases=['emoji', 'einfo', 'emojiinfo', 'jumbo'])
    async def jumbomoji(self, ctx, *, emoji_string: str):
        """Jumboifies an emoji."""
        emojis = self.extract_emojis(emoji_string, True)
        if len(emojis) > self.max_jumbo:
            await ctx.send(f"{ctx.message.author.mention}: that's a little too many emojis. Max is {self.max_jumbo}.")
            return
        emoji_text = f"{ctx.message.author.mention}: "
        for emoji in emojis:
            emoji_format = "gif" if emoji[1] == "a" else "png"
            emoji_url = f"https://cdn.discordapp.com/emojis/{emoji[3]}.{emoji_format}?v=1"
            emoji_text += f"\n{emoji_url}"
        await ctx.send(emoji_text)
    
def setup(bot):
    bot.add_cog(Emoji(bot))