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
        self.max_jumbo = 5
        self.max_emoji_size = 256 * 1024
        self.emoji_dim_max = 128


    def extract_emojis(self, text: str, raw=False):
        regex_to_use = self.raw_emoji_regex if raw else self.emoji_regex
        regex_results = re.findall(regex_to_use, text)
        if raw:
            return regex_results
        emojis = list(dict(regex_results).keys())
        return emojis

    async def resize_emoji_png(self, image_bytes, no_none=False, check_size=True):
        """Resizes a given emoji to the hardcoded max emoji dimensions of discord. 
        
        If no_none (default: False) is set to True, function return old image data if it fails to resize and stay under size limitations. If it is set to false, function return None.
        
        If check_size (default: True) is set to True, function will return None or emoji data depending on no_none if emoji is bigger than discord's maximum size, which is currently hardcoded to 256kb. If it is set to false, function will return the image no matter the size (to ensure that you never get None, even when image is smaller than discord dimensions yet too big, set no_none to True)."""

        bigger_than_max = len(image_bytes) > self.max_emoji_size
        # Prepare fail result so that we can use tertiary if in
        # other palces and not have terrible code
        fail_return = image_bytes if no_none else None

        # Load image from bytes
        im = PIL.Image.open(io.BytesIO(image_bytes))
        w, h = im.size
        
        # Check if dimensions are smaller or equal to hardcoded max size
        if w <= self.emoji_dim_max and h <= self.emoji_dim_max:
            # Return fail result (image bytes or None) if image is bigger
            # than limit, otherwise return image_bytes, as it's smaller
            # than size and dimension limit
            return fail_return if (check_size and bigger_than_max) else image_bytes
        elif w > h:
            # Get height to hardcoded discord max size ratio
            # so we can we scale down height
            ratio = w / self.emoji_dim_max
            # Scale down height by ratio determined on prev step
            # and turn it to int so that PIL doesn't complain
            new_h = int(h / ratio)
            im = im.resize((self.emoji_dim_max, new_h))
        # If both dimensions are equal or height is bigger than width
        # resize based on height
        else:
            ratio = h / self.emoji_dim_max
            new_w = int(w / ratio)
            im = im.resize((new_w, self.emoji_dim_max))

        # Create a BytesIO storage to store image
        emoji_bytes = io.BytesIO()
        im.save(emoji_bytes, format='PNG')
        emoji_bytes = emoji_bytes.getvalue()
        
        # If check_size and emoji size is bigger than discord limit
        # Return fail_return (None or base byte data, based on no_none)
        # if it is not, return resized emoji
        if check_size and (len(emoji_bytes) > self.max_emoji_size):
            return fail_return
        return emoji_bytes


    async def resize_emoji_gif(self, image_bytes):
        """INCOMPLETE: Currently checks if a gif is smaller than max limit and returns image bytes back, and if it is not, returns None."""
        bigger_than_max = len(image_bytes) > self.max_emoji_size
        return None if bigger_than_max else image_bytes


    async def download_and_add_emoji(self, guild_id: int, emoji_name: str, url: str):
        emoji_guild = self.bot.get_guild(guild_id)
        emoji_bytes = await self.bot.aiogetbytes(url)
        result_bytes = None

        filename = await self.bot.url_get_filename(url)
        file_ext = await self.bot.filename_get_ext(filename)

        if file_ext.lower() == "gif":
            result_bytes = await self.resize_emoji_gif(emoji_bytes)
        else:
            result_bytes = await self.resize_emoji_png(emoji_bytes)

        # Check if result is None or not, returns None if it is
        # If it is not, adds emoji and returns that
        if result_bytes:
            added_emoji = await emoji_guild.create_custom_emoji(name=emoji_name, image=emoji_bytes)
            return added_emoji
        return None


    def construct_emoji_url(self, emoji_id, emoji_format):
        return f"https://cdn.discordapp.com/emojis/{emoji_id}.{emoji_format}?v=1"


    @commands.command(aliases=['avemoji', 'avemojiinvite', 'avemojisinvite', 'ainvite'])
    async def avemojis(self, ctx):
        """Gives an invite link to Avemojis. """
        await ctx.send(f"{ctx.message.author.mention}: {self.bot.config['emojis']['emojiinvite']}")


    @commands.command(hidden=True)
    async def emojilist(self, ctx):
        """Gives out the emoji list for the current server. Priv or up only."""

        # Permission checks
        author_level = await self.bot.get_permission(ctx.author.id)
        if author_level < 2:
            return

        messages = []
        current_message = ""
        for emoji in ctx.guild.emojis:
            text_to_add = f"{str(emoji)} `:{emoji.name}:`"

            # Try to split messages as cleanly as possible. One extra character for \n.
            if (len(text_to_add) + len(current_message) + 1) > 2000:
                messages.append(current_message)
                current_message = text_to_add
            else:
                current_message += "\n" + text_to_add
        messages.append(current_message)

        for message in messages:
            await ctx.send(message)


    @commands.command(hidden=True)
    async def addavemoji(self, ctx, emoji_name: str = "", url: str = ""):
        """Adds an emoji to avemojis. Mod only.
        
        Automatically resizes images down to discord limits.

        You can use attachments, but only first image will be used.

        If you don't specify emoji name, then filename will be used."""

        # Permission checks
        author_level = await self.bot.get_permission(ctx.author.id)
        if author_level < 8:
            return

        # If there's no emoji name, then pick the filename from url, or from the attachment.
        if not emoji_name:
            url_filename = ""
            if url:
                url_filename = await self.bot.url_get_filename(url)
            else:
                url_filename = ctx.message.attachments[0].filename
            emoji_name = await self.bot.filename_get_woext(url_filename)

        # If there's no URL, then pick the first attachment and use its url.
        if not url and ctx.message.attachments:
            url = ctx.message.attachments[0].url

        added_emoji = await self.download_and_add_emoji(self.emoji_guild_id, emoji_name, url)
        result_str = f"Added {str(added_emoji)}" if added_emoji else "This emoji is too big or there aren't emoji slots left."
        await ctx.send(f"{ctx.message.author.mention}: {result_str}")

        announcements_channel = self.bot.get_channel(int(self.bot.config['base']['emoji-announcements-channel']))
        await announcements_channel.send(f"New emoji! {str(added_emoji)}, added by {ctx.author.mention} ({ctx.author}).")
        await announcements_channel.send(str(added_emoji))


    @commands.command(hidden=True)
    async def deleteavemoji(self, ctx, emoji_string: str):
        """Deletes one or more avemoji(s), mod+ only"""

        author_level = await self.bot.get_permission(ctx.author.id)
        if author_level < 8:
            return

        emojis = self.extract_emojis(emoji_string, True)
        for i_emoji in emojis:
            emoji_name = i_emoji[2]
            emoji_id = int(i_emoji[3])
            the_emoji = self.bot.get_emoji(emoji_id)

            await the_emoji.delete(reason=f"delete requested by {ctx.author} / {ctx.author.id}")
            await ctx.send(f"{ctx.author.mention}: Emoji `:{emoji_name}:` deleted.")
            
            announcements_channel = self.bot.get_channel(int(self.bot.config['base']['emoji-announcements-channel']))
            await announcements_channel.send(f"Emoji deletion: `:{emoji_name}:` got removed by {ctx.author.mention} ({ctx.author})")


    @commands.command(hidden=True)
    async def editavemoji(self, ctx, emoji_string: str, new_name: str):
        """Renames an emoji, mod+ only.
        
        This only works if the emoji is added by avebot."""
        
        author_level = await self.bot.get_permission(ctx.author.id)
        if author_level < 8:
            return

        emojis = self.extract_emojis(emoji_string, True)
        if not emojis:
            await ctx.send(f"{ctx.author.mention}: no emojis found in specified thingy")
            return
        initial_emoji_name = emojis[0][2]
        emoji_id = int(emojis[0][3])
        the_emoji = self.bot.get_emoji(emoji_id)

        self.bot.log.info(f"rename on {the_emoji} - {emoji_id}")

        await the_emoji.edit(name=new_name, reason=f"rename requested by {ctx.author} / {ctx.author.id}")
        await ctx.send(f"{ctx.author.mention}: Successfully renamed - {the_emoji}")

        announcements_channel = self.bot.get_channel(int(self.bot.config['base']['emoji-announcements-channel']))
        await announcements_channel.send(f"Emoji `:{initial_emoji_name}:` {the_emoji} renamed to `:{new_name}:` by {ctx.author.mention} ({ctx.author})")


    @commands.is_owner()
    @commands.command(hidden=True)
    async def stealavemoji(self, ctx, *, emoji_string: str):
        emojis = self.extract_emojis(emoji_string, True)
        for emoji in emojis:
            emoji_format = "gif" if emoji[1] == "a" else "png"
            emoji_name = emoji[2]
            emoji_url = self.construct_emoji_url(emoji[3], emoji_format)

            added_emoji = await self.download_and_add_emoji(self.emoji_guild_id, emoji_name, emoji_url)
            result_str = f"Added {str(added_emoji)}" if added_emoji else "This emoji is too big."
            await ctx.send(f"{ctx.author.mention}: {result_str}")


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
            emoji_url = self.construct_emoji_url(emoji[3], emoji_format)
            emoji_text += f"\n{emoji_url}"
        await ctx.send(emoji_text)
    
def setup(bot):
    bot.add_cog(Emoji(bot))
