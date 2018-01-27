# AveBot Commands:<br>

### How to read the variables
- A `<>` after a command will state a required variable
- A `[]` after a command will state an optional variable

## Basic Bot Commands:<br>
**ab!help:** Shows help and links to this. **[ported, improved]**<br>
**ab!servercount:** Returns the amount of servers AveBot is in. **[ported, improved]**<br>
**ab!whoami:** Returns your information. **[removed]**<br>
**ab!info:** Returns bot's information. **[ported, improved]**<br>
**ab!uinfo:** Returns information about the user. **[ported, improved]**<br>
**ab!sinfo [mention people to get their info]:** Returns information about the server. **[ported, improved]**<br>
**ab!feedback \<message>:** Sends feedback to developers. **[ported]**<br>
**ab!ping:** Calculates the ping between the bot and the discord server. **[ported, improved]**

## Server Commands:<br>
**ab!invite:** Gives a link that can be used to add AveBot **[ported]**.<br>
**ab!ginvite \<discord ID>:** Generates a bot invite link. **[new in v3]**<br>
**ab!howmanymessages:** Counts how many messages you sent in this channel in last 10000 **[ported]**.<br>

## Stocks Commands<br>
**ab!s \<ticker>:** Returns stock info about the given ticker. **[ported]**<br>
**ab!c \<ticker>:** Returns stock chart of the given ticker. **[ported]**<br>
**ab!btc:** Returns a 30 day BTC/USD chart, last close, and the change since last close. **[ported]**<br>

## Fun Commands<br>
**ab!copypasta \<ticker>:** Generates a buy copypasta for StockStream using the given ticker. **[ported]**<br>
**ab!copypastasell \<ticker>:** Generates a sell copypasta for StockStream using the given ticker. **[ported]**<br>
**ab!bigly \<text>:** Makes a piece of text as big as the hands of the god emperor. **[ported, improved]**<br>
**ab!roll \<NdN>:** Rolls a dice in NdN format. **[ported]**<br>
**abddg!\<bang> \<query>:** Resolves a duckduckgo bang. **[removed]**<br>
**ab!xkcd:** Returns info about the specified xkcd comic. **[ported]**<br>
**ab!xkcdlatest:** Returns info about the latest xkcd comic. **[ported]**<br>

## NSFW Commands<br>
**ab!tumblrgrab \<tumblr link>:** Gets images from a tumblr post. **[ported, improved]**<br>

## Image Commands<br>
**ab!sbahjify \<image link or uploaded image>:** Makes images hella and sweet. **[ported]**<br>
**ab!jpegify \<image link or uploaded image>:** Makes images jaypeg. **[ported]**<br>
**ab!ultrajpegify \<image link or uploaded image>:** Makes images ULTRA jaypeg. **[ported]**<br>
**ab!joelify \<image link or uploaded image>:** Stretches and shrinks images randomly, similar to what Joel does in many Windows Destruction streams. **[ported]**<br>
**ab!ultrajoelify \<image link or uploaded image>:** like joelify but more joel. **[ported]**<br>
**ab!mazeify \<image link or uploaded image>:** mazeifies an image. **[ported]**<br>
**ab!ultramazeify \<image link or uploaded image>:** makes images even more maze. **[ported]**<br>
**ab!gifify \<text>:** turns images into gifs of 128x128 size, to turn into emojis. **[ported]**<br>
**ab!howold <attach or link image>** Returns gender and age data based on Microsoft Cognitive Services' Face API. Pretty unreliable. **[ported]**<br>

## Linguistic Commands<br>
**ab!similar \<word or a word group>:** Finds a similar word **[ported]**<br>
**ab!typo \<word or a word group>:** Fixes a typo **[ported]**<br>
**ab!soundslike \<word or a word group>:** Finds a word that sounds like that **[ported]**<br>
**ab!rhyme \<word or a word group>:** Finds a word that rhymes with it **[ported]**<br>

## Technical Commands<br>
**ab!unfurl \<url>:** Finds where a URL redirects to. **[ported]**<br>
**ab!resolve \<domain>:** Resolves a domain to its DNS values. **[ported]**<br>
**ab!epoch:** Returns the Unix Time / Epoch. **[ported]**<br>
**ab!aveheat:** Shows heat chart and heat values from my house. **[ported]**<br>
**ab!render \<url>:** Returns the page render of that URL. **[ported and made public]**<br>

## Privileged-only Commands<br>
**ab!get:** Gets a file from the internet (Privileged/Mod/Admin only). **[ported, improved]**<br>
**ab!dget:** Directly gets (doesn't care about name) a file from the internet (Privileged/Mod/Admin only).  **[removed, use direct variable of get instead]**<br>
**ab!material:** Gets a file from material.io's icons gallery (Privileged/Mod/Admin only) **[removed]**<br>

## Mod-only Commands<br>
**ab!say \<text>:** Says something (Mod/Owner only). **[ported]**<br>
**ab!addpriv \<tag as many people as you like>:** Adds a privileged user (Mod/Owner only)<br>
**ab!rmpriv \<tag as many people as you like>:** Removes a privileged user (Mod/Owner only)<br>
**ab!ban \<tag as many people as you like>:** Bans a user (Mod/Owner only)<br>
**ab!unban \<tag as many people as you like>:** Unbans a user (Mod/Owner only)<br>

## Owner-only Commands<br>
**ab!addmod \<tag as many people as you like>:** Adds a mod (Owner only)<br>
**ab!rmmod \<tag as many people as you like>:** Removes a mod (Owner only)<br>
**ab!log \<count>:** Returns a log of the last <count> messages in this channel. This will only be used by the dev on servers owned by them, so it's not a ToS violation. (Owner only) **[ported]**<br>
**ab!fetchlog:** replies with the log file (Owner only) **[ported]**<br>
**ab!exit:** Quits the bot (Owner only). **[ported]**<br>
**ab!pull:** Does a `git pull` (Owner only). **[ported]**<br>
**ab!eval:** Evalulates smth. **[ported]**<br>
**ab!sh:** Runs a shell command, command can be wrapped in \` or \`\`\` (Owner only). **[ported]**<br>
