import discord
from discord.ext import commands
from discord import app_commands

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

class MyGroup(app_commands.Group):
    @app_commands.command()
    async def join(self, ctx, *, input_channel: discord.VoiceChannel = None):
        if ctx.guild.voice_client is None:
            if ctx.user.voice:
                print("User in voice channel")
                await ctx.user.voice.channel.connect()
                await ctx.response.send_message(f"Joining {ctx.user.name} in {ctx.user.voice.channel}")
            elif input_channel:
                print("Joining user specified channel")
                await input_channel.connect()
                await ctx.response.send_message(f"Joining {input_channel}...")
            else:
                await ctx.response.send_message("User not in voice channel or did not specify channel to join")

    @app_commands.command()
    async def leave(self, ctx):
        await ctx.guild.voice_client.disconnect()
        await ctx.response.send_message("Leaving...")

    @app_commands.command()
    async def play(self, ctx, music_search: str = None):
        async def play_random_song(self, ctx, music_search):
            temp_list = []
            if music_search:
                for file in music_files:
                    if re.search(f'.*{music_search}.*', file):
                        temp_list.append(file)
            
            if not temp_list:
                temp_list = music_files

            song = random.choice(temp_list)
            source = source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song))
            ctx.guild.voice_client.play(source)
            await ctx.channel.send(f"Currently playing {os.path.split(song)[-1]}...")


        await ctx.response.send_message(f"Now playing")
        await play_random_song(self, ctx, music_search)
            
    @app_commands.command()
    async def pause(self, ctx):
        ctx.guild.voice_client.pause()
        await ctx.response.send_message("Music paused")
    
    @app_commands.command()
    async def resume(self, ctx):
        ctx.guild.voice_client.resume()
        await ctx.response.send_message("Music resumed")

async def setup(bot):
    bot.tree.add_command(MyGroup(name="music"), guild=MY_GUILD)