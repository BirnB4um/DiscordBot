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

import module.random_screenshot as rand_screenshot
import module.youtube_downloader as yt_dl
import module.GIF_search as GIF_search


##### SETUP #####

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='.', intents=intents)


def log(text, print_to_console=False):
    log_msg = datetime.now().strftime("[%d/%m/%Y %H:%M:%S] ") + text
    with open("data/log.txt", "a") as file:
        file.write(log_msg+"\n")

    if print_to_console:
        print(log_msg)

def constrain(x, minX, maxX):
    return max(minX, min(maxX, x))

#=======================

#witze list
witze_list = []
with open("data/witze.json", "r") as file:
    witze_list = json.load(file)

#sprüche list
sprueche_list = []
with open("data/sprueche.json", "r") as file:
    sprueche_list = json.load(file)

#word list
with open("data/german.dic", "rb") as file:
    all_words = file.read().decode("latin-1")
word_list = all_words.splitlines()
word_list_lower = all_words.lower().splitlines()

# schaf-links 
sheep_links = []
with open("data/schaf_links.txt","r") as file:
    sheep_links = file.readlines()

# id lists
user_id = {"josef":762641864335556608,
        "thimo":618140491879546881,
        "philipp":335489399968104450,
        "tim":791411006513217536,
        "birnbot":955887644578046032}
                    
# florida man stories
florida_man_data = []
with open("data/florida_man.json", "r") as file:
    florida_man_data = json.load(file)


months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

sound_files = {
    "biffler":"sounds/biffler.mp3",
    "oink":"sounds/oink.wav",
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
    if not (message.author == bot.user) and not (message.author.id == user_id["thimo"]) and (message.channel.type == discord.ChannelType.private): 
        log_message = datetime.now().strftime("[%d/%m/%Y %H:%M:%S]") + f" {message.author}: {message.content}"
        user = await bot.fetch_user(user_id["thimo"])
        await user.send(f"```{log_message}```")
        with open("data/chat.txt", "a") as file:
            file.write(log_message + "\n")

    #execute command
    await bot.process_commands(message)



@bot.event
async def on_presence_update(before, after):
    # print(f"user update: {after}")
    pass

@bot.event
async def on_user_update(before, after):
    pass

@bot.event
async def on_member_ban(guild, user):
    pass

@bot.event
async def on_message_edit(before, after):
    # log(f" >> edit '{before.author.name}' message:{before.content} zu {after.content}")
    # await after.reply("edited")
    pass

@bot.event
async def on_message_delete(message):
    # log(f" >> deleted message:{message.content}")
    pass

@bot.event
async def on_reaction_add(reaction, user):
    # log(f" >> {user.name} added reaction:{reaction.message.content},{reaction.count},{reaction.emoji}")

    if reaction.emoji == "🗑️" and reaction.message.author == bot.user:
        log("deleting message")
        await reaction.message.delete()

@bot.event
async def on_reaction_remove(reaction, user):
    # log(f" >> reaction removed:{user.name},{reaction.message.content},{reaction.count},{reaction.emoji}")
    pass

@bot.event
async def on_voice_state_update(member, before, after):
    global voice_channel, voice_client, PLAYING_SOUND

    # log(f" >> voice state update:{member.name}")
    if(member == bot.user):
        pass

@bot.event
async def on_error(event, *args, **kwargs):
    if event == 'on_message':
        log(f'Unhandled message: {args[0]}\n')
    else:
        log("ERROR: other error occured!")


##### COMMANDS ######



@bot.command(name='spruch', help=' - get random spruch (.spruch [amount])')
async def spruch(ctx, amount=1):
    amount = constrain(amount, 1, 10)
    await ctx.send("\n".join([random.choice(sprueche_list) for i in range(amount)]))


@bot.command(name='joke', help=' - get random joke (.joke [amount])')
async def joke(ctx, amount=1):
    amount = constrain(amount, 1, 10)
    await ctx.send("\n\n\n".join([random.choice(witze_list) for i in range(amount)]))


@bot.command(name='florida_man', help=' - get random story about florida man (.florida_man [today] [score:100] [18+])\for example: .florida_man score:1000 18+ today  -> story about florida man today, 18+, score at least 1000')
async def florida_man(ctx, *message):

    today = False
    min_score = 0
    only_over_18 = False
    
    for msg in message:
        if msg.lower() == "today":
            today = True
        if "score:" in msg.lower():
            value = msg.lower().split(":")[1]
            try:
                min_score = int(value)
            except:
                await ctx.send(f"cannot resolve score:{msg}. score has to be an integer.")
                return

    results = []
    date_today = datetime.now().strftime("%d/%m/%Y]").split("/")

    #check stories
    for story in florida_man_data:

        #check today
        if today:
            event_time = story["time"].split(" ")
            if not( event_time[0] == months[int(date_today[1])-1] and\
                int(event_time[1][:-1]) == int(date_today[0])):
                continue

        #check score
        if story["score"] < min_score:
            continue

        #check 18+
        if only_over_18 and not story["over_18"]:
            continue

        results.append(story)


    if len(results) == 0:
        await ctx.send("no storys found.")
        return

    story = random.choice(results)
    message = f"**Title:** {story['title']}\n**Date**: {story['time']}\n**Score**: {story['score']}"
    await ctx.send(message)



@bot.command(name='thumbnail', help=' - get thumbnail of a YouTube video (.thumbnail [link])')
async def thumbnail(ctx, link=""):
    if link == "":
        await ctx.send("please provide a link (Bsp: .thumbnail https://www.youtube.com/watch?v=dQw4w9WgXcQ)")
        return

    headers = {'User-Agent': 'Chrome'}
    try:
        page = requests.get(link, headers=headers)
    except:
        await ctx.send("Error: link invalid")
        return

    soup = BeautifulSoup(page.content, "html.parser")
    thumbnail_image = soup.find("link", {"rel":"image_src"})["href"]
    await ctx.send(thumbnail_image)



@bot.command(name='screenshot', help=' - get random screenshot (.screenshot [amount])')
async def screenshot(ctx, amount=1):
    amount = constrain(amount, 1, 50)

    max_tries = 10
    sleep_between_images = 4
    sleep_between_tries = 2

    for number in range(amount):
        tries = 0
        while True:
            tries += 1
            if tries > max_tries:
                await ctx.send(f"exceeded max number of tries. Nr: {number+1}/{amount}")
                sleep(sleep_between_images)
                break

            id = rand_screenshot.get_random_id(6)
            url = rand_screenshot.get_image_url(id)
            if url == -1:
                sleep(sleep_between_tries)
                continue

            data = rand_screenshot.get_image_data(url)
            if data == -1:
                sleep(sleep_between_tries)
                continue   
            if len(data) == 503:
                sleep(sleep_between_tries)
                continue
            
            msg = f"ID: {id}, image nr.: {number+1}/{amount}, nr tries: {tries}, URL: {url}"
            if "imgur" in url:
                await ctx.send(msg)
            else:
                with open("temp/screenshot.png", 'wb') as file:
                    file.write(data)

                await ctx.send(msg, file=discord.File("temp/screenshot.png"))
            sleep(sleep_between_images)
            break


@bot.command(name='server_status', help=' - show server status (.server_status)')
async def server_status(ctx):

    CPU = psutil.cpu_percent(interval=0.5)
    RAM = psutil.virtual_memory().percent
    await ctx.send(f"**CPU**: {CPU}%\n**RAM**: {RAM}%")



@bot.command(name='delete', help=' - delete message by id (.delete [id])')
async def delete(ctx, id=0):
    if id == 0:
        return
    
    try:   
        message = await ctx.fetch_message(id)
    except:
        await ctx.send("not a valid id.")
        return

    try:
        await message.delete()
    except:
        await ctx.send("cannot delete message")


@bot.command(name='dice', help=' - roll a dice (.dice)')
async def dice(ctx):
    await ctx.send(str(random.choice(range(1, 7))))


@bot.command(name='coin', help=' - flip a coin (.coin)')
async def coin(ctx):
    if random.random() > 0.5:
        await ctx.send("Head")
    else:
        await ctx.send("Tail")


@bot.command(name='to', help=' - send a message to ... (.to [name] [message])')
async def to(ctx, name="", *message):

    if name.lower() not in user_id:
        await ctx.send(f"name '{name}' not found. try one of these: " + ", ".join(user_id.keys()))
        return
    
    message = " ".join(message)
    if message == "":
        await ctx.send("cannot send empty message")
        return

    name = name.lower()
    log(f">> send message to {name}: {message}")
    user = await bot.fetch_user(user_id[name])
    await user.send(message)


@bot.command(name='sheep', help=' - random image of a sheep (.sheep [amount])')
async def sheep(ctx, amount=1):
    amount = constrain(amount, 1, 10)
    msg = "\n".join([random.choice(sheep_links) for i in range(amount)])
    await ctx.send(msg)


@bot.command(name='gif', help=' - get random GIF of top 50 GIFs (.gif [search term])')
async def gif(ctx, *message):
    search = " ".join(message)

    if search == "":
        await ctx.send("please provide a search-term (eg. .gif uwu)")
        return
    
    gif = random.choice(GIF_search.get_list_of_gifs(search))
    log(f"sending GIF: {gif}")
    await ctx.send(gif)


@bot.command(name='set_status', help=' - change status of the bot (.status off/on)')
async def set_status(ctx, status=""):

    if status == "":
        return
    elif status.lower() == "off":
        await bot.change_presence(status=discord.Status.invisible)
        log(f"{ctx.author.name} set status to OFF")
    elif status.lower() == "on":
        await bot.change_presence(status=discord.Status.online)
        log(f"{ctx.author.name} set status to ON")


@bot.command(name='repeat', help=' - repeats the message')
async def repeat(ctx, *message):
    await ctx.send(" ".join(message))


@bot.command(name='restart', help=' - restart the bot')
async def restart(ctx):
    await bot.close()

   


# run bot
bot.run(TOKEN)
print("THE END")