import os
from os import listdir
import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound, ChannelNotFound
from ruamel.yaml import YAML
from dotenv import load_dotenv


load_dotenv()
yaml = YAML()

with open("./config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)

client = commands.Bot(command_prefix=config['prefix'], intents=discord.Intents.all(), case_insensitive=True)
client.remove_command('help')

def convert(time):
    pos = ["s", "m", "h", "d", "w"]
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24, "w": 3600 * 24 * 7}
    unit = time[-1]

    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2

    return val * time_dict[unit]


@client.event
async def on_ready():
    print('------')
    print('Online! Details:')
    print(f"Bot Username: {client.user.name}")
    print(f"BotID: {client.user.id}")
    print('------')
    for command in client.commands:
        print(f"Loaded: {command}")
    print("------")
    configactivity = config['bot_activity']
    activity = discord.Game(name=config['bot_status_text'])
    await client.change_presence(status=configactivity, activity=activity)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    if isinstance(error, ChannelNotFound):
        await ctx.send("Channel was not found!")
        return
    raise error

for fn in listdir("Commands"):
    if fn.endswith(".py"):
        client.load_extension(f"Commands.{fn[:-3]}")

token = os.getenv("DISCORD_TOKEN")
client.run(token)
