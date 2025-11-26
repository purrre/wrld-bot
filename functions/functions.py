import discord

from datetime import datetime
import time
import random, aiohttp, traceback, json

start_time = None



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



async def loading(method, x=None):
    """loading message, x = additional information"""
    return discord.Embed(description=f"{random.choice(gifs)} Getting {method} information.. {x or ''}", color=colors.main)

def apierror(status, statustext):
    embed = discord.Embed(
        title=f'{random.choice(gifs)} HTTP Error',
        description='An error occured while querying.\n\nPlease try again later. '
                    'If this persists, you can report it to [@purree](https://pure.is-a.dev/)',
        color=colors.red,
        timestamp=datetime.now()
    )
    embed.set_footer(text=f'Error {status}: {statustext}')
    return embed

async def httpcall(url, method='GET', headers=None, data=None, params=None, expect_json=True, paginate=False, embed_resp=True):
    """Makes an HTTP request via aiohttp with optional pagination"""
    try:
        all_results = [] if paginate else None
        current_url = url
        current_params = params or {}

        while current_url:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, current_url, headers=headers, json=data, params=current_params) as resp:
                    if resp.status != 200:
                        e_embed = apierror(status=resp.status, statustext=resp.reason)
                        return False, e_embed if embed_resp else resp

                    content = bytearray()
                    async for chunk in resp.content.iter_chunked(64 * 1024):
                        content.extend(chunk)

                    if expect_json:
                        json_data = json.loads(content.decode())
                        if paginate:
                            batch = json_data.get('results', [])
                            all_results.extend(batch)
                            next_url = json_data.get('next')
                            if next_url:
                                current_url = next_url
                                current_params = None 
                                continue
                            else:
                                return True, all_results
                        else:
                            return True, json_data
                    else:
                        return True, content.decode()

            break

        if paginate:
            return True, all_results

    except aiohttp.ClientError as e:
        traceback.print_exc()
        e_embed = apierror(status="ClientError", statustext=str(e))
        return False, e_embed

    except Exception as e:
        traceback.print_exc()
        e_embed = apierror(status="Exception", statustext=str(e))
        return False, e_embed
    
def cdict(data: dict) -> dict | None:
    """Cleans a dict"""
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
    prefix = str(category or '').strip().replace('\\', '.').replace('/', '.').rstrip('.')
    return [
        cmd for cmd in bot.walk_commands()
        if (cog := getattr(cmd, 'cog', None)) and isinstance(getattr(cog, '__module__', None), str)
        and cog.__module__.startswith(prefix)
    ]


def format_uptime():
    uptime_seconds = int(time.time() - start_time)
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    return days, hours, minutes

def print_err(ctx=None, error=None, invoke=None):
    """Prints detailed error info"""
    print("─" * 60)
    print(f"[{invoke or type(error).__name__}]")

    if ctx is not None:
        try:
            print(f"Command   : {getattr(ctx, 'command', None)}")
            print(f"User      : {ctx.author} ({ctx.author.id})")
            print(f"Message   : {ctx.message.content}")
        except Exception:
            print("(Context info N/A)")

    original = getattr(error, "original", error)
    print(f"Error Type: {type(original).__name__}")
    print(f"Error Msg : {original}")
    print("─" * 60)
    traceback.print_exception(type(original), original, original.__traceback__)
    print("─" * 60)

def notfound_embed(query, ctx=None, type='track'):
    if type == 'track':
        return discord.Embed(
            description=f'No tracks found for **{query}**',
            footer=discord.EmbedFooter('TIP: Be less specific'),
            color=colors.main
        )