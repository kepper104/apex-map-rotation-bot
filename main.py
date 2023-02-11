import logging
from formatter import ColourFormatter
import discord
from discord.ext import commands
import asyncio
from requests import get
from TOKEN import discord_key, als_key
from datetime import datetime
from pytz import timezone

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix='!')


def to_MSC(time_str):
    time_utc = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

    utc_tz = timezone("UTC")
    time_utc = utc_tz.localize(time_utc)

    moscow_tz = timezone("Europe/Moscow")
    time_moscow = time_utc.astimezone(moscow_tz)

    return time_moscow.strftime("%Y-%m-%d %H:%M:%S")


@bot.event
async def on_ready():
    logger.info(f'We have logged in as {bot.user}')


@bot.command()
async def init_status(ctx):
    logger.info("Status Message Initiated")
    message = await ctx.send("This is a status message")
    await ctx.message.delete()

    while True:
        request = await get_data()
        # logger.info("Updating Data")

        if request is None:
            logger.warning("Redoing Request in 5 Seconds")
            await asyncio.sleep(5)
            continue

        game_activity_string = construct_status_string(request)
        report_string = construct_report_string(request)

        await message.edit(content=report_string)
        await update_status(game_activity_string)

        await asyncio.sleep(0.5)


async def update_status(new_status):

    status = discord.Game(new_status)

    await bot.change_presence(activity=status)


def construct_report_string(res):
    time_utc_start = res['current']['readableDate_start'].split()
    time_utc_end = res['current']['readableDate_end'].split()
    map = res['current']['map']
    remaining = res['current']['remainingTimer']
    next_map = res['next']['map']
    time_msc_start = to_MSC(" ".join(time_utc_start)).split()
    time_msc_end = to_MSC(" ".join(time_utc_end)).split()
    result = f"From  {time_utc_start[1]}  UTC ({time_msc_start[1]} MSK)\nTo       {time_utc_end[1]}  UTC ({time_msc_end[1]} MSK)\nThe map is {map}\n{remaining} remains until {next_map}"

    # print("----------START-REPORT----------")
    # print(result)
    # print("----------END---REPORT----------")

    return result


def construct_status_string(res):
    cur_map = res['current']['map']
    cur_rem = res['current']['remainingMins']
    res_str = cur_map + ': ' + str(cur_rem) + " Min"
    return res_str


async def get_data():
    res = get(
        f'https://api.mozambiquehe.re/maprotation?auth={als_key}').json()
    try:
        test = res['current']
    except TypeError:
        logger.error("Type Error")
        pass
    except KeyError:
        logger.error("Request is Throttling")
        res = None
    return res


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

    bot.run(discord_key, log_handler=None)
