import discord

from datetime import datetime
import random, aiohttp, traceback

class colors:
    red = 0xe74c3c
    main = 0x6A0DAD

class emojis:
  reply = '<:reply:1407148693802455120>'
  reply2 = '<:reply2:1407148805287182348>'
  joemad = '<:redjoemad:1342971742561370224>'

gifs = ['<a:gif1:1407139666511265984>', 
        '<a:gif2:1407139813781409904>', 
        '<a:gif3:1407139882882695218>',
        '<a:gif4:1407139953498128505>', 
        '<a:gif5:1407140141805338778>', 
        '<a:gif6:1407140173665271898>',
        '<a:gif7:1407140324807278664>', 
        '<a:gif8:1407140374203469896>', 
        '<a:gif9:1407140399834730636>',
        '<a:gif10:1411972696836804648>',
        '<a:gif11:1411972803154149457>']

async def loading(method):
    return discord.Embed(description=f'{random.choice(gifs)} Getting {method} information..', color=colors.main)

def apierror(status, statustext):
    embed=discord.Embed(
        title=f'{random.choice(gifs)} HTTP Error', 
        description=f'An error occured while querying.\n\nPlease try again later. If this persists, you can report it to `@purree`', 
        color=colors.red, 
        timestamp=datetime.now())
    embed.set_footer(text=f'Error {status}: {statustext}')
    return embed

async def httpcall(url, method='GET', headers=None, data=None, params=None):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, json=data, params=params) as resp:
                status = resp.status
                if not status == 200:
                    apierror(status=status, statustext=resp.reason)
                    print(f'Request failed with status {status}: {resp.reason}')
                else:
                    response = await resp.json()
                    return response
    except aiohttp.ClientError as e:
        print(f'HTTP request failed: {e}')
        traceback.print_exc()
        return f'HTTP request failed: {e}'
    except Exception as e:
        print(f'An error occurred: {e}')
        traceback.print_exc()
        return f'An error occurred: {e}'
    
def cdict(data: dict) -> dict | None:
    if not isinstance(data, dict):
        return None
    cleaned = {}
    for key, value in data.items():
        if isinstance(value, dict):
            cleaned[key] = cdict(value) or None
        elif isinstance(value, list):
            cleaned[key] = [v for v in value if v and (not isinstance(v, str) or v.strip())]
        elif isinstance(value, str):
            cleaned[key] = value.strip() or None
        else:
            cleaned[key] = value
    return cleaned

def find_commands(bot, category):
    commands_in_category = []
    for command in bot.walk_commands():
        if command.cog:
            cog_path = command.cog.__module__.replace('.', '/') + '.py'
            if cog_path.startswith(category):
                commands_in_category.append(command)
    return commands_in_category