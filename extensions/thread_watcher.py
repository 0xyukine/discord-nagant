import discord
from discord.ext import commands, tasks
from discord import app_commands

import time
import json
import threadWatcher

with open('config.json', 'r') as config:
    config = json.load(config)
ID = config['guild']
MY_GUILD = discord.Object(id=ID)

class Panopticon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        channels = self.bot.get_guild(ID).channels
        for c in channels:
            if c.name == "test":
                print("\t" "Channel: " + c.name)
                print(c.threads)
                self.channel = c

    @tasks.loop(seconds=300)
    async def fetch_updates(self):
        ti = time.time()
        print(f"{ti}: Fetching updates")
        self.tw.auto_watch()
        x = self.tw.update_watched()
        print(x)
        for board in x:
            print(board)
            for thread_id in x[board]:
                print(thread_id)
                ch_thread = [t for t in self.channel.threads if t.name == str(thread_id)]
                if not ch_thread:
                    ch_thread = await self.channel.create_thread(name=str(thread_id), type=discord.ChannelType.public_thread)
                else:
                    ch_thread = ch_thread[0]
                for post in x[board][thread_id][-50:]:
                    if post.com != None:
                        await ch_thread.send(self.tw.format_comment(post.com)[:1000])
    
    @commands.command()
    async def start_threader(self, ctx):
        self.tw = threadWatcher.ThreadWatcher(config='/bot/res')
        self.tw.update_watched()
        print("Starting")
        self.fetch_updates.start()

async def setup(bot):
    await bot.add_cog(Panopticon(bot))