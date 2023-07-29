import discord
from daily_kana import randomkana

rk = randomkana.RandomKana()

async def start(message, **kwargs):
    client = kwargs["client"]
    if message.content.startswith("$JP"):
        await random_kana(message, client, message.author.id, False)
    elif message.content.startswith("$contJP"):
        await message.channel.send("Game will continue until user types 'Break', react to this message to begin")
        def check(reaction, user):
            return str(reaction.emoji) != None
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await message.channel.send("Nevermind then I guess")
        else:
            await message.channel.send("Okay")
            await random_kana(message, client, user.id, True)

async def random_kana(message, client, player_id, cont):
    r = rk.random()
    sent_message = await message.channel.send(r[0])
    def check(m):
        return m.author.id == player_id
    msg = await client.wait_for('message', check=check)
    if msg.content == "Break":
        return
    if msg.content == r[1][0]:
        await message.channel.send("Correct {}".format(msg.author.mention))
    else:
        await message.channel.send("Wrong {}, correct answer is {}".format(msg.author.mention, r[1][0]))
    if cont == True:
        await random_kana(message, client, player_id, True)
    else:
        return