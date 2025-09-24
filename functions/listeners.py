import discord
from discord.ext import commands

import traceback

from functions.functions import *

class handlerscog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.NotOwner):
           return
        elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title=f'{ctx.command.name}', 
                description=f'{emojis.reply}{ctx.command.description}',
                color=colors.main, 
                timestamp=discord.utils.utcnow())
            
            if ctx.command._buckets._cooldown:
               cooldown = ctx.command._buckets._cooldown
               cd_text = f'{round(cooldown.per)} second(s)'
            else:
               cd_text = 'None'

            if ctx.command.aliases:
               aliases = ', '.join(ctx.command.aliases)
            else:
               aliases = 'None'

            embed.add_field(name='Usage', value=f'{ctx.prefix}{ctx.command.usage}')
            embed.add_field(name='Cooldown', value=f'{cd_text}')
            embed.add_field(name='Aliases', value=f'{aliases}')
            embed.set_footer(text=f'{self.bot.user.name}', icon_url=f'{self.bot.user.avatar.url}')
            return await ctx.reply(embed=embed)
        elif isinstance(error, commands.CommandOnCooldown):
            time_remaining = error.retry_after
            minutes, seconds = divmod(int(time_remaining), 60)

            msg = await ctx.reply(f'{random.choice(gifs)} Too fast. Try again in {minutes}m {seconds}s')
            await msg.delete(delay=5)
        elif isinstance(error, commands.CommandInvokeError):
            traceback.print_exc()
            embed = discord.Embed(
                title=f'<:juiceL:1407602749851435059> wrld Collided',
                description=
                f'Please report this to `@purree`'
                f'\n\n**Error:** ```{error.original}```',
                color=colors.red,
                timestamp=discord.utils.utcnow())
            embed.set_footer(text=f'{self.bot.user.name}', icon_url=f'{self.bot.user.avatar.url}')
            msg = await ctx.reply(embed=embed)
        else:
            traceback.print_exc()
            embed = discord.Embed(title=f'Unexpected Error', description=f'wrld failed to handle this error.', color=colors.red)
            await ctx.reply(embed=embed)

    @commands.Cog.listener()
    async def on_error(self, event_method):
        print(f'Error in {event_method}')
        traceback.print_exc()

def setup(bot):
    bot.add_cog(handlerscog(bot))