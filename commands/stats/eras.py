import discord
from discord.ext import commands, bridge

from functions.functions import colors, loading, httpcall

class erascog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command(
        name='eras',
        description='List all eras',
        usage='eras',
        aliases=['era', 'eraslist']
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def eras(self, ctx):
        msg = await ctx.reply(embed=await loading('era'))
        api = await httpcall('https://juicewrldapi.com/juicewrld/eras/')
        embed = discord.Embed(title=':milky_way: Eras', color=colors.main)
        for era in api.get('results', []):
            if era.get('time_frame'):
                embed.add_field(name=f'__{era.get('name')}__', value=f'{era.get('description')}\n-# {era.get('time_frame')}', inline=True)

        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        await msg.edit(embed=embed)

    @bridge.bridge_command(
            name='albums', 
            description='List all albums', 
            usage='album'
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def album(self, ctx):
        msg = await ctx.reply(embed=await loading('album'))
        api = await httpcall('https://juicewrldapi.com/juicewrld/albums/')
        embed= discord.Embed(title=':cd: Albums', color=colors.main)
        for album in api.get('results', []):
            embed.add_field(name=f'__{album.get('title')}__', value=f'{album.get('description')}\n-# Released: {album.get('release_date')}', inline=False)

        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        await msg.edit(embed=embed)

def setup(bot):
    bot.add_cog(erascog(bot))