import discord
from discord.ext import bridge, commands

import random

from functions.functions import colors, loading, cdict, httpcall, gifs
from functions.file_utils import SongButton, SnipButton, SessionButton, fetch_urls


def build_embed(data: dict, bot):
    track_titles = data.get('track_titles', ['Unknown'])
    embed = discord.Embed(
        title=f'{track_titles[0]}\n{', '.join(track_titles[1:])}',
        description=(
            f'-# Artists: {data.get('credited_artists', 'N/A')}\n'
            f'-# Producers: {data.get('producers', 'N/A')}\n'
            f'-# Engineers: {data.get('engineers', 'N/A')}\n'
            f'-# Era: {data.get('era', {}).get('name', 'Unknown')}'
        ),
        color=colors.main
    )

    fields = [
        ('File Names', 'file_names'),
        ('Instrumental Names', 'instrumental_names'),
        ('Session', 'session_titles'),
        ('Recording Locations', 'recording_locations'),
        ('Vocals', 'record_dates'),
        ('Preview', 'preview_date'),
        ('Release', 'release_date'),
        ('Dates', 'dates'),
        ('Length', 'length'),
        ('Leak', 'date_leaked'),
        ('Category / Type', 'leak_type'),
    ]

    for name, key in fields:
        value = data.get(key)
        if value and value != 'N/A':
            if isinstance(value, list):
                value = ', '.join(str(v) for v in value if v)
            embed.add_field(name=name, value=value, inline=False)

    if image_url := data.get('image_url'):
        embed.set_thumbnail(url=f'https://juicewrldapi.com{image_url}')
        embed.set_author(
            name=' '.join(data.get('category', 'unknown').replace('_', ' ').title().split()),
            icon_url=f'https://juicewrldapi.com{image_url}'
        )
    embed.set_footer(text=bot.name, icon_url=bot.avatar.url)
    return embed


def _add_media_buttons(view: discord.ui.View, song: dict):
    category = song.get('category', '').lower()
    name = song.get('name', 'Unknown')
    filename = song.get('file_names')
    track_titles = song.get('track_titles', [])

    if category == 'unsurfaced':
        view.add_item(SnipButton(name, filename, title='Snippets', track_titles=track_titles))
    elif category == 'recording_session':
        view.add_item(SessionButton(name, filename, title=name))
    else:
        view.add_item(SongButton(name, filename, title=name))


class SongSelect(discord.ui.Select):
    def __init__(self, songs: list[dict], bot, user_id):
        self.bot = bot
        self.songs = songs
        options = [
            discord.SelectOption(
                label=song.get('name', 'Unknown'),
                description=(
                    (', '.join([t for t in (song.get('track_titles') or []) if t != song.get('name')][:2]) + ' | ' 
                    if [t for t in (song.get('track_titles') or []) if t != song.get('name')][:2] 
                    else '') +
                    song.get('category', 'N/A').replace('_', ' ').title()
                ),
                value=str(song['public_id'])
            )
            for song in songs[:25]
        ]

        super().__init__(placeholder='Choose a song...', max_values=1, min_values=1, options=options)
        self.user_id = int(user_id)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(f'This is not for you {random.choice(gifs)}', ephemeral=True)
        
        await interaction.response.defer()

        song_id = self.values[0]
        song_data = await httpcall(f'https://juicewrldapi.com/juicewrld/songs/{song_id}/')
        song_dict = cdict(song_data)

        embed = build_embed(song_dict, self.bot)
        view = discord.ui.View(timeout=None)
        view.add_item(SongSelect(self.songs, self.bot, self.user_id))
        _add_media_buttons(view, song_dict)
        await interaction.edit_original_response(embed=embed, view=view)


class SongView(discord.ui.View):
    def __init__(self, songs: list[dict], bot, user_id):
        super().__init__(timeout=None)
        self.add_item(SongSelect(songs, bot, user_id))


class searchcog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command(
        usage='info <song>',
        aliases=['songinfo', 'sinfo', 'track'],
        description='Search for a song and return information about it'
    )
    @bridge.bridge_option(name='song', description='Name of the song to search for', required=True)
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def info(self, ctx, *, song: str):
        msg = await ctx.reply(embed=await loading('song'))
        songs = await httpcall(
            f'https://juicewrldapi.com/juicewrld/songs/',
            params={'search': song}
        )

        if songs['count'] == 0:
            await msg.edit(embed=discord.Embed(description='No songs found.', color=colors.main))
        elif songs['count'] == 1:
            song_dict = cdict(songs['results'][0])
            embed = build_embed(song_dict, self.bot.user)
            view = discord.ui.View(timeout=None)
            view.add_item(SongSelect([song_dict], self.bot.user, ctx.author.id))
            _add_media_buttons(view, song_dict)
            await msg.edit(embed=embed, view=view)
        else:
            embed = discord.Embed(
                title='Multiple songs found',
                description='Please choose a song from the dropdown below.',
                color=colors.main
            )
            await msg.edit(embed=embed, view=SongView(songs['results'], self.bot.user, ctx.author.id))

    @bridge.bridge_command(
        usage='random',
        aliases=['r', 'randomsong'],
        description='Fetch a random song'
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def random(self, ctx):
        msg = await ctx.reply(embed=await loading('song'))
        song = await httpcall('https://juicewrldapi.com/juicewrld/radio/random/')
        if not song or not song.get('title'):
            return await msg.edit(embed=discord.Embed(
                description='Failed to fetch a random song :(',
                color=colors.red))

        title = song['title']
        search = await httpcall(
            'https://juicewrldapi.com/juicewrld/songs/',
            params={'search': title}
        )

        if not search or search.get('count', 0) == 0:
            return await msg.edit(embed=discord.Embed(
                description=f'Failed :(',
                color=colors.red))

        if search.get('count', 0) > 1:
            song_dict = cdict(random.choice(search['results']))
        else:
            song_dict = cdict(search['results'][0])

        embed = build_embed(song_dict, self.bot.user)
        view = discord.ui.View(timeout=None)
        _add_media_buttons(view, song_dict)

        await msg.edit(embed=embed, view=view)


def setup(bot):
    bot.add_cog(searchcog(bot))