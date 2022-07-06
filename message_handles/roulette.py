import discord
import random

async def roulette(message, **kwargs):
	file_list = kwargs["fl"]
	if len(message.content.split(" ")) > 1 and message.content.split(" ")[1].isnumeric():
		count = int(message.content.split(" ")[1])
		if count > 10:
			count = 10
	elif len(message.content.split(" ")) > 1 and message.content.split(" ")[1] == "count":
		await message.channel.send(len(file_list))
		return
	else:
		count = 1
	for x in range(count):
		filepath = random.choice(file_list)
		file = discord.File(filepath)
		await message.channel.send("{}".format(filepath), file=file)