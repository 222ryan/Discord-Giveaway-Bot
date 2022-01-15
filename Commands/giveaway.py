from main import convert
import discord
from discord.ext import commands
import asyncio
import random
from ruamel.yaml import YAML

yaml = YAML()

with open("./config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)

class reroll(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_role(config['giveaway_role'])
    async def giveaway(self, ctx):
        timeout = config["setup_timeout"]
        embedq1 = discord.Embed(title="<a:HyperTada:812709871291334666> | SETUP WIZARD",
                                description=f"Welcome to the Setup Wizard. Answer the following questions within ``{timeout}`` Seconds!")
        embedq1.add_field(name=":star: | Question 1",
                          value="Where should we host the Giveaway?\n\n **Example**: ``#General``")
        embedq2 = discord.Embed(title=":gift: | SETUP WIZARD",
                                description="Great! Let's move onto the next question.")
        embedq2.add_field(name=":star: | Question 2",
                          value="How long should it last? ``<s|m|h|d|w>``\n\n **Example**:\n ``1d``")
        embedq3 = discord.Embed(title=":gift: | SETUP WIZARD",
                                description="Awesome. You've made it to the last question!")
        embedq3.add_field(name=":star: | Question 2",
                          value="What is the prize the winner will receive?\n\n **Example**:\n ``NITRO``")

        questions = [embedq1,
                     embedq2,
                     embedq3]

        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        for i in questions:
            await ctx.send(embed=i)

            try:
                msg = await self.client.wait_for('message', timeout=config['setup_timeout'], check=check)
            except asyncio.TimeoutError:
                embed = discord.Embed(title="<a:HyperTada:812709871291334666> **Giveaway Setup Wizard**",
                                      description=":x: You didn't answer in time!")
                await ctx.send(embed=embed)
                return
            else:
                answers.append(msg.content)

        try:
            c_id = int(answers[0][2: -1])
        except:
            embed = discord.Embed(title="<a:HyperTada:812709871291334666> **Giveaway Setup Wizard**",
                                  description=":x: You didn't specify a channel correctly!")
            await ctx.send(embed=embed)
            return

        channel = self.client.get_channel(c_id)

        time = convert(answers[1])
        if time == -1:
            embed = discord.Embed(title="<a:HyperTada:812709871291334666> **Giveaway Setup Wizard**",
                                  description=":x: You didn't set a proper time unit!")
            await ctx.send(embed=embed)
            return
        elif time == -2:
            embed = discord.Embed(title="<a:HyperTada:812709871291334666> **Giveaway Setup Wizard**",
                                  description=":x: Time unit **MUST** be an integer")
            await ctx.send(embed=embed)
            return
        prize = answers[2]

        embed = discord.Embed(title="<a:HyperTada:812709871291334666> **Giveaway Setup Wizard**",
                              description="Okay, all set. The Giveaway will now begin!")
        embed.add_field(name="Hosted Channel:", value=f"{channel.mention}")
        embed.add_field(name="Time:", value=f"{answers[1]}")
        embed.add_field(name="Prize:", value=prize)
        await ctx.send(embed=embed)
        print(
            f"New Giveaway Started! Hosted By: {ctx.author.mention} | Hosted Channel: {channel.mention} | Time: {answers[1]} | Prize: {prize}")
        print("------")
        embed = discord.Embed(title=f"<a:HyperTada:812709871291334666> **GIVEAWAY FOR: {prize}**",
                              description=f"React With {config['react_emoji']} To Participate!")
        embed.add_field(name="Lasts:", value=answers[1])
        embed.add_field(name=f"Hosted By:", value=ctx.author.mention)
        msg = await channel.send(embed=embed)

        await msg.add_reaction(config['react_emoji'])
        await asyncio.sleep(time)

        new_msg = await channel.fetch_message(msg.id)
        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.client.user))

        winner = random.choice(users)
        if config['ping_winner_message'] == True:
            await channel.send(f":tada: Congratulations! {winner.mention} won: **{prize}**!")
            print(f"New Winner! User: {winner.mention} | Prize: {prize}")
            print("------")

        embed2 = discord.Embed(title=f"<a:HyperTada:812709871291334666> **GIVEAWAY FOR: {prize}**",
                               description=f":trophy: **Winner:** {winner.mention}")
        embed2.set_footer(text="Giveaway Has Ended")
        await msg.edit(embed=embed2)



def setup(client):
    client.add_cog(reroll(client))
