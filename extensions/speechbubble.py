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
async def bubbleify(interaction: discord.Interaction, _file: discord.Attachment):
    await interaction.response.defer()
    # def check(m):
    #     if m.attachments:
    #         m_img = m.attachments[0]
    #         print(m_img.content_type)
    #         if m_img.content_type == "image/png" or  m_img.content_type == "image/jpeg" or m_img.content_type == "image/gif":
    #             return True
    #         else:
    #             return False
    #     else:
    #         return False

    # await interaction.response.defer()
    # await interaction.channel.send("Please post the image you would like to use", delete_after=20)
    # try:
    #     message = await interaction.client.wait_for('message', timeout=30, check=check)
    # except asyncio.TimeoutError:
    #     await interaction.followup.send("You took too long to respond", delete_after=20)
    # else:
    #     image = message.attachments[0]

    file_type = _file.content_type.split('/')[1]
    print(file_type)
    if file_type in ['png', 'jpeg', 'gif']:
        s_img_path = f"/temp/sent_image.{file_type}"
        await _file.save(s_img_path)                                #Save discord image locally

        #Read local images into PIL
        b_img = Image.open("/mnt/e/Stuff/bubble.jpg")               #Bubble image
        s_img = Image.open(s_img_path)                              #Sent image

        new_height = int(b_img.height / b_img.width * s_img.width)  #Scale change in width with height
        #Keep default height on larger images
        if new_height > b_img.height:
            new_height = b_img.height
        b_img = b_img.resize((s_img.width, new_height))             #Resize the bubble image to same width as the sent image, with new scaled height

        #Dimensions for new image output
        width = s_img.width
        height = b_img.height + s_img.height

        if file_type == "png" or file_type == "jpeg":
            new = Image.new(s_img.mode, (width, height))
            new.paste(b_img)
            new.paste(s_img,(0,b_img.height))
            new.save(f"/temp/spb_image.{file_type}")
        elif file_type == "gif":
            frames = []
            for i in range(s_img.n_frames):
                s_img.seek(i)
                new = Image.new("RGBA", (width, height))
                new.paste(b_img)
                new.paste(s_img,(0,b_img.height))
                frames.append(new)
            frames[0].save(f"/temp/spb_image.{file_type}", save_all=True, duration=100, loop=0, append_images=frames[1:])
        else:
            await interaction.followup.send("Unknwon error occurred")
        
        file = discord.File(f"/temp/spb_image.{file_type}")
        await interaction.followup.send(file=file)
        print("file sent")
    else:
        await interaction.followup.send("Uknown or unsupported file type")

async def setup(bot):
    bot.tree.add_command(bubbleify, guild=MY_GUILD)