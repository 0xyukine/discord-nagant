import discord
from discord.ext import commands
from discord import app_commands

from typing import Literal, NamedTuple

import random
import json
import os
import re

print("Opening config")
with open('config.json', 'r') as config:
    config = json.load(config)

MY_GUILD = discord.Object(id=config['guild'])

print("Compiling file list")
file_list = []
with open('res/filesources.json', 'r') as x:
    file_sources = json.load(x)

for start_path in file_sources["sources"]:
    for filtered_dir in file_sources["sources"][start_path]:
        for dir_path, dirs, files in os.walk(start_path + filtered_dir):
            for file in files:
                if re.search("\.(jpg|jpeg|png|apng|gif|webp|mp4|mkv|mov|3gp|webm)", file):
                    if any(blacklist in dir_path for blacklist in file_sources["blacklist"]):
                        pass
                    else:
                        file_list.append("{}/{}".format(dir_path, file))
print("file list finished compiling")

param_desc = {"count":"Numbers of files to send at once", 
        "filter":"Phrase to restrict files returned to", 
        "is_embed":"Separate posting and additional information", 
        "filesize":"Maximum filesize limit, default 8MB, hard limit 25MB, bigger limits will slow down returns"}

class Roulette(app_commands.Group):
    @app_commands.command()
    @app_commands.rename(is_embed='embed')
    @app_commands.describe(**param_desc)
    async def all(self, ctx, count: int=1, filter: str="", is_embed: Literal['false', 'true'] = 'false', filesize: app_commands.Range[int, 0, 26214400] = 8388608):
        await ctx.response.defer(thinking=True)
        await get_file(ctx, "all", count, filter, is_embed, filesize)

    @app_commands.command()
    @app_commands.rename(is_embed='embed')
    @app_commands.describe(**param_desc)
    async def image(self, ctx, count: int=1, filter: str="", is_embed: Literal['false', 'true'] = 'false', filesize: app_commands.Range[int, 0, 26214400] = 8388608):
        await ctx.response.defer(thinking=True)
        await get_file(ctx, "image", count, filter, is_embed, filesize)

    @app_commands.command()
    @app_commands.rename(is_embed='embed')
    @app_commands.describe(**param_desc)
    async def gif(self, ctx, count: int=1, filter: str="", is_embed: Literal['false', 'true'] = 'false', filesize: app_commands.Range[int, 0, 26214400] = 8388608):
        await ctx.response.defer(thinking=True)
        await get_file(ctx, "gif", count, filter, is_embed, filesize)

    @app_commands.command()
    @app_commands.rename(is_embed='embed')
    @app_commands.describe(**param_desc)
    async def video(self, ctx, count: int=1, filter: str="", is_embed: Literal['false', 'true'] = 'false', filesize: app_commands.Range[int, 0, 26214400] = 8388608):
        await ctx.response.defer(thinking=True)
        await get_file(ctx, "video", count, filter, is_embed, filesize)

async def get_file(ctx, file_type, count, filter, is_embed, filesize):
    print(file_type, count, filter, is_embed, filesize)
    print("Getting file")
    temp_list = file_list

    img_filter = re.compile(".*{}.*\.(jpg|jpeg|png|apng|gif|webp)$".format(filter), re.IGNORECASE)
    vid_filter = re.compile(".*{}.*\.(mp4|mkv|mov|3gp|webm)$".format(filter), re.IGNORECASE)
    gif_filter = re.compile(".*{}.*\.(apng|gif)$".format(filter), re.IGNORECASE)

    if file_type != "all" or filter != "":
        temp_list = []
        if file_type == "image":
            ex = img_filter
        if file_type == "video":
            ex = vid_filter
        if file_type == "gif":
            ex = gif_filter
        if file_type == "all":
            print("no filter")
            ex = re.compile(".*{}.*".format(filter), re.IGNORECASE)

        for file in file_list:
            if re.search(ex, file):
                temp_list.append(file)

    if not temp_list:
        await ctx.followup.send("No results found")
        return

    files = []

    for x in range(count):
        while True:
            filepath = random.choice(temp_list)
            print(filepath)
            if os.path.getsize(filepath) < filesize:
                break

        file = discord.File(filepath)
        files.append(file)

        embed = discord.Embed(title=filepath.split("/")[-1], description="/".join(filepath.split("/")[3:-1]))
        embed.set_author(name="Anchovy", url="https://www.youtube.com/watch?v=oczQbHlfvg0", icon_url="https://img3.gelbooru.com//samples/02/f8/sample_02f8c86b66ad0487eca49f54565f0675.jpg")
        embed.set_image(url="attachment://{}".format(filepath.split("/")[-1]))

    if is_embed == "true":
        await ctx.followup.send(file=files[0], embed=embed)
        for x in range(len(files[1:])):
            await ctx.channel.send(file=files[1:][x], embed=embed)
    elif is_embed == "false":
        await ctx.followup.send(files=files[:10])
    return

async def setup(bot):
    bot.tree.add_command(Roulette(name="roulette"), guild=MY_GUILD)