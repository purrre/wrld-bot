import discord
from discord.ext import bridge, commands
import os
import random
from dotenv import load_dotenv

from functions.functions import colors, httpcall, loading, gifs

load_dotenv()


async def fetch_buys():
    try:
        resp = await httpcall(
            'https://sheets.googleapis.com/v4/spreadsheets/1qWCsoTTGMiXxymTui319zFwMtpZE7a5SYqmybz6mkBY/values/lOG/',
            params={'key': os.environ.get('G_API_KEY')}
        )
        rows = resp.get('values', [])
    except:
        return []

    if len(rows) < 5:
        return []

    headers = [h.strip().lower().replace(' ', '_').replace(':', '') for h in rows[1]]
    entries, last_values = [], {}

    for row in rows[4:]:
        if not any(row[1:]):
            continue
        row += [''] * (len(headers) - len(row))
        raw = dict(zip(headers, row))

        buyinfo = {k: (raw.get(k, '').strip() or last_values.get(k, '')) for k in headers}
        last_values.update({k: v for k, v in buyinfo.items() if v})

        entries.append({
            'title': buyinfo.get('content_advertised', ''),
            'project': buyinfo.get('project_|_era', ''),
            'price': buyinfo.get('price', ''),
            'start_date': buyinfo.get('start_date', '').replace('Start Date\n', ''),
            'end_date': buyinfo.get('end_date', '').replace('End Date\n', ''),
            'finished': buyinfo.get('finished', ''),
            'ogfile': buyinfo.get('surfaced_with_og_file', ''),
            'additional_info': buyinfo.get('additional_information', '')
        })

    return entries


def build_song_embed(song, bot):
    finished = song['finished'].lower()
    ogfile = song.get('ogfile', '').lower()

    finished_status = '✅' if finished == 'true' else '❌' if finished == 'false' else song['finished'] or 'N/A'
    og_status = '✅' if ogfile == 'true' else '❌' if ogfile == 'false' else song.get('ogfile', '') or 'N/A'

    embed = discord.Embed(
        title=song['title'],
        description=f"Price: {song['price'] or 'N/A'}",
        color=colors.main
    )
    embed.add_field(name='ERA', value=song['project'] or 'N/A', inline=False)
    embed.add_field(name='Start Date', value=song['start_date'] or 'N/A', inline=True)
    embed.add_field(name='End Date', value=song['end_date'] or 'N/A', inline=True)
    embed.add_field(name='Status', value=f"Finished: {finished_status}\nOG File: {og_status}", inline=False)
    embed.add_field(name='Notes', value=f"```{song['additional_info']}```", inline=False)

    embed.set_footer(text=bot.user.name, icon_url=bot.user.avatar.url)
    embed.set_thumbnail(url=bot.user.avatar.url)
    return embed


class SongSelect(discord.ui.Select):
    def __init__(self, entries, msg, bot, user):
        options = []
        for i, e in enumerate(entries[:25]):
            title = e.get('title', '')
            if not title:
                continue

            title = title.replace("\n", " | ")

            label = title[:97] + '...' if len(title) > 100 else title
            desc = e.get('additional_info', '')[:100]

            options.append(discord.SelectOption(label=label, value=str(i), description=desc))

        super().__init__(placeholder='Choose a buy...', options=options)
        self.entries, self.bot, self.msg, self.user = entries, bot, msg, user

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user:
            return await interaction.response.send_message(f'This is not for you {random.choice(gifs)}', ephemeral=True)
        
        await interaction.response.defer()

        song = self.entries[int(self.values[0])]
        embed = build_song_embed(song, self.bot)
        await self.msg.edit(embed=embed)


class BuyInfo(discord.ui.View):
    def __init__(self, entries, msg, bot, user):
        super().__init__()
        self.add_item(SongSelect(entries, msg, bot, user))


class groupbuyscog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.entries = []

    @bridge.bridge_command(description='Search for a groupbuy/privatebuy', aliases=['gbs', 'groupbuy', 'groupbuys'], usage='gb <buy>')
    @bridge.bridge_option(name='buy', description='Name of the buy', required=True)
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def gb(self, ctx, *, buy: str):
        if not self.entries:
            self.entries = await fetch_buys()

        msg = await ctx.reply(embed=await loading('groupbuy'))
        matches = [e for e in self.entries if buy.lower() in e.get('title', '').lower()]

        if not matches:
            await msg.edit(embed=discord.Embed(description='No buys found.', color=colors.main))
            return

        if len(matches) == 1:
            await msg.edit(embed=build_song_embed(matches[0], self.bot))
        else:
            await msg.edit(
                embed=discord.Embed(
                    title='Multiple buys found',
                    description='Please choose a buy from the dropdown below.',
                    color=colors.main
                ),
                view=BuyInfo(matches, msg, self.bot, ctx.author.id)
            )


def setup(bot):
    bot.add_cog(groupbuyscog(bot))