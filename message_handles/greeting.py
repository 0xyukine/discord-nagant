import discord

async def hello(message, **kwargs):
	print(message.content)
	await message.channel.send("hello")