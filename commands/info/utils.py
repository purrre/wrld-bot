import discord
from discord.ext import bridge, commands

import asyncio, time

from functions.functions import httpcall, loading, colors

class UtilsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.region = None
        self.country = None

    @bridge.bridge_command(
        usage='ping',
        description='Pings juicewrldapi to check the status',
        aliases=['p'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ping(self, ctx):
        msg = await ctx.reply(embed=await loading('TCPing'))
        if not self.country or self.country.lower() == 'unknown':
            ip = await httpcall('https://api.ipify.org', expect_json=False)
            r = await httpcall(f'https://ipinfo.io/{ip[1]}/json')
            self.country = r[1].get('country', 'unknown')
            self.region = r[1].get('region', '')

        embed = discord.Embed(title='juicewrldapi Status', url='https://downforeveryoneorjustme.com/juicewrldapi.com', color=colors.main)

        hosts = {
            'main': 'juicewrldapi.com',
            'media (master)': 'm.juicewrldapi.com'
        }

        for name, host in hosts.items():
            start = time.perf_counter()

            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, 80),
                    timeout=3
                )

                writer.close()
                if hasattr(writer, 'wait_closed'):
                    await writer.wait_closed()

                ping_ms = (time.perf_counter() - start) * 1000

                embed.add_field(
                    name=f'<:status_online:1443125660552921142> {name.title()}',
                    value=f'Ping: {ping_ms:.2f} ms',
                    inline=True
                )

            except Exception as e:
                embed.add_field(
                    name=f'<:status_offline:1443125840501014572> {name.title()}',
                    value=f'Error: `{type(e).__name__}`\nDetails: `{str(e)}`',
                    inline=True
                )

        embed.set_footer(text=f'{self.bot.user.name} | Pinged from {self.region}, {self.country}', icon_url=self.bot.user.avatar.url)
        await msg.edit(embed=embed)

def setup(bot):
    bot.add_cog(UtilsCog(bot))