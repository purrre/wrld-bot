import discord
from discord.ext import commands, bridge
from discord.gateway import DiscordWebSocket

import os, traceback, time, logging
from dotenv import load_dotenv

import config
from functions import mobile as setup
import functions.functions as func

if config.HEALTH:
    from flask import Flask
    import threading

load_dotenv()
key = os.environ.get('G_API_KEY')

DiscordWebSocket.identify = setup.WRLD
bot = bridge.Bot(
    command_prefix=commands.when_mentioned_or(config.PREFIX or ','),
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
    creds = config.TOKEN
    if not creds or not key:
        raise SystemExit('Missing Credidentials. Check the README')
    return True, creds

def health_endpoint():
    app = Flask(__name__)

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    @app.route('/health')
    def health():
        return 'OK', 200

    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=config.PORT, use_reloader=False, debug=config.DEV), daemon=True).start()

if __name__ == '__main__':
    if token_check()[0]:
        try:
            bot.load_extension('functions.listeners')
            load_cogs()
            if config.HEALTH:
                health_endpoint()
            bot.run(token_check()[1], reconnect=True)
        except Exception as e:
            print(f'Error during startup: {e}')
            traceback.print_exc()