#bot.py
import os
import re
import random
import asyncio
import discord
import datetime
import traceback

from dotenv import load_dotenv, find_dotenv

from message_handles import *

"""
Loads in values from a local .env file
Bot will fail to function without .env file and the subsequent bot token provided within
Attempts should and will be made to prevent the necessitation of several values needing to be
supplied through the .env but the necessity of the bot token in its current form will not doubt
remain as is
"""
if find_dotenv() != "":
    load_dotenv()
    TOKEN = os.getenv('TOKEN')
    if TOKEN == None:
        print("Enter token manually:")
        TOKEN = input()
    idsDict = {
        "OWNER" : int(os.getenv('OWNER')),
        "GUILD" : int(os.getenv('GUILD')),
        "ANN_CHANNEL" : int(os.getenv('ANN_CHANNEL')),
        "BOT_CHANNEL" : int(os.getenv('BOT_CHANNEL')),
        "LOG_CHANNEL" : int(os.getenv('LOG_CHANNEL')),
        "GEN_CHANNEL" : int(os.getenv('GEN_CHANNEL'))
        }
else:
    print("No .env file present in local directory, bot feautures may not work correctly")

#Boilerplate bot initialisation
intents = discord.Intents.default()
intents.members = True
intents.presences = True
client = discord.Client(intents=intents)

#Global variables
TERMS = []
tallyDict = {}
tagsDict = {}

startpath = "/mnt/e/"
startdirs = ["Stuff", "Manga"]
file_list = []

commands = {
    "$JP":[japanese.start,"Random kana"],
    "$contJP":[japanese.start,"Continous random kana"],
    "$wipe":[wipe.wipe,"Clears channel's messages"],
    "$count":[count.count,"Counts channel's messages"],
    "$boob":[boob.boob,"boob"],
    "$tally":[tally.tally,"uhh tally stuffy"],
    "$tag":[tag.start,"tag stuff"],
    ",":[tag.start,"also tag stuff"],
    "$roulette":[roulette.roulette, "probably pulls something illegal from my drive"]
}

for item in startdirs:
    for dirpath, dirs, files in os.walk(startpath + item):
        for file in files:
            if re.search("\.jpg|\.png|\.gif|\.webm|\.mp4", file):
                if "beast" in dirpath:
                    pass
                else:
                    file_list.append("{}/{}".format(dirpath, file))

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
    command = message.content.split()[0]
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        #await message.channel.send('Hello!')
        await greeting.hello(message)

    try:
        if message.content.startswith("$") and message.channel.id != idsDict["BOT_CHANNEL"]:
            await message.channel.send("Please refrain from calling bot commands in non bot channel")
        else:
            if message.content.startswith("$help"):
                output = ""
                for item in commands:
                    output = output + "{}: {} \n".format(item, commands[item][1])
                await message.channel.send(output)
            #    await message.channel.send(
            #        "Current commands:\n"
            #        "Random kana: $JP \n"
            #        "Continous random kana: $contJP \n"
            #        "Clear channel: $wipe \n"
            #        "boob: $boob"
            #        )
            elif command in commands.keys():
                await commands[command][0](message, client=client, tally=tallyDict, TERMS=TERMS, tags=tagsDict, fl=file_list, ids=idsDict)
                #if command == "$tally":
                #    await commands[command][0](message, tallyDict, TERMS)
                #elif command == "$tag":
                #    await commands[command][0](message,tags)
                #elif command == "$"
                #else:
                #    await commands[command][0](message)
            #elif message.content.startswith("$JP") or message.content.startswith("$contJP"):
            #    await japanese.start(message)
            #elif message.content.startswith("$wipe"):
            #    await wipe.wipe(message)
            #elif message.content.startswith("$count"):
            #    await count.count(message)
            #elif message.content.startswith("$boob"):
            #    await boob.boob(message)
            #elif message.content.startswith("$tally"):
            #    await tally.tally(message)
            #elif message.content.startswith("$tag") or message.content.startswith(","):
            #    await tag.start(message)
    except NameError:
        await message.channel.send("Bot channel non-existant:\n{}\n{}".format(e, traceback.print_exc()))
    except Exception as e:
        await message.channel.send("Unknown error occured:\n{}\n{}".format(e, traceback.print_exc()))

    matched_terms = re.findall(r'|'.join(TERMS), message.content, re.IGNORECASE)
    if matched_terms:
        if message.author.id not in tallyDict.keys():
            tallyDict[message.author.id] = {}
        for term in matched_terms:
            if term not in tallyDict[message.author.id].keys():
                tallyDict[message.author.id][term] = 0
            tallyDict[message.author.id][term] += 1

@client.event
async def on_member_join(member):
    await client.get_channel(958710298729140237).send("{} https://cdn.discordapp.com/attachments/958720490334199839/987711913070845992/Tyler-_EVERYONE_BOO_shorts.mp4".format(member.mention))

client.run(TOKEN)