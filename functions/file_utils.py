import discord

import aiohttp, io, asyncio, traceback
import urllib.parse

from functions.functions import httpcall, colors, loading

# i hate this file. 

async def fetch_urls(name, filename=None, ext=None, track_titles=None):
    queries = [filename] if ext == '.mp3' and filename else []
    if track_titles:
        queries.extend(track_titles)
    queries.append(name)

    for query in queries:
        if not query:
            continue

        data = await httpcall(f'https://juicewrldapi.com/juicewrld/files/browse/?search={urllib.parse.quote(query)}')
        if not data.get('items'):
            continue

        urls = [
            f'https://juicewrldapi.com/juicewrld/files/download/?path={urllib.parse.quote(file.get('path'))}'
            for file in data['items']
            if file.get('extension') == ext and query.lower() in file.get('name', '').lower()
        ]
        if urls:
            return urls

    return []


async def send_file(interaction: discord.Interaction, url: str, filename: str, kind: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    return await interaction.followup.send(
                        embed=discord.Embed(description=f'Failed to fetch the {kind} file.', color=colors.red),
                        ephemeral=True
                    )
                data = await resp.read()

        try:
            await interaction.followup.send(file=discord.File(io.BytesIO(data), filename=filename), ephemeral=True)
        except discord.HTTPException as e:
            if e.code == 40005:  # too large, may hardcode values for faster sending & less errors
                size_mb = len(data) / 1024 / 1024
                await interaction.edit_original_response(
                    embed=discord.Embed(
                        title='File Too Large',
                        description=f'{kind} is too large ({size_mb:.2f} MB). Download it [here]({url})',
                        color=colors.main
                    )
                )
            else:
                raise

    except Exception as e:
        traceback.print_exc()
        await interaction.edit_original_response(
            embed=discord.Embed(description=f'⚠️ Error: {e}', color=colors.red)
        )



class SongButton(discord.ui.Button):
    def __init__(self, name: str, filename: str | None = None, title: str | None = None):
        super().__init__(emoji='💿', style=discord.ButtonStyle.gray)
        self.name = name
        self.filename = filename
        self.title = title or name
        self.stream_urls: list[str] = []

    async def callback(self, interaction: discord.Interaction):
        if not self.stream_urls:
            self.stream_urls = await fetch_urls(self.name, self.filename, '.mp3')
        if not self.stream_urls:
            return await interaction.response.send_message(
                embed=discord.Embed(description='Couldnt find an MP3 :(', color=colors.main),
                ephemeral=True
            )

        await interaction.response.send_message(embed=await loading('mp3'), ephemeral=True)
        await send_file(interaction, self.stream_urls[0], f'{self.title}.mp3', 'MP3')

class SnipButton(discord.ui.Button):
    def __init__(self, name, filename=None, title='Snippets', track_titles=None):
        super().__init__(emoji='👀', style=discord.ButtonStyle.gray)
        self.name = name
        self.filename = filename
        self.track_titles = track_titles
        self.title = title
        self.stream_urls: list[str] = []

    async def callback(self, interaction: discord.Interaction):
        if not self.stream_urls:
            self.stream_urls = await fetch_urls(self.name, self.filename, '.mp4', self.track_titles)
        if not self.stream_urls:
            return await interaction.response.send_message(
                embed=discord.Embed(description='Couldnt find any MP4 snippets :(', color=colors.main),
                ephemeral=True
            )

        await interaction.response.send_message(embed=await loading('mp4'), ephemeral=True)
        async with aiohttp.ClientSession() as session:
            for i, url in enumerate(self.stream_urls, start=1):
                await send_file(interaction, url, f'{self.title}_{i}.mp4', f'Snippet {i}')
                await asyncio.sleep(0.3)


class MediaView(discord.ui.View):
    def __init__(self, name, filename=None, track_titles=None, title='Media'):
        super().__init__(timeout=None)
        self.add_item(SongButton(name, filename, title))
        self.add_item(SnipButton(name, filename, title, track_titles))
