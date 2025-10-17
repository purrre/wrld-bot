import discord
from discord.ext import commands, bridge

from functions.functions import colors, loading, httpcall
from functions.file_utils import SongButton, SnipButton

class filescog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _choose_song(self, msg, songs, button_type='mp3'):
        opts = [
            discord.SelectOption(
                label=s.get('name', 'Unknown')[:100],
                description=f"{s.get('original_key', 'N/A')} | {s.get('category', 'N/A').replace('_', ' ').title()}"[:100],
                value=str(s['public_id'])
            )
            for s in songs[:25]
        ]

        class SongSelect(discord.ui.Select):
            def __init__(self, songs_list):
                super().__init__(placeholder="Pick a song...", options=opts, min_values=1, max_values=1)
                self.songs = songs_list

            async def callback(self, interaction: discord.Interaction):
                await interaction.response.defer()
                chosen = next((s for s in self.songs if str(s['public_id']) == self.values[0]), None)
                if chosen:
                    await self.view.parent.send_embed(msg, interaction, chosen, button_type=button_type)

        view = discord.ui.View(timeout=None)
        view.parent = self
        view.add_item(SongSelect(songs))

        embed = discord.Embed(
            title="Multiple songs found",
            description="Please choose a song from the dropdown below.",
            color=colors.main
        )
        await msg.edit(embed=embed, view=view)

    async def _build_embed(self, song, snip=False):
        description = f"-# {song.get('category', 'N/A').replace('_', ' ').title()}\n\n"

        if not snip:
            description += (
                f"Length: {song.get('length', 'N/A')}\n"
                f"{song.get('leak_type', 'N/A')}"
            )
        else:
            preview = song.get('preview_date', 'N/A')
            preview = preview.replace("First Previewed", "First Previewed:")

            description += preview

        titles = [s for s in song.get('track_titles', []) if s != song.get('name')]

        embed = discord.Embed(
            title = f"**{song.get('name', 'Unknown')}{f' ({', '.join(titles[:2])})' if len(titles) > 1 else ''}**",
            description=description,
            color=colors.main
        )

        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)

        if song.get('image_url'):
            embed.set_thumbnail(url=song['image_url'])

        return embed

    async def send_embed(self, msg, ctx_or_inter, song, button_type='mp3'):
        embed = await self._build_embed(song, snip=(button_type == 'snip'))
        view = discord.ui.View(timeout=None)

        if button_type == 'mp3':
            view.add_item(SongButton(song['name'], song.get('file_names'), song.get('name', 'Unknown')))
        else:
            view.add_item(SnipButton(song['name'], song.get('file_names'), song.get('name', 'Unknown'), song.get('track_titles', [])))

        if isinstance(ctx_or_inter, discord.Interaction):
            if ctx_or_inter.response.is_done():
                await ctx_or_inter.edit_original_response(embed=embed, view=view)
            else:
                await ctx_or_inter.response.edit_message(embed=embed, view=view)
        else:
            await msg.edit(embed=embed, view=view)

    @bridge.bridge_command(aliases=['song'], usage='leak <song>', description='Get the MP3 for a track')
    @bridge.bridge_option(name='song', description='Song name', required=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def leak(self, ctx, *, song: str):
        msg = await ctx.reply(embed=await loading('song'))
        songs = await httpcall('https://juicewrldapi.com/juicewrld/songs/', params={'search': song})
        results = [s for s in songs.get('results', []) if s.get('category') not in ('unsurfaced', 'recording_session')]

        if not results:
            return await msg.edit(embed=discord.Embed(description="No songs found.", color=colors.main))
        if len(results) == 1:
            return await self.send_embed(msg, ctx, results[0], button_type='mp3')

        await self._choose_song(msg, results, button_type='mp3')

    @bridge.bridge_command(aliases=['snippet', 'snip'], usage='snippets <song>', description='Get snippet(s) for a track')
    @bridge.bridge_option(name='song', description='Song name', required=True)
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def snippets(self, ctx, *, song: str):
        msg = await ctx.reply(embed=await loading('snippet'))
        songs = await httpcall('https://juicewrldapi.com/juicewrld/songs/', params={'search': song})
        results = [s for s in songs.get('results', []) if s.get('category') == 'unsurfaced']

        if not results:
            return await msg.edit(embed=discord.Embed(description="No snippets found.", color=colors.main))
        if len(results) == 1:
            return await self.send_embed(msg, ctx, results[0], button_type='snip')

        await self._choose_song(msg, results, button_type='snip')


def setup(bot):
    bot.add_cog(filescog(bot))