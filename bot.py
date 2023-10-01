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

import random_screenshot
import youtube_downloader
import GIF_search

os.system("cls")

##### SETUP #####

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='.', intents=intents)


def log(text):
    print(datetime.now().strftime("[%d/%m/%Y %H:%M:%S]"), text)


SENDING_SCREENSHOTS = False
SHUTDOWN = False

#=======================
#word list
word_list = []
with open("./data/german.dic", 'r') as file:
    word_list = file.read().splitlines()

with open("./data/other_words.txt", 'r') as file:
    w = file.read().splitlines()
    [word_list.append(i) for i in w]

word_list_lower = [word.lower() for word in word_list]

log(f"loaded {len(word_list)} words into dictionary")

#=======================
# schaf-links 
log("schaf_links werden geladen...")
SENDING_SCHAFE = False
schaf_links = []
with open("data/schaf_links.txt",'r') as file:
    schaf_links = file.readlines()

log(f"loaded {len(schaf_links)} schaf links")

#=======================
# id lists
user_id = {"josef":762641864335556608,
        "thimo":618140491879546881,
        "philipp":335489399968104450,
        "tim":791411006513217536,
        "birnbot":955887644578046032}
        
text_channel_id = {"allgemein":819099151429271555, "screenshots":955948966380449823,
           "müll":819118562874490891, "links":819495379128680478, "schule":819107525482774558,
           "emoji":819130821523800084, "morse":819146403816931361, "schaf":822006051230056478,
           "zahlen":821648945637490749, "minecraft":893212180130971658, "meme":921413108826796073}

voice_channel_id = {"ks_krasse_loge" : 819132948003029022, "allgemeine_loge" : 834806819133849603,
                    "8_bit" : 836949502102339645, "minecraft":915583439800000532,
                    "ecke":834806307563372584, "kurz_weg":914130684111622205,
                    "wc":937800824099315713, "keller":925172665667420180,
                    "verbannung":836958553230409808, "verbannung_in_der_verbannung":836959365990449152,
                    "pornokeller":927717321756270702}
                    
#=======================

florida_man_data = []
with open("data/florida_man.json", 'r') as file:
    florida_man_data = json.load(file)

log(f"loaded {len(florida_man_data)} stories about florida men")

#=======================

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

#=======================

voice_channel = 0
PLAYING_SOUND = False

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
    "nutella":"sounds/nutella.wav"
    }

#=======================


##### EVENTS ######

@bot.event
async def on_ready():

    log("Bot is ready!")

async def on_voice_state_update(member, before, after):
    global voice_channel
    if after.channel is not None:
        voice_channel = after.channel
    else:
        voice_channel = 0

    if before.channel is not None and after.channel is None:
        await voice_channel.disconnect()
        voice_channel = 0

#on_message blockiert alle command-events
# @bot.event
# async def on_message(message):
#     log(message.content)

@bot.event
async def on_user_update(before, after):
    pass

@bot.event
async def on_member_ban(guild, user):
    pass

@bot.event
async def on_message_edit(before, after):
    log(after.content)
    #log(f" >> edit '{before.author.name}' message:{before.content} zu {after.content}")
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
    log(f" >> voice state update:{member.name}")

@bot.event
async def on_error(event, *args, **kwargs):
    if event == 'on_message':
        log(f'Unhandled message: {args[0]}\n')
    else:
        log("ERROR: other error occured!")


##### COMMANDS ######

@bot.command(name='join', help=' - join current vc (.join)')
async def join(ctx):
    global voice_channel, PLAYING_SOUND
    log(f">> {ctx.author.name}: {ctx.message.content}")

    channel = ctx.author.voice.channel
    if channel == None:
        await ctx.send("you need to join a voicechannel first")
        return

    if voice_channel != 0:
        voice_channel.stop()

    if voice_channel != 0:
        await voice_channel.disconnect()
        voice_channel = 0

    PLAYING_SOUND = False
    voice_channel = await channel.connect()
    
@bot.command(name='leave', help=' - leave vc (.leave)')
async def leave(ctx):
    global voice_channel, PLAYING_SOUND
    log(f">> {ctx.author.name}: {ctx.message.content}")

    PLAYING_SOUND = False
    if voice_channel != 0:
        voice_channel.stop()
        await voice_channel.disconnect()
        voice_channel = 0
    
@bot.command(name='play', help=f" - play sounds if joined vc first (.play [sound])")
async def play(ctx, sound=""):
    global voice_channel, PLAYING_SOUND
    log(f">> {ctx.author.name}: {ctx.message.content}")

    if voice_channel != 0:
        if not PLAYING_SOUND:
            if sound in list(sound_files.keys()):
                PLAYING_SOUND = True
                voice_channel.play(FFmpegPCMAudio(sound_files[sound]))

                while voice_channel.is_playing() or voice_channel.is_paused():
                    await asyncio.sleep(0.5)

                log("stopped playing")
            else:
                log("sound not in list")
                await ctx.send(f"sound not in list. try one of these:\n"+ "\n".join(f"-{sound}" for sound in list(sound_files.keys())))

            PLAYING_SOUND = False
    else:
        await ctx.send("bot needs to join first (.join)")

    
@bot.command(name='stop', help=' - stop current sound (.stop)')
async def stop(ctx):
    global voice_channel, PLAYING_SOUND
    log(f">> {ctx.author.name}: {ctx.message.content}")

    PLAYING_SOUND = False
    if voice_channel != 0:
        voice_channel.stop()
    
@bot.command(name='pause', help=' - pause current sound (.pause)')
async def pause(ctx):
    global voice_channel
    log(f">> {ctx.author.name}: {ctx.message.content}")

    if voice_channel != 0 and PLAYING_SOUND:
        voice_channel.pause()
    
@bot.command(name='resume', help=' - resume current sound (.resume)')
async def resume(ctx):
    global voice_channel
    log(f">> {ctx.author.name}: {ctx.message.content}")

    if voice_channel != 0 and PLAYING_SOUND:
        voice_channel.resume()
    

@bot.command(name='shutdown', help=' - trigger bot shutdown (.shutdown)')
async def shutdown(ctx):
    global SHUTDOWN
    log(f">> {ctx.author.name}: {ctx.message.content}")

    if ctx.author.name == "BirnBaum":
        SHUTDOWN = True
        await bot.close()
    else:
        await ctx.send("nenene so nich mein Freund")

@bot.command(name='florida_man', help=' - get random story about florida man (.florida_man [today] [score:100] [18+])\nBsp: .florida_man score:1000 18+ today  -> story about florida man today, 18+, score at least 100')
async def florida_man(ctx):
    log(f">> {ctx.author.name}: {ctx.message.content}")

    data = florida_man_data

    today = False
    min_score = 0
    only_over_18 = False
    for command in ctx.message.content.split(" ")[1:]:
        if command[:6].lower() == "score:":
            min_score = int(command.split(":")[1])
        elif command.lower() == "today":
            today = True
        elif command.lower() == "18+":
            only_over_18 = True

    #check today
    data_copy = data.copy()
    data = []
    if today:
        date = datetime.now().strftime("%d/%m/%Y]").split("/")
        for event in data_copy:
            if event["time"].split(" ")[0] == months[int(date[1])-1] and\
                int(event["time"].split(" ")[1][:-1]) == int(date[0]):
                data.append(event)
    else:
        data = data_copy.copy()

    #check score
    data_copy = data.copy()
    data = []
    if min_score > 0:
        for event in data_copy:
            if event["score"] > min_score:
                data.append(event)
    else:
        data = data_copy.copy()

    #check over 18
    data_copy = data.copy()
    data = []
    if only_over_18:
        for event in data_copy:
            if event["over_18"]:
                data.append(event)
    else:
        data = data_copy.copy()

    log(f"found {len(data)} stories")
    if len(data) == 0:
        await ctx.send("no story found.")
        return

    random.seed(time.time())
    data = random.choice(data)

    message = f"**Title:** {data['title']}\n**Date**: {data['time']}\n**Score**: {data['score']}"#\nLink: {data['url']}
    await ctx.send(message)





@bot.command(name='thumbnail', help=' - get thumbnail of a YouTube video (.thumbnail [link])')
async def thumbnail(ctx, link=""):
    log(f">> {ctx.author.name}: {ctx.message.content}")

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

@bot.command(name='words_with', help=' - check words with given letters (.words_with [letters])')
async def in_words(ctx, letters=""):
    log(f">> {ctx.author.name}: {ctx.message.content}")

    if letters == "":
        return
    letters = letters.lower()
    anzahl = 0
    l = []
    c = 0
    for word in word_list_lower:
        if letters in word:
            if c < 10:
                l.append(word)
                c += 1
            anzahl += 1
    await ctx.send(f"{anzahl} wörter mit '{letters}'")

    await ctx.send("".join(w + "\n" for w in l))


@bot.command(name='in_words', help=' - check if word is in list (.in_words [word])')
async def in_words(ctx, word=""):
    log(f">> {ctx.author.name}: {ctx.message.content}")

    if word == "":
        return

    if word.lower() in word_list_lower:
        await ctx.send(f"'{word}' ist schon in der Liste")
    else:
        await ctx.send(f"'{word}' war nicht vorhanden und wurde hinzugefügt")
        with open("other_words.txt", "a") as f:
            f.write(word + "\n")
        word_list.append(word)
        word_list_lower.append(word.lower)


@bot.command(name='pc_status', help=' - show pc status (.pc_status)')
async def pc_status(ctx, id=0):
    log(f">> {ctx.author.name}: {ctx.message.content}")

    battery_sensor = psutil.sensors_battery()
    BATTERY = str(battery_sensor.percent)
    PLUGGED = "Plugged In" if battery_sensor.power_plugged else "Not Plugged In"
    CPU = psutil.cpu_percent(interval=0.5)
    RAM = psutil.virtual_memory().percent
    await ctx.send(f"**Battery**: {BATTERY}% - {PLUGGED}\n**CPU**: {CPU}%\n**RAM**: {RAM}%")


@bot.command(name='delete', help=' - delete message by id (.delete [id])')
async def delete(ctx, id=0):
    log(f">> {ctx.author.name}: {ctx.message.content}")
    if id == 0:
        return
    try:   
        message = await ctx.fetch_message(id)
    except:
        await ctx.send("not a valid id.")
        return

    if message.author == bot.user:
        log(f"deleting this massage: {message.content}")
        await message.delete()


@bot.command(name='dice', help=' - roll a dice (.dice)')
async def dice(ctx):
    log(f">> {ctx.author.name}: {ctx.message.content}")
    await ctx.send(str(random.choice(range(1, 7))))


@bot.command(name='coin', help=' - flip a coin (.coin)')
async def coin(ctx):
    log(f">> {ctx.author.name}: {ctx.message.content}")
    if random.random() > 0.5:
        await ctx.send("Kopf")
    else:
        await ctx.send("Zahl")


@bot.command(name='punkt', help=' - PUNKT!')
async def punkt(ctx):
    log(f">> {ctx.author.name}: {ctx.message.content}")
    await ctx.send(".\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n.")


@bot.command(name='an', help=' - sende Nachricht an ... (.an [name] [message])')
async def an(ctx, name=""):

    log(f">> {ctx.author.name}: {ctx.message.content}")

    if name == "":
        return
    
    message = " ".join(ctx.message.content.split(" ")[2:])
    name = name.lower()
    if name in user_id:
        log(f">> sende an {name}: {message}")
        user = await bot.fetch_user(user_id[name])
        await user.send(message)


@bot.command(name='schaf', help=' - random schafbild (.schaf [amount])')
async def schaf(ctx, amount=1):
    global SENDING_SCHAFE

    log(f">> {ctx.author.name}: {ctx.message.content}")

    if SENDING_SCHAFE:
        await ctx.send("Already sending schafe")
        return
    SENDING_SCHAFE = True

    if amount < 1:
        amount = 1
    elif amount > 20:
        amount = 20
    
    for number in range(amount):
        await ctx.send(random.choice(schaf_links))
        sleep(3)

    SENDING_SCHAFE = False


@bot.command(name='restart', help=' - restart bot (.restart)')
async def restart(ctx):
    log(f">> {ctx.author.name}: {ctx.message.content}")

    if voice_channel != 0:
        await voice_channel.disconnect()

    await bot.close()



@bot.command(name='gif', help=' - get random GIF of top 50 GIFs (.gif [search term])')
async def gif(ctx):
    search = " ".join(ctx.message.content.split(" ")[1:])

    if search == "":
        await ctx.send("please provide a search-term (Bsp. .gif uwu)")
        return
    
    gif = random.choice(GIF_search.get_list_of_gifs(search))
    log(f"send: {gif}")
    await ctx.send(gif)


@bot.command(name='status', help=' - change status (.status OFF/ON)')
async def status(ctx, status=""):

    log(f">> {ctx.author.name}: {ctx.message.content}")

    if status == "":
        return
    elif status.lower() == "off":
        await bot.change_presence(status=discord.Status.invisible)
        log("OFF")
    elif status.lower() == "on":
        await bot.change_presence(status=discord.Status.online)
        log("ON")


@bot.command(name='screenshot', help=' - get random screenshot (.screenshot [amount])')
async def screenshot(ctx, amount=1):
    global SENDING_SCREENSHOTS

    log(f">> {ctx.author.name}: {ctx.message.content}")

    if SENDING_SCREENSHOTS:
        await ctx.send("Already sending screenshots")
        return
    SENDING_SCREENSHOTS = True

    if amount < 1:
        amount = 1
    elif amount > 50:
        amount = 50

    for number in range(amount):
        while True:
            id = random_screenshot.get_random_id(6)
            url = random_screenshot.get_image_url(id)
            if url == -1:
                log("random_screenshot: no image!")
                sleep(2)
                continue
            data = random_screenshot.get_image_data(url)
            if data == -1:
                log("random_screenshot: no image!")
                sleep(1)
                continue
   
            if len(data) == 503:
                log("random_screenshot: no image!")
                sleep(1)
                continue

            with open("temp/screenshot.png", 'wb') as file:
                file.write(data)

            break

        message = f"ID: {id}\nURL: {url}\n{number+1}/{amount}"
        log(message)
        if "imgur" in url:
            await ctx.send(message)
        else:
            await ctx.send(message, file=discord.File("temp/screenshot.png"))
        
        sleep(4)

    SENDING_SCREENSHOTS = False


@bot.command(name='download', help=' - download YouTube video as audio (.download [URL])')
async def download(ctx, link="", type="wav"):
    log(f">> {ctx.author.name}: {ctx.message.content}")

    if link == "":
        await ctx.send("no link provided. try '.download [link]'")
        return

    await ctx.send("downloading audio... Bot is unresponsive meanwhile but will queue up commmands")
    log(f"downloading audio... [{link}]")

    if(youtube_downloader.download_audio(path="temp/", link=link, type=type)):
        #send file
        await ctx.send(f"took {int(youtube_downloader.download_duration)} seconds to download",file=discord.File(youtube_downloader.download_path))
    else:
        await ctx.send(youtube_downloader.download_error)

    #delete temp audio file
    try:
        filelist = [f for f in os.listdir("temp")]
        for f in filelist:
            os.remove(os.path.join("temp", f))
    except:
        pass


# run bot
bot.run(TOKEN)
print("ENDEEEE")
sleep(2)
if SHUTDOWN:
    exit(666)
else:
    exit(0)