import discord
from discord.ext import commands

import random, io, contextlib, traceback, asyncio

from functions.functions import *

class OwnerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage='reload <cog>', description='Reloads a cog')
    @commands.is_owner()
    async def reload(self, ctx, cog):
        try:
            if cog.lower() == 'all':
                for ext in list(self.bot.extensions):
                    self.bot.reload_extension(ext)
                    print(f'reloaded {ext}')
                await ctx.reply(f'{random.choice(gifs)} reloaded all commands')
                return
            
            self.bot.reload_extension(cog)
            print(f'reloaded {cog}')
            await ctx.reply(f'{random.choice(gifs)} reloaded')
        except Exception as e:
            print(e)
            await ctx.reply(f'failed. ```{e}```')

    @commands.command(usage='disable <cog>', description='Disables a cog')
    @commands.is_owner()
    async def disable(self, ctx, cog):
        try:
            self.bot.unload_extension(cog)
            print(f'disabled {cog}')
            await ctx.reply(f'{random.choice(gifs)} disabled `{cog}`')
        except Exception as e:
            print(e)
            await ctx.reply(f'failed. ```{e}```')

    @commands.command(usage='enable <cog>', description='Enables a cog')
    @commands.is_owner()
    async def enable(self, ctx, cog):
        try:
            self.bot.load_extension(cog)
            print(f'enabled {cog}')
            await ctx.reply(f'{random.choice(gifs)} loaded `{cog}`')
        except Exception as e:
            print(e)
            await ctx.reply(f'failed. ```{e}```')

        
    @commands.command(
        aliases=['ss', 'status'], usage='setstatus <type: listening/playing/watching/streaming/custom> <text>', description='Sets the bots custom status')
    @commands.is_owner()
    async def setstatus(self, ctx, typ, *desc):
        if not typ or not desc:
            await ctx.reply(':x:')
        else:
            if typ.lower() == 'custom':
                desc = ' '.join(desc)
                await self.bot.change_presence(activity=discord.CustomActivity(name='Custom Status', state=f'{desc}'))
            else:
                desc = ' '.join(desc)
                await self.bot.change_presence(activity=discord.Activity(type=getattr(discord.ActivityType, typ), name=desc))

            await ctx.reply(':thumbsup:')

    @commands.command(usage='eval <func>', description='Runs the query')
    @commands.is_owner()
    async def eval(self, ctx, *, code):
        if code.startswith("```") and code.endswith("```"):
            code = code[3:-3]
            if code.startswith("python\n"):
                code = code[7:]
            elif code.startswith("py\n"):
                code = code[3:]
        
        env = {
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
            "discord": discord,
            "commands": commands
        }
        
        stdout = io.StringIO()
        
        try:
            with contextlib.redirect_stdout(stdout):
                exec(f"async def _eval_func():\n" + "\n".join(f"    {line}" for line in code.split("\n")), env)
                result = await env["_eval_func"]()
            
            output = stdout.getvalue()
            
            response = ""
            if output:
                response += f"```\n{output}\n```\n"
            if result is not None:
                response += f"```py\n{result}\n```"
            
            if not response:
                response = "✅ Executed successfully ```No Output```"
            
            await ctx.reply(response[:2000])
            
        except Exception as e:
            error = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            await ctx.reply(f"Error:\n```py\n{error[:1900]}\n```")

def setup(bot):
    bot.add_cog(OwnerCog(bot))
