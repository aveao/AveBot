import re
import math
import datetime
import secrets
import discord
from discord.ext import commands


class BooruE621:
    """Booru class for e621"""
    name = "e621"
    domain = "e621.net"
    random_supported = True

    def get_api_url(self, tags: str):
        return f"https://{self.domain}/post/index.json?limit=1&tags="\
               f"order:random score:>10 -webm {tags}"

    def get_post_url(self, post_id):
        return f"https://{self.domain}/post/show/{post_id}"

    def get_post_hash(self, post_json):
        return post_json["md5"]

    def get_post_timestr(self, post_json):
        return datetime.datetime.utcfromtimestamp(post_json["created_at"]["s"])

    def get_image_url(self, post_json):
        return post_json["sample_url"]

    def get_owner_name(self, post_json):
        return post_json['author']

    def get_post_tags(self, post_json):
        return post_json['tags']

    def get_post_score(self, post_json):
        return post_json['score']


class BooruHypnohub:
    """Booru class for Hypnohub"""
    name = "Hypnohub"
    domain = "hypnohub.net"
    random_supported = False

    def get_api_url(self, tags: str):
        return f"https://{self.domain}/post/index.json?limit=100&tags=score:>10 {tags}"

    def get_post_url(self, post_id):
        return f"https://{self.domain}/post/show/{post_id}"

    def get_post_hash(self, post_json):
        return post_json["md5"]

    def get_post_timestr(self, post_json):
        return datetime.datetime.utcfromtimestamp(post_json["created_at"])

    def get_image_url(self, post_json):
        return "https:" + post_json["sample_url"].replace(".net//", ".net/")  # fuck hh

    def get_owner_name(self, post_json):
        return post_json['author']

    def get_post_tags(self, post_json):
        return post_json['tags']

    def get_post_score(self, post_json):
        return post_json['score']


class BooruGelbooru:
    """Booru class for Gelbooru"""
    name = "Gelbooru"
    domain = "gelbooru.com"
    random_supported = False

    def get_api_url(self, tags: str):
        return f"https://{self.domain}/index.php?page=dapi&s=post&q=index&limit=100&json=1"\
               f"&tags=score:>=10 -webm {tags}"

    def get_post_url(self, post_id):
        return f"https://{self.domain}/index.php?page=post&s=view&id={post_id}"

    def get_post_hash(self, post_json):
        return post_json["hash"]

    def get_post_timestr(self, post_json):
        return datetime.datetime.utcfromtimestamp(post_json["change"])

    def get_image_url(self, post_json):
        return post_json["file_url"]

    def get_owner_name(self, post_json):
        return post_json['owner']

    def get_post_tags(self, post_json):
        return post_json['tags']

    def get_post_score(self, post_json):
        return post_json['score']


class BooruDanbooru:
    """Booru class for Danbooru"""
    name = "Danbooru"
    domain = "danbooru.donmai.us"
    random_supported = True

    def get_api_url(self, tags: str):
        return f"https://{self.domain}/posts.json?random=true&limit=1&tags=score:%3E10%20{tags}"

    def get_post_url(self, post_id):
        return f"https://{self.domain}/posts/{post_id}"

    def get_post_hash(self, post_json):
        return post_json["md5"]

    def get_post_timestr(self, post_json):  # fucking danbooru gives a dumb timestring
        danb_timestr = post_json["created_at"]
        tz_diff = danb_timestr[-5:]
        danb_timestr = danb_timestr.replace(tz_diff, tz_diff.replace(":", ""))  # Remove : from timezone
        return datetime.datetime.strptime(danb_timestr, "%Y-%m-%dT%H:%M:%S.%f%z")

    def get_image_url(self, post_json):
        return f"https://{self.domain}{post_json['file_url']}"

    def get_owner_name(self, post_json):
        return post_json['uploader_name']

    def get_post_tags(self, post_json):
        return post_json['tag_string']

    def get_post_score(self, post_json):
        return post_json['up_score'] - post_json['down_score']


class BooruRule34:
    """Booru class for Rule34"""
    name = "Rule34"
    domain = "rule34.xxx"
    random_supported = False

    def get_api_url(self, tags: str):
        return f"https://{self.domain}/index.php?page=dapi&s=post&q=index&limit=100&json=1"\
               f"&tags=score:>=10 -webm {tags}"

    def get_post_url(self, post_id):
        return f"https://{self.domain}/index.php?page=post&s=view&id={post_id}"

    def get_post_hash(self, post_json):
        return post_json["hash"]

    def get_post_timestr(self, post_json):
        return datetime.datetime.utcfromtimestamp(post_json["change"])

    def get_image_url(self, post_json):
        return f"https://{self.domain}/images/"\
               f"{post_json['directory']}/{post_json['image']}"

    def get_owner_name(self, post_json):
        return post_json['owner']

    def get_post_tags(self, post_json):
        return post_json['tags']

    def get_post_score(self, post_json):
        return post_json['score']


class BooruRealbooru:
    """Booru class for Realbooru"""
    name = "Realbooru"
    domain = "realbooru.com"
    random_supported = False

    def get_api_url(self, tags: str):
        return f"https://{self.domain}/index.php?page=dapi&s=post&q=index&limit=100&json=1"\
               f"&tags=score:>=10 -webm {tags}"

    def get_post_url(self, post_id):
        return f"https://{self.domain}/index.php?page=post&s=view&id={post_id}"

    def get_post_hash(self, post_json):
        return post_json["hash"]

    def get_post_timestr(self, post_json):
        return datetime.datetime.utcfromtimestamp(post_json["change"])

    def get_image_url(self, post_json):
        return f"https://{self.domain}/images/"\
               f"{post_json['directory']}/{post_json['image']}"

    def get_owner_name(self, post_json):
        return post_json['owner']

    def get_post_tags(self, post_json):
        return post_json['tags']

    def get_post_score(self, post_json):
        return post_json['score']


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

    async def booru(self, ctx, service, tags: str):
        """Central function to handle booru interactions"""
        nsfw_result = await self.nsfw_check(ctx)
        if not nsfw_result:
            return

        api_url = service.get_api_url(tags)
        booru_json = await self.bot.aiojson(api_url)
        if not booru_json:
            await ctx.send("No results found on "
                           f"`{service.name}` with tag `{tags}`")
            return
        chosen_post = booru_json[0] if service.random_supported else secrets.choice(booru_json)

        res_desc = f"Tags: `{service.get_post_tags(chosen_post)[:2000]}`\n"\
                   f"Uploader: `{service.get_owner_name(chosen_post)}`\n"\
                   f"Score: `{service.get_post_score(chosen_post)}`"

        post_url = service.get_post_url(chosen_post['id'])
        image_url = service.get_image_url(chosen_post)
        embed_color = self.bot.hex_to_int(service.get_post_hash(chosen_post)[0:6])
        embed_timestamp = service.get_post_timestr(chosen_post)

        embed = discord.Embed(title=f"{service.name} result for {tags}",
                              color=embed_color,
                              description=res_desc,
                              url=post_url,
                              timestamp=embed_timestamp)

        embed.set_image(url=image_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['gel'])
    async def gelbooru(self, ctx, *, tags: str = ""):
        """Returns a random image from gelbooru from given tags"""
        async with ctx.typing():
            await self.booru(ctx, BooruGelbooru(), tags)

    @commands.command(aliases=['dan'])
    async def danbooru(self, ctx, *, tags: str = ""):
        """Returns a random image from danbooru from given tags"""
        async with ctx.typing():
            await self.booru(ctx, BooruDanbooru(), tags)

    @commands.command(aliases=['r34'])
    async def rule34(self, ctx, *, tags: str = ""):
        """Returns a random image from rule34 from given tags"""
        async with ctx.typing():
            await self.booru(ctx, BooruRule34(), tags)

    @commands.command(aliases=['rb'])
    async def realbooru(self, ctx, *, tags: str = ""):
        """Returns a random image from realbooru from given tags"""
        async with ctx.typing():
            await self.booru(ctx, BooruRealbooru(), tags)

    @commands.command(aliases=['hh'])
    async def hypnohub(self, ctx, *, tags: str = ""):
        """Returns a random image from hypnohub from given tags"""
        async with ctx.typing():
            await self.booru(ctx, BooruHypnohub(), tags)

    @commands.command(aliases=['e6'])
    async def e621(self, ctx, *, tags: str = ""):
        """Returns a random image from e621 from given tags"""
        async with ctx.typing():
            await self.booru(ctx, BooruE621(), tags)

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
