import discord
from discord.ext import bridge, commands

import random

import platform
from functions.functions import colors, loading, gifs, find_commands, emojis, httpcall, format_uptime

class Dropdown(discord.ui.Select):
    def __init__(self, bot, user_id, bot_avatar_url):
        options = [
            discord.SelectOption(label='Files', description='Commands that provide files'),
            discord.SelectOption(label='Info', description='Commands that provide information/data'),
            discord.SelectOption(label='Owner', description='Commands for bot owner'),
        ]

        super().__init__(
            placeholder='Select a command category...',
            min_values=1,
            max_values=1,
            options=options
        )

        self.bot = bot
        self.user_id = user_id
        self.bot_avatar_url = bot_avatar_url

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.id == self.user_id:
            await interaction.response.send_message(f'This is not for you {random.choice(gifs)}', ephemeral=True)
            return
        
        selection = self.values[0]
        message = interaction.message
        
        commands = find_commands(self.bot, category=f'commands/{selection.lower()}')
        if commands:
            embed = message.embeds[0]
            embed.clear_fields()
            
            embed.title = f'wrld - {selection}'
            embed.description = f'Use `help <command>` to view more information on a command.'
            for command in commands:
                description = command.description if command.description else 'No description'
                embed.add_field(name=f'> {command.name}', value=description, inline=False)
            
            embed.set_thumbnail(url=self.bot_avatar_url)

            await interaction.response.edit_message(embed=embed)
        else:
            await message.channel.send(f'No commands found in the {selection} category.')

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command(
        usage='help [command]', 
        aliases=['h'], 
        description='Displays a list of commands'
    )
    @bridge.bridge_option(name='command', description='Command to get help for', required=False)
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def help(self, ctx, command=None):
        msg = await ctx.reply(embed=await loading('command'))

        if command:
            cmd = self.bot.get_command(command)
            if cmd:
                aliases = ', '.join(cmd.aliases) if cmd.aliases else 'None'
                
                cooldown_per = getattr(cmd._buckets._cooldown, 'per', None)
                cd_text = f'{round(cooldown_per)} second(s)' if cooldown_per else 'None'

                embed = discord.Embed(
                    title=f'wrld - {cmd.name}', 
                    description=f'{emojis.reply}{cmd.description}', 
                    color=colors.main
                )
                embed.set_footer(text=f'help to view a list of all commands')
                embed.add_field(name='Usage', value=f'{getattr(ctx, 'clean_prefix', '/')}{cmd.usage}')
                embed.add_field(name='Cooldown', value=cd_text)
                embed.add_field(name='Aliases', value=aliases)
                
                await msg.edit(embed=embed)
            else:
                await msg.edit(content=f'Invalid command. Run `{ctx.prefix}help` for a list of commands', embed=None)
        else:
            view = discord.ui.View()
            dropdown = Dropdown(self.bot, ctx.author.id, self.bot.user.avatar.url)
            view.add_item(dropdown)

            embed = discord.Embed(
                title='wrld', 
                description=f'Welcome to the help menu. Here you can find a list of all commands and their descriptions. You can run `{getattr(ctx, 'clean_prefix', '/')}help <command>` for more information on a specific command.\n\n> Select a category below to list the commands', 
                color=colors.main
            )
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            await msg.edit(embed=embed, view=view)

    @bridge.bridge_command(
        aliases=['invite', 'git'],
        usage='git', 
        description='Get information about wrld'
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def about(self, ctx):
        days, hours, minutes = format_uptime()
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label='GitHub', url='https://github.com/purrre/wrld-bot'))
        view.add_item(discord.ui.Button(label='Invite', url='https://discord.com/oauth2/authorize?client_id=806666114666725378&permissions=563364418145344&integration_type=0&scope=bot'))
        embed = discord.Embed(title='wrld', description=f'wrld is an open-source Discord bot that provides information about Juice WRLD. Created in Python v{platform.python_version()} with Pycord v{discord.__version__} and made possible by juicewrldapi.com', color=colors.main)
        embed.add_field(name='📊 Stats', value=
                        f'`{len(self.bot.guilds)}` servers\n'
                        f'`{len(self.bot.users)}` users\n'
                        f'`{len(self.bot.commands)}` commands\n'
                        f'`{self.bot.shard_count}` shards\n'
                        f'`{days}d {hours}h {minutes}m` uptime'
                        )
        embed.add_field(name='<:github:1413031789961805875> GitHub', value='[Click Here](https://github.com/purrre/wrld-bot)')
        embed.add_field(name='<:love:1413032472731582505> Invite Bot', value='[Click Here](https://discord.com/oauth2/authorize?client_id=806666114666725378&permissions=563364418145344&integration_type=0&scope=bot)')
        embed.add_field(name='❤️ Sources', value='[juicewrldapi](https://juicewrldapi.com/)\n[gabedoesntgaf GB/PB Tracker](https://docs.google.com/spreadsheets/d/1qWCsoTTGMiXxymTui319zFwMtpZE7a5SYqmybz6mkBY/edit)')
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text='Made with 💖 by @purree')
        await ctx.reply(embed=embed, view=view)

    @bridge.bridge_command(
        aliases=['cl', 'changelog'],
        usage='changes',
        description='Most recent changes to wrld'
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def changes(self, ctx):
        msg = await ctx.reply(embed=await loading('changelog'))
        success, file = await httpcall('https://raw.githubusercontent.com/purrre/wrld-bot/refs/heads/main/CHANGES.md', expect_json=False)
        if not success:
            return await msg.edit(embed=file)
        lines = file.splitlines()
        
        embed = discord.Embed(title=f'v{lines[2]} Changelog', color=colors.main)
        changes = [line for line in lines[3:] if line.strip()]
        embed.description = f'{lines[0]}\n\n' + '\n'.join(changes)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        await msg.edit(embed=embed)


def setup(bot):
    bot.add_cog(HelpCog(bot))