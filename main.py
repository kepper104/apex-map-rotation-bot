import discord
from discord.ext import commands
import asyncio
import requests
from TOKEN import auth_key

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix='!')


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    while True:
        await update_stats()
        await asyncio.sleep(60)


@bot.command()
async def s(ctx):
    res = await get_data()
    if(res is None):
        await ctx.send("Error when calling API, please try at least 5 seconds later")
        return
    report = construct_report_string(res)

    await ctx.send(report)


async def update_status(new_status):
    status = discord.Game(new_status)

    await bot.change_presence(activity=status)


async def update_stats():
    res = await get_data()
    if(res is None):
        return
    status_str = construct_status_string(res)

    await update_status(status_str)

    print("Updated status:", status_str)


def construct_report_string(res):
    time_start = res['current']['readableDate_start'].split()
    time_end = res['current']['readableDate_end'].split()
    map = res['current']['map']
    remaining = res['current']['remainingTimer']
    next_map = res['next']['map']
    result = f"From  {time_start[1]} UTC (LOCAL HERE)\nTo       {time_end[1]}  UTC (LOCAL HERE)\nThe map is {map}\n{remaining} remains until {next_map}"

    print("----------REPORT----------")
    print(result)
    print("----------REPORT----------")

    return result


def construct_status_string(res):
    cur_map = res['current']['map']
    cur_rem = res['current']['remainingMins']
    next_map = res['next']['map']
    res_str = cur_map + ': ' + str(cur_rem) + " Min"
    return res_str


async def get_data():
    res = requests.get(
        'https://api.mozambiquehe.re/maprotation?auth=ea74f8c48b5699e23c76a50c2a9d6b40').json()
    try:
        cur_map = res['current']['map']
        cur_rem = res['current']['remainingMins']
        next_map = res['next']['map']
        res_str = cur_map + ': ' + str(cur_rem) + " Min"

    except TypeError:
        print("ERROR: TYPE ERROR")
    except KeyError:
        print("ERROR: KEY ERROR")
        res = None

    return res

bot.run(auth_key)
