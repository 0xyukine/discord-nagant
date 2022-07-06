import discord

async def wipe(message, **kwargs):
	client = kwargs["client"]
	OWNER = kwargs["ids"]["OWNER"]
	sm = await message.channel.send("Are you sure you want to proceed? Reply (Yes/No)")
	def check(m):
	    if m.reference is not None:
	        if m.reference.message_id == sm.id:
	            return message.author.id == m.author.id and message.author.id == OWNER
	msg = await client.wait_for('message', check=check)
	if msg.content == "Yes":
		if len(message.content.split(" ")) > 1 and message.content.split(" ")[1].isnumeric():
			loop = messages.content.split(" ")[1]/100
		else:
			loop = 1
		for x in range(loop):
	    	messages = await message.channel.history(limit=100).flatten()
	    	await message.channel.delete_messages(messages)
	elif msg.content == "No":
	    await message.channel.send("Nevermind")
	else:
	    await message.channel.send("Invalid respone or unknown error occured")