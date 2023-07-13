import discord
from discord.ext import commands
from discord import app_commands

from async_timeout import timeout

import subprocess
import traceback
import asyncio
import random
import eyed3
import json
import os
import re

with open('config.json', 'r') as config:
    config = json.load(config)

MY_GUILD = discord.Object(id=config['guild'])

music_files = []

for dir_path, dirs, files in os.walk('/music'):
    for file in files:
        if re.search('\.(mp3|flac)', file):
            music_files.append(f'{dir_path}/{file}')

class MusicPlayer:
    def __init__(self, ctx):
        self.bot = ctx.client
        self._guild = ctx.guild

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None
        self.volume = 1
        self.current = None

        self.counter = 1

        ctx.client.loop.create_task(self.player_loop())

    async def player_loop(self):
        print("waiting until ready")
        await self.bot.wait_until_ready()
        print(self.queue._queue)
        while not self.bot.is_closed():
            print(f"loop q print{self.queue._queue}")
            print("next clear")
            self.next.clear()

            try:
                async with timeout(300):
                    print("self queue get")
                    print(f"queue before get {self.queue._queue}")
                    source = await self.queue.get()
                    print(source)
                    print(f"queue after get {self.queue._queue}")
            except asyncio.TimeoutError:
                print("destroying")
                return self.destroy()
            except exception as e:
                print("e")

            print("aAAAAAAAAAAAAAaaaaaa")
            source.volume = self.volume

            self.current = source

            print("playing current")
            self._guild.voice_client.play(source, after=lambda _:self.bot.loop.call_soon_threadsafe(self.next.set))
            print("next wait")
            await self.next.wait()

            self.current = None

class MyGroup(app_commands.Group):
    @app_commands.command()
    async def test(self, ctx):
        self.player = MusicPlayer(ctx)
        await ctx.response.send_message("creating player", delete_after=20)

    @app_commands.command()
    async def join(self, ctx, *, input_channel: discord.VoiceChannel = None):
        if ctx.guild.voice_client is None:
            if ctx.user.voice:
                print("User in voice channel")
                await ctx.user.voice.channel.connect()
                await ctx.response.send_message(f"Joining {ctx.user.name} in {ctx.user.voice.channel}", delete_after=20)
            elif input_channel:
                print("Joining user specified channel")
                await input_channel.connect()
                await ctx.response.send_message(f"Joining {input_channel}...", delete_after=20)
            else:
                await ctx.response.send_message("User not in voice channel or did not specify channel to join", delete_after=20)

    @app_commands.command()
    async def leave(self, ctx):
        await ctx.guild.voice_client.disconnect()
        await ctx.response.send_message("Leaving...", delete_after=20)

    @app_commands.command()
    async def play(self, ctx, music_search: str = None):
        temp_list = []
        if music_search:
            for file in music_files:
                if re.search(f'.*{music_search}.*', file, flags=re.IGNORECASE):
                    temp_list.append(file)
        
        if not temp_list:
            temp_list = music_files

        song = random.choice(temp_list)
        print(song)
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song))
        await self.player.queue.put(source)
        print(f"play q print{self.player.queue._queue}")
        await ctx.response.send_message("adding to queue", delete_after=20)
    
    @app_commands.command()
    async def queue_info(self, ctx):
        await ctx.response.send_message(list(self.player.queue._queue), delete_after=20)
            
    @app_commands.command()
    async def pause(self, ctx):
        ctx.guild.voice_client.pause()
        await ctx.response.send_message("Music paused", delete_after=20)
    
    @app_commands.command()
    async def resume(self, ctx):
        ctx.guild.voice_client.resume()
        await ctx.response.send_message("Music resumed", delete_after=20)

async def setup(bot):
    bot.tree.add_command(MyGroup(name="music"), guild=MY_GUILD)