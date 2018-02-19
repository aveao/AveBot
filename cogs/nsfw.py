import discord
from discord.ext import commands
import re
import math


class NSFW:
    """NSFW commands for the lewd people."""
    def __init__(self, bot):
        self.bot = bot
        self.discord_max_embed = 5
        self.tumblr_api_key = bot.config['tumblr']['apikey']

    @commands.command(aliases=['fucksafemode'])
    async def tumblrgrab(self, ctx, *, link: str):
        """Returns images from the specified tumblr link."""
        reg = r'([a-z0-9-.]{1,})\/post\/([0-9]{1,})'
        regex_result = re.search(reg, link)
        if regex_result:
            site = regex_result.group(1)
            postid = regex_result.group(2)
            channel_is_nsfw = ctx.channel.is_nsfw() if ctx.guild else True
            channel_allows_nsfw = (("no_nsfw" not in ctx.channel.topic)
                                   if ctx.channel.topic else True) if ctx.guild else True

            tumblrapicall_link = f"https://api.tumblr.com/v2/blog/{site}/posts/photo?id={postid}"\
                f"&api_key={self.tumblr_api_key}"
            tumblr_json = await self.bot.aiojson(tumblrapicall_link)
            tumblr_is_nsfw = ("x_tumblr_content_rating" in tumblr_json["meta"])

            if (not channel_is_nsfw and tumblr_is_nsfw):
                await ctx.send("The contents of this post are marked NSFW, "
                               "and this isn't an NSFW channel.")
                return
            elif (channel_is_nsfw and tumblr_is_nsfw and not channel_allows_nsfw):
                await ctx.send("The contents of this post are marked NSFW, "
                               "and this channel does not allow NSFW posts "
                               "(has `no_nsfw` on channel topic).")
                return

            tumblr_image_base = "\n{}"

            tumblr_json_images = tumblr_json["response"]["posts"][0]["photos"]
            self.bot.log.info(f"tumblr json images: {repr(tumblr_json_images)}")
            tumblr_text = f"{ctx.message.author.mention}, here are your requested image(s):"
            split_count = 0
            total_pages = math.floor(len(tumblr_json_images) / 5)
            for image in tumblr_json_images:
                split_count += 1
                tumblr_text += tumblr_image_base.format(
                    image["original_size"]["url"])
                if split_count % 5:
                    await ctx.send(tumblr_text
                                   + f"\n({split_count / 5}/{total_pages})")
                    tumblr_text = ""
            if tumblr_is_nsfw and ctx.guild:
                tumblr_text += "\nDon't want NSFW posts on this channel? Add `no_nsfw` on any part"\
                    " of the topic and AveBot will no longer allow NSFW commands to run here."
            self.bot.log.info(tumblr_text)
            await ctx.send(tumblr_text)
        else:
            await ctx.send("No tumblr link detected")


def setup(bot):
    bot.add_cog(NSFW(bot))
