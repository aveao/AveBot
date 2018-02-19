# AveBot

A discord bot that does a ton of weird (and neat) stuff.

This is v3, which uses Discord.py rewrite and is finally on COGS.

Please check out `COMMANDS` to see the command list.


---

Due to Discord Developer ToS, I am required to tell you that AveBot DOES log messages that start with AveBot's prefix (`ab!`), and you shouldn't add it to your server or use it if you don't agree with that.

Invite link: https://discordapp.com/oauth2/authorize?client_id=305708836361207810&scope=bot

---

### How can I set it up?
- Install python3.6 or higher.
- Install `imagemagick` on pip if you plan to enable `imagemanip` or `emojis` cogs
- Install `colors` on pip if you plan to enable `finance` cog
- Install `psutil` and `humanize` on pip
- Install `psycopg2` 
- Install postgres, create a user, a database and whatnot, then execute this: `CREATE TABLE permissions (discord_id bigint UNIQUE, permlevel int);`. Note down the database name, username and password.
- Install `discord.py` (`pip3 install -U discord.py`).
- Install `python-dateutil` (`pip3 install python-dateutil`)
- Install `pillow` ([See this for more info on how to install it](https://askubuntu.com/a/427359/511534))
- Download [Mukta Malar](https://fonts.google.com/specimen/Mukta+Malar) and copy `MuktaMalar-Medium.ttf` to AveBot folder (or change font name in ini)
- Learn your bot token ([hint](https://discordapp.com/developers/applications/me)).
- Set up a room for `ab!contact` messages and one for messages on launch time, note their IDs down (looks like `305715263951732737`). Developer mode will help with this one.
- Copy `avebot.ini.example` to `avebot.ini`.
- Put the token, Room IDs and postgres info on the `avebot.ini` file.
- Add your bot to your server. (Find the Client ID on same place as the one you found out the bot token, replace it with BOT_TOKEN on this link: https://discordapp.com/oauth2/authorize?client_id=BOT_TOKEN&scope=bot)
- Run `python3.6 avebot.py`. I recommend using pm2 and just running `pm2 start avebot.py --interpreter python3.6` if you want it to be restarted automatically after system restarts and crashes.
- Enjoy.
