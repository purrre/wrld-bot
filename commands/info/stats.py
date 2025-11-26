import discord
from discord.ext import bridge, commands

from functions.functions import *

class StatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command(
        usage='stats',
        description='Get song & era statistics')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stats(self, ctx):
        msg = await ctx.reply(embed=await loading('song'))
        try:
            success, stats = await httpcall('https://juicewrldapi.com/juicewrld/stats/')
            if not success:
                return await msg.edit(embed=stats)

            categories = '\n'.join(f'**{key.replace('_', ' ').title()}:** {value}' for key, value in stats['category_stats'].items())
            sorted_eras = sorted(stats['era_stats'].items(), key=lambda x: x[1], reverse=True)
            eras = '\n'.join(f'**{k.replace("_", " ").title()}:** {v}' for k, v in sorted_eras)

            embed = discord.Embed(title=f'Total Songs: {stats['total_songs']}', 
                                  color=colors.main)
            embed.add_field(name='🌌 __Eras__', value=eras, inline=True)
            embed.add_field(name='📁 __Categories__', value=categories, inline=True)
            embed.set_author(name='🎸 Song Statistics')
            embed.set_footer(icon_url=self.bot.user.avatar.url, text=self.bot.user.display_name)
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            await msg.edit(embed=embed)

        except Exception as e:
            print(f'Error while fetching stats: {e}')
            traceback.print_exc()
            await msg.edit(content='Failed to complete request :(')

def setup(bot):
    bot.add_cog(StatsCog(bot))