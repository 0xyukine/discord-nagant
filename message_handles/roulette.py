import discord
import random

async def roulette(message, **kwargs):
	#file_list = kwargs["fl"]
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
		#await message.channel.send("{}".format(filepath), file=file)
		embed = discord.Embed(title=filepath.split("/")[-1], description="/".join(filepath.split("/")[3:-1]))
		embed.set_author(name="Anchovy", url="https://www.youtube.com/watch?v=oczQbHlfvg0", icon_url="https://img3.gelbooru.com//samples/02/f8/sample_02f8c86b66ad0487eca49f54565f0675.jpg")
		embed.set_image(url="attachment://{}".format(filepath.split("/")[-1]))

		await message.channel.send(file=file, embed=embed)