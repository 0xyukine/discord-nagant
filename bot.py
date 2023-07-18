import discord
from discord.ext import commands
from discord import app_commands

import logging, logging.handlers
import json
import os

with open('config.json', 'r') as config:
    config = json.load(config)

MY_GUILD = discord.Object(id=config['guild'])

description = "Silly little discord bot"

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024,
    backupCount=5,
)

dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='?', description=description, intents=intents)

bot.synced = False

@bot.event
async def on_ready():
    print(f'{bot.user} online')

    # if not discord.opus.is_loaded():
    #     discord.opus.load_opus('opus')

    if not bot.synced:
        # await bot.load_extension('extensions.hello')
        # await bot.load_extension('extensions.roulette')
        # await bot.load_extension('extensions.music')
        await bot.load_extension('extensions.speechbubble')
        await bot.tree.sync(guild=MY_GUILD)
        bot.synced = True


bot.run(config['token'])