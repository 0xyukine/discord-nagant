import discord
from discord.ext import commands
from discord import app_commands

from PIL import Image, ImageDraw, ImageFont, ImageSequence

import textwrap
import asyncio
import json
import os
import io

with open('config.json', 'r') as config:
    config = json.load(config)

MY_GUILD = discord.Object(id=config['guild'])

def gif_to_frames(path, new_size = None):
    frames = []
    with Image.open(path) as im:
        if new_size == None:
            new_width, new_height = im.size
        else:
            new_width, new_height = new_size
        for i in range(im.n_frames):
            try:
                im.seek(i)
                new = Image.new("RGBA", im.size)
                new.paste(im)
                new = new.resize((new_width, new_height))
                frames.append(new)
            except EOFError:
                print(f"EOF error occured on frame {i}")
    
    return frames

def _resize(im, *, new_x = None, new_y = None, max_x = None, max_y = None):
    if new_x and new_y:
        print("Both dimensions cannot be provided")
        return None

    if new_x:
        new_y = int(im.height / im.width * new_x)
    elif new_y:
        new_x = int(im.width / im.height * new_y)

    if max_x and new_x > max_x:
        new_x = max_x
    
    if max_y and new_y > max_y:
        new_y = max_y

    im = im.resize((new_x, new_y))
    return im

@app_commands.command(name="spb")
async def bubbleify(interaction: discord.Interaction, _file: discord.Attachment):
    await interaction.response.defer()

    file_type = _file.content_type.split('/')[1]
    print(file_type)
    if file_type in ['png', 'jpeg', 'gif']:
        s_img_path = f"/temp/sent_image.{file_type}"
        await _file.save(s_img_path)                                #Save discord image locally

        #Read local images into PIL
        b_img = Image.open("/res/bubble.jpg")               #Bubble image
        s_img = Image.open(s_img_path)                              #Sent image

        new_height = int(b_img.height / b_img.width * s_img.width)  #Scale change in width with height
        #Keep default height on larger images
        if new_height > b_img.height:
            new_height = b_img.height
        #Shrink height on images with a smaller height
        if b_img.height > s_img.height:
            new_height = s_img.height
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
            frames[0].save(f"/temp/spb_image.{file_type}", save_all=True, duration=40, loop=0, append_images=frames[1:])
        else:
            await interaction.followup.send("Unknwon error occurred")
        
        file = discord.File(f"/temp/spb_image.{file_type}")
        await interaction.followup.send(file=file)
        print("file sent")
    else:
        await interaction.followup.send("Uknown or unsupported file type")

@app_commands.command(name="gg")
async def goodness(interaction: discord.Interaction, _file: discord.Attachment):
    await interaction.response.defer()

    file_type = _file.content_type.split('/')[1]
    print(file_type)
    if file_type in ['png', 'jpeg', 'gif']:
        s_img_path = f"/temp/sent_image.{file_type}"
        await _file.save(s_img_path)

        #Read local images into PIL
        g_img = Image.open("/res/goodness.gif")         #Bubble image
        s_img = Image.open(s_img_path)                              #Sent image

        duration = g_img.info['duration']
        if file_type == "gif":
            s_frames = s_img.n_frames

        #Try to fit image nicely to template
        # new_height = int(s_img.height / s_img.width * 195)
        # if new_height > 230:
        #     new_height = 230

        # new_width = 195

        # s_img = s_img.resize((195, new_height))

        s_img = _resize(s_img, new_x = 195, max_x = 195, max_y = 230)
        new_width, new_height = s_img.size
        width, height = g_img.size

        frames = []

        if file_type == "png" or file_type == "jpeg":
            for i in range(g_img.n_frames):
                g_img.seek(i)
                new = Image.new("RGBA", (width, height))
                new.paste(g_img)
                new.paste(s_img,(220,270))
                frames.append(new)
            frames[0].save(f"/temp/goodness_image.gif", save_all=True, duration=duration, loop=0, append_images=frames[1:])
        elif file_type == "gif":
            frames = []
            g_frames = gif_to_frames("/res/goodness.gif")
            s_frames = gif_to_frames(s_img_path, (new_width, new_height))

            j = 0
            for i in g_frames:
                if j == len(s_frames):
                    j = 0
                new = Image.new("RGBA", (width, height))
                new.paste(i)
                # new.paste(s_frames[j],(316,186-s_img.height))
                new.paste(s_frames[j],(220,270))
                frames.append(new)
                j += 1

            frames[0].save(f"/temp/goodness_image.gif", save_all=True, duration=duration, loop=0, append_images=frames[1:])
        else:
            await interaction.followup.send("Unsupported file format")
            return
        
        file = discord.File(f"/temp/goodness_image.gif")
        await interaction.followup.send(file=file)
        print("file sent")

    else:
        await interaction.followup.send("Unknown error occurred")

@app_commands.command(name="gtm")
async def panther(interaction: discord.Interaction, _file: discord.Attachment):
    await interaction.response.defer()

    file_type = _file.content_type.split('/')[1]
    print(file_type)
    if file_type in ['png', 'jpeg', 'gif']:
        s_img_path = f"/temp/sent_image.{file_type}"
        await _file.save(s_img_path)

        #Read local images into PIL
        t_img = Image.open("/res/tchalla.gif")          #Tchalla image
        s_img = Image.open(s_img_path)                              #Sent image
        #316 114 TL
        #316 186 BL

        if file_type == "gif":
            s_frames = s_img.n_frames
            print(s_frames)

        duration = t_img.info['duration']

        if s_img.height > 72:
            new_height = 72

        new_width = int(s_img.width / s_img.height * new_height)
        if new_width > 163:
            new_width = 163

        s_img = _resize(s_img, new_y = 100, max_x = 163)
        new_width, new_height = s_img.size
        width, height = t_img.size

        frames = []

        if file_type == "png" or file_type == "jpeg":
            s_img = s_img.resize((new_width, new_height))
            for i in range(t_img.n_frames):
                t_img.seek(i)
                new = Image.new("RGBA", (width, height))
                new.paste(t_img)
                new.paste(s_img,(316,186-s_img.height))
                frames.append(new)
            frames[0].save(f"/temp/getthisman_image.gif", save_all=True, duration=duration, loop=0, append_images=frames[1:])
        elif file_type == "gif":

            frames = []
            t_frames = gif_to_frames("/res/tchalla.gif")
            s_frames = gif_to_frames(s_img_path, (new_width, new_height))

            j = 0
            for i in t_frames:
                if j == len(s_frames):
                    j = 0
                new = Image.new("RGBA", (width, height))
                new.paste(i)
                # new.paste(s_frames[j],(316,186-s_img.height))
                new.paste(s_frames[j],(316,186-s_frames[j].height))
                frames.append(new)
                j += 1

            frames[0].save(f"/temp/getthisman_image.gif", save_all=True, duration=duration, loop=0, append_images=frames[1:])
        else:
            await interaction.followup.send("Unsupported file format")
            return
        
        file = discord.File(f"/temp/getthisman_image.gif")
        await interaction.followup.send(file=file)
        print("file sent")
    else:
        await interaction.followup.send("Unknown error occurred")

@app_commands.command(name="caption")
async def caption(interaction: discord.Interaction, _file: discord.Attachment, caption: str):
    await interaction.response.defer()

    # with io.BytesIO() as image_binary:
    #     await _file.save(image_binary)
    #     image_binary.seek(0)
    #     s_img = Image.open(image_binary)

    file_type = _file.content_type.split('/')[1]
    print(file_type)
    if file_type in ['png', 'jpeg', 'gif']:
        s_img_path = f"/temp/sent_image.{file_type}"
        await _file.save(s_img_path) 
    
    s_img = Image.open(s_img_path)  

    width, height = s_img.size

    size = 30

    offset = 50
    caption_size = (width - offset) / size
    split_caption = textwrap.wrap(caption, caption_size)
    
    cap_height = (len(split_caption) * 50) + offset

    wrapped_caption = "\n".join(split_caption)

    
    font_size = (size / 60) * 100 #increases font because fonts get consistently reduced by 60%
    font = ImageFont.truetype("res/Menlo-Regular.ttf", font_size)
    im = Image.new("RGB", (width, cap_height), "white")
    d = ImageDraw.Draw(im)
    d.text((width/2,0), wrapped_caption, fill="black", anchor="ma", font=font)

    result = Image.new("RGBA", (width, height + cap_height))
    result.paste(im)
    result.paste(s_img,(0,cap_height))

    with io.BytesIO() as image_binary:
        result.save(image_binary, 'PNG')
        image_binary.seek(0)
        file=discord.File(fp=image_binary, filename='caption.png')
        await interaction.followup.send(file=file)

async def setup(bot):
    bot.tree.add_command(bubbleify, guild=MY_GUILD)
    bot.tree.add_command(goodness, guild=MY_GUILD)
    bot.tree.add_command(panther, guild=MY_GUILD)
    bot.tree.add_command(caption, guild=MY_GUILD)