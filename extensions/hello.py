import discord
from discord.ext import commands
from discord import app_commands

import json

with open('config.json', 'r') as config:
    config = json.load(config)

MY_GUILD = discord.Object(id=config['guild'])

@commands.command()
async def hello(ctx):
    await ctx.send(f"hewwo {ctx.author.display_name}")

@app_commands.command(name="hello")
async def slash_hello(interaction: discord.Interaction):
    await interaction.response.send_message(F"slash command hewwo {interaction.user} ^.^")

async def setup(bot):
    bot.add_command(hello)
    bot.tree.add_command(slash_hello, guild=MY_GUILD)