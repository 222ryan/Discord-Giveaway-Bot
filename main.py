import discord
from discord.ext import commands
import asyncio
import random
from ruamel.yaml import YAML

yaml = YAML()

with open("./config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)

client = commands.Bot(command_prefix=config['prefix'], intents=discord.Intents.all(), case_insensitive=True)


def convert(time):
    pos = ["s", "m", "h", "d"]
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24}
    unit = time[-1]

    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2

    return val * time_dict[unit]


@client.command()
@commands.has_role(config['giveaway_role'])
async def giveaway(ctx):
    embed = discord.Embed(title=":tada: **Giveaway Setup Wizard**", description="Please answer the questions provided!")
    await ctx.send(embed=embed)

    questions = [":star:: Which channel should it be hosted in?",
                 ":star:: How long should the giveaway last? ``<s|m|h|d>``",
                 ":star:: What is the prize?"]

    answers = []

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    for i in questions:
        await ctx.send(i)

        try:
            msg = await client.wait_for('message', timeout=15.0, check=check)
        except asyncio.TimeoutError:
            embed = discord.Embed(title=":tada: **Giveaway Setup Wizard**", description=":x: You didn't answer in time!")
            await ctx.send(embed=embed)
            return
        else:
            answers.append(msg.content)

    try:
        c_id = int(answers[0][2: -1])
    except:
        embed = discord.Embed(title=":tada: **Giveaway Setup Wizard**", description=":x: You didn't specify a channel correctly!")
        await ctx.send(embed=embed)
        await ctx.send(embed=embed)
        return

    channel = client.get_channel(c_id)

    time = convert(answers[1])
    if time == -1:
        embed = discord.Embed(title=":tada: **Giveaway Setup Wizard**", description=":x: You didn't set a proper time unit!")
        await ctx.send(embed=embed)
        return
    elif time == -2:
        mbed = discord.Embed(title=":tada: **Giveaway Setup Wizard**", description=":x: Time unit **must** be an integer")
        await ctx.send(embed=embed)
        return
    prize = answers[2]

    embed = discord.Embed(title=":tada: **Giveaway Setup Wizard**", description="Okay, all set.")
    embed.add_field(name="Hosted Channel:", value=f"{channel.mention}")
    embed.add_field(name="Time:", value=f"{answers[1]}")
    await ctx.send(embed=embed)

    embed = discord.Embed(title=":tada: **GIVEAWAY**")
    embed.add_field(name="Prize", value=prize)
    embed.add_field(name="Ends In:", value=answers[1])
    msg = await channel.send(embed=embed)

    await msg.add_reaction("🎉")
    await asyncio.sleep(time)

    msg = await ctx.channel.fetch_message(msg.id)
    users = await msg.reactions[0].users().flatten()
    users.pop(users.index(client.user))

    winner = random.choice(users)

    await channel.send(f":tada: Congratulations! {winner.mention} won: **{prize}**!")


@client.command()
@commands.has_role(config['giveaway_role'])
async def reroll(ctx, channel : discord.TextChannel, id_ : int):
    try:
        msg = await channel.fetch_message(id_)
    except:
        prefix = config['prefix']
        await ctx.send(f"Incorrect usage! Do: `{prefix}reroll <Channel Name. Example: #general / general> <Giveaway messageID>` ")

    users = await msg.reactions[0].users().flatten()
    users.pop(users.index(client.user))

    winner = random.choice(users)

    await channel.send(f":tada: Congratulations! {winner.mention} won!")


client.run(config['token'])
