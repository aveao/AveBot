import discord
from discord.ext import commands
import traceback
import psycopg2


class PermManage:
    def __init__(self, bot):
        self.bot = bot
        self.bot.get_permission = self.get_permission
        self.bot.set_permission = self.set_permission

    # Based on https://stackoverflow.com/a/18708605/3286892 by Jaymon (https://stackoverflow.com/users/5006/jaymon)
    async def dummy_pgsql(self):
        try:
            cur = self.bot.postgres_connection.cursor()
            cur.execute('SELECT 1')
            cur.close()
        except psycopg2.OperationalError:
            pass

    # Based on https://stackoverflow.com/a/18708605/3286892 by Jaymon (https://stackoverflow.com/users/5006/jaymon)
    async def ensure_pgsql(self):
        # TODO: improve code repetition here
        # I'm doing this because I want to reduce db calls
        # as much as possible if they're not needed.
        await self.reconnect_pgsql(True)
        await self.dummy_pgsql()
        await self.reconnect_pgsql(True)

    async def reconnect_pgsql(self, only_if_closed=False):
        if (only_if_closed and (self.bot.postgres_connection.closed != 0)) or not only_if_closed:
            self.bot.postgres_connection = psycopg2.connect(
                self.bot.config['base']['postgres-connection-string'])

    async def get_permission(self, id):
        if id == self.bot.bot_info.owner.id:
            return 99  # Bot owner's level is locked to 99
        try:
            await self.ensure_pgsql()
            perm_sql = f"SELECT permlevel FROM permissions WHERE discord_id = {id};"
            cursor = self.bot.postgres_connection.cursor()
            cursor.execute(perm_sql)
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else 1
        except:
            self.bot.log.error(f"Error on get_permission: {traceback.format_exc()}")
            cursor.close()
            return 1

    async def set_permission(self, id, permlevel):
        cursor = self.bot.postgres_connection.cursor()
        try:
            await self.ensure_pgsql()
            cursor.execute(f"DELETE FROM permissions WHERE discord_id = {id}")
            if permlevel != 1:  # Just remove regular users from database
                cursor.execute("INSERT INTO permissions (discord_id, permlevel) VALUES (%s, %s)",
                               (id, permlevel))
            self.bot.postgres_connection.commit()
        except:
            self.bot.log.error(f"Error on set_permission: {traceback.format_exc()}")
        cursor.close()

    @commands.is_owner()
    @commands.command(hidden=True)
    async def setperm(self, ctx, user: discord.User, check: bool = True):
        await self.set_permission(user.id, level)
        return_message = f"Set permission level of {user.id} to {level}"
        if check:
            actual_level = await self.get_permission(user.id)
            if level == actual_level:
                await ctx.send(f"{return_message} (successfully verified as being {actual_level})")
            else:
                self.bot.log.error(f"Tried to set perm level of {user.id} to {level} but value reads as {actual_level}.")
                await ctx.send(f"{return_message} (verification failed, value is {actual_level}!)")
        else:
            await ctx.send(f"{return_message} (blind)")

    @commands.is_owner()
    @commands.command(hidden=True, aliases=['addmod'])
    async def setmod(self, ctx, user: discord.User, check: bool = True):
        await self.set_permission(user.id, 8)
        return_message = f"Successfully added {user} as mod"
        if check:
            actual_level = await self.get_permission(user.id)
            if actual_level == 8:
                await ctx.send(f"{return_message} (successfully verified as being {actual_level})")
            else:
                self.bot.log.error(f"Tried to set perm level of {user.id} to 8 but value reads as {actual_level}.")
                await ctx.send(f"{return_message} (verification failed, value is {actual_level}!)")
        else:
            await ctx.send(f"{return_message} (blind)")

    @commands.command(hidden=True, aliases=['addpriv'])
    async def setpriv(self, ctx, user: discord.User, check: bool = True):
        author_level = await self.get_permission(ctx.author.id)
        user_level = await self.get_permission(user.id)
        if author_level < 8 or (user_level >= author_level and ctx.author != user):
            return
        await self.set_permission(user.id, 2)
        return_message = f"Successfully set {user} as privileged user"
        if check:
            actual_level = await self.get_permission(user.id)
            if actual_level == 2:
                await ctx.send(f"{return_message} (successfully verified as being {actual_level})")
            else:
                self.bot.log.error(f"Tried to set perm level of {user.id} to 2 but value reads as {actual_level}.")
                await ctx.send(f"{return_message} (verification failed, value is {actual_level}!)")
        else:
            await ctx.send(f"{return_message} (blind)")

    @commands.command(hidden=True, aliases=['unban', 'rmmod', 'unmod', 'rmpriv', 'unpriv'])
    async def setregular(self, ctx, user: discord.User, check: bool = True):
        author_level = await self.get_permission(ctx.author.id)
        user_level = await self.get_permission(user.id)
        if author_level < 8 or (user_level >= author_level and ctx.author != user):
            return
        await self.set_permission(user.id, 1)
        return_message = f"Successfully set {user} as regular user"
        if check:
            actual_level = await self.get_permission(user.id)
            if actual_level == 1:
                await ctx.send(f"{return_message} (successfully verified as being {actual_level})")
            else:
                self.bot.log.error(f"Tried to set perm level of {user.id} to 1 but value reads as {actual_level}.")
                await ctx.send(f"{return_message} (verification failed, value is {actual_level}!)")
        else:
            await ctx.send(f"{return_message} (blind)")

    @commands.command(hidden=True)
    async def ban(self, ctx, user: discord.User, check: bool = True):
        author_level = await self.get_permission(ctx.author.id)
        user_level = await self.get_permission(user.id)
        if author_level < 8 or user_level >= author_level or ctx.author == user:
            return
        await self.set_permission(user.id, 0)
        return_message = f"Successfully banned {user}"
        if check:
            actual_level = await self.get_permission(user.id)
            if actual_level == 0:
                await ctx.send(f"{return_message} (successfully verified as being {actual_level})")
            else:
                self.bot.log.error(f"Tried to set perm level of {user.id} to 0 but value reads as {actual_level}.")
                await ctx.send(f"{return_message} (verification failed, value is {actual_level}!)")
        else:
            await ctx.send(f"{return_message} (blind)")


def setup(bot):
    bot.add_cog(PermManage(bot))
