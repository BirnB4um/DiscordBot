import os
from discord.ext import commands
import discord
from discord import FFmpegPCMAudio
from dotenv import load_dotenv
from time import sleep
import time
from datetime import datetime
import random
import asyncio
from bs4 import BeautifulSoup
import requests
import json
import psutil

import module.random_screenshot
import module.youtube_downloader
import module.GIF_search


##### SETUP #####

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='.', intents=intents)


def log(text):
    print(datetime.now().strftime("[%d/%m/%Y %H:%M:%S]"), text)


SENDING_SCREENSHOTS = False

voice_channel = None
voice_client = None
PLAYING_SOUND = False

#=======================

#witze list
witze_list = []
with open("data/witze.json", "r") as file:
    witze_list = json.load(file)
log(f"loaded {len(witze_list)} witze")

#sprüche list
sprueche_list = []
with open("data/sprueche.json", "r") as file:
    sprueche_list = json.load(file)
log(f"loaded {len(sprueche_list)} Sprüche")

#word list
with open("data/german.dic", 'rb') as file:
    all_words = file.read().decode("latin-1")
word_list = all_words.splitlines()
word_list_lower = all_words.lower().splitlines()
log(f"loaded {len(word_list)} words into dictionary")

# schaf-links 
SENDING_SCHAFE = False
schaf_links = []
with open("data/schaf_links.txt",'r') as file:
    schaf_links = file.readlines()
log(f"loaded {len(schaf_links)} schaf links")

# id lists
user_id = {"josef":762641864335556608,
        "thimo":618140491879546881,
        "philipp":335489399968104450,
        "tim":791411006513217536,
        "birnbot":955887644578046032}
                    
# florida man stories
florida_man_data = []
with open("data/florida_man.json", 'r') as file:
    florida_man_data = json.load(file)
log(f"loaded {len(florida_man_data)} stories about florida men")


months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

sound_files = {
    "biffler":'sounds/biffler.mp3',
    "oink":'sounds/oink.wav',
    "swag":"sounds/swag.wav",
    "song":"sounds/song.wav",
    "wind":"sounds/Wind.wav",
    "wood":"sounds/wood2.wav",
    "wasser":"sounds/Wasser2.wav",
    "ghast":"sounds/Ghast.wav",
    "ghast2":"sounds/Ghast2.wav",
    "jesus" : "sounds/jesus.wav",
    "schüttellied" : "sounds/schüttellied.ogg",
    "jiggle" : "sounds/jigglejiggle.wav",
    "ansprache" : "sounds/epischeansprachevonjosef.mp3",
    "josef": "sounds/josef1.wav",
    "dune": "sounds/dune.wav",
    "nutella":"sounds/nutella.wav",
    "korn":"sounds/Korn.mp3"
    }

#=======================


##### EVENTS ######

@bot.event
async def on_ready():
    log("Bot is ready!")
    user = await bot.fetch_user(user_id["thimo"])
    await user.send("Bot Ready!")


async def on_voice_state_update(member, before, after):
    global voice_channel
    if after.channel is not None:
        voice_channel = after.channel
    else:
        voice_channel = 0

    if before.channel is not None and after.channel is None:
        await voice_channel.disconnect()
        voice_channel = 0



@bot.event
async def on_message(message):
    if (message.author is not bot.user) and (message.author.id is not user_id["thimo"]) and (message.channel.type == discord.ChannelType.private): 
        log_message = datetime.now().strftime("[%d/%m/%Y %H:%M:%S]") + f" {message.author}: {message.content}"
        user = await bot.fetch_user(user_id["thimo"])
        await user.send(f"```{log_message}```")
        with open("data/chat.txt", "a") as file:
            file.write(log_message + "\n")

    #execute command
    await bot.process_commands(message)



@bot.event
async def on_presence_update(before, after):
    print(f"user update: {after}")

@bot.event
async def on_user_update(before, after):
    pass

@bot.event
async def on_member_ban(guild, user):
    pass

@bot.event
async def on_message_edit(before, after):
    log(f" >> edit '{before.author.name}' message:{before.content} zu {after.content}")
    # await after.reply("edited")

@bot.event
async def on_message_delete(message):
    log(f" >> deleted message:{message.content}")

@bot.event
async def on_reaction_add(reaction, user):
    log(f" >> {user.name} added reaction:{reaction.message.content},{reaction.count},{reaction.emoji}")

    if reaction.emoji == "🗑️" and reaction.message.author == bot.user:
        log("deleting message")
        await reaction.message.delete()

@bot.event
async def on_reaction_remove(reaction, user):
    log(f" >> reaction removed:{user.name},{reaction.message.content},{reaction.count},{reaction.emoji}")

@bot.event
async def on_voice_state_update(member, before, after):
    global voice_channel, voice_client, PLAYING_SOUND

    log(f" >> voice state update:{member.name}")
    if(member == bot.user):
        pass

@bot.event
async def on_error(event, *args, **kwargs):
    if event == 'on_message':
        log(f'Unhandled message: {args[0]}\n')
    else:
        log("ERROR: other error occured!")


##### COMMANDS ######


@bot.command(name='test', help='a test command')
async def test(ctx):
    print(ctx)
    await ctx.send("test")

   


# run bot
bot.run(TOKEN)
print("THE END")