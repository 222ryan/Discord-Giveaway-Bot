import discord
from discord.ext import commands
from ruamel.yaml import YAML

yaml = YAML()

with open("./config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)

class help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_role(config['giveaway_role'])
    async def help(self, ctx):
        if config['help_command'] == True:
            prefix = config['prefix']
            embed = discord.Embed(title="**HELP PAGE | :book:**",
                                  description=f"Commands & Information. **Prefix**: ``{prefix}``")
            embed.add_field(name="Giveaway:", value=f"``{prefix}giveaway`` *Starts the Setup Wizard*")
            embed.add_field(name="Reroll:", value=f"``{prefix}reroll <channel> <messageid>`` *Rerolls a winner*")
            embed.set_thumbnail(url=ctx.guild.icon_url)
            await ctx.channel.send(embed=embed)
        else:
            return



def setup(client):
    client.add_cog(help(client))