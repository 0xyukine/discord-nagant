import discord
from discord.ext import commands, tasks
from discord import app_commands

from typing import Literal, NamedTuple

import extensions.structs
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

embed = {"color":13352355,
        "title":None,
        "description":None,
        "image":{"url":None},
        "video":{"url":None},
        "author":{"name":"Anchovy",
                "url":"https://www.youtube.com/watch?v=oczQbHlfvg0",
                "icon_url":"https://img3.gelbooru.com//samples/02/f8/sample_02f8c86b66ad0487eca49f54565f0675.jpg"}
        }

class Roulette(app_commands.Group):
    @app_commands.command()
    @app_commands.rename(is_embed='embed')
    @app_commands.describe(**param_desc)
    async def pull(self, ctx, type: Literal['all','image','video','gif'] = 'all', count: int=1, filter: str="", is_embed: Literal['false', 'true'] = 'false', filesize: app_commands.Range[int, 0, 26214400] = 8388608):
        await ctx.response.defer(thinking=True)
        files = get_file(type, count, filter, filesize)
        if not files:
            await ctx.followup.send("No results found")
            return

        for _file in files:
            if is_embed == "true":
                e = embed
                ex = re.compile(".*{}.*\.(jpg|jpeg|png|apng|gif|webp)$".format(filter), re.IGNORECASE)
                if re.search(ex, _file.filename):
                    e["title"] = _file.filename; e["description"] = _file.fp; e["image"]["url"] = f"attachment://{_file.filename}"
                else:
                    e["title"] = _file.filename; e["description"] = _file.fp; e["video"]["url"] = f"attachment://{_file.filename}"
                await ctx.channel.send(file=_file, embed=discord.Embed.from_dict(e))
            else:
                await ctx.channel.send(files=files)
                break
        await ctx.followup.send(f"{len(files)} files sent successfully")
    
    @app_commands.command(name="auto")
    async def auto(self, ctx, filter: str=""):
        await ctx.response.send_message("Starting auto roulette")
        self.auto_roulette.start(ctx.channel, filter)

    @tasks.loop(seconds=60)
    async def auto_roulette(self, channel, filter):
        _file = get_file("all",1,filter,10000000)[0]
        e = embed
        e["title"] = _file.filename; e["description"] = _file.fp; e["image"]["url"] = f"attachment://{_file.filename}"
        await channel.send(file=_file, embed=discord.Embed.from_dict(embed))

def get_file(file_type, count, filter, filesize):
    print(f"Getting file(s): {file_type}, {count}, {filter}, {filesize}")
    temp_list = file_list
    files = []

    if file_type != "all" or filter != "":
        temp_list = []
        if file_type == "image":
            ex = re.compile(".*{}.*\.(jpg|jpeg|png|apng|gif|webp)$".format(filter), re.IGNORECASE)
        if file_type == "video":
            ex = re.compile(".*{}.*\.(mp4|mkv|mov|3gp|webm)$".format(filter), re.IGNORECASE)
        if file_type == "gif":
            ex = re.compile(".*{}.*\.(apng|gif)$".format(filter), re.IGNORECASE)
        if file_type == "all":
            print("no filter")
            ex = re.compile(".*{}.*".format(filter), re.IGNORECASE)

        for file in file_list:
            if re.search(ex, file):
                temp_list.append(file)

    if not temp_list:
        return files

    for x in range(count):
        while True:
            filepath = random.choice(temp_list)
            if os.path.getsize(filepath) < filesize:
                break

        print(f"File {x}: {filepath}")
        file = discord.File(filepath, filename=os.path.basename(filepath))
        files.append(file)

    return files

async def setup(bot):
    bot.tree.add_command(Roulette(name="roulette"), guild=MY_GUILD)