import discord
from discord.ext import commands, bridge
import random
import re
from datetime import datetime

from functions.functions import colors, loading, httpcall, gifs


class ErasCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache = {}

    @staticmethod
    def parse_date_key(time_frame: str) -> str:
        s = (time_frame or '').strip().strip('()')
        parts = [p.strip() for p in re.split(r'[\-]', s, maxsplit=1)]
        start = parts[0] if parts else ''
        for fmt in ('%B %Y', '%b %Y', '%Y-%m-%d', '%Y-%m', '%Y'):
            try:
                dt = datetime.strptime(start, fmt)
                return f'{dt.year:04d}-{dt.month:02d}-{getattr(dt, "day", 1):02d}'
            except ValueError:
                continue
        m = re.search(r'(\d{4})', start)
        if m:
            return f'{int(m.group(1)):04d}-12-31'
        return '9999-12-31'

    @staticmethod
    def chunk(items, size):
        return [items[i:i + size] for i in range(0, len(items), size)]

    @staticmethod
    def make_eras_embed(bot_user, items, index, total):
        embed = discord.Embed(title='🌌 Eras', color=colors.main)
        for i, era in enumerate(items, start=index * 9 + 1):
            embed.add_field(
                name=f'{i}. __{era.get('name', 'Unknown')}__',
                value=f'{era.get('description', 'No description.')}\n-# {era.get('time_frame', 'N/A')}',
                inline=True,
            )
        embed.set_thumbnail(url=bot_user.avatar.url)
        embed.set_footer(text=f'{bot_user.name} • Page {index + 1}/{total}', icon_url=bot_user.avatar.url)
        return embed

    @staticmethod
    def make_albums_embed(bot_user, items, index, total):
        embed = discord.Embed(title='💿 Albums', color=colors.main)
        for album in items:
            embed.add_field(
                name=f'__{album.get('title', 'Unknown')}__',
                value=f'{album.get('description', 'No description.')}\n-# Released: {album.get('release_date', 'N/A')}',
                inline=False,
            )
        embed.set_thumbnail(url=bot_user.avatar.url)
        embed.set_footer(text=f'{bot_user.name} • Page {index + 1}/{total}', icon_url=bot_user.avatar.url)
        return embed

    async def get_cached(self, ctx, key, url):
        if key not in self.cache:
            success, data = await httpcall(url, paginate=True)
            
            if not success:
                await ctx.reply(embed=data)
                self.cache[key] = {} 
                return {}
            
            self.cache[key] = data
            
        return self.cache[key]

    class Pager(discord.ui.View):
        def __init__(self, bot_user, author, make_embed, pages):
            super().__init__(timeout=60)
            self.bot_user = bot_user
            self.author = author
            self.make_embed = make_embed
            self.pages = pages
            self.index = 0

        async def interaction_check(self, interaction):
            if interaction.user.id != self.author.id:
                await interaction.response.send_message(
                    f"This isn't for you {random.choice(gifs)}", ephemeral=True
                )
                return False
            return True

        async def update(self, interaction):
            embed = self.make_embed(self.bot_user, self.pages[self.index], self.index, len(self.pages))
            try:
                await interaction.response.edit_message(embed=embed)
            except discord.errors.InteractionResponded:
                await interaction.edit_original_response(embed=embed)

        @discord.ui.button(label='🡰', style=discord.ButtonStyle.gray)
        async def previous(self, _, interaction: discord.Interaction):
            self.index = (self.index - 1) % len(self.pages)
            await self.update(interaction)

        @discord.ui.button(label='🡲', style=discord.ButtonStyle.gray)
        async def next(self, _, interaction: discord.Interaction):
            self.index = (self.index + 1) % len(self.pages)
            await self.update(interaction)

    @bridge.bridge_command(
        description='List all eras in order',
        aliases=['era', 'eraslist'],
        usage='eras')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def eras(self, ctx):
        msg = await ctx.reply(embed=await loading('era'))
        data = await self.get_cached(ctx, 'eras', 'https://juicewrldapi.com/juicewrld/eras/')
        
        if not data:
            await msg.delete()
            return

        eras = [e for e in data if e.get('time_frame')]
        eras.sort(key=lambda e: self.parse_date_key(e.get('time_frame')))
        pages = self.chunk(eras, 9) or [[]]

        embed = self.make_eras_embed(self.bot.user, pages[0], 0, len(pages))
        view = self.Pager(self.bot.user, ctx.author, self.make_eras_embed, pages)
        await msg.edit(embed=embed, view=view)

    @bridge.bridge_command(
        description='List all albums in order', 
        aliases=['album'],
        usage='albums')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def albums(self, ctx):
        msg = await ctx.reply(embed=await loading('album'))
        data = await self.get_cached(ctx, 'albums', 'https://juicewrldapi.com/juicewrld/albums/')
        
        if not data:
            await msg.delete()
            return
            
        data.sort(key=lambda a: a.get('release_date') or '9999-99-99')
        pages = self.chunk(data, 5) or [[]]

        embed = self.make_albums_embed(self.bot.user, pages[0], 0, len(pages))
        view = self.Pager(self.bot.user, ctx.author, self.make_albums_embed, pages)
        await msg.edit(embed=embed, view=view)


def setup(bot):
    bot.add_cog(ErasCog(bot))