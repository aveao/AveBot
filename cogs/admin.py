import discord
from discord.ext import commands
import traceback
import inspect
import re


class AdminCog:
    def __init__(self, bot):
        self.bot = bot
        self.last_eval_result = None
        self.previous_eval_code = None

    @commands.is_owner()
    @commands.command(aliases=['echo'], hidden=True)
    async def say(self, ctx, *, the_text: str):
        """Repeats a given text."""
        await ctx.send(the_text)

    @commands.is_owner()
    @commands.command(name='exit', hidden=True)
    async def _exit(self, ctx):
        """Shuts down AveBot, owner only."""
        await ctx.send(":wave: Exiting AveBot, goodbye!")
        await self.bot.logout()

    @commands.is_owner()
    @commands.command(hidden=True)
    async def load(self, ctx, ext: str):
        """Loads a cog, owner only."""
        try:
            self.bot.load_extension("cogs." + ext)
        except:
            await ctx.send(f':x: Cog loading failed, traceback: ```\n{traceback.format_exc()}\n```')
            return
        self.bot.log.info(f'Loaded ext {ext}')
        await ctx.send(f':white_check_mark: `{ext}` successfully loaded.')

    @commands.is_owner()
    @commands.command(hidden=True, aliases=['writeconfig'])
    async def saveconfig(self, ctx):
        with open("avebot.ini", 'w') as configfile:
            self.bot.config.write(configfile)
        await ctx.send("Successfully wrote config file.")

    @commands.is_owner()
    @commands.command(hidden=True, aliases=['reloadconfig', 'readconfig'])
    async def loadconfig(self, ctx):
        self.bot.config.read("avebot.ini")
        await ctx.send("Successfully read config file.")

    @commands.is_owner()
    @commands.command(hidden=True)
    async def setconfig(self, ctx, section: str, key: str, value: str):
        botconfig = self.bot.config
        if not section in botconfig:
            botconfig[section] = {}
        botconfig[section][key] = value
        self.bot.config = botconfig
        await ctx.send("Successfully set value, don't forget to `ab!saveconfig`.")

    @commands.is_owner()
    @commands.command(hidden=True)
    async def getconfig(self, ctx, section: str, key: str):
        botconfig = self.bot.config
        if section in botconfig and key in botconfig[section]:
            value = botconfig[section][key]
            await ctx.send(f"Config value for [{section}]->\"{key}\" is \"{value}\".")
        elif section in botconfig:
            await ctx.send(f"Section \"{section}\" does exist, but \"{key}\" doesn't.")
        else:
            await ctx.send(f"Section \"{section}\" does not exist.")

    @commands.is_owner()
    @commands.command(hidden=True)
    async def fetchlog(self, ctx):
        """Returns log"""
        await ctx.send(file=discord.File("avebot.log"), content="Here's the current log file:")

    @commands.is_owner()
    @commands.command(name='eval', hidden=True)
    async def _eval(self, ctx, *, code: str):
        """Evaluates some code (Owner only)"""
        try:
            code = code.strip('` ')

            env = {
                'bot': self.bot,
                'ctx': ctx,
                'message': ctx.message,
                'server': ctx.guild,
                'guild': ctx.guild,
                'channel': ctx.message.channel,
                'author': ctx.message.author,

                # modules
                'discord': discord,
                'commands': commands,

                # utilities
                '_get': discord.utils.get,
                '_find': discord.utils.find,

                # last result
                '_': self.last_eval_result,
                '_p': self.previous_eval_code,
            }
            env.update(globals())

            self.bot.log.info(f"Evaling {repr(code)}:")
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result

            if result is not None:
                self.last_eval_result = result

            self.previous_eval_code = code

            sliced_message = await self.bot.slice_message(repr(result), prefix="```", suffix="```")
            for msg in sliced_message:
                await ctx.send(msg)
        except:
            sliced_message = await self.bot.slice_message(traceback.format_exc(), prefix="```", suffix="```")
            for msg in sliced_message:
                await ctx.send(msg)

    @commands.is_owner()
    @commands.command(hidden=True)
    async def sh(self, ctx, *, command: str):
        """Runs a command on shell."""
        command = command.strip('`')
        tmp = await ctx.send(f'Running `{command}`...')
        self.bot.log.info(f"Running {command}")
        shell_output = await self.bot.async_call_shell(command)
        shell_output = f"\"{command}\" output:\n\n{shell_output}"
        self.bot.log.info(shell_output)
        sliced_message = await self.bot.slice_message(shell_output, prefix="```", suffix="```")
        if len(sliced_message) == 1:
            await tmp.edit(content=sliced_message[0])
            return
        await tmp.delete()
        for msg in sliced_message:
            await ctx.send(msg)

    @commands.is_owner()
    @commands.command(hidden=True)
    async def pull(self, ctx, auto=False):
        """Does a git pull (Owner only)."""
        tmp = await ctx.send('Pulling...')
        git_output = self.bot.call_shell("git pull")
        await tmp.edit(content=f"Pull complete. Output: ```{git_output}```")
        await self.bot.change_presence(activity=discord.Game(name=f'ab!help | {self.bot.get_git_revision_short_hash()}'))
        if auto:
            cogs_to_reload = re.findall('cogs/([a-z]*).py[ ]*\|', git_output)
            for cog in cogs_to_reload:
                try:
                    self.bot.unload_extension("cogs." + cog)
                    self.bot.load_extension("cogs." + cog)
                    self.bot.log.info(f'Reloaded ext {cog}')
                    await ctx.send(f':white_check_mark: `{cog}` successfully reloaded.')
                except:
                    await ctx.send(f':x: Cog reloading failed, traceback: ```\n{traceback.format_exc()}\n```')
                    return

    @commands.is_owner()
    @commands.command(hidden=True)
    async def unload(self, ctx, ext: str):
        """Unloads a cog, owner only."""
        self.bot.unload_extension("cogs." + ext)
        self.bot.log.info(f'Unloaded ext {ext}')
        await ctx.send(f':white_check_mark: `{ext}` successfully unloaded.')

    @commands.is_owner()
    @commands.command(hidden=True)
    async def reload(self, ctx, ext="_"):
        """Reloads a cog, owner only."""
        if ext == "_":
            ext = self.lastreload
        else:
            self.lastreload = ext

        try:
            self.bot.unload_extension("cogs." + ext)
            self.bot.load_extension("cogs." + ext)
        except:
            await ctx.send(f':x: Cog reloading failed, traceback: ```\n{traceback.format_exc()}\n```')
            return
        self.bot.log.info(f'Reloaded ext {ext}')
        await ctx.send(f':white_check_mark: `{ext}` successfully reloaded.')

    @commands.is_owner()
    @commands.command(hidden=True)
    async def log(self, ctx, count: int):
        """Returns a file out of the last N messages submitted in this channel."""
        log_text = "===start of log, exported by avebot===\n"
        async for mlog in ctx.channel.history(limit=count):
            log_text += "[{}]<{}>{}\n".format(str(mlog.created_at),
                                              str(mlog.author), mlog.clean_content)
        mlog_file_name = "files/{}.log".format(ctx.channel.id)
        file = open(mlog_file_name, "w")
        file.write(log_text)
        file.write("===end of log, exported by avebot===")
        file.close()
        await ctx.send(file=discord.File(mlog_file_name), content=f"{ctx.message.author.mention}: Here's the log file you requested.")


def setup(bot):
    bot.add_cog(AdminCog(bot))
