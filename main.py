#bot.py
import os
import re
import asyncio
import discord
import datetime
import traceback

from randomkana import RandomKana
from dotenv import load_dotenv, find_dotenv
rk = RandomKana()

"""
Loads in values from a local .env file
Bot will fail to function without .env file and subsequently the bot token provided within
Attempts should and will be made to prevent the necessitation of several values needing to be
supplied through the .env but the necessity of the bot token in its current form will not doubt
remain as is
"""
if find_dotenv() != "":
    load_dotenv()
    TOKEN = os.getenv('TOKEN')
    OWNER = int(os.getenv('OWNER'))
    GUILD = int(os.getenv('GUILD'))
    BOT_CHANNEL = int(os.getenv('BOT_CHANNEL'))
    ANN_CHANNEL = int(os.getenv('ANN_CHANNEL'))
    GEN_CHANNEL = int(os.getenv('GEN_CHANNEL'))
else:
    print("No .env file present in local directory, bot feautures may not work correctly")

#Boilerplate bot initialisation
intents = discord.Intents.default()
intents.members = True
intents.presences = True
client = discord.Client(intents=intents)

#Global variables
tally = {}
TERMS = []
tags = {}

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord')

    """
    Iterates through all servers the bot is a member
    and lists all the categoies, channels, and members
    of those servers. Exists mostly as a reminder and
    aid during development
    """
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

    #Confirmation and notification to discord server that the bot is online
    #await client.get_guild(GUILD).get_channel(BOT_CHANNEL).send("Bot online: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send('Hello!')

    try:
        if message.content.startswith("$") and message.channel.id != BOT_CHANNEL:
            await message.channel.send("Please refrain from calling bot commands in non bot channel")
        else:
            if message.content.startswith("$help"):
                await message.channel.send(
                    "Current commands:\n"
                    "Random kana: $JP \n"
                    "Continous random kana: $contJP \n"
                    "Clear channel: $wipe \n"
                    "boob: $boob"
                    )
            elif message.content.startswith("$JP"):
                await random_kana(message, message.author.id, False)
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
                    await random_kana(message, user.id, True)
            elif message.content.startswith("$wipe"):
                sm = await message.channel.send("Are you sure you want to proceed? Reply (Yes/No)")
                def check(m):
                    if m.reference is not None:
                        if m.reference.message_id == sm.id:
                            return message.author.id == m.author.id and message.author.id == OWNER

                msg = await client.wait_for('message', check=check)
                if msg.content == "Yes":
                    messages = await message.channel.history(limit=100).flatten()
                    await message.channel.delete_messages(messages)
                elif msg.content == "No":
                    await message.channel.send("uhhhhh ogey then")
                else:
                    await message.channel.send("you fucked up somewhere")
            elif message.content.startswith("$count"):
                await message.channel.send("Currently limits to 200")
                messages = await message.channel.history(limit=200).flatten()
                await message.channel.send("Channel currently contains {} messages".format(len(messages)))
            elif message.content.startswith("$boob"):
                await message.channel.send(
                    "What were you expecting? What could you have hoped for in response "
                    "to your petulant insistence of shoehorning the word 'boob' into every "
                    "interaction you take upon yourself to appease your childlike and underdeveloped "
                    "sense of humour? I'd genuinely ask you to tell me, but this is all purely rhetorical "
                    "as I know for a fact there is no reason behind it, and trying to find reason in a "
                    "meaningless act is an endless endeavour. So in short: go fuck yourself ( . )Y( . )"
                    )
            elif message.content.startswith("$tally"):
                if len(message.content.split()) == 1:
                    await word_tally(message)
                elif len(message.content.split()) == 2:
                    await word_tally(message, message.content.split()[1])
                elif len(message.content.split()) == 3:
                    await word_tally(message, message.content.split()[1], message.content.split()[2])
                elif message.raw_mentions and len(messgae.content.split()) - len(message.raw_mentions) == 3:
                    await word_tally(message, message.content.split()[1], message.content.split()[2], message.raw_mentions[0])
                else:
                    await word_tally(message, "help")
            elif message.content.startswith("$tag"):
                if len(message.content.split()) == 2:
                    await tag(message, message.content.split()[1])
                elif len(message.content.split()) == 4:
                    await tag(message, message.content.split()[1], message.content.split()[2], message.content.split()[3])
                else:
                    await message.channel.send("peepeepoopoo")
            elif message.content.startswith(","):
                if message.content[1:] in tags.keys():
                    await message.channel.send(tags[message.content[1:]])
    except NameError:
        await message.channel.send("Bot channel non-existant")
    except Exception as e:
        await message.channel.send("Unknown error occured:\n{}\n{}".format(e, traceback.print_exc()))

    matched_terms = re.findall(r'|'.join(TERMS), message.content, re.IGNORECASE)
    if matched_terms:
        if message.author.id not in tally.keys():
            tally[message.author.id] = {}
        for term in matched_terms:
            if term not in tally[message.author.id].keys():
                tally[message.author.id][term] = 0
            tally[message.author.id][term] += 1

async def tag(message, criteria, tag=None, link=None):
    if criteria == "help":
        await message.channel.send("$tag [help, list, add, remove] [tag] [link]\nGet tagged media by using ,[tag]")
    elif criteria == "list":
        await message.channel.send(tags)
    elif criteria == "add":
        if tag not in tags.keys():
            tags[tag] = link
        else:
            message.channel.send("Tag already in use")
    elif criteria == "remove":
        pass

async def word_tally(message, criteria=None, term=None, user=None):
    if criteria == None:
        await message.channel.send(tally)
    elif criteria == "help":
        await message.channel.send("$tally [help, list, add, user] [term] [@user,...]")
    elif criteria == "list":
        await message.channel.send(', '.join(TERMS))
    elif criteria == "add":
        TERMS.append(term)
    elif criteria == "user":
        if term != None and user != None:
            try:
                await message.channel.send(tally[user][term])
            except KeyError as e:
                await message.channel.send("User or term not found\n{}".format(e))
        else:
            await message.channel.send("$tally user [term] [@user]")
    else:
        await word_tally(message, "help")


async def random_kana(message, player_id, cont):
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
        await random_kana(message, player_id, True)
    else:
        return

@client.event
async def on_member_join(member):
    await client.get_channel(958710298729140237).send("{} https://cdn.discordapp.com/attachments/958720490334199839/987711913070845992/Tyler-_EVERYONE_BOO_shorts.mp4".format(member.mention))

client.run(TOKEN)