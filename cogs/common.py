import discord
from discord.ext import commands
import re
import aiohttp

class Common:
    def __init__(self, bot):
        self.bot = bot
        self.bot.aiosession = aiohttp.ClientSession()
        self.bot.aiojson = self.aiojson
        self.bot.aioget = self.aioget
        self.bot.slice_message = self.slice_message
        self.bot.git_pull = self.git_pull
        self.bot.download_file = self.download_file
        self.bot.aiogetbytes = self.aiogetbytes


    async def download_file(self, url, local_filename):  # This function is based on https://stackoverflow.com/a/35435419/3286892 by link2110 (https://stackoverflow.com/users/5890923/link2110), modified by Ave (https://github.com/aveao), licensed CC-BY-SA 3.0
        file_resp = await self.bot.aiosession.get(url)
        file = await file_resp.read()
        with open(local_filename, "wb") as f:
            f.write(file)


    async def aioget(self, url):
        try:
            data = await self.bot.aiosession.get(url)
            if data.status == 200:
                text_data = await data.text()
                self.bot.log.info(f"Data from {url}: {text_data}")
                return text_data
            else:
                self.bot.log.error(f"HTTP Error {data.status} while getting {url}")
        except:
            self.bot.log.error(f"Error while getting {url} on aioget: {traceback.format_exc()}")

    async def aiogetbytes(self, url):
        try:
            data = await self.bot.aiosession.get(url)
            if data.status == 200:
                byte_data = await data.read()
                self.bot.log.debug(f"Data from {url}: {byte_data}")
                return byte_data
            else:
                self.bot.log.error(f"HTTP Error {data.status} while getting {url}")
        except:
            self.bot.log.error(f"Error while getting {url} on aiogetbytes: {traceback.format_exc()}")


    async def aiojson(self, url):
        try:
            data = await self.bot.aiosession.get(url)
            if data.status == 200:
                text_data = await data.text()
                self.bot.log.info(f"Data from {url}: {text_data}")
                return await data.json(content_type=data.headers['Content-Type'])
            else:
                self.bot.log.error(f"HTTP Error {data.status} while getting {url}")
        except:
            self.bot.log.error(f"Error while getting {url} on aiojson: {traceback.format_exc()}")

    def slice_message(self, text, size):
        reply_list = []
        while len(text) > size:
            reply_list.append(text[:size])
            text = text[size:]
        reply_list.append(text)
        return reply_list

    def git_pull(self):
        return self.bot.call_shell("git pull")

def setup(bot):
    bot.add_cog(Common(bot))