import os
from dotenv import load_dotenv
import time
from datetime import datetime
import random
import asyncio
from bs4 import BeautifulSoup
from gpiozero import CPUTemperature
import requests
import json
import psutil
import speedtest
import subprocess
import matplotlib.pyplot as plt
from discord.ext import commands
import discord
from discord import FFmpegPCMAudio

import module.random_screenshot as rand_screenshot
import module.youtube_downloader as yt_dl
import module.GIF_search as GIF_search
from module.chatbot import Chatbot


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

def error(text):
    print(datetime.now().strftime("[%d/%m/%Y %H:%M:%S] ") + text)

def constrain(x, minX, maxX):
    return max(minX, min(maxX, x))


#=======================

chatbot = Chatbot()

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
    "korn":"sounds/Korn.mp3",
    "grünen":"sounds/die_gruenen.mp3",
    }

#=======================


##### EVENTS ######

@bot.event
async def on_ready():
    log("Bot is ready!")
    user = await bot.fetch_user(user_id["thimo"])
    await user.send("Bot Ready!")


@bot.event
async def on_voice_state_update(member, before, after):

    if bot.user.id == member.id:

        for vc in bot.voice_clients:
            vc.stop()

        if before.channel != None:
            for vc in bot.voice_clients:
                if vc.channel == before.channel:
                    await vc.disconnect()

        if len(bot.voice_clients) > 1:
            log(f"voice state update with more than 1 voice_clients: {bot.voice_clients}")
            for i in range(1,len(bot.voice_clients)):
                bot.voice_clients[i].stop()
                await bot.voice_clients[i].disconnect()



@bot.event
async def on_message(message):
    if (message.author == bot.user):
        return

    #if someone sends dm
    if (message.channel.type == discord.ChannelType.private): 
        user_is_thimo = message.author.id == user_id["thimo"]
        log_message = datetime.now().strftime("[%d/%m/%Y %H:%M:%S]") + f" {message.author}: {message.content}"

        #if not a command, send to chatbot
        if message.content[0] != ".":
            input = f"{message.author.name}:{chatbot.TOKENS['start_of_message']}{message.content}{chatbot.TOKENS['end_of_message']}furby:{chatbot.TOKENS['start_of_message']}"
            if chatbot.check_if_running():
                await message.channel.send("chatbot is already running! try again later.")
                log_message += "\n" + datetime.now().strftime("[%d/%m/%Y %H:%M:%S]") + f" chatbot was already running!"
            else:
                output = await bot.loop.run_in_executor(None, chatbot.run, input, 50)
                log_message += "\n" + datetime.now().strftime("[%d/%m/%Y %H:%M:%S]") + f" furby: {output}"
                await message.channel.send(output)

        if not user_is_thimo:
            user = await bot.fetch_user(user_id["thimo"])
            await user.send(f"```{log_message}```")
            with open("data/chat.txt", "a") as file:
                file.write(log_message + "\n")

    #execute command
    if message.content[0] == ".":
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
async def on_error(event, *args, **kwargs):
    if event == 'on_message':
        log(f'Unhandled message: {args[0]}\n')
    else:
        log(f"ERROR: other error occured! {args} {kwargs}")


##### COMMANDS ######


@bot.command(name='reset_chatbot', help=' - reset chatbot (.reset_chatbot)')
async def reset_chatbot(ctx):
    chatbot.reset_hidden()
    await ctx.send("resetting complete.")

@bot.command(name='set_chatbot_confidence', help=' - set confidence of chatbot. value < 1 -> more confident, value > 1 -> more random (default: 0.5)  (.set_chatbot_confidence [value])')
async def set_chatbot_confidence(ctx, conf=None):
    try:
        conf = float(conf)
    except:
        await ctx.send("value has to be a float")
        return
    chatbot.temperature = conf
    await ctx.send(f"confidence set to {chatbot.temperature}")

@bot.command(name='talk', help=' - talk to furby (.talk [message])')
async def talk(ctx, *message):
    msg = " ".join(message)
    if msg == "":
        await ctx.send("add a message (.talk [message])")
        return

    input = f"{ctx.author.name}:{chatbot.TOKENS['start_of_message']}{msg}{chatbot.TOKENS['end_of_message']}furby:{chatbot.TOKENS['start_of_message']}"
    if chatbot.check_if_running():
        await ctx.send("chatbot is already running! try again later.")
        return
    output = await bot.loop.run_in_executor(None, chatbot.run, input, 50)
    await ctx.send(output)

@bot.command(name='pull_update', help=' - pulls the latest update from github (.pull_update yes)')
async def pull_update(ctx, confirmation=""):
    if ctx.author.id == user_id["thimo"]:
        if confirmation.lower() == "yes":
            await ctx.send("pulling update...")
            log("pulling update...")
            code = os.system("git pull")
            await ctx.send(f"update completed! exitcode: {code}")
            return
        await ctx.send("confirm with '.pull_update yes'")

@bot.command(name='shutdown', help=' - shuts down server (.shutdown yes)')
async def shutdown(ctx, confirmation=""):
    if ctx.author.id == user_id["thimo"]:
        if confirmation.lower() == "yes":
            await ctx.send("shutting down...")
            log("shutting down server...")
            os.system("sudo shutdown -h 0")
            return
        await ctx.send("confirm with '.shutdown yes'")

@bot.command(name='reboot', help=' - reboot server (.reboot yes)')
async def reboot(ctx, confirmation=""):
    if ctx.author.id == user_id["thimo"]:
        if confirmation.lower() == "yes":
            await ctx.send("rebooting...")
            log("rebooting server...")
            os.system("sudo reboot")
            return
        await ctx.send("confirm with '.reboot yes'")


@bot.command(name='get_log', help=' - send log files (.get_log)')
async def get_log(ctx):
    log("sending log files")
    if ctx.author.id == user_id["thimo"]:
        await ctx.send("server_log:", file=discord.File("data/log.txt"))
        await ctx.send("launcher_log:", file=discord.File("data/launcher_log.txt"))

        if os.path.exists("../server_logs/log.txt"):
            await ctx.send("server_state_log:", file=discord.File("../server_logs/log.txt"))
            
            with open("../server_logs/log.txt", "r") as file:
                lines = file.read().splitlines()
            cpu = []
            cpu_temp = []
            ram = []
            dates = []
            for line in lines:
                line = line.split(" ")
                date = datetime.strptime(" ".join(line[:2]), "[%d/%m/%Y %H:%M:%S]")
                dates.append(date)
                line = line[2].split("/")
                cpu.append(float(line[0].split(":")[1]))
                cpu_temp.append(float(line[1].split(":")[1]))
                ram.append(float(line[2].split(":")[1]))

            plt.figure(figsize=(12,8))
            plt.plot(dates, cpu, c="b")
            plt.plot(dates, cpu_temp, c="r")
            plt.plot(dates, ram, c="g")
            plt.xlabel("Dates")
            plt.ylabel("% and °C")
            plt.title("Server state log")
            plt.legend(["CPU", "CPU_TEMP", "RAM"])
            plt.tight_layout()
            plt.savefig("temp/server_state_log.png")
            await ctx.send("server_state_log plot:", file=discord.File("temp/server_state_log.png"))
            


@bot.command(name='clear_log', help=' - clear log files (.clear_log)')
async def clear_log(ctx):
    if ctx.author.id == user_id["thimo"]:
        with open("data/log.txt", "w") as file:
            file.write("")
        with open("data/launcher_log.txt", "w") as file:
            file.write("")
        log("clearing log files")
        await ctx.send("cleared logs")
        


@bot.command(name='join', help=' - join current vc (.join)')
async def join(ctx):

    auth_voice = ctx.author.voice
    if auth_voice == None:
        await ctx.send("you need to join a voicechannel first")
        return


    log(f"joining channel {auth_voice.channel.id}")
    
    for vc in bot.voice_clients:
        vc.stop()
        await vc.disconnect()

    await auth_voice.channel.connect()
   
    
@bot.command(name='leave', help=' - leave vc (.leave)')
async def leave(ctx):

    if len(bot.voice_clients) == 0:
        await ctx.send("bot needs to join first (.join)")
        return
    
    for vc in bot.voice_clients:
        log(f"leave voice channel {vc.channel}")
        await vc.disconnect()
    

@bot.command(name='play', help=f" - play sounds if joined vc first (.play [sound])")
async def play(ctx, sound=""):

    if len(bot.voice_clients) == 0:
        await ctx.send("bot needs to join first (.join)")
        return
    voice_client = bot.voice_clients[0]

    if sound in list(sound_files.keys()):
        log(f"playing audio: {sound_files[sound]}")
        
        try:
            if voice_client.is_playing() or voice_client.is_paused():
                voice_client.stop()

            options = {
                'options': '-b:a 4k',
            }
            voice_client.play(FFmpegPCMAudio(sound_files[sound], **options))

            while voice_client.is_playing() or voice_client.is_paused():
                await asyncio.sleep(0.5)

        except Exception as e:
            error(str(e))
        finally:
            voice_client.stop()

    else:
        await ctx.send(f"sound {sound} not in list. try one of these:\n"+ "\n".join(f"-{sound}" for sound in list(sound_files.keys())))

    
@bot.command(name='stop', help=' - stop current sound (.stop)')
async def stop(ctx):
    if len(bot.voice_clients) == 0:
        await ctx.send("bot needs to join first (.join)")
        return
    
    log("stop audio")
    for vc in bot.voice_clients:
        vc.stop()


@bot.command(name='pause', help=' - pause current sound (.pause)')
async def pause(ctx):
    if len(bot.voice_clients) == 0:
        await ctx.send("bot needs to join first (.join)")
        return
    
    log("pausing audio")
    for vc in bot.voice_clients:
        if vc.is_playing():
            vc.pause()
    

@bot.command(name='resume', help=' - resume current sound (.resume)')
async def resume(ctx):
    if len(bot.voice_clients) == 0:
        await ctx.send("bot needs to join first (.join)")
        return
    
    log("resuming audio")
    for vc in bot.voice_clients:
        if vc.is_paused():
            vc.resume()
    



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
    log(f"send thumbnail url: {thumbnail_image}")
    await ctx.send(thumbnail_image)



@bot.command(name='screenshot', help=' - get random screenshot (.screenshot [amount])')
async def screenshot(ctx, amount=1):
    amount = constrain(amount, 1, 30)

    sleep_between_images = 4

    for number in range(amount):
        id, url, data, tries = await bot.loop.run_in_executor(None, rand_screenshot.get_random_screenshot)

        if url == None:
            await ctx.send(f"exceeded number of tries ({tries})! skipping this image...")
            await asyncio.sleep(sleep_between_images)
            continue
        
        msg = f"ID: {id}, image nr.: {number+1}/{amount}, nr tries: {tries}, URL: {url}"
        if "imgur" in url:
            await ctx.send(msg)
        else:
            with open("temp/screenshot.png", 'wb') as file:
                file.write(data)

            await ctx.send(msg, file=discord.File("temp/screenshot.png"))
        await asyncio.sleep(sleep_between_images)



@bot.command(name='server_status', help=' - show server status (.server_status [do_network_speed])')
async def server_status(ctx, do_network_speed="no"):

    if do_network_speed.lower() == "yes":
        try:
            st = speedtest.Speedtest()
            st.get_best_server()

            DL_SPEED = round(st.download() / 1_000_000, 3)
            UP_SPEED = round(st.upload() / 1_000_000, 3)
        except:
            DL_SPEED = -1
            UP_SPEED = -1
    else:
            DL_SPEED = -1
            UP_SPEED = -1

    try:
        CPU_TEMP = CPUTemperature().temperature
    except:
        CPU_TEMP = -1
    CPU = psutil.cpu_percent(interval=0.5)
    RAM = psutil.virtual_memory().percent
    await ctx.send(f"**CPU**: {CPU}%\n**CPU TEMP**: {CPU_TEMP}\n**RAM**: {RAM}%\n**Download speed**: {DL_SPEED} Mbps\n**Upload speed**: {UP_SPEED} Mbps")



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
    log(f"send message to {name}: {message}")
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
    await ctx.send("restarting...")
    await bot.close()



# run bot
log("starting bot")
bot.run(TOKEN)
log("restarting...")
time.sleep(5)
