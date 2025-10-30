import discord
from discord.ext import commands, bridge

from functions.functions import colors, loading, httpcall
from functions.file_utils import SongButton, SnipButton, SessionButton

class filescog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _choose_song(self, msg, songs, button_type='mp3'):
        opts = [
            discord.SelectOption(
                label=s.get('name', 'Unknown')[:100],
                description=(
                    (', '.join([t for t in (s.get('track_titles') or []) if t != s.get('name')][:2]) + ' | ' 
                    if [t for t in (s.get('track_titles') or []) if t != s.get('name')][:2] 
                    else '') +
                    s.get('category', 'N/A').replace('_', ' ').title()
                ),
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

#need to redo this function eventually
    async def _build_embed(self, song, snip=False, session=False):
        description = f"-# {song.get('category', 'N/A').replace('_', ' ').title()}\n\n"

        if session:
            description += song.get('session_tracking', 'N/A')
        elif snip:
            preview = song.get('preview_date', 'N/A')
            preview = preview.replace("First Previewed", "First Previewed:")
            description += preview
        else:
            description += (
                f"Length: {song.get('length', 'N/A')}\n"
                f"{song.get('leak_type', 'N/A')}"
            )

        titles = [s for s in song.get('track_titles', []) if s != song.get('name')]

        embed = discord.Embed(
            title=f"**{song.get('name', 'Unknown')}{f' ({', '.join(titles[:2])})' if len(titles) >= 1 else ''}**",
            description=description,
            color=colors.main
        )

        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)

        if song.get('image_url'):
            embed.set_thumbnail(url=f"https://juicewrldapi.com{song['image_url']}")

        return embed

    async def send_embed(self, msg, ctx_or_inter, song, button_type='mp3'):
        embed = await self._build_embed(
            song,
            snip=(button_type == 'snip'),
            session=(button_type == 'session')
        )
        view = discord.ui.View(timeout=None)

        if button_type == 'mp3':
            view.add_item(SongButton(
                song['name'],
                song.get('file_names'),
                song.get('name', 'Unknown'),
                (song.get('era') or {}).get('name')
            ))
        elif button_type == 'snip':
            view.add_item(SnipButton(song['name'], song.get('file_names'), song.get('name', 'Unknown'), song.get('track_titles', [])))
        elif button_type == 'session':
            view.add_item(SessionButton(song['name'], song.get('file_names'), song.get('name', 'Recording Session')))

        if isinstance(ctx_or_inter, discord.Interaction):
            if ctx_or_inter.response.is_done():
                await ctx_or_inter.edit_original_response(embed=embed, view=view)
            else:
                await ctx_or_inter.response.edit_message(embed=embed, view=view)
        else:
            await msg.edit(embed=embed, view=view)

    @bridge.bridge_command(aliases=['song'], usage='leak <song>', description='Get the audio file for a track')
    @bridge.bridge_option(name='song', description='Song name', required=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def leak(self, ctx, *, song: str):
        msg = await ctx.reply(embed=await loading('song'))
        songs = await httpcall('https://juicewrldapi.com/juicewrld/songs/', params={'search': song})
        results = [s for s in songs.get('results', []) if s.get('category') not in ('unsurfaced', 'recording_session')]

        if not results:
            return await msg.edit(embed=discord.Embed(
                description="No mp3 or wav found :(", 
                color=colors.main,
                footer=discord.EmbedFooter(text='Note: Only surfaced songs are available.')))
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
            return await msg.edit(embed=discord.Embed(
                description="No snippets found :(", 
                color=colors.main,
                footer=discord.EmbedFooter(text='Note: Only unsurfaced songs are available.')))
        if len(results) == 1:
            return await self.send_embed(msg, ctx, results[0], button_type='snip')

        await self._choose_song(msg, results, button_type='snip')

    @bridge.bridge_command(aliases=['session', 'rs'], usage='sessions <song>', description='Get the recording session for a track')
    @bridge.bridge_option(name='session', description='Session name', required=True)
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def sessions(self, ctx, *, session: str):
        msg = await ctx.reply(embed=await loading('session'))
        songs = await httpcall('https://juicewrldapi.com/juicewrld/songs/', params={'search': session})
        results = [s for s in songs.get('results', []) if s.get('category') == 'recording_session']

        if not results:
            return await msg.edit(embed=discord.Embed(
                description="No session found :(", 
                color=colors.main))
        if len(results) == 1:
            return await self.send_embed(msg, ctx, results[0], button_type='session')

        await self._choose_song(msg, results, button_type='session')


def setup(bot):
    bot.add_cog(filescog(bot))