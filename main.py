import discord
from discord.ext import commands
import asyncio
import random
from discord.ext.commands import CommandNotFound
from ruamel.yaml import YAML

yaml = YAML()

with open("./config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)

client = commands.Bot(command_prefix=config['prefix'], intents=discord.Intents.all(), case_insensitive=True)
client.remove_command('help')


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error


@client.event
async def on_ready():
    print('------')
    print('Online! Details:')
    print(f"Bot Username: {client.user.name}")
    print(f"BotID: {client.user.id}")
    print('------')
    for command in client.commands:
        print(f"Loaded: {command}")
    configactivity = config['bot_activity']
    activity = discord.Game(name=config['bot_status_text'])
    await client.change_presence(status=configactivity, activity=activity)


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


@client.command()
@commands.has_role(config['giveaway_role'])
async def giveaway(ctx):
    embed = discord.Embed(title=":tada: **Giveaway Setup Wizard**", description="Please answer the provided questions!")
    await ctx.send(embed=embed)

    embedq1 = discord.Embed(title=":star: | QUESTION 1", description="Which channel should it be hosted in?")
    embedq2 = discord.Embed(title=":star: | QUESTION 2", description="How long should the giveaway last? ``<s|m|h|d|w>``")
    embedq3 = discord.Embed(title=":star: | QUESTION 3", description="What is the prize?")

    questions = [embedq1,
                 embedq2,
                 embedq3]

    answers = []

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    for i in questions:
        await ctx.send(embed=i)

        try:
            msg = await client.wait_for('message', timeout=config['setup_timeout'], check=check)
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
        return

    channel = client.get_channel(c_id)

    time = convert(answers[1])
    if time == -1:
        embed = discord.Embed(title=":tada: **Giveaway Setup Wizard**", description=":x: You didn't set a proper time unit!")
        await ctx.send(embed=embed)
        return
    elif time == -2:
        embed = discord.Embed(title=":tada: **Giveaway Setup Wizard**", description=":x: Time unit **must** be an integer")
        await ctx.send(embed=embed)
        return
    prize = answers[2]

    embed = discord.Embed(title=":tada: **Giveaway Setup Wizard**", description="Okay, all set. The Giveaway will now begin!")
    embed.add_field(name="Hosted Channel:", value=f"{channel.mention}")
    embed.add_field(name="Time:", value=f"{answers[1]}")
    embed.add_field(name="Prize:", value=prize)
    await ctx.send(embed=embed)
    print(f"New Giveaway Started! Hosted By: {ctx.author.mention} | Hosted Channel: {channel.mention} | Time: {answers[1]} | Prize: {prize}")
    print("------")
    embed = discord.Embed(title=f":tada: **GIVEAWAY FOR: {prize}**", description=f"React With {config['react_emoji']} To Enter!")
    embed.add_field(name="Lasts:", value=answers[1])
    embed.add_field(name=f"Hosted By:", value=ctx.author.mention)
    msg = await channel.send(embed=embed)

    await msg.add_reaction(config['react_emoji'])
    await asyncio.sleep(time)

    new_msg = await channel.fetch_message(msg.id)
    users = await new_msg.reactions[0].users().flatten()
    users.pop(users.index(client.user))

    winner = random.choice(users)
    if config['ping_winner_message'] == True:
        await channel.send(f":tada: Congratulations! {winner.mention} won: **{prize}**!")
        print(f"New Winner! User: {winner.mention} | Prize: {prize}")
        print("------")

    embed2 = discord.Embed(title=f":tada: **GIVEAWAY FOR: {prize}**", description=f":trophy: **Winner:** {winner.mention}")
    embed2.set_footer(text="Giveaway Has Ended")
    await msg.edit(embed=embed2)


@client.command()
@commands.has_role(config['giveaway_role'])
async def reroll(ctx, channel: discord.TextChannel, id_: int):
    try:
        new_msg = await channel.fetch_message(id_)
    except:
        prefix = config['prefix']
        await ctx.send(f"Incorrect usage! Do: `{prefix}reroll <Channel Name - Must be the channel which previously held the giveaway> <messageID of the giveaway message>` ")

    users = await new_msg.reactions[0].users().flatten()
    users.pop(users.index(client.user))

    winner = random.choice(users)

    await ctx.channel.send(f":tada: The new winner is: {winner.mention}!")


@client.command()
async def help(ctx):
    if config['help_command'] == True:
        prefix = config['prefix']
        embed = discord.Embed(title="**HELP PAGE | :book:**", description="Commands & Bot Settings:")
        embed.add_field(name="Prefix:", value=f"``{prefix}``")
        embed.add_field(name="Giveaway:", value=f"``{prefix}giveaway`` *Starts the Setup Wizard*")
        embed.add_field(name="Reroll:", value=f"``{prefix}reroll <channel> <messageid>`` *Rerolls a winner*")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.channel.send(embed=embed)
    else:
        return


client.run(config['token'])
