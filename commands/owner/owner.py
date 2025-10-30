import discord
from discord.ext import commands

import random

from functions.functions import *

class ownercog(commands.Cog):
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

        
    @commands.command(aliases=['ss', 'status'], usage='setstatus <type: listening/playing/watching/streaming/custom> <text>', description='Sets the bots custom status')
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

def setup(bot):
    bot.add_cog(ownercog(bot))