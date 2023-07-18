import discord
from discord.ext import commands
from discord import app_commands

from PIL import Image

import asyncio
import json
import os

with open('config.json', 'r') as config:
    config = json.load(config)

MY_GUILD = discord.Object(id=config['guild'])

@app_commands.command(name="spb")
async def bubbleify(interaction: discord.Interaction):
    def check(m):
        if m.attachments:
            m_img = m.attachments[0]
            print(m_img.content_type)
            if m_img.content_type == "image/png" or  m_img.content_type == "image/jpeg" or m_img.content_type == "image/gif":
                return True
            else:
                return False
        else:
            return False

    await interaction.response.defer()
    await interaction.channel.send("Please post the image you would like to use", delete_after=20)
    try:
        image_message = await interaction.client.wait_for('message', timeout=30, check=check)
    except asyncio.TimeoutError:
        await interaction.followup.send("You took too long to respond", delete_after=20)
    else:
        img_mes_atch = image_message.attachments[0]
        await img_mes_atch.save(f"/mnt/e/Stuff/t_file.{img_mes_atch.content_type.split('/')[1]}")
        # await interaction.followup.send("image saved probably")

        r = "/mnt/e/Stuff/"
        b = Image.open(f"{r}bubble.jpg")
        t = Image.open(f"{r}t_file.gif")

        # b = b.resize((t.width, b.height))
        # new = Image.new(t.mode, (t.width, b.height + t.height))
        # new.paste(b, (0,0))
        # new.paste(t, (0,b.height))
        # new.save(f"{r}wwww.png")

        if img_mes_atch.content_type.split('/')[1] == 'gif':
            w = t.size[0]
            h = int(b.height / b.width * t.width) + t.size[1]

            frames = []
            for i in range(t.n_frames):
                t.seek(i)

                new = Image.new(t.mode, (w,h))
                new.paste(b.resize((t.size[0], int(b.height / b.width * t.width))), mask=b.resize((t.size[0], int(b.height / b.width * t.width))).convert("RGBA"))
                new.paste(t, (0, int(b.height / b.width * t.width)), mask=t.convert("RGBA"))
                frames.append(new)                
            frames[1].save(f"{r}wwww.gif", save_all=True, duration=100, loop=0, append_images=frames[2:])

        else:
            w = t.size[0]
            h = int(b.height / b.width * t.width) + t.size[1]
            new = Image.new(t.mode, (w,h))
            new.paste(b.resize((t.size[0], int(b.height / b.width * t.width))))
            new.paste(t, (0,int(b.height / b.width * t.width)))
            new.save(f"{r}wwww.gif")

        file = discord.File(f"{r}wwww.gif")
        await interaction.followup.send(file=file)


async def setup(bot):
    bot.tree.add_command(bubbleify, guild=MY_GUILD)