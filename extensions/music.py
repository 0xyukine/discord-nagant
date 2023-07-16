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

class MusicSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, user, fn):
        super().__init__(source)
        self.user = user
        self.fn = fn

    @classmethod
    async def create_source(cls, ctx, music_search: str):
        temp_list = []
        if music_search:
            for file in music_files:
                if re.search(f'.*{music_search}.*', file, flags=re.IGNORECASE):
                    temp_list.append(file)
        
        if not temp_list:
            temp_list = music_files

        song_fn = random.choice(temp_list)
        print(song_fn)
    
        return cls(discord.FFmpegPCMAudio(song_fn), user=ctx.user.display_name, fn=song_fn)

    @staticmethod
    async def create_embed(song):
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

        return {"embed":embed,"file":thumbnail}

class MusicPlayer:
    def __init__(self, ctx):
        self.bot = ctx.client
        self._guild = ctx.guild
        self._channel = ctx.channel

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None
        self.volume = 1
        self.current = None

        self.counter = 1

        ctx.client.loop.create_task(self.player_loop())

    async def player_loop(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                async with timeout(300):
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                # print("destroying")
                # return self.destroy()
                await self._guild.voice_client.disconnect()
            except exception as e:
                print("e")

            source.volume = self.volume

            self.current = source

            print("playing current")
            self._guild.voice_client.play(source, after=lambda _:self.bot.loop.call_soon_threadsafe(self.next.set))
            await self._channel.send(**await MusicSource.create_embed(source.fn))
            await self.next.wait()

            self.current = None

class Pagination(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, music_files, increment):
        super().__init__(timeout=30)
        self._ctx = interaction
        self.mf = music_files
        self.increment = increment
        self.offset = 0

    @discord.ui.button(label="<<<", style=discord.ButtonStyle.primary, custom_id="pag_forward")
    async def forward(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.offset -= self.increment
        print(f"-100 {self.offset}")
        await self.pagination_result()

    @discord.ui.button(label=">>>", style=discord.ButtonStyle.primary, custom_id="pag_backward")
    async def backward(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.offset += self.increment
        print(f"+100 {self.offset}")
        await self.pagination_result()

    @staticmethod
    async def pagination_result():
        original = await self._ctx.original_response()
        t_mf = self.mf[self.offset:]
        m_files = "\n".join(f"{os.path.split(m_file)[0]}/**{os.path.split(m_file)[1]}**" for m_file in t_mf[:increment])
        embed = discord.Embed(title="Search", description=m_files)
        await original.edit(embed=embed)

    # async def interaction_check(self, interaction: discord.Interaction):
    #     pass

    async def on_timeout(self):
        print("timed out")
        original = await self._ctx.original_response()
        await original.edit(view=None)

class Music(app_commands.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.player = None

    def get_player(self, ctx):
        if self.player is None:
            self.player = MusicPlayer(ctx)
        return self.player

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
    async def search(self, ctx, search_term: str):
        await ctx.response.defer(thinking=True)
        temp_list = []
        for file in music_files:
            if re.search(f'.*{search_term}.*', file, flags=re.IGNORECASE):
                temp_list.append(file)
        
        if not temp_list:
            return await ctx.followup.send("No matching files found", delete_after=20)
        else:
            m_files = "\n".join(f"{os.path.split(m_file)[0]}/**{os.path.split(m_file)[1]}**" for m_file in temp_list)
            # m_files = "```" + m_files[:1900] + "```"
            embed = discord.Embed(title="Search", description=m_files[:4000])
            # navigation = discord.ui.View()
            # navigation.add_item(discord.ui.Button(label="<<<", style=discord.ButtonStyle.primary, custom_id="left"))
            # navigation.add_item(discord.ui.Button(label=">>>", style=discord.ButtonStyle.primary, custom_id="right"))
            message = await ctx.followup.send(embed=embed, view=Pagination(ctx, temp_list, 30))

            # await navigation.wait()
            # if navigation.value == "left":
            #     print("left")
            # elif navigation.value == "right":
            #     print("right")
            # else:
            #     print("idk")

            # async def interaction_check(self, interaction: discord.Interaction):
            #     print("interaction")
            #     print(interaction.id)
            #     if interaction.id == "left":
            #         print("left")
            #     elif interaction.id == "right":
            #         print("right")
            #     else:
            #         print("uh oh")

    @app_commands.command()
    async def leave(self, ctx):
        await ctx.guild.voice_client.disconnect()
        await ctx.response.send_message("Leaving...", delete_after=20)

    @app_commands.command()
    async def play(self, ctx, music_search: str = None):
        source = await MusicSource.create_source(ctx, music_search)
        await self.get_player(ctx).queue.put(source)
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
    bot.tree.add_command(Music(name="music"), guild=MY_GUILD)