import discord
from discord.ext import commands
from discord import app_commands

import subprocess
import traceback
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
        async def play_random_song(self, ctx, music_search):
            temp_list = []
            if music_search:
                for file in music_files:
                    if re.search(f'.*{music_search}.*', file, flags=re.IGNORECASE):
                        temp_list.append(file)
            
            if not temp_list:
                temp_list = music_files

            song = random.choice(temp_list)
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song))
            ctx.guild.voice_client.play(source)

            try:
                #Excepts if audio file doesn't have a thumbnail
                thumb_check = subprocess.run(['ffmpeg', '-y', '-i', song, '-an', '-c:v', 'copy', '/temp/thumbnail.jpg'], text=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                thumbnail = discord.File('/temp/thumbnail.jpg', filename='thumb.jpg')
            except subprocess.CalledProcessError:
                thumbnail = discord.File('/mnt/e/Stuff/dfn.jpg', filename='thumb.jpg')

            #Get audio duration from ffprobe output
            pattern = re.compile("Duration:\s*([^\n\r]*[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2})")
            song_info = str(subprocess.run(['ffprobe','-i', song], capture_output=True, text=True))
            song_length = ":".join(re.search(pattern, song_info).group(1).split(":")[1:])

            embed = discord.Embed(title=os.path.split(song)[-1], description=f'00:00 / {song_length}')
            embed = embed.set_author(name='Nagant Player')
            embed = embed.set_thumbnail(url='attachment://thumb.jpg')
            embed = embed.set_footer(text=song)

            await ctx.response.send_message(file=thumbnail, embed=embed)

        await play_random_song(self, ctx, music_search)
            
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