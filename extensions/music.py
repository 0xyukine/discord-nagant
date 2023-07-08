import discord
from discord.ext import commands
from discord import app_commands

import ffmpeg
import json
import os

with open('config.json', 'r') as config:
    config = json.load(config)

MY_GUILD = discord.Object(id=config['guild'])
        
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
    async def play(self, ctx):
        #hard coded music file :p
        song = '/mnt/e/Stuff/RADIANT_FORCE.flac'
        source = source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song))
        ctx.guild.voice_client.play(source)

        await ctx.response.send_message("Playing...")
    
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