# Apex Legends Map Rotation Bot By kepper104
## A little discord bot with info on Apex Legends Map Rotation
Did this in several hours for my local server with friends, this bot provides info about current map in rotation
## It provides:
- Current map and it's time remaining in bot's status.
- Everything else about map rotation in info message, which updates live after you spawn it with !init_status command in channel you like.
## How to set up
If you for some reason also want to try it, create a file called `TOKEN.py` in project's directory and fill it out like this:
```
discord_key = "Your discord app key"
als_key = "Your Apex Legends Status API key"
```
How to get these API keys:
- ALS Key at https://portal.apexlegendsapi.com/
- Discord Key at https://discord.com/developers/applications

Pip Dependencies are located in the `requirements.txt`

To update data faster than once per 2 seconds (why tho?), you will need to also authorize your discord account on ALS site.

Program's config is located on lines 11-15 in `main.py`

Finaly, launch the program using `python main.py` or `python3 main.py`