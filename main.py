import discord
from discord.ext import commands, bridge
from discord.gateway import DiscordWebSocket

import os, traceback, time
from dotenv import load_dotenv

import config
from functions import mobile as setup
from functions.file_utils import MediaView
import functions.functions as func

load_dotenv()
token = os.environ.get('BOT_TOKEN')
dev_token = os.environ.get('DEV_TOKEN')
key = os.environ.get('G_API_KEY')

DiscordWebSocket.identify = setup.WRLD

bot = bridge.Bot(
    command_prefix=commands.when_mentioned_or(config.DEV_PREFIX if config.DEV and config.DEV_PREFIX else ','),
    intents=discord.Intents.all(),
    help_command=None,
    case_insensitive=True,
    heartbeat_timeout=75,
    allowed_mentions=discord.AllowedMentions(
        everyone=False,
        users=True,
        roles=False,
        replied_user=False
    ),
    shard_count=1
)

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def wrld(ctx):
    await ctx.reply(f'🎸 \n-# {round(bot.latency * 1000)}ms')

@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name='Juice WRLD')
    )
    print('Made with love by pure, powered by juicewrldapi.com')
    print(f'Registered {len(bot.commands)} commands')
    print(f'Logged in as {bot.user.id} ({bot.user.name}) in {len(bot.guilds)} guilds with {len(bot.users)} users\n------')
    func.start_time = time.time()

def load_cogs():
    for root, _, files in os.walk('commands'):
        for fn in files:
            if fn.endswith('.py'):
                module = os.path.join(root, fn).replace(os.sep, '.')[:-3]
                if module not in bot.extensions:
                    try:
                        bot.load_extension(module)
                        print(f'{fn} Loaded')
                    except Exception as e:
                        print(f'{fn} | ❌ ({e})')
                        traceback.print_exc()

def token_check():
    creds = dev_token if config.DEV else token
    if not creds or not key:
        raise SystemExit('Missing Credidentials. Check the README')
    return True, creds

if __name__ == '__main__':
    if token_check()[0]:
        try:
            bot.load_extension('functions.listeners')
            load_cogs()
            bot.run(token_check()[1], reconnect=True)
        except Exception as e:
            print(f'Error during startup: {e}')
            traceback.print_exc()