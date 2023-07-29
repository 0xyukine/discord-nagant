import discord
import random
import json

async def sop(message, **kwargs):
	client = kwargs["client"]

	with open('res/sop.json', 'r') as x:
		characters = json.load(x)

	chara = random.choice(list(characters.keys()))
	embed = discord.Embed(title=characters[chara]["name"])
	embed.set_image(url=characters[chara]["image"])
	embed.add_field(name=" ", value=characters[chara]["series"], inline=True)
	embed.set_footer(text="Smash or Pass")
	await message.channel.send(embed=embed)

	def check(reaction, user):
		return str(reaction.emoji) != None
	try:
		reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
	except asyncio.TimeoutError:
		pass
	else:
		if reaction.emoji == "👍":
			await message.channel.send("{} chose to smash... :face_with_raised_eyebrow:".format(user.name))
		elif reaction.emoji == "👎":
			await message.channel.send("{} chose to pass... :yawning_face:".format(user.name))