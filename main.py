#bot.py
import os
import re
import time
import random
import asyncio
import discord
import datetime
import traceback

from typing import List
from discord import app_commands

from utils import *
from message_handles import *
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
intents.message_content = True
client = discord.Client(intents=intents)

#Interactions
tree = app_commands.CommandTree(client)
client.synced = False

#Validate persistent files and assign global variables
validate.validate()
TERMS, tallyDict, tagsDict = saveload.load()

#Dictionary for commands and their associated method calls
commands = {
    "$hello":[greeting.hello,"says hello, what'd you expect?"],
    "$JP":[japanese.start,"Random kana"],
    "$contJP":[japanese.start,"Continous random kana"],
    "$wipe":[wipe.wipe,"Clears channel's messages"],
    "$count":[count.count,"Counts channel's messages"],
    "$boob":[boob.boob,"boob"],
    "$tally":[tally.tally,""],
    "$tag":[tag.start,"tag media, see <$tag help> for usage"],
    ",":[tag.start,"calls a specific tag"],
    "$roulette":[roulette.roulette, "probably pulls something illegal from my drive"],
    "$save":[saveload.save, "exports current state of data structures"],
    "$sop":[smashorpass.sop,""]
}

TIME_INIT = time.time() - TIME_START

#Path and select directories for file compilation
file_list = filecomp.comp("/mnt/e/", ["Stuff", "Manga"])

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
    """
    #Confirmation and notification to discord server that the bot is online
    await client.get_channel(idsDict["LOG_CHANNEL"]).send("Bot online: {}\nTime to initialise variables: {} Time to compile directory files: {} Time for bot to 'Ready': {}"
        .format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), TIME_INIT, TIME_FILES, TIME_READY))
    """

    #Command tree sync
    await client.wait_until_ready()
    if not client.synced:
        await tree.sync(guild = discord.Object(id = idsDict["GUILD"]))
        client.synced = True

@client.event
async def on_message(message):
    TIME_RECEIVED = time.time()
    TIMESTAMP_RECEIVED = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if message.author == client.user:
        return
    try:
        if message.content.startswith("$") or message.content.startswith(","):
            if message.content.startswith("$") and message.channel.id != idsDict["BOT_CHANNEL"]:
                await client.get_channel(idsDict["BOT_CHANNEL"]).send("Please refrain from calling bot commands in non bot channel {}".format(message.author.mention))
            elif message.content.startswith("$"):
                command = message.content.split()[0]
                if message.content.startswith("$help"):
                    output = "```bash\n"
                    for command, desc in commands.items():
                        output = output + "{:<10s} : \"{}\" \n".format(command, desc[1])
                    await message.channel.send(output + "```")
                elif command in commands.keys():
                    await commands[command][0](message, client=client, tally=tallyDict, TERMS=TERMS, tags=tagsDict, fl=file_list, ids=idsDict)
                elif message.content == "$test":
                    myembed = discord.Embed(
                        title="Duce",
                        description="Anchovy"
                        )
                    myembed.set_image(url="https://cdn.discordapp.com/attachments/958720490334199839/994684667640959116/mayoi_kamimaminamisaminamiwamiamiyamitamihamirami.mp4")
                    await message.channel.send(embed=myembed)
            elif message.content.startswith(","):
                await tag.start(message, client=client, tally=tallyDict, TERMS=TERMS, tags=tagsDict, fl=file_list, ids=idsDict)

            TIME_PROCESSED = time.time() - TIME_RECEIVED
            await client.get_channel(idsDict["LOG_CHANNEL"]).send("Time command '{}' received: {} Message timestamp: {} Time to respond: {}"
                .format(message.content.split()[0], TIMESTAMP_RECEIVED, message.created_at.strftime("%Y-%m-%d %H:%M:%S"), TIME_PROCESSED))    
    except NameError as e:
        print(e)
        await message.channel.send("{} not assigned\n{}".format(e.args[0], e))
    except KeyError as e:
        print(e)
        await message.channel.send("{} not assigned".format(e.args[0]))
    except Exception as e:
        print(e)
        await message.channel.send("Unknown error occured:\n{}".format(e))

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
    await client.get_channel(958710298729140237).send("{} https://cdn.discordapp.com/attachments/958720490334199839/987711913070845992/Tyler-_EVERYONE_BOO_shorts.mp4"
        .format(member.mention))

@client.event
async def on_interaction(interaction):
    if interaction.type == "InteractionType.application_command":
        print("Slash command received ", interaction.command)

"""
Slash Commands
"""

#Multi image embed that replicates the format of e.g twitter embeds
#Done by creating an embed per image
#First embed takes any additional style or formatting
#All embeds must use the same url

@tree.command(description="Test embed", guild=discord.Object(id=idsDict["GUILD"]))
async def embedtest(interaction: discord.Interaction):

    images = ["https://media.discordapp.net/attachments/993331059955601498/1038874633702744104/102160288_p0.png?width=568&height=676",
    "https://media.discordapp.net/attachments/993331059955601498/1038874634470297692/102239380_p0.png?width=568&height=676",
    "https://media.discordapp.net/attachments/993331059955601498/1038874622478778470/102214475_p0.png?width=568&height=676",
    "https://media.discordapp.net/attachments/993331059955601498/1038874619144306768/101874010_p0.png?width=568&height=676",
    "https://media.discordapp.net/attachments/993331059955601498/1038874602065113161/101743398_p0.png?width=568&height=676",
    "https://media.discordapp.net/attachments/993331059955601498/1038874595660415076/101792151_p0.png?width=568&height=676",
    "https://media.discordapp.net/attachments/993331059955601498/1038874589536727141/101981020_p0.png?width=568&height=676",
    "https://media.discordapp.net/attachments/993331059955601498/1038874578904154132/101949970_p0.png?width=568&height=676",
    "https://media.discordapp.net/attachments/993331059955601498/1038874638647840768/102262969_p0.png?width=568&height=676",
    "https://media.discordapp.net/attachments/993331059955601498/1038874643303497758/102108972_p0.png?width=568&height=676"]
    embeds = []

    embed = discord.Embed(title="Multi image embed", description=f"Number of images: {len(images)}", url="https://yukine.moe")
    for i in images:
        embed.set_image(url=i)
        embeds.append(embed)
        embed = discord.Embed(url="https://yukine.moe")

    await interaction.response.send_message(embeds=embeds)

    # a = discord.Embed(url="https://yukine.moe")
    # b = discord.Embed(url="https://yukine.moe")
    # c = discord.Embed(url="https://yukine.moe")
    # d = discord.Embed(url="https://yukine.moe")

    # a.set_image(url="https://media.discordapp.net/attachments/993331059955601498/1038874633702744104/102160288_p0.png?width=568&height=676")
    # b.set_image(url="https://media.discordapp.net/attachments/993331059955601498/1038874634470297692/102239380_p0.png?width=568&height=676")
    # c.set_image(url="https://media.discordapp.net/attachments/993331059955601498/1038874622478778470/102214475_p0.png?width=568&height=676")
    # d.set_image(url="https://media.discordapp.net/attachments/993331059955601498/1038874619144306768/101874010_p0.png?width=568&height=676")

    # await interaction.response.send_message(embeds=[a,b,c,d])

@tree.command(description="Test command", guild=discord.Object(id=idsDict["GUILD"]))
async def test(interaction: discord.Interaction, a: str):
    if a == 'armpit':
        await interaction.response.send_message('https://cdn.discordapp.com/attachments/993331059955601498/1034624122753392691/unknown.png')
    if a == 'starbucks':
        await interaction.response.send_message('https://cdn.discordapp.com/attachments/993331059955601498/1034625470169358436/unknown.png')
    if a == 'maccies':
        await interaction.response.send_message('https://cdn.discordapp.com/attachments/993331059955601498/1034625587102359602/unknown.png')

@test.autocomplete('a')
async def a_autocomplete(interaction: discord.Interaction, current: str,):# -> List[app_commands.Choice[str]]:
    choices = ['armpit', 'starbucks', 'maccies']
    return [
        app_commands.Choice(name=a, value=a)
        for a in choices if current.lower() in a.lower()
        ]

@tree.command(name="serverprofile", description="displays the server's profile", guild=discord.Object(id=idsDict["GUILD"]))
async def serverprofile(interaction: discord.Interaction):
    guild = interaction.guild
    print(guild.bitrate_limit)
    embed = discord.Embed(title=guild.name)
    embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Owner: ", value=guild.owner, inline=False)
    embed.add_field(name="No. Members: ", value=guild.member_count, inline=False)
    #embed.add_field(name=, value=, inline=)

    await interaction.response.send_message(embed=embed)

@tree.command(name="userprofile", description="displays the user's profile", guild=discord.Object(id=idsDict["GUILD"]))
async def userprofile(interaction: discord.Interaction, user:discord.Member=None):
    if user == None:
        user = interaction.guild.get_member(interaction.user.id)

    embed = discord.Embed(title=user.name)
    embed.set_thumbnail(url=user.avatar.url)
    embed.add_field(name="User tag: ", value="{}".format(user.discriminator), inline=False)
    embed.add_field(name="User id: ", value="{}".format(user.id), inline=False)
    embed.add_field(name="User created at: ", value="{}".format(user.created_at), inline=False)
    embed.add_field(name="User joined at: ", value="{}".format(user.joined_at), inline=False)

    if user.activity != None:
        for activity in user.activities:
            if type(activity) == discord.Spotify:
                embed.add_field(name="Currently listening to: ", value="{}, {} by {}".format(activity.title, activity.album, activity.artist), inline=False)
            else:
                embed.add_field(name="Currently playing: ", value="{}".format(activity.name), inline=False)

    await interaction.response.send_message(embed=embed)

@tree.command(name="roulette", description="pulls a random file from the host's local storage", guild=discord.Object(id=idsDict["GUILD"]))
async def roulette(interaction: discord.Interaction, count: int = 1, type: str = "All", filter: str = ""):

    await interaction.response.defer(thinking=True)

    if count > 10:
        count = 10

    def genresponse(count, type, filter):
        img_types = [".jpg", ".jpeg", ".png", ".apng", ".gif", ".webp"]
        vid_types = [".mp4", ".mkv", ".mov", ".3gp", ".webm"]

        img_filter = re.compile(".*{}.*\.(jpg|jpeg|png|apng|gif|webp)$".format(filter))
        vid_filter = re.compile(".*{}.*\.(mp4|mkv|mov|3gp|webm)$".format(filter))

        temp_list = file_list

        if type != "All" or filter != "":
            temp_list = []
            if type == "Image":
                ex = img_filter
            if type == "Video":
                ex = vid_filter
            if type == "All":
                ex = re.compile(".*{}.*".format(filter))

            for file in file_list:
                if re.search(ex, file):
                    temp_list.append(file)

        while True:
            filepath = random.choice(temp_list)
            print(filepath)
            if os.path.getsize(filepath) < 8388608:
                break
        file = discord.File(filepath)
        if re.search(vid_filter, filepath):
            return({'file':file})
        elif re.search(img_filter, filepath):
            embed = discord.Embed(title=filepath.split("/")[-1], description="/".join(filepath.split("/")[3:-1]))
            embed.set_author(name="Anchovy", url="https://www.youtube.com/watch?v=oczQbHlfvg0", icon_url="https://img3.gelbooru.com//samples/02/f8/sample_02f8c86b66ad0487eca49f54565f0675.jpg")
            embed.set_image(url="attachment://{}".format(filepath.split("/")[-1]))

            return({'file':file,'embed':embed})
        else:
            return({'content':"unknown filetype"})

    await interaction.followup.send(**genresponse(count, type, filter))
    
    for x in range(count-1):
        await client.get_channel(interaction.channel_id).send(**genresponse(count, type, filter))

@roulette.autocomplete('type')
async def types_autocomplete(interaction: discord.Interaction, current: str,):
    types = ['Any', 'Video', 'Image']
    return [
        app_commands.Choice(name=type, value=type)
        for type in types if current.lower() in type.lower()
        ]

@tree.command(name="purge", description="clears a channe's messages", guild=discord.Object(id=idsDict["GUILD"]))
async def purge(interaction: discord.Interaction, count: int = 100):
    for x in range(int(count/100)):
        messages = [message async for message in client.get_channel(interaction.channel_id).history(limit=100)]
        await client.get_channel(interaction.channel_id).delete_messages(messages)
    messages = [message async for message in client.get_channel(interaction.channel_id).history(limit=100)]
    await client.get_channel(interaction.channel_id).delete_messages(messages)

@tree.command(name="dumbpurge", description="clears a channe's messages", guild=discord.Object(id=idsDict["GUILD"]))
async def dumbpurge(interaction: discord.Interaction, count: int = 99):
    async for message in client.get_channel(interaction.channel_id).history(limit=count%100):
        await message.delete()

client.run(TOKEN)