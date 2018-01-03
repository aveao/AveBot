# AveBot

A discord bot that does a ton of weird (and neat) stuff.

Please check out `help.md` to see the command list.


# THIS INFO IS OUT OF DATE FOR THIS BRANCH
AveBot v3 will use discord.py rewrite and make use of COGS, however, it's not working yet, so the setup stuff etc are outdated. However, they'll be updated when v3 is stable.

---

Thanks to Discord ToS, I am required to tell you that AveBot DOES log messages that start with AveBot's prefix (`ab!`), and you shouldn't add it to your server or use it if you don't agree with that.

Invite link: https://discordapp.com/oauth2/authorize?client_id=305708836361207810&scope=bot

---

### How can I set it up?
- Install python3 (3.4+).
- Install `imagemagick`
- Install `discord.py` (`pip3 install -U discord.py`).
- Install `python-dateutil` (`pip3 install python-dateutil`)
- Install `pillow` ([See this for more info on how to install it](https://askubuntu.com/a/427359/511534))
- Learn your bot token ([hint](https://discordapp.com/developers/applications/me)).
- Set up a room for `ab!contact` messages and one for messages on launch time, note their IDs down (looks like `305715263951732737`). Developer mode will help with this one.
- Learn your Discord ID (looks like `137584770145058817`). Developer mode will help with this one.
- Copy `avebot.ini.example` to `avebot.ini`.
- Put the token, Room IDs and your Discord ID on the `avebot.ini` file.
- Add your bot to your server. (Find the Client ID on same place as the one you found out the bot token, replace it with BOT_TOKEN on this link: https://discordapp.com/oauth2/authorize?client_id=BOT_TOKEN&scope=bot)
- Run `run.sh` if you want it to be restarted automatically if it crashes, or just `python3 avebot.py` if you aren't worried about that.
- Enjoy.
