import discord
import aiohttp, io, asyncio, traceback
import urllib.parse

from functions.functions import httpcall, colors, loading
import config


# fetch file urls
async def fetch_urls(song: dict, ext=None):
    name = song.get('name', '')
    track_titles = song.get('track_titles', []) or []

    queries = list(dict.fromkeys([name] + track_titles))

    exts = [ext] if ext else []
    if ext == '.mp3':
        exts.append('.wav')
    elif ext == '.mp4':
        exts.append('.mov')

    for query in queries:
        success, data = await httpcall(
            f'https://juicewrldapi.com/juicewrld/files/browse/?search={urllib.parse.quote(query)}'
        )

        if not success or not isinstance(data, dict) or not data.get('items'):
            continue

        all_urls = []
        found_ext = None
        
        for current_ext in exts:
            urls = [
                f'https://juicewrldapi.com/juicewrld/files/download/?path={urllib.parse.quote(file['path'])}'
                for file in data['items']
                if file.get('extension') == current_ext
            ]
            
            if urls:
                all_urls.extend(urls)
                if found_ext is None:
                    found_ext = current_ext

        if all_urls:
            urls_deduped = list(dict.fromkeys(all_urls))
            return urls_deduped, found_ext

    return [], None


# file sender
async def send_file(interaction: discord.Interaction, url, filename, kind, session: aiohttp.ClientSession=None):
    given_session = session is not None
    if not given_session:
        session = aiohttp.ClientSession()

    try:
        async with session.get(url, timeout=30) as resp:
            if resp.status != 200:
                return await interaction.followup.send(
                    embed=discord.Embed(description=f'Failed to fetch the {kind} file.', color=colors.red),
                    ephemeral=True
                )

            data = io.BytesIO()
            boost_level = interaction.guild.premium_tier if interaction.guild else 0
            max_size = config.upload_limits.get(boost_level, config.upload_limits[0])

            async for chunk in resp.content.iter_chunked(1024*256):
                data.write(chunk)
                size = data.tell() / 1024 / 1024
                if size > max_size:
                    view = discord.ui.View()
                    view.add_item(discord.ui.Button(label='Open', url=url))
                    return await interaction.followup.send(
                        embed=discord.Embed(
                            title='File Too Large',
                            description=f'{kind} is too large. Download or View it [here ↗]({url})',
                            color=colors.main
                        ),
                        ephemeral=True,
                        view=view
                    )

            data.seek(0)
            await interaction.followup.send(
                file=discord.File(data, filename=filename),
                ephemeral=True
            )

    except Exception as e:
        traceback.print_exc()
        return await interaction.followup.send(
            embed=discord.Embed(description=f'⚠️ Error: {e}', color=colors.red),
            ephemeral=True
        )
    finally:
        if 'data' in locals() and hasattr(data, 'close'):
            data.close()
        if not given_session and session:
            await session.close()


# mp3 / song
class SongButton(discord.ui.Button):
    def __init__(self, song: dict):
        super().__init__(emoji='💿', style=discord.ButtonStyle.gray)
        self.song = song
        self.stream_urls: list[str] = []
        self.found_ext: str | None = None

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, invisible=False)

        if not self.stream_urls:
            urls, found_ext = await fetch_urls(self.song, ext='.mp3')
            self.stream_urls = list(dict.fromkeys(urls))
            self.found_ext = found_ext

        if not self.stream_urls:
            return await interaction.followup.send(
                embed=discord.Embed(description="Couldn't find an audio file :(", color=colors.main),
                ephemeral=True
            )

        file_ext = self.found_ext or '.mp3'
        file_kind = 'MP3' if file_ext == '.mp3' else 'WAV'
        await send_file(interaction, self.stream_urls[0], f'{self.song.get('name')}{file_ext}', file_kind)


# mp4 / snip
class SnipButton(discord.ui.Button):
    def __init__(self, song: dict):
        super().__init__(emoji='👀', style=discord.ButtonStyle.gray)
        self.song = song
        self.stream_urls: list[tuple[str, str]] = []

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, invisible=False)

        if not self.stream_urls:
            urls, found_ext = await fetch_urls(self.song, ext='.mp4')


            if urls:
                self.stream_urls = [(u, found_ext) for u in urls]

        if not self.stream_urls:
            return await interaction.followup.send(
                embed=discord.Embed(description="Couldn't find any snippets :(", color=colors.main),
                ephemeral=True
            )

        await interaction.followup.send(
            embed=await loading('mp4', x=f'({len(self.stream_urls)} found). {'This may take a while' if len(self.stream_urls) > 5 else ''}'),
            ephemeral=True
        )

        async with aiohttp.ClientSession() as session:
            for i, (url, ext) in enumerate(self.stream_urls, start=1):
                filename = f'{self.song.get('name')}{ext}'
                await send_file(interaction, url, filename, f'Snippet {i}', session=session)
                await asyncio.sleep(0.4)


# session / zip
class SessionButton(discord.ui.Button):
    def __init__(self, song: dict):
        super().__init__(emoji='🎙️', style=discord.ButtonStyle.gray)
        self.song = song
        self.stream_urls: list[str] = []

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, invisible=False)

        if not self.stream_urls:
            urls, _ = await fetch_urls(self.song, ext='.zip')
            self.stream_urls = list(dict.fromkeys(urls))

        if not self.stream_urls:
            return await interaction.followup.send(
                embed=discord.Embed(description="Couldn't find a session :(", color=colors.main),
                ephemeral=True
            )

        await send_file(interaction, self.stream_urls[0], f'{self.song.get('name')}_session.zip', 'Recording Session')


class MediaView(discord.ui.View):
    def __init__(self, song: dict):
        super().__init__(timeout=None)
        self.add_item(SongButton(song))
        self.add_item(SnipButton(song))
        self.add_item(SessionButton(song))