# wrld
A fairly simple Python bot that pulls information using [juicewrldapi.com](https://juicewrldapi.com) and [gabedoesntgaf GB tracker](https://docs.google.com/spreadsheets/d/1qWCsoTTGMiXxymTui319zFwMtpZE7a5SYqmybz6mkBY/edit). You can use it publicly, or self-host your own version. 

This will mostly be maintained, though I mainly made it for fun as an open-source alternative to [moonlight](https://discord.gg/YTWdnuNTbk) by yash, [hh wrld](https://discord.gg/P5nCDdMnBV) by hunter, and other Juice wrld bots. I wanted a bot that was solely for Juice, rather than being combined with server management. Hosting costs will be extremely low, so this bot is completely free to use. ✨🎉

In addition, Ill try to keep adding features as they come available from juicewrldapi or any other helpful sources.

You can view the to-do list [here](https://trello.com/b/kqv64MH9/wrld)

Made in [Pycord](https://pycord.dev/)

## Invite
If you just want to use the public bot, you can [invite it here](). Otherwise, keep reading to learn how to build it yourself. **If you're not experienced in python, do not attempt to host your own instance. I will not provide support on self-hosting**

# Usage
The default prefix is `,`. There is currently no way to set your own, however I can add that if this bot does well.

wrld supports both text and application (slash) commands. You can do ,help or /help to view all commands.

The bot is really simple, and therefore is pretty self explanatory to use. It's pretty hard to not understand, however if you need help with anything contact me on `Twitter/X @purezeroh` or `Discord @purree` **Do not contact me regarding self-hosting unless it's about fair use**

# Building
### If you're not experienced in python, stop here. You don't need to self-host until you know what you're doing. I will not provide support on self-hosting
This being said, if you want to host wrld yourself: 
1. wrld is written in [pycord](https://pycord.dev/), a discord.py fork. Please ensure its installed (instructions below)
2. Clone the Repo or download.  
3. Create a file named `.env` in the base directory and paste the following:
```env
BOT_TOKEN=
DEV_TOKEN=
G_API_KEY=
```
4. Paste your bot’s token into `BOT_TOKEN`. Leave `DEV_TOKEN` blank unless you’re going to use a separate dev bot.
5. Get a Google Sheets API key & paste it into `G_API_KEY`
6. Run `start.bat` or `start.sh` and you’ll have your own instance running!

### Pycord Installation
wrld is written in [pycord](https://pycord.dev/). Here's how you can install it:
1. Uninstall discord.py (Recommended unless you're going to use a virtual env)
2. Install Pycord:
```bash
pip install py-cord
```
Done!

Pycord is a great fork of discord.py. If you're interested in using it, you can [get started here](https://guide.pycord.dev/introduction)

### Dev Mode
If you want to run a separate dev bot alongside your main one:
1. Make sure you’ve done the steps above.  
2. Paste your dev bot’s token into `DEV_TOKEN`.  
3. In `config.py`, set `DEV = True`.  

**Note:** With `DEV = True`, the bot will default to the dev token on startup..  

You’re free to make your own public bot with this, but I just ask that you give me (pure) credit somewhere on the bot.  

### API Wrapper
The creator of the API recently made an [API Wrapper](https://github.com/HackinHood/juicewrld-api-wrapper) to allow easier usage. wrld will NOT adapt to this package, however if you're interested:
1. Install
2. This can be done either via GitHub:
```bash
pip install git+https://github.com/hackinhood/juicewrld-api-wrapper.git
```
3. Or via pypi:
```bash
pip install juicewrld-api-wrapper
```

### Contributing
If you would like to contribute; fork the repo, make your changes, and open a pull request. Id like if things were kept fairly simple.

If you have a larger idea, either reach out on my socials or open an issue & we can discuss.

## Fair Use
You are welcome to use this code to build your own bot, extend its functionality, or share it publicly. However, selling the code, claiming it as your own, or distributing it without proper credit is prohibited. Credit is defined as including my name (Pure) in any publicly accessible part of your project.

All data accessed by this bot remains the property of its respective owners and should be used respectfully.

Please contact me with any questions or negotiations at Twitter/X @purezeroh or Discord @purree.

## Site Access
I couldn't remember the access code & didn't feel like searching or contacting the developer (even though i did anyways, shoutout to him hes cool asf) so I did the next best thing.. the simplest form of Reverse Engineering there is.
 
**The access code is `juicetracker`.**   

## Credits
- juicewrldapi 💖  
- gabedoesntgaf GB/PB Tracker 💖
