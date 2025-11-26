import discord
from discord.ext import bridge, commands
import random

from functions.functions import colors, loading, cdict, httpcall, gifs, emojis, notfound_embed
from functions.file_utils import SongButton, SnipButton, SessionButton
from commands.info.eras import ErasCog



def build_embed(song: dict, bot_user: discord.User) -> discord.Embed:
    track_titles = song.get('track_titles', ['Unknown'])
    subtitle = ', '.join(track_titles[1:]) if len(track_titles) > 1 else ''

    embed = discord.Embed(
        title=f'{track_titles[0]}{f'\n({subtitle})' if subtitle else ''}',
        description=(
            f'-# Artists: {song.get('credited_artists', 'N/A')}\n'
            f'-# Producers: {song.get('producers', 'N/A')}\n'
            f'-# Engineers: {song.get('engineers', 'N/A')}\n'
            f'-# Era: {song.get('era', {}).get('name', 'Unknown')}'
        ),
        color=colors.main,
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
        ('Bitrate', 'bitrate'),
    ]

    for name, key in fields:
        value = song.get(key)
        if not value or value == 'N/A':
            continue
        if isinstance(value, list):
            value = ', '.join(str(v) for v in value if v)
        embed.add_field(name=name, value=value, inline=False)

    image_url = song.get('image_url')
    if image_url:
        full_url = f'https://juicewrldapi.com{image_url}'
        embed.set_thumbnail(url=full_url)
        embed.set_author(
            name=song.get('category', 'Unknown').replace('_', ' ').title(),
            icon_url=full_url,
        )

    embed.set_footer(text=bot_user.name, icon_url=bot_user.avatar.url)
    return embed


def add_media_buttons(view: discord.ui.View, song: dict):
    category = (song.get('category') or '').lower()
    name = song.get('name', 'Unknown')
    filename = song.get('file_names')
    track_titles = song.get('track_titles', [])

    if category == 'unsurfaced':
        view.add_item(SnipButton(song))
    elif category == 'recording_session':
        view.add_item(SessionButton(song))
    else:
        view.add_item(SongButton(song))

class SongSelect(discord.ui.Select):
    def __init__(self, songs: list[dict], bot, user_id: int):
        self.bot = bot
        self.songs = songs
        self.user_id = int(user_id)

        options = []
        for song in songs[:25]:
            name = song.get('name', 'Unknown')
            track_titles = song.get('track_titles') or []
            aka = [t for t in track_titles if t != name][:2]
            desc = (', '.join(aka) + ' | ' if aka else '') + song.get('category', 'N/A').replace('_', ' ').title()

            options.append(discord.SelectOption(label=name, description=desc, value=str(song['public_id'])))

        super().__init__(placeholder='Choose a song...', options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(f"This isn't for you {random.choice(gifs)}", ephemeral=True)

        await interaction.response.defer()

        song_id = self.values[0]
        success, song_data = await httpcall(f'https://juicewrldapi.com/juicewrld/songs/{song_id}/')
        if not success:
            return await interaction.followup.send(embed=song_data, ephemeral=True)

        song = cdict(song_data)
        embed = build_embed(song, self.bot)
        view = discord.ui.View(timeout=None)
        view.add_item(SongSelect(self.songs, self.bot, self.user_id))
        add_media_buttons(view, song)
        await interaction.edit_original_response(embed=embed, view=view)


class SongView(discord.ui.View):
    def __init__(self, songs: list[dict], bot, user_id: int):
        super().__init__(timeout=None)
        self.add_item(SongSelect(songs, bot, user_id))


class SearchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command(
        description='Get information related to a track',
        usage='info <song>',
        aliases=['songinfo', 'sinfo', 'track', 'search'],
    )
    @bridge.bridge_option(name='song', description='Name of the song to search for', required=True)
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def info(self, ctx, *, song: str):
        msg = await ctx.reply(embed=await loading('song'))
        success, data = await httpcall('https://juicewrldapi.com/juicewrld/songs/', params={'search': song})
        if not success:
            return await msg.edit(embed=data)

        if not data or data.get('count', 0) == 0:
            return await msg.edit(embed=notfound_embed(song))

        results = data['results']
        if len(results) == 1:
            song_dict = cdict(results[0])
            embed = build_embed(song_dict, self.bot.user)
            view = discord.ui.View(timeout=None)
            add_media_buttons(view, song_dict)
            return await msg.edit(embed=embed, view=view)

        embed = discord.Embed(
            title='Multiple songs found',
            description='Please choose a song from the dropdown below.',
            color=colors.main,
        )
        await msg.edit(embed=embed, view=SongView(results, self.bot.user, ctx.author.id))

    @bridge.bridge_command(
        description='Fetch a random Juice track',
        usage='random',
        aliases=['r', 'randomsong'],
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def random(self, ctx):
        msg = await ctx.reply(embed=await loading('song'))
        success, song = await httpcall('https://juicewrldapi.com/juicewrld/radio/random/')
        
        if not success or not song.get('title'):
            return await msg.edit(embed=discord.Embed(description='Failed to fetch a random song :(', color=colors.red))

        song_dict = cdict(song.get('song'))
        embed = build_embed(song_dict, self.bot.user)
        view = discord.ui.View(timeout=None)
        add_media_buttons(view, song_dict)

        await msg.edit(embed=embed, view=view)


    @bridge.bridge_command(
        description='Get a list of songs by a specific producer',
        usage='prod <producer>',
        aliases=['prodsearch', 'producersearch', 'prodby', 'ps'],
    )
    @bridge.bridge_option(name='producer', description='Name of the producer to search for', required=True)
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def prod(self, ctx, *, producer: str):
        msg = await ctx.reply(embed=await loading('producer'))
        success, data = await httpcall(
            'https://juicewrldapi.com/juicewrld/songs/',
            params={'searchall': producer}, 
            paginate=True
        )
        if not success:
            return await msg.edit(embed=data)
        
        results = [s for s in data if producer.lower() not in s.get('name', '').lower()]

        if not results:
            return await msg.edit(embed=discord.Embed(
                description=f'No songs found produced by `{producer}`.',
                color=colors.main
            ))

        page_size = 6
        pages = [results[i:i + page_size] for i in range(0, len(results), page_size)]

        def make_embed(page_items, page_idx, total_pages):
            embed = discord.Embed(
                title=f'Songs Produced by {producer.title()}',
                description=f'Songs Found: {len(results)}',
                color=colors.main,
            )
            for song in page_items:
                track_titles = song.get('track_titles', ['Unknown'])
                embed.add_field(
                    name=f'╭─ __{song.get('name', 'Unknown')}__',
                    value=(
                        (
                            f'├ AKA: `{', '.join(track_titles[1:])}`\n'
                            if len(track_titles) > 1 else ''
                        )
                        + f'├ Category: {song.get('category', 'N/A').replace('_', ' ').title()}\n'
                        + f'├ Era: {song.get('era', {}).get('name', 'N/A')}\n'
                        + f'└─ Type: {song.get('leak_type', 'N/A')}'
                    ),
                    inline=False,
                )
            embed.set_footer(
                text=f'{self.bot.user.name} • Page {page_idx + 1}/{total_pages}',
                icon_url=self.bot.user.avatar.url,
            )
            return embed

        pager = ErasCog.Pager(
            self.bot.user,
            ctx.author,
            lambda bot_user, items, idx, total: make_embed(items, idx, total),
            pages
        )
        song_select = SongSelect(results, self.bot.user, ctx.author.id)

        async def dropdown_callback(interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                return await interaction.response.send_message(
                    f"This isn't for you {random.choice(gifs)}", ephemeral=True
                )

            await interaction.response.defer()
            song_id = song_select.values[0]
            success, song_data = await httpcall(f'https://juicewrldapi.com/juicewrld/songs/{song_id}/')
            if not success:
                return await interaction.followup.send(embed=song_data, ephemeral=True)
            song = cdict(song_data)

            embed = build_embed(song, self.bot.user)
            view = discord.ui.View(timeout=None)
            add_media_buttons(view, song)
            await interaction.edit_original_response(embed=embed, view=view)

        song_select.callback = dropdown_callback
        prev, next = pager.children[0], pager.children[1]

        pager.clear_items()
        pager.add_item(song_select)
        pager.add_item(prev)
        pager.add_item(next)

        await msg.edit(embed=make_embed(pages[0], 0, len(pages)), view=pager)


def setup(bot):
    bot.add_cog(SearchCog(bot))
