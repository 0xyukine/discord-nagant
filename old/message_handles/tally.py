import discord

async def tally(message, **kwargs):
    tally = kwargs["tally"]
    TERMS = kwargs["TERMS"]
    if len(message.content.split()) == 1:
        await word_tally(message, tally=tally, TERMS=TERMS)
    elif len(message.content.split()) == 2:
        await word_tally(message, message.content.split()[1], tally=tally, TERMS=TERMS)
    elif len(message.content.split()) == 3:
        await word_tally(message, message.content.split()[1], message.content.split()[2], tally=tally, TERMS=TERMS)
    elif message.raw_mentions and len(messgae.content.split()) - len(message.raw_mentions) == 3:
        await word_tally(message, message.content.split()[1], message.content.split()[2], message.raw_mentions[0], tally=tally, TERMS=TERMS)
    else:
        await word_tally(message, "help")

async def word_tally(message, criteria=None, term=None, user=None, tally=None, TERMS=None):
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