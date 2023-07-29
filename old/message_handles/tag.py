import discord
from utils import saveload

async def start(message, **kwargs):
	tags = kwargs["tags"]
	if message.content.startswith("$tag"):
		if len(message.content.split()) == 2:
			await tag(message, message.content.split()[1], tags=tags)
		elif len(message.content.split()) == 4:
			await tag(message, message.content.split()[1], message.content.split()[2], message.content.split()[3], tags=tags)
		else:
			await message.channel.send("Improper command syntaxt")
	elif message.content.startswith(","):
		if message.content[1:] in tags.keys():
			if message.reference:
				await message.channel.send(tags[message.content[1:]], reference=await message.channel.fetch_message(message.reference.message_id))
			else:
				await message.channel.send(tags[message.content[1:]])

async def tag(message, criteria, tag=None, link=None, tags=None):
    if criteria == "help":
        await message.channel.send("$tag [help, list, add, remove] [tag] [link]\nGet tagged media by using ,[tag]")
    elif criteria == "list":
        await message.channel.send(list(tags))
    elif criteria == "add" or "remove":
	    if criteria == "add":
	        if tag not in tags.keys():
	            tags[tag] = link
	        else:
	            await message.channel.send("Tag already in use")
	    elif criteria == "remove":
	        tags.pop(tag)
	        await message.channel.send("{} tag removed".format(tag))
	    await saveload.save(message, tags=tags)