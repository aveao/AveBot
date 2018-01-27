import discord
from discord.ext import commands
import re

class NSFW:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['fucksafemode'])
    async def tumblrgrab(self, ctx, *, link: str):
        """Returns images from the specified tumblr link."""
        reg = r'([a-z0-9-.]{1,})\/post\/([0-9]{1,})'
        m = re.search(reg, link)
        if m:
            site = m.group(1)
            postid = m.group(2)
            api_key = self.bot.config['tumblr']['apikey']
            channel_is_nsfw = ctx.channel.is_nsfw() if ctx guild else True
            channel_allows_nsfw = (("no_nsfw" not in ctx.channel.topic) if ctx.channel.topic else True) if ctx.guild else True # oh god why

            tumblrapicall_link = f"https://api.tumblr.com/v2/blog/{site}/posts/photo?id={postid}&api_key={api_key}"
            tumblr_json = await self.bot.aiojson(tumblrapicall_link)
            tumblr_is_nsfw = ("x_tumblr_content_rating" in tumblr_json["meta"])

            if (channel_is_nsfw == False and tumblr_is_nsfw):
                await ctx.send("The contents of this post are marked NSFW, and this isn't an NSFW channel.")
                return
            elif (channel_is_nsfw and tumblr_is_nsfw and not channel_allows_nsfw):
                await ctx.send("The contents of this post are marked NSFW, "
                    "and this channel does not allow NSFW posts (has `no_nsfw` on channel topic).")
                return

            tumblr_image_base = "\n{}"

            tumblr_json_images = tumblr_json["response"]["posts"][0]["photos"]
            self.bot.log.info(f"tumblr json images: {repr(tumblr_json_images)}")
            tumblr_text = f"{ctx.message.author.mention}, here are your requested image(s):"
            for image in tumblr_json_images:
                current_count = len(tumblr_text)+1
                total_count = len(tumblr_json_images)
                tumblr_text += tumblr_image_base.format(image["original_size"]["url"])
            if tumblr_is_nsfw and ctx.guild:
                tumblr_text += "\nDon't want NSFW posts on this channel? Add `no_nsfw` on any part of the topic and AveBot will no longer allow NSFW commands to run here."
            self.bot.log.info(tumblr_text)
            await ctx.send(tumblr_text)
        else:
            await ctx.send("No tumblr link detected")

def setup(bot):
    bot.add_cog(NSFW(bot))