import asyncio
import aiohttp
import datetime
import humanize
import traceback
from urllib.parse import urlparse
import os


class Common:
    def __init__(self, bot):
        self.bot = bot
        self.bot.aiosession = aiohttp.ClientSession(
            headers={"User-Agent": "AveBot/3.0'"})
        self.bot.aiojson = self.aiojson
        self.bot.aioget = self.aioget
        self.bot.slice_message = self.slice_message
        self.bot.git_pull = self.git_pull
        self.bot.download_file = self.download_file
        self.bot.aiogetbytes = self.aiogetbytes
        self.bot.get_relative_timestamp = self.get_relative_timestamp
        self.bot.async_call_shell = self.async_call_shell
        self.bot.haste = self.haste
        self.bot.filename_get_woext = self.filename_get_woext
        self.bot.url_get_filename = self.url_get_filename
        self.bot.filename_get_ext = self.filename_get_ext
        self.bot.hex_to_int = self.hex_to_int
        self.max_split_length = int(bot.config["advanced"]["max-slice"])

    async def async_call_shell(self, shell_command: str,
                               inc_stdout=True, inc_stderr=True):
        sp_pipe = asyncio.subprocess.PIPE
        p = await asyncio.create_subprocess_shell(str(shell_command),
                                                  stdout=sp_pipe,
                                                  stderr=sp_pipe)
        # await p.wait()
        # God I hate having to account for a fuckton of different shit
        if not (inc_stdout or inc_stderr):
            return "??? you set both stdout and stderr to False????"

        proc_result = await p.communicate()
        stdout_str = proc_result[0].decode('utf-8').strip()
        stderr_str = proc_result[1].decode('utf-8').strip()

        if inc_stdout and not inc_stderr:
            return stdout_str
        elif inc_stderr and not inc_stdout:
            return stderr_str

        if stdout_str and stderr_str:
            return f"stdout:\n\n{stdout_str}\n\n"\
                   f"======\n\nstderr:\n\n{stderr_str}"
        elif stdout_str:
            return f"stdout:\n\n{stdout_str}"
        elif stderr_str:
            return f"stderr:\n\n{stderr_str}"
        else:
            return "No output."

    # based on https://stackoverflow.com/a/18727481/3286892
    # by Ofir Israel (https://stackoverflow.com/users/2713087/ofir-israel)
    async def url_get_filename(self, url):
        a = urlparse(url)
        return os.path.basename(a.path)

    async def filename_get_ext(self, filename):
        filename = os.path.splitext(filename)[1]
        if "?" in filename:
            filename = filename.split('?')[0]

        return filename

    async def filename_get_woext(self, filename):
        filename = os.path.splitext(filename)[0]
        return filename

    def hex_to_int(self, color_hex: str):
        """Turns a given hex color into an integer"""
        return int("0x" + color_hex.strip('#'), 16)

    # This function is based on https://stackoverflow.com/a/35435419/3286892
    # by link2110 (https://stackoverflow.com/users/5890923/link2110)
    # modified by Ave (https://github.com/aveao), licensed CC-BY-SA 3.0
    async def download_file(self, url, local_filename):
        file_resp = await self.bot.aiosession.get(url)
        file = await file_resp.read()
        with open(local_filename, "wb") as f:
            f.write(file)

    async def haste(self, text,
                    haste_domain: str = 'https://hastebin.com/'):
        response = await self.bot.aiosession.post(f"{haste_domain}documents",
                                                  data=text)
        if response.status == 200:
            result_json = await response.json()
            return f"{haste_domain}{result_json['key']}"

    def get_relative_timestamp(self, time_from=None, time_to=None,
                               humanized=False, include_from=False,
                               include_to=False):
        # Setting default value to utcnow() makes it show time from cog load,
        # which is not what we want
        if not time_from:
            time_from = datetime.datetime.utcnow()
        if not time_to:
            time_to = datetime.datetime.utcnow()
        if humanized:
            humanized_string = humanize.naturaltime(time_to - time_from)
            if include_from and include_to:
                str_with_from_and_to = f"{humanized_string} "\
                                       f"({str(time_from).split('.')[0]} "\
                                       f"- {str(time_to).split('.')[0]})"
                return str_with_from_and_to
            elif include_from:
                str_with_from = f"{humanized_string} "\
                                f"({str(time_from).split('.')[0]})"
                return str_with_from
            elif include_to:
                str_with_to = f"{humanized_string} "\
                              f"({str(time_to).split('.')[0]})"
                return str_with_to
            return humanized_string
        else:
            epoch = datetime.datetime.utcfromtimestamp(0)
            epoch_from = (time_from - epoch).total_seconds()
            epoch_to = (time_to - epoch).total_seconds()
            second_diff = epoch_to - epoch_from
            result_string = str(datetime.timedelta(
                seconds=second_diff)).split('.')[0]
            return result_string

    async def aioget(self, url):
        try:
            data = await self.bot.aiosession.get(url)
            if data.status == 200:
                text_data = await data.text()
                self.bot.log.info(f"Data from {url}: {text_data}")
                return text_data
            else:
                self.bot.log.error(f"HTTP {data.status} while getting {url}")
        except:
            self.bot.log.error(f"Error while getting {url} on "
                               f"aioget: {traceback.format_exc()}")

    async def aiogetbytes(self, url):
        try:
            data = await self.bot.aiosession.get(url)
            if data.status == 200:
                byte_data = await data.read()
                self.bot.log.debug(f"Data from {url}: {byte_data}")
                return byte_data
            else:
                self.bot.log.error(f"HTTP {data.status} while getting {url}")
        except:
            self.bot.log.error(f"Error while getting {url} on "
                               f"aiogetbytes: {traceback.format_exc()}")

    async def aiojson(self, url):
        try:
            data = await self.bot.aiosession.get(url)
            if data.status == 200:
                text_data = await data.text()
                self.bot.log.info(f"Data from {url}: {text_data}")
                ctype = data.headers['Content-Type']
                return await data.json(content_type=ctype)
            else:
                self.bot.log.error(f"HTTP {data.status} while getting {url}")
        except:
            self.bot.log.error(f"Error while getting {url} on "
                               f"aiojson: {traceback.format_exc()}")

    # 2000 is maximum limit of discord
    async def slice_message(self, text, size=2000, prefix="", suffix=""):
        if len(text) > size * self.max_split_length:
            haste_url = await self.haste(text)
            return [f"Message is too long ({len(text)} > "
                    f"{size * self.max_split_length} ({size} * "
                    f"{self.max_split_length})), go to haste: <{haste_url}>"]
        reply_list = []
        size_wo_fix = size - len(prefix) - len(suffix)
        while len(text) > size_wo_fix:
            reply_list.append(f"{prefix}{text[:size_wo_fix]}{suffix}")
            text = text[size_wo_fix:]
        reply_list.append(f"{prefix}{text}{suffix}")
        return reply_list

    def git_pull(self):
        return self.bot.call_shell("git pull")


def setup(bot):
    bot.add_cog(Common(bot))
