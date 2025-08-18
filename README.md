# wrld bot
A simple Python bot that pulls Juice WRLD info using [juicewrldapi.com](https://juicewrldapi.com). You can use it publicly, or self-host your own version to tweak however you like.  

I can’t promise this bot will always stay updated. I mainly made it for fun as an open-source alternative to [moonlight]() by yash, [hh wrld]() by hunter, and other Juice WRLD bots. I don’t really expect it to blow up, so for now it’ll stay completely free to use.  

## Invite
If you just want to use the public bot, you can [invite it here](). Otherwise, keep reading to learn how to build it yourself.  

# Usage
Coming soon.  

# Building
If you want to host wrld yourself:  
1. Download the repo as a `.zip` and extract it.  
2. Create a file named `creds.env` and paste the following:  
```
BOT_TOKEN=
DEV_TOKEN=
```
3. Paste your bot’s token into `BOT_TOKEN`. Leave `DEV_TOKEN` blank unless you’re going to use a separate dev bot.  
4. Run `start.bat` and you’ll have your own instance running!  

### Dev Mode
If you want to run a separate dev bot alongside your main one:  
1. Make sure you’ve done the steps above.  
2. Paste your dev bot’s token into `DEV_TOKEN`.  
3. In `config.py`, set `DEV = True`.  

**Note:** With `DEV = True`, the bot will default to the dev token on startup. To switch back to your main bot, just change it back to `False`.  

You’re free to make your own public bot with this, but I just ask that you give me (pure) credit somewhere on the bot.  

## Site Access
When the site first launched, an access code was given out, but months later I couldn’t find it (after some lazy searching). So I did the next best thing… some super simple reverse engineering.  

The code ended up being inside [62d43f4b.js](https://juicewrldapi.com/assets/index.62d43f4b.js).  
**The access code is `juicetracker`.**  
(easily guessable ngl, but I didn’t bother guessing lol)  

## Credits
- juicewrldapi 💖  
