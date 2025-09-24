import discord
from discord.ext import commands, bridge

from functions.functions import colors, loading, httpcall
from functions.file_utils import SongButton, SnipButton, fetch_urls


class Files(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _choose_song(self, ctx_or_msg, songs):
        options = [
            discord.SelectOption(
                label=s.get('name', 'Unknown')[:100],
                description=f"{s.get('original_key', 'N/A')} | {s.get('category', 'N/A').replace('_', ' ').title()}"[:100],
                value=str(s['public_id'])
            )
            for s in songs[:25]
        ]

        class SongSelect(discord.ui.Select):
            def __init__(self, songs_list):
                super().__init__(placeholder='Choose a song...', options=options, max_values=1, min_values=1)
                self.songs_list = songs_list

            async def callback(self, interaction: discord.Interaction):
                await interaction.response.defer()
                selected = next((s for s in self.songs_list if str(s['public_id']) == self.values[0]), None)
                if selected:
                    await self.view.parent.send_embed(interaction.message, interaction, selected)

        view = discord.ui.View(timeout=None)
        view.parent = self
        view.add_item(SongSelect(songs))
        embed = discord.Embed(
            title='Multiple songs found',
            description='Please choose a song from the dropdown below.',
            color=colors.main
        )
        await ctx_or_msg.edit(embed=embed, view=view)

    async def _build_embed(self, song_data):
        embed = discord.Embed(
            title=song_data.get('name', 'Unknown'),
            description=(
                f"Category: {song_data.get('category', 'N/A').replace('_', ' ').title()}\n"
                f"Length: {song_data.get('length', 'N/A')}"
            ),
            color=colors.main
        )
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
        if image := song_data.get('image_url'):
            embed.set_thumbnail(url=image)
        return embed

    async def send_embed(self, msg, ctx_or_interaction, song_data, button_type='mp3'):
        embed = await self._build_embed(song_data)
        view = discord.ui.View(timeout=None)

        if button_type == 'mp3':
            view.add_item(SongButton(song_data['name'], song_data.get('file_names'), song_data.get('name', 'Unknown')))
        elif button_type == 'snip':
            view.add_item(SnipButton(
                song_data['name'],
                song_data.get('file_names'),
                song_data.get('name', 'Unknown'),
                song_data.get('track_titles', [])
            ))

        if isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.response.edit_message(embed=embed, view=view)
        else:
            await msg.edit(embed=embed, view=view)

    @bridge.bridge_command(
        aliases=['song'],
        usage='leak <song>',
        description='Fetches the mp3 for a track'
    )
    @bridge.bridge_option(name='song', description='Name of the song to search for', required=True)
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def leak(self, ctx, *, song: str):
        msg = await ctx.reply(embed=await loading('song'))
        songs = await httpcall('https://juicewrldapi.com/juicewrld/songs/', params={'search': song})
        results = [s for s in songs.get('results', []) if s.get('category') not in ('unsurfaced', 'recording_session')]

        if not results:
            await msg.edit(embed=discord.Embed(description='No songs found.', color=colors.main))
        elif len(results) == 1:
            await self.send_embed(msg, ctx, results[0], button_type='mp3')
        else:
            await self._choose_song(msg, results, send_embed_callback=lambda s: self.send_embed(msg, ctx, s, button_type='mp3'))

    @bridge.bridge_command(
        aliases=['snippet', 'snip'],
        usage='snippets <song>',
        description='Fetches the snippet(s) for a track (unsurfaced only)'
    )
    @bridge.bridge_option(name='song', description='Name of the song to search for', required=True)
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def snippets(self, ctx, *, song: str):
        msg = await ctx.reply(embed=await loading('song'))
        songs = await httpcall('https://juicewrldapi.com/juicewrld/songs/', params={'search': song})
        results = [s for s in songs.get('results', []) if s.get('category') == 'unsurfaced']

        if not results:
            await msg.edit(embed=discord.Embed(description='No songs found.', color=colors.main))
        elif len(results) == 1:
            await self.send_embed(msg, ctx, results[0], button_type='snip')
        else:
            await self._choose_song(msg, results, send_embed_callback=lambda s: self.send_embed(msg, ctx, s, button_type='snip'))


def setup(bot):
    bot.add_cog(Files(bot))