import logging
from formatter import ColourFormatter
import discord
from discord.ext import commands
import asyncio
from requests import get
from TOKEN import discord_key, als_key
from datetime import datetime
from pytz import timezone, all_timezones

# --------- Configuration ---------
update_message = False
time_zone = "UTC"
update_frequency_seconds = 4
# --------- Configuration ---------

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents, command_prefix='!')

info_message = None

start_time = None

def convert_time(time_str):
    time_utc = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

    utc_tz = timezone("UTC")
    time_utc = utc_tz.localize(time_utc)

    converted_tz = timezone(time_zone)
    converted_time = time_utc.astimezone(converted_tz)

    return converted_time.strftime("%Y-%m-%d %H:%M:%S")


def construct_report_string(res):
    current_start_time = res['current']['readableDate_start'].split()
    current_end_time = res['current']['readableDate_end'].split()
    current_map = res['current']['map']
    remaining = res['current']['remainingTimer']

    next_start_time = res['next']['readableDate_start'].split()
    next_end_time = res['next']['readableDate_end'].split()
    next_map = res['next']['map']
    next_duration = res['next']['DurationInMinutes']

    current_time = str(datetime.now(timezone(time_zone))).split('.')[0]

    if time_zone != "UTC":
        current_start_time = convert_time(" ".join(current_start_time)).split()
        current_end_time = convert_time(" ".join(current_end_time)).split()
        next_start_time = convert_time(" ".join(next_start_time)).split()
        next_end_time = convert_time(" ".join(next_end_time)).split()

    result = f"The map is `{current_map}` for `{remaining}`\n" \
             f"\tFrom  {current_start_time[1]}\n" \
             f"\tTo       {current_end_time[1]}\n" \
             f"The next map will be `{next_map}` for `{next_duration} minutes`:\n" \
             f"\tFrom  {next_start_time[1]}\n" \
             f"\tTo       {next_end_time[1]}\n" \
             f"Used timezone is {time_zone}\n" \
             f"Last updated `{current_time}\n`" \
             f"Bot has been running since `{start_time}`"

    return result


def construct_status_string(res):
    cur_map = res['current']['map']
    cur_rem = res['current']['remainingMins']
    res_str = cur_map + ': ' + str(cur_rem) + " Min"
    return res_str


@bot.event
async def on_ready():
    global start_time
    logger.info(f'We have logged in as {bot.user}')
    start_time = str(datetime.now(timezone(time_zone))).split('.')[0]

    while True:
        try:
            await update()
            await asyncio.sleep(update_frequency_seconds)
        except Exception:
            await asyncio.sleep(update_frequency_seconds + 7)


async def update():
    request = await get_data()
    if request is None:
        logger.error(f"Request Unsuccessful! Trying again in {update_frequency_seconds + 5} Seconds")
        await asyncio.sleep(update_frequency_seconds + 5)
        return
    game_activity_string = construct_status_string(request)
    report_string = construct_report_string(request)

    if info_message is not None:
        await info_message.edit(content=report_string)

    await update_status(game_activity_string)


@bot.command()
async def init_status(ctx):
    global info_message
    if info_message is not None:
        await info_message.delete()
        logger.info("Old Status Message Deleted")

    info_message = await ctx.send("Moving the Status Message Here!")
    logger.info("Status Message Initiated")

    await ctx.message.delete()


async def update_status(new_status):

    status = discord.Game(new_status)

    await bot.change_presence(activity=status)


async def get_data():
    res = get(
        f'https://api.mozambiquehe.re/maprotation?auth={als_key}')
    if "Error" in res.json().keys():
        logger.error(res.json()["Error"])
        if "Slow down" in res.json()["Error"]:
            logger.error("You should try lowering your update frequency, values under 1 second are not recommended!")
        return None
    elif res.status_code != 200:
        logger.error(f"Error Response Code from Apex Legends Status API: {res.status_code}")
        logger.error(res.json())
        return None

    return res.json()


if __name__ == "__main__":
    # Setting Up Logging
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    logging.getLogger('discord.http').setLevel(logging.INFO)
    handler = logging.StreamHandler()
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = ColourFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if time_zone not in all_timezones:
        logger.critical("Couldn't find a timezone with specified name!")
        logger.critical("The program will now print all available timezones and exit.")
        logger.critical(all_timezones)
        exit(-1)

    bot.run(discord_key, log_handler=None)
