import discord

async def count(message, **kwargs):
	await message.channel.send("Currently limits to 200")
	messages = await message.channel.history(limit=200).flatten()
	await message.channel.send("Channel currently contains {} messages".format(len(messages)))