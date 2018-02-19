import re
import math
import discord
from discord.ext import commands


class NSFW:
    """NSFW commands for the lewd people."""
    def __init__(self, bot):
        self.bot = bot
        self.discord_max_embed = 5
        self.tumblr_api_key = bot.config['tumblr']['apikey']
        self.tumblr_post_regex = r'([a-z0-9-.]{1,})\/post\/([0-9]{1,})'

    async def nsfw_check(self, ctx, post_nsfw: bool = True, send_message: bool = True):
        """Checks if the given channel is NSFW."""
        if ctx.guild:
            channel_is_nsfw = ctx.channel.is_nsfw()
            if not channel_is_nsfw and post_nsfw:
                if send_message:
                    await ctx.send("This isn't an NSFW channel, "
                                   "you can't use NSFW commands here.")
                return False

            channel_allows_nsfw = (("no_nsfw" not in ctx.channel.topic)
                                   if ctx.channel.topic else True)
            if not channel_allows_nsfw:
                if send_message:
                    await ctx.send("This command cannot be used on this channel"
                                   " as it has `no_nsfw` on channel topic.")
                return False
        return True

    @commands.command(aliases=['fucksafemode'])
    async def tumblrgrab(self, ctx, *, link: str):
        """Returns images from the specified tumblr link."""
        regex_result = re.search(self.tumblr_post_regex, link)
        if regex_result:
            tumblrapicall_link = f"https://api.tumblr.com/v2/blog/{regex_result.group(1)}"\
                                 f"/posts?id={regex_result.group(2)}"\
                                 f"&api_key={self.tumblr_api_key}"

            tumblr_json = await self.bot.aiojson(tumblrapicall_link)
            tumblr_is_nsfw = ("x_tumblr_content_rating" in tumblr_json["meta"])

            nsfw_result = await self.nsfw_check(ctx, tumblr_is_nsfw)
            if not nsfw_result and tumblr_is_nsfw:
                return

            tumblr_json_images = tumblr_json["response"]["posts"][0]["photos"]
            self.bot.log.info(f"tumblr json images: {repr(tumblr_json_images)}")
            tumblr_text = f"{ctx.message.author.mention}, here are your requested image(s):"
            if not tumblr_is_nsfw:
                tumblr_text += f"\n**Post is marked as SAFE FOR WORK, which is why these images"\
                               " are being posted on a non-nsfw channel. If this is a NSFW post,"\
                               " please report to tumblr for unmarked NSFW content.**"

            split_count = 0
            total_pages = math.floor(len(tumblr_json_images) / 5)
            for image in tumblr_json_images:
                split_count += 1
                tumblr_text += "\n" + image["original_size"]["url"]
                if not split_count % 5:
                    await ctx.send(tumblr_text
                                   + f"\n({int(split_count / 5)}/{total_pages})")
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
