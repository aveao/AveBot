# AveBot

Batteries not included. See `How can I set it up FAQ:`.

The stuff it can do can be seen by running `>help` on a server it's added on or by reading `help.md` file here.

### How can I use your setup?
- Add it to your server with: https://discordapp.com/oauth2/authorize?client_id=305708836361207810&scope=bot
- I don't add anyone as mod. Sorry.

### How can I set it up?
- Install python3.
- Install `discord.py` (`pip install -U discord.py`).
- Install `pillow` ([See this for more info on how to install it](https://askubuntu.com/a/427359/511534))
- Learn your bot token ([hint](https://discordapp.com/developers/applications/me)).
- Set up a room for `>contact` messages and one for messages on launch time, note their IDs down (looks like `305715263951732737`). Developer mode will help with this one.
- Learn your Discord ID (looks like `137584770145058817`). Developer mode will help with this one.
- Copy `avebot.ini.example` to `avebot.ini`.
- Put the token, Room IDs and your Discord ID on the `avebot.ini` file.
- Add your bot to your server. (Find the Client ID on same place as the one you found out the bot token, replace it with BOT_TOKEN on this link: https://discordapp.com/oauth2/authorize?client_id=BOT_TOKEN&scope=bot)
- Run `run.sh` if you want it to be restarted automatically if it crashes, or just `python3 avebot.py` if you aren't worried about that.
- Enjoy.