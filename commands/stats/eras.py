import discord
from discord.ext import commands, bridge

import random

from functions.functions import colors, loading, httpcall, gifs

class erascog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache = {}

    def _era_sort_key(self, time_frame):
        import re
        from datetime import datetime
        s = (time_frame or '').strip().strip('()')
        parts = [p.strip() for p in re.split(r'[\-–]', s, maxsplit=1)]
        start = parts[0] if parts else ''
        for fmt in ("%B %Y", "%b %Y", "%Y-%m-%d", "%Y-%m", "%Y"):
            try:
                dt = datetime.strptime(start, fmt)
                return f"{dt.year:04d}-{dt.month:02d}-{getattr(dt, 'day', 1):02d}"
            except:
                pass
        m = re.search(r"(\d{4})", start)
        if m:
            return f"{int(m.group(1)):04d}-12-31"
        return '9999-12-31'

    def _chunk(self, items, size):
        return [items[i:i + size] for i in range(0, len(items), size)]

    def _build_eras_embed(self, bot_user, page_items, page_idx, total_pages):
        embed = discord.Embed(title=':milky_way: Eras', color=colors.main)
        for i, era in enumerate(page_items, start=page_idx * 9 + 1):
            embed.add_field(
                name=f"{i}. __{era.get('name')}__",
                value=f"{era.get('description')}\n-# {era.get('time_frame')}",
                inline=True
            )
        embed.set_footer(text=f"{bot_user.name} • Page {page_idx + 1}/{total_pages}", icon_url=bot_user.avatar.url)
        embed.set_thumbnail(url=bot_user.avatar.url)
        return embed

    def _build_albums_embed(self, bot_user, page_items, page_idx, total_pages):
        embed = discord.Embed(title=':cd: Albums', color=colors.main)
        for album in page_items:
            embed.add_field(
                name=f"__{album.get('title')}__",
                value=f"{album.get('description')}\n-# Released: {album.get('release_date')}",
                inline=False
            )
        embed.set_footer(text=f"{bot_user.name} • Page {page_idx + 1}/{total_pages}", icon_url=bot_user.avatar.url)
        embed.set_thumbnail(url=bot_user.avatar.url)
        return embed

    class Pager(discord.ui.View):
        def __init__(self, bot_user, author, make_embed, pages):
            super().__init__(timeout=60)
            self.bot_user = bot_user
            self.author = author
            self.make_embed = make_embed
            self.pages = pages
            self.i = 0

        async def interaction_check(self, interaction):
            if interaction.user.id != self.author.id:
                await interaction.response.send_message(
                    f'This is not for you {random.choice(gifs)}', ephemeral=True
                )
                return False
            return True

        async def render(self, interaction):
            try:
                await interaction.response.edit_message(embed=self.make_embed(self.bot_user, self.pages[self.i], self.i, len(self.pages)))
            except discord.errors.InteractionResponded:
                await interaction.edit_original_response(embed=self.make_embed(self.bot_user, self.pages[self.i], self.i, len(self.pages)))


        @discord.ui.button(label='Previous', style=discord.ButtonStyle.gray)
        async def prev(self, _, interaction: discord.Interaction):
            self.i = (self.i - 1) % len(self.pages)
            await self.render(interaction)

        @discord.ui.button(label='Next', style=discord.ButtonStyle.gray)
        async def next(self, _, interaction: discord.Interaction):
            self.i = (self.i + 1) % len(self.pages)
            await self.render(interaction)

    async def _get_cached(self, key, url):
        if key not in self.cache:
            self.cache[key] = await httpcall(url)
        return self.cache[key]

    @bridge.bridge_command(name='eras', description='List all eras', aliases=['era', 'eraslist'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def eras(self, ctx):
        msg = await ctx.reply(embed=await loading('era'))
        api = await self._get_cached('eras', 'https://juicewrldapi.com/juicewrld/eras/')
        eras = [e for e in api.get('results', []) if e.get('time_frame')]
        eras.sort(key=lambda e: self._era_sort_key(e.get('time_frame')))
        pages = self._chunk(eras, 9) or [[]]
        make_embed = self._build_eras_embed
        await msg.edit(embed=make_embed(self.bot.user, pages[0], 0, len(pages)), view=self.Pager(self.bot.user, ctx.author, make_embed, pages))

    @bridge.bridge_command(name='albums', description='List all albums', aliases=['album'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def albums(self, ctx):
        msg = await ctx.reply(embed=await loading('album'))
        api = await self._get_cached('albums', 'https://juicewrldapi.com/juicewrld/albums/')
        albums = api.get('results', [])
        albums.sort(key=lambda a: (a.get('release_date') or '9999-99-99'))
        pages = self._chunk(albums, 5) or [[]]
        make_embed = self._build_albums_embed
        await msg.edit(embed=make_embed(self.bot.user, pages[0], 0, len(pages)), view=self.Pager(self.bot.user, ctx.author, make_embed, pages))

def setup(bot):
    bot.add_cog(erascog(bot))