import re
import math
import discord
from discord.ext import commands
import datetime
import secrets


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

    async def booru(self, ctx, service: str, tags: str):
        """Central function to handle booru interactions"""
        random_supported = service in ["e621.net"]
        gel_style = service in ["gelbooru.com", "rule34.xxx"]

        nsfw_result = await self.nsfw_check(ctx)
        if not nsfw_result:
            return

        api_url = ""
        if gel_style:
            api_url = f"https://{service}/index.php?page=dapi&s=post&q=index&limit=100&json=1"\
                      f"&tags=score:>=10 -webm {tags}"
        elif service == "hypnohub.net":
            api_url = f"http://hypnohub.net/post/index.json?limit=100&tags=score:>10 {tags}"
        elif service == "e621.net":
            api_url = "https://e621.net/post/index.json?limit=1&tags="\
                      f"order:random score:>10 -webm {tags}"
        else:
            return
        booru_json = await self.bot.aiojson(api_url)
        # TODO: check if empty
        chosen_post = booru_json[0] if random_supported else secrets.choice(booru_json)

        res_desc = f"Tags: `{chosen_post['tags']}`\n"
        res_desc += (f"Owner: `{chosen_post['owner']}`\n" if gel_style else
                   f"Author: `{chosen_post['author']}`\n")
        res_desc += f"Score: `{chosen_post['score']}`"

        post_url = ""
        if gel_style:
            post_url = f"https://{service}/index.php?page=post&s=view&id={chosen_post['id']}"
        elif service in ["hypnohub.net", "e621.net"]:
            post_url = f"https://{service}/post/show/{chosen_post['id']}"

        embed_color = ""
        if gel_style:
            embed_color = self.bot.hex_to_int(chosen_post["hash"][0:6])
        elif service in ["hypnohub.net", "e621.net"]:
            embed_color = self.bot.hex_to_int(chosen_post["md5"][0:6])

        embed_timestamp = ""
        if gel_style:
            embed_timestamp = datetime.datetime.utcfromtimestamp(chosen_post["change"])
        elif service == "hypnohub.net":
            embed_timestamp = datetime.datetime.utcfromtimestamp(chosen_post["created_at"])
        elif service == "e621.net":
            embed_timestamp = datetime.datetime.utcfromtimestamp(chosen_post["created_at"]["s"])

        embed = discord.Embed(title=f"{service} result",
                              color=embed_color,
                              description=res_desc,
                              url=post_url,
                              timestamp=embed_timestamp)

        image_url = ""
        if service == "gelbooru.com":
            image_url = chosen_post["file_url"]
        elif service == "rule34.xxx":
            image_url = "https://rule34.xxx/images/"\
                        f"{chosen_post['directory']}/{chosen_post['image']}"
        elif service == "hypnohub.net":
            image_url = "https:" + chosen_post["preview_url"].replace(".net//", ".net/") # fuck hh
        elif service == "e621.net":
            image_url = chosen_post["sample_url"]

        embed.set_image(url=image_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['gel'])
    async def gelbooru(self, ctx, *, tags: str = ""):
        """Returns a random image from gelbooru from given tags"""
        await self.booru(ctx, "gelbooru.com", tags)

    @commands.command(aliases=['r34'])
    async def rule34(self, ctx, *, tags: str = ""):
        """Returns a random image from rule34 from given tags"""
        await self.booru(ctx, "rule34.xxx", tags)

    @commands.command(aliases=['hh'])
    async def hypnohub(self, ctx, *, tags: str = ""):
        """Returns a random image from hypnohub from given tags"""
        await self.booru(ctx, "hypnohub.net", tags)

    @commands.command(aliases=['e6'])
    async def e621(self, ctx, *, tags: str = ""):
        """Returns a random image from e621 from given tags"""
        await self.booru(ctx, "e621.net", tags)

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
