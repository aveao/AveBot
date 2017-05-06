# AveBot

Batteries not included. See `How can I set it up FAQ:`.

The stuff it can do can be seen by running `>help` on a server it's added on or by reading `help.md` file here.

### How can I use your setup?
- Add it to your server with: https://discordapp.com/oauth2/authorize?client_id=305708836361207810&scope=bot
- I don't add anyone as mod. Sorry.

### How can I set it up?
- It uses python3 (python 3.6 requirement was fixed).
- Change botowner on line 16 from `botowner = "137584770145058817"` to `botowner = "your discord id"`. Developer mode will help with this one.
- You need `discord.py`: `pip install -r requirements.txt` or `pip install -U discord.py`.
- You need to set the bot token: `echo -n "bot's token" > bottoken`
- Wondering what a token is? [Go here](https://discordapp.com/developers/applications/me), authenticate, create a new app, create a bot, click on `click to reveal` under username. Enjoy.
- Add yourself as a mod after starting it.