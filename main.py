#bot.py
import os
import asyncio
import discord
import datetime

from randomkana import RandomKana
from dotenv import load_dotenv
load_dotenv()

rk = RandomKana()

TOKEN = os.getenv('TOKEN')
GUILD = int(os.getenv('GUILD'))
BOT_CHANNEL = int(os.getenv('BOT_CHANNEL'))
OWNER = int(os.getenv('OWNER'))

intents = discord.Intents.default()
intents.members = True
intents.presences = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord')

    for guild in client.guilds:
        print(f'Server: {guild.name}')
        for category in guild.categories:
            print(f'{category}')
            for channel in category.channels:
                print(f'\t{channel}')

        print(f"\nSever owner: {guild.owner}")
        print("\nServer members: ")
        for member in guild.members:
            print(f'{member}, {member.activity}')

    #await client.get_guild(GUILD).get_channel(BOT_CHANNEL).send("Bot online: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send('Hello!')
    elif message.content.startswith("$help"):
        await message.channel.send('Current commands: ')
    elif message.content.startswith("$JP"):
        r = rk.random()
        sent_message = await message.channel.send(r[0])
        def check(m):
            if m.reference is not None:
                if m.reference.message_id == sent_message.id:
                    return True
            return False

        msg = await client.wait_for('message', check=check)
        if msg.content == r[1][0]:
            await message.channel.send("Correct @{}".format(msg.author))
        else:
            await message.channel.send("Wrong @{}".format(msg.author))
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
            await contjp(message, user.id)
    elif message.content.startswith("$wipe"):
        sm = await message.channel.send("Are you sure you want to proceed? Reply (Yes/No)")
        def check(m):
            if m.reference is not None:
                if m.reference.message_id == sm.id:
                    return message.author.id == m.author.id and message.author.id == OWNER

        msg = await client.wait_for('message', check=check)
        if msg.content == "Yes":
            #async for x in message.channel.history(limit=200):
            #    await x.delete()
            messages = await message.channel.history(limit=100).flatten()
            await message.channel.delete_messages(messages)
        elif msg.contetn == "No":
            await message.channel.send("uhhhhh ogey then")
        else:
            await message.channel.send("you fucked up somewhere")

async def contjp(message, player_id):
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
        await message.channel.send("Wrong @{}, correct answer is {}".format(msg.author, r[1][0]))
    await contjp(message, player_id)

@client.event
async def on_member_join(member):
    await client.get_channel(958710298729140237).send("{} https://cdn.discordapp.com/attachments/958720490334199839/987711913070845992/Tyler-_EVERYONE_BOO_shorts.mp4".format(member.mention))

client.run(TOKEN)