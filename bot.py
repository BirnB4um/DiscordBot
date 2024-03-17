import os
import re
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
from module.chatbot import DiscordChatbot, FourchanChatbot


##### SETUP #####

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
yt_dl.load_youtube_api()
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='.', intents=intents)
restart_delay = 0
link_pattern = re.compile(r'https?://\S+', re.IGNORECASE)


def log(text, print_to_console=False):
    log_msg = datetime.now().strftime("[%d/%m/%Y %H:%M:%S] ") + text
    with open("data/log.txt", "a") as file:
        file.write(log_msg+"\n")

    if print_to_console:
        print(log_msg)

def log_error(text):
    print(datetime.now().strftime("[%d/%m/%Y %H:%M:%S] Error: ") + text)

def constrain(x, minX, maxX):
    return max(minX, min(maxX, x))


#=======================

discord_chatbot = DiscordChatbot()
fourchan_chatbot = FourchanChatbot()
chatbot_mode = "discord"
chatbot = discord_chatbot
discord_chatbot_name = "furby"

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

#4chan links
with open("data/4chan_link.json", "r") as file:
    fourchan_links = json.load(file)


months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

sound_files = {
    "biffler":"sounds/biffler.mp3",
    "oink":"sounds/oink.wav",
    "swag":"sounds/swag.wav",
    "wind":"sounds/Wind.wav",
    "wood":"sounds/wood2.wav",
    "wasser":"sounds/Wasser2.wav",
    "ghast":"sounds/Ghast.wav",
    "ghast2":"sounds/Ghast2.wav",
    "jesus" : "sounds/jesus.wav",
    "schüttellied" : "sounds/schüttellied.ogg",
    "jiggle" : "sounds/jigglejiggle.wav",
    "dune": "sounds/dune.wav",
    "nutella":"sounds/nutella.wav",
    "korn":"sounds/Korn.mp3",
    "grünen":"sounds/die_gruenen.mp3",
    "missile": "sounds/missile.mp3",
    "alarm": "sounds/alarm.mp3",
    "creeper": "sounds/creeper.mp3"
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
    
    is_command = message.content[0] == "."

    # crazy? I was crazy once.
    if not is_command and "crazy" in message.content.lower():
        await message.channel.send("Crazy?")
        await asyncio.sleep(1)
        await message.channel.send("I was crazy once.")
        await asyncio.sleep(1)
        await message.channel.send("They locked me in a room.")
        await asyncio.sleep(1)
        await message.channel.send("A rubber room.")
        await asyncio.sleep(1)
        await message.channel.send("A rubber room with rats.")
        await asyncio.sleep(1)
        await message.channel.send("And rats make me crazy.")
        return
    
    #if in furby channel
    if message.channel.id == 1166426231445655653 and not is_command:
        if chatbot_mode == "discord":
            input = f"{message.author.name}:{chatbot.TOKENS['start_of_message']}{message.content}{chatbot.TOKENS['end_of_message']}{discord_chatbot_name}:{chatbot.TOKENS['start_of_message']}"
        elif chatbot_mode == "4chan":
            input = f"{message.content}{chatbot.TOKENS['seperator']}"

        if chatbot.check_if_running():
            await message.channel.send("chatbot is already running! try again later.")
        else:
            output = await bot.loop.run_in_executor(None, chatbot.run, input, 50)
            await message.channel.send(output)
        return


    #if someone sends dm
    if (message.channel.type == discord.ChannelType.private): 
        user_is_thimo = message.author.id == user_id["thimo"]
        log_message = datetime.now().strftime("[%d/%m/%Y %H:%M:%S]") + f" {message.author}: {message.content}"

        #send to chatbot
        if not is_command:
            if chatbot_mode == "discord":
                input = f"{message.author.name}:{chatbot.TOKENS['start_of_message']}{message.content}{chatbot.TOKENS['end_of_message']}{discord_chatbot_name}:{chatbot.TOKENS['start_of_message']}"
            elif chatbot_mode == "4chan":
                input = f"{message.content}{chatbot.TOKENS['seperator']}"

            if chatbot.check_if_running():
                await message.channel.send("chatbot is already running! try again later.")
                log_message += "\n" + datetime.now().strftime("[%d/%m/%Y %H:%M:%S]") + f" chatbot was already running!"
            else:
                output = await bot.loop.run_in_executor(None, chatbot.run, input, 50)
                log_message += "\n" + datetime.now().strftime("[%d/%m/%Y %H:%M:%S]") + f" furby: {output}"
                await message.channel.send(output)

        #send to thimo
        if not user_is_thimo:
            user = await bot.fetch_user(user_id["thimo"])
            await user.send(f"```{log_message}```")
            with open("data/chat.txt", "a") as file:
                file.write(log_message + "\n")

    #execute command
    if is_command:
        await bot.process_commands(message)


@bot.event
async def on_presence_update(before, after):

    if before.id == bot.user.id:
        return

    # only for one server
    if before.guild.id != 819099151429271552:
        return

    # log presence
    if before.status != after.status:
        msg = datetime.now().strftime("%d/%m/%Y %H:%M:%S ") + f"{after.name}:{after.status}"
        with open("data/presence.txt", "a") as file:
            file.write(msg + "\n")

@bot.event
async def on_user_update(before, after):
    pass

@bot.event
async def on_member_update(before, after):
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
        log_error(f'error occured in on_message(): {args[0]}\n')
    else:
        log_error(f"other error occured! {args} {kwargs}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("that command doesn't exist. Try .help")
    log_error(str(error))


##### COMMANDS ######
    

@bot.command(name='set_discord_chatbot_name', help=' - set name of the discord chatbot (default: furby) (.set_discord_chatbot_name [name])')
async def set_discord_chatbot_name(ctx, *name):
    name = " ".join(name)
    if name == "":
        await ctx.send("please provide a name (.set_discord_chatbot_name furby)")
        return
    
    global discord_chatbot_name
    discord_chatbot_name = name
    await ctx.send(f"discord chatbot name set to: {discord_chatbot_name}")
    
@bot.command(name='yt_token', help=' - get login page for new token (.yt_token [exp/get/ref])')
async def yt_token(ctx, mode="none"):
    if ctx.author.id == user_id["thimo"]:
        if mode.lower() == "exp":
            ts = yt_dl.get_token_expiration()
            if ts == None:
                await ctx.send("no token available")
            else:
                await ctx.send(f"token expires at {datetime.fromtimestamp(ts)}")
        elif mode.lower() == "get":
            try:
                url, code = yt_dl.get_token_refresh_url()
                await ctx.send(f"Open {url} and enter {code}\nThen type '.yt_token ref' to refresh token")
            except:
                await ctx.send("error occured")
        elif mode.lower() == "ref":
            try:
                yt_dl.refresh_token()
                await ctx.send("token refreshed!")
            except:
                await ctx.send("error occured")
        else:
            await ctx.send("mode has to be either 'exp' for token expiration date or 'get' for getting a new token")

@bot.command(name='download_audio', help=' - download audio of a YT video (.download_audio [URL] [mp4/webm])')
async def download_audio(ctx, url="", extension="mp4"):
    if url == "":
        await ctx.send("please provide a link (.download_audio https://www.youtube.com/watch?v=dQw4w9WgXcQ)")
        return
    
    extension = extension.replace(".", "")
    if extension not in ["mp4", "webm"]:
        await ctx.send("extension has to be either 'mp4' or 'webm'.\nTry webm extension with .download_audio [URL] webm")
        return
    
    start_time = time.time()
    file_path = await bot.loop.run_in_executor(None, yt_dl.download_yt_audio, url, "temp/", extension)
    duration = int(time.time() - start_time)
    file_name = file_path.split("/")[-1]
    if file_path == "unavailable":
        await ctx.send("video ID is unavailable")
        return
    elif file_path == "error":
        await ctx.send("error occured")
        return
    elif file_path == "no_stream":
        await ctx.send("no stream found. Try webm extension with .download_audio [URL] webm")
        return
    elif file_path == "too_large":
        await ctx.send("audio too large :(")
        return
    elif file_path == "age_restricted":
        await ctx.send("video is age restricted")
        return
    else:
        if os.path.isfile(file_path):
            try:
                await ctx.send(file_name + f"\nTime taken: {duration} sec", file=discord.File(file_path))
            except:
                await ctx.send("file too big :(")
            os.remove(file_path)
        else:
            await ctx.send("file not found :(")

        

@bot.command(name='download_video', help=' - download YT video (.download_video [URL])')
async def download_video(ctx, url="", extension="mp4"):
    if url == "":
        await ctx.send("please provide a link (.download_video https://www.youtube.com/watch?v=dQw4w9WgXcQ)")
        return
    
    extension = extension.replace(".", "")
    if extension not in ["mp4", "webm"]:
        await ctx.send("extension has to be either 'mp4' or 'webm'. \nTry webm extension with .download_video [URL] webm")
        return
    
    start_time = time.time()
    file_path = await bot.loop.run_in_executor(None, yt_dl.download_yt_video, url, "temp/", extension, True)
    duration = int(time.time() - start_time)
    file_name = file_path.split("/")[-1]
    if file_path == "unavailable":
        await ctx.send("video ID is unavailable")
        return
    elif file_path == "error":
        await ctx.send("error occured")
        return
    elif file_path == "no_stream":
        await ctx.send("no stream found. Try webm extension with .download_video [URL] webm")
        return
    elif file_path == "too_large":
        await ctx.send("video too large :(")
        return
    elif file_path == "age_restricted":
        await ctx.send("video is age restricted")
        return
    else:
        if os.path.isfile(file_path):
            try:
                await ctx.send(file_name + f"\nTime taken: {duration} sec", file=discord.File(file_path))
            except:
                await ctx.send("file too big :(")
            os.remove(file_path)
        else:
            await ctx.send("file not found :(")


@bot.command(name='4chan_link', help=' - get a random link from 4chan (.4chan_link amount:1 category:image)')
async def fourchan_link(ctx, *message):
    amount = 1
    category = None
    for msg in message:
        if msg.split(":")[0].lower() == "amount":
            try:
                amount = int(":".join(msg.split(":")[1:]))
            except:
                await ctx.send("amount has to be an integer")
                return
        
        elif msg.split(":")[0].lower() == "category":
            cat = ":".join(msg.split(":")[1:]).lower()
            if not (cat in fourchan_links):
                await ctx.send(f"category '{cat}' not found. try one of these:\n" + ",\n".join(fourchan_links))
                return
            else:
                category = cat
                
    amount = constrain(amount, 1, 20)
    if category == None:
        await ctx.send("\n".join([random.choice(fourchan_links[random.choice(list(fourchan_links))]) for x in range(amount)]))
    else:
        await ctx.send("\n".join(random.sample(fourchan_links[category], amount)))


@bot.command(name='generate_4chan', help=' - generate a 4chan conversation (.generate_4chan [number_of_tokens])')
async def generate_4chan(ctx, number_of_tokens="500"):

    try:
        number_of_tokens = int(number_of_tokens)
    except:
        await ctx.send("number_of_tokens has to be an integer")
        return
    number_of_tokens = constrain(number_of_tokens, 1, 1000)
    
    if chatbot.check_if_running():
        await ctx.send("chatbot is already running! try again later.")
    else:
        temp_hidden = fourchan_chatbot.hidden_state
        temp_cell = fourchan_chatbot.cell_state
        fourchan_chatbot.reset_hidden()

        output = await bot.loop.run_in_executor(None, fourchan_chatbot.run_continuous, number_of_tokens)
        output = "```" + "```\n```".join(output.split(fourchan_chatbot.TOKENS["seperator"])) + "```"

        fourchan_chatbot.hidden_state = temp_hidden
        fourchan_chatbot.cell_state = temp_cell

        await ctx.send(output)


@bot.command(name='generate_discord', help=' - generate a discord conversation (.generate_discord [number_of_tokens])')
async def generate_discord(ctx, number_of_tokens="500"):

    try:
        number_of_tokens = int(number_of_tokens)
    except:
        await ctx.send("number_of_tokens has to be an integer")
        return
    number_of_tokens = constrain(number_of_tokens, 1, 1000)
    
    if chatbot.check_if_running():
        await ctx.send("chatbot is already running! try again later.")
    else:
        temp_hidden = discord_chatbot.hidden_state
        temp_cell = discord_chatbot.cell_state
        discord_chatbot.reset_hidden()

        output = await bot.loop.run_in_executor(None, discord_chatbot.run_continuous, number_of_tokens)

        discord_chatbot.hidden_state = temp_hidden
        discord_chatbot.cell_state = temp_cell

        await ctx.send(output)

@bot.command(name='set_chatbot', help=' - set which chatbot to use (.set_chatbot [discord/4chan])')
async def set_chatbot(ctx, model="discord"):
    global chatbot_mode, chatbot
    if model == "discord":
        chatbot = discord_chatbot
        chatbot_mode = "discord"
    elif model == "4chan":
        chatbot = fourchan_chatbot
        chatbot_mode = "4chan"
    else:
        await ctx.send("model has to be either 'discord' or '4chan'")
        return
    
    chatbot.reset_hidden()
    await ctx.send("chatbot set to: " + model)


@bot.command(name='reset_chatbot', help=' - reset chatbot (.reset_chatbot)')
async def reset_chatbot(ctx):
    chatbot.reset_hidden()
    await ctx.send("resetting complete.")

@bot.command(name='set_chatbot_confidence', category='Chatbot', help=' - set confidence of chatbot. value < 1 -> more confident, value > 1 -> more random (default: 0.5)  (.set_chatbot_confidence [value])')
async def set_chatbot_confidence(ctx, conf=None):
    try:
        conf = float(conf)
    except:
        await ctx.send("value has to be a float")
        return
    chatbot.temperature = conf
    await ctx.send(f"confidence of chatbot {chatbot_mode} set to {chatbot.temperature}")

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

@bot.command(name='get_status_diagram', help=' - get graph of server-status (.get_status_diagram)')
async def get_status_diagram(ctx):
    log("sending status diagram")
    if ctx.author.id == user_id["thimo"]:
        if os.path.exists("../server_logs/log.txt"):
            
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
    

@bot.command(name='stream', help=f" - stream youtube audio in a voicechannel (.stream [youtube url OR search term])")
async def stream(ctx, *msg):
    msg = " ".join(msg)

    if len(bot.voice_clients) == 0:
        await ctx.send("bot needs to join first (.join)")
        return
    voice_client = bot.voice_clients[0]

    if msg == "":
        await ctx.send("please provide a link or a search term (.stream https://www.youtube.com/watch?v=dQw4w9WgXcQ)")
        return

    #check if url or search term
    if bool(re.match(link_pattern, msg)):
        url = msg
    else:
        videos = yt_dl.get_search_result(msg)
        if videos == None:
            await ctx.send("no video found or quota exceeded")
            return

        #get video
        url = ""
        for vid in videos:
            if yt_dl.check_video(vid):
                url = vid
                break

        if url == "":
            await ctx.send("no matching video found")
            return

        await ctx.send("streaming video: " + url)

    
    file_path = await bot.loop.run_in_executor(None, yt_dl.download_yt_audio, url, "temp/", "mp4", 50)
    file_name = file_path.split("/")[-1]
    if file_path == "unavailable":
        await ctx.send("video ID is unavailable")
        return
    elif file_path == "error":
        await ctx.send("error occured")
        return
    elif file_path == "no_stream":
        await ctx.send("no stream found")
        return
    elif file_path == "too_large":
        await ctx.send("audio too large :(")
        return
    elif file_path == "age_restricted":
        await ctx.send("video is age restricted")
        return

    if os.path.isfile("temp/"+file_name):
        try:
            if voice_client.is_playing() or voice_client.is_paused():
                voice_client.stop()

            options = {
                'options': '-b:a 32k',
            }
            ffmpeg_streamer = FFmpegPCMAudio("temp/"+file_name, **options)
            voice_client.play(ffmpeg_streamer)

            while voice_client.is_playing() or voice_client.is_paused():
                await asyncio.sleep(0.5)

        except Exception as e:
            log_error(str(e))
        finally:
            voice_client.stop()
            ffmpeg_streamer.cleanup()
            

        os.remove("temp/"+file_name)
    else:
        await ctx.send("file not found :(")


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
                'options': '-b:a 32k',
            }
            ffmpeg_streamer = FFmpegPCMAudio(sound_files[sound], **options)
            voice_client.play(ffmpeg_streamer)

            while voice_client.is_playing() or voice_client.is_paused():
                await asyncio.sleep(0.5)

        except Exception as e:
            log_error(str(e))
        finally:
            voice_client.stop()
            ffmpeg_streamer.cleanup()

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
async def spruch(ctx, amount="1"):
    try:
        amount = int(amount)
    except:
        await ctx.send("amount should be an integer.")
        return

    amount = constrain(amount, 1, 10)
    await ctx.send("\n".join([random.choice(sprueche_list) for i in range(amount)]))


@bot.command(name='joke', help=' - get random joke (.joke [amount])')
async def joke(ctx, amount="1"):
    try:
        amount = int(amount)
    except:
        await ctx.send("amount should be an integer.")
        return

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

    url = yt_dl.get_yt_thumbnail(link)
    if url == "error":
        await ctx.send("error occured")
        return
    elif url == "unavailable":
        await ctx.send("video ID is unavailable")
        return
    elif url == "age_restricted":
        await ctx.send("video is age restricted")
        return
    else:
        await ctx.send(url)



@bot.command(name='screenshot', help=' - get random screenshot (.screenshot [amount])')
async def screenshot(ctx, amount="1"):
    try:
        amount = int(amount)
    except:
        await ctx.send("amount should be an integer.")
        return
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
async def sheep(ctx, amount="1"):
    try:
        amount = int(amount)
    except:
        await ctx.send("amount should be an integer.")
        return
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
async def restart(ctx, delay="0"):
    global restart_delay
    try:
        restart_delay = int(delay)
        restart_delay = constrain(restart_delay, 0, 3600) # max 1 hour delay
        await ctx.send(f"restarting in {restart_delay} seconds...")
    except:
        restart_delay = 0
        await ctx.send("restarting...")
    await bot.close()

@bot.command(name='ip', help=' - get ip info')
async def ip(ctx):
    if ctx.author.id != user_id["thimo"]:
        return
    
    r = requests.get('https://ipinfo.io/json')
    if r.status_code == 200:
        data = r.json()
        try:
            msg = f"**IP**: {data['ip']}\n"
            msg += f"**City**: {data['city']}\n"
            msg += f"**Region**: {data['region']}\n"
            msg += f"**Country**: {data['country']}\n"
            msg += f"**Location**: {data['loc']}\n"
            msg += f"**Hostname**: {data['hostname']}\n"
            msg += f"**Org**: {data['org']}\n"
            msg += f"**Postal**: {data['postal']}\n"
            msg += f"**Timezone**: {data['timezone']}"
            await ctx.send(msg)
        except Exception as e:
            log_error(f"error when getting ip info. {e}")
            await ctx.send(f"error occured. Error: {e}")
    else:
        await ctx.send(f"error occured. status code: {r.status_code}")


@bot.command(name='set_vpn_pw', help=' - set vpn password')
async def ip(ctx, password=""):
    if ctx.author.id != user_id["thimo"]:
        return

    if password == "":
        await ctx.send("please provide a password")
        return
    
    prev_data = []
    with open("../BloomSMP/login.txt", "r") as file:
        prev_data = file.read().splitlines()

    with open("../BloomSMP/login.txt", "w") as file:
        file.write(prev_data[0] + "\n" + password)
        
    await ctx.send("password set")



# run bot
log("starting bot")
bot.run(TOKEN)
log("restarting...")
time.sleep(5+restart_delay)
