import discord
from discord.ext import commands, tasks
from discord import app_commands

from typing import Literal, NamedTuple

#import extensions.structs
import subprocess
import threading
import sqlite3
import random
import json
import time
import os
import re

con = sqlite3.connect("/database/bot.db")
cur = con.cursor()

print("Opening config")
with open('config.json', 'r') as config:
    config = json.load(config)

MY_GUILD = discord.Object(id=config['guild'])

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

@app_commands.command(name="buildfilelist")
async def build_file_db(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    #Splits the passed list into equal parts of size n
    def chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]


    def format(chunk, thread_no):
        start = time.time()
        data = []
        for i in chunk:
            data.append((subprocess.run(["md5sum",i],capture_output=True).stdout.decode("UTF-8").split(" ")[0],
                        os.path.splitext(os.path.basename(i))[0],
                        i,
                        os.path.splitext(os.path.basename(i))[1],
                        os.path.getsize(i)/(1024*1024)))
        print(f"thread {thread_no} finished in {time.time() - start}")
        results[thread_no] = data

    file_list = []
    thread_count = 12
    threads = [None] * thread_count
    results = [None] * thread_count

    start = time.time()
    print("Compiling file list")
    with open('res/filesources.json', 'r') as x:
        file_sources = json.load(x)

    for start_path in file_sources["sources"]:
        for filtered_dir in file_sources["sources"][start_path]:
            for dir_path, dirs, files in os.walk(start_path + filtered_dir):
                os.listdir(start_path + filtered_dir)
                for file in files:
                    if re.search("\.(jpg|jpeg|png|apng|gif|webp|mp4|mkv|mov|3gp|webm)", file):
                        if any(blacklist in dir_path for blacklist in file_sources["blacklist"]):
                            pass
                        else:
                            file_list.append("{}/{}".format(dir_path, file))
    end = time.time() - start
    print("file list finished compiling: ", end, len(file_list))

    #Yields chunks of the file list split by the length of the list divided by the number of threads rounded up
    for i, chunk in enumerate(chunks(file_list,-(-len(file_list)//thread_count))):
        threads[i] = threading.Thread(target=format, args=(chunk,i))
        threads[i].start()

    for i in range(len(threads)):
        threads[i].join()

    table_name = "files"
    files_schema = (f'CREATE TABLE {table_name}(md5 TEXT PRIMARY KEY,'
                'name TEXT DEFAULT \"\",'
                'uri TEXT DEFAULT \"\",'
                'ext TEXT DEFAULT \"\",'
                'size REAL DEFAULT 0)')

    start = time.time()

    #Check if table already exists
    res = cur.execute(f"SELECT name FROM sqlite_master WHERE NAME='{table_name}'")
    if res.fetchone() is None:
        cur.execute(files_schema)

    for i in results:
        for j in i:
            try:
                cur.execute(f"INSERT INTO {table_name}(md5,name,uri,ext,size) VALUES (?,?,?,?,?)",j)
            except sqlite3.Error:
                # await interaction.channel.send(f"Duplicate hash: {j}")
                pass
    con.commit()
    end = time.time() - start
    await interaction.followup.send(f"finished building db in {end}")

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

        print(type(filepath))
        print(f"File {x}: {filepath}")
        file = discord.File(filepath, filename=os.path.basename(filepath))
        files.append(file)

    return files

async def setup(bot):
    bot.tree.add_command(Roulette(name="roulette"), guild=MY_GUILD)
    bot.tree.add_command(build_file_db, guild=MY_GUILD)