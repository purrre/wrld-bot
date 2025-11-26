import discord
from discord.ext import bridge, commands
import random

from functions.functions import colors, loading, httpcall, gifs
from functions.file_utils import SongButton, SnipButton, SessionButton
from commands.info.eras import ErasCog
from commands.files.search import SongSelect, SongView


class FilesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def build_embed(self, song, snip=False, session=False):
        description = f"-# {song.get('category', 'N/A').replace('_', ' ').title()}\n\n"
        if session:
            description += song.get('session_tracking', 'N/A')
        elif snip:
            preview = song.get('preview_date', 'N/A')
            description += preview
        else:
            description += f"Length: {song.get('length', 'N/A')}\n>>> {song.get('leak_type', 'N/A')}"

        titles = [t for t in song.get('track_titles', []) if t != song.get('name')]
        embed = discord.Embed(
            title=f"**{song.get('name', 'Unknown')}{f' ({', '.join(titles[:2])})' if titles else ''}**",
            description=description,
            color=colors.main
        )

        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
        if song.get('image_url'):
            embed.set_thumbnail(url=f'https://juicewrldapi.com{song["image_url"]}')
        return embed

    async def send_embed(self, msg, ctx_or_inter, song, button_type='mp3'):
        embed = await self.build_embed(song, snip=(button_type=='snip'), session=(button_type=='session'))
        view = discord.ui.View(timeout=None)

        if button_type == 'mp3':
            view.add_item(SongButton(song))
        elif button_type == 'snip':
            view.add_item(SnipButton(song))
        elif button_type == 'session':
            view.add_item(SessionButton(song))

        if isinstance(ctx_or_inter, discord.Interaction):
            if ctx_or_inter.response.is_done():
                await ctx_or_inter.edit_original_response(embed=embed, view=view)
            else:
                await ctx_or_inter.response.edit_message(embed=embed, view=view)
        else:
            await msg.edit(embed=embed, view=view)

    async def multi_choice(self, msg, songs, ctx_or_inter, button_type='mp3'):
        view = SongView(songs, self.bot.user, ctx_or_inter.author.id if hasattr(ctx_or_inter, 'author') else ctx_or_inter.user.id)

        for item in view.children:
            if isinstance(item, SongSelect):
                async def dropdown_callback(interaction: discord.Interaction, item=item):
                    if interaction.user.id != (ctx_or_inter.author.id if hasattr(ctx_or_inter, 'author') else ctx_or_inter.user.id):
                        return await interaction.response.send_message(f"This isn't for you {random.choice(gifs)}", ephemeral=True)
                    await interaction.response.defer()
                    song_id = item.values[0]
                    success, song_data = await httpcall(f'https://juicewrldapi.com/juicewrld/songs/{song_id}/')
                    if not success:
                        return await interaction.followup.send(embed=song_data, ephemeral=True)
                    await self.send_embed(msg, interaction, song_data, button_type=button_type)
                item.callback = dropdown_callback

        embed = discord.Embed(
            title='Multiple songs found',
            description='Please choose a song from the dropdown below.',
            color=colors.main
        )
        await msg.edit(embed=embed, view=view)

    @bridge.bridge_command(
        aliases=['song'],
        usage='leak <song>',
        description='Get the audio file for a track')
    @bridge.bridge_option(name='song', description='Song name', required=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def leak(self, ctx, *, song: str):
        msg = await ctx.reply(embed=await loading('song'))
        success, data = await httpcall('https://juicewrldapi.com/juicewrld/songs/', params={'search': song})
        if not success:
            return await msg.edit(embed=data)

        results = [s for s in data.get('results', []) if s.get('category') not in ('unsurfaced', 'recording_session')]
        if not results:
            return await msg.edit(embed=discord.Embed(description='No audio file found :(', color=colors.main))
        if len(results) == 1:
            return await self.send_embed(msg, ctx, results[0], button_type='mp3')

        await self.multi_choice(msg, results, ctx, button_type='mp3')

    @bridge.bridge_command(
        aliases=['snippet', 'snip'],
        usage='snippets <song>',
        description='Get snippet(s) for a track')
    @bridge.bridge_option(name='song', description='Song name', required=True)
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def snippets(self, ctx, *, song: str):
        msg = await ctx.reply(embed=await loading('snippet'))
        success, data = await httpcall('https://juicewrldapi.com/juicewrld/songs/', params={'search': song})
        if not success:
            return await msg.edit(embed=data)

        results = data.get('results', [])
        if not results:
            return await msg.edit(embed=discord.Embed(description='No snippets found :(', color=colors.main))
        if len(results) == 1:
            return await self.send_embed(msg, ctx, results[0], button_type='snip')

        await self.multi_choice(msg, results, ctx, button_type='snip')

    @bridge.bridge_command(
        aliases=['sessions', 'rs'],
        usage='session <song>',
        description='Get the recording session for a track')
    @bridge.bridge_option(name='session', description='Session name', required=True)
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def session(self, ctx, *, session: str):
        msg = await ctx.reply(embed=await loading('session'))
        success, data = await httpcall('https://juicewrldapi.com/juicewrld/songs/', params={'search': session})
        if not success:
            return await msg.edit(embed=data)

        results = [s for s in data.get('results', []) if s.get('category') == 'recording_session']
        if not results:
            return await msg.edit(embed=discord.Embed(description='No session found :(', color=colors.main))
        if len(results) == 1:
            return await self.send_embed(msg, ctx, results[0], button_type='session')

        await self.multi_choice(msg, results, ctx, button_type='session')


def setup(bot):
    bot.add_cog(FilesCog(bot))