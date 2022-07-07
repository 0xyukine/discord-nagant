#bot.py
import os
import re
import time
import random
import asyncio
import discord
import datetime
import traceback
from message_handles import *
from utils import *
from dotenv import load_dotenv, find_dotenv

TIME_START = time.time()

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
        if re.search("^[a-zA-Z0-9]{24}\.?[a-zA-Z0-9]{6}\.?[a-zA-Z0-9]{27}", TOKEN) == None:
            print("Invalid token provided")
            exit()
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

validate.validate()
TERMS, tallyDict, tagsDict = saveload.load()

#Global variables
#TERMS = []
#tallyDict = {}
#tagsDict = {}

startpath = "/mnt/e/"
startdirs = ["Stuff", "Manga"]
file_list = []

commands = {
    "$hello":[greeting.hello,"says hello, what'd you expect?"],
    "$JP":[japanese.start,"Random kana"],
    "$contJP":[japanese.start,"Continous random kana"],
    "$wipe":[wipe.wipe,"Clears channel's messages"],
    "$count":[count.count,"Counts channel's messages"],
    "$boob":[boob.boob,"boob"],
    "$tally":[tally.tally,"uhh tally stuffy"],
    "$tag":[tag.start,"tag media, see '$tag help' for usage"],
    ",":[tag.start,"calls a specific tag"],
    "$roulette":[roulette.roulette, "probably pulls something illegal from my drive"]
}

TIME_INIT = time.time() - TIME_START

for item in startdirs:
    for dirpath, dirs, files in os.walk(startpath + item):
        for file in files:
            if re.search("\.jpg|\.png|\.gif|\.webm|\.mp4", file):
                if "beast" in dirpath:
                    pass
                else:
                    file_list.append("{}/{}".format(dirpath, file))

TIME_FILES = time.time() - TIME_START

@client.event
async def on_ready():
    TIME_READY = time.time() - TIME_START
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
    await client.get_channel(idsDict["LOG_CHANNEL"]).send("Bot online: {}\nTime to initialise variables: {} Time to compile directory files: {} Time for bot to 'Ready': {}"
        .format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), TIME_INIT, TIME_FILES, TIME_READY))

@client.event
async def on_message(message):
    TIME_RECEIVED = time.time()
    TIMESTAMP_RECEIVED = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if message.author == client.user:
        return
    try:
        if message.content.startswith("$") or message.content.startswith(",") and message.channel.id != idsDict["BOT_CHANNEL"]:
            await message.channel.send("Please refrain from calling bot commands in non bot channel")
        elif message.content.startswith("$"):
            command = message.content.split()[0]
            if message.content.startswith("$help"):
                output = ""
                for item in commands:
                    output = output + "{}: {} \n".format(item, commands[item][1])
                await message.channel.send(output)
            elif command in commands.keys():
                await commands[command][0](message, client=client, tally=tallyDict, TERMS=TERMS, tags=tagsDict, fl=file_list, ids=idsDict)
            TIME_PROCESSED = time.time() - TIME_RECEIVED
            await client.get_channel(idsDict["LOG_CHANNEL"]).send("Time command '{}' received: {} Message timestamp: {} Time to respond: {}".format(command, TIMESTAMP_RECEIVED, message.created_at.strftime("%Y-%m-%d %H:%M:%S"), TIME_PROCESSED))    
        elif message.content.startswith(","):
            await tag.start(message, client=client, tally=tallyDict, TERMS=TERMS, tags=tagsDict, fl=file_list, ids=idsDict)
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