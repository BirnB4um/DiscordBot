import os
from pathlib import Path
import re
import time
from datetime import datetime
import random
import asyncio
# from bs4 import BeautifulSoup
from gpiozero import CPUTemperature
import requests
import json
import psutil
import speedtest
from discord.ext import commands
import discord
# from discord import FFmpegPCMAudio

import random_screenshot as rand_screenshot
import youtube_downloader as yt_dl
import GIF_search as GIF_search
from archive import get_archived_data
from Logger import get_logger


##### SETUP #####

TOKEN = os.getenv('DISCORD_TOKEN')
yt_dl.load_youtube_api()
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='.', intents=intents)
restart_delay = 0
link_pattern = re.compile(r'https?://\S+', re.IGNORECASE)
yt_vid_url = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=)?([a-zA-Z0-9_-]{11})', re.IGNORECASE)
standby_mode = False

data_folder = Path("/opt/discord-bot/data/")
temp_folder = data_folder / "temp"

logger = get_logger("bot")
chat_logger = get_logger("chat")

def log(text):
    logger.info(text)

def log_error(text):
    logger.error(text, exec_info=True)
    
def constrain(x, minX, maxX):
    return max(minX, min(maxX, x))


#=======================

# id lists
user_id = {"josef":762641864335556608,
        "thimo":618140491879546881,
        "philipp":335489399968104450,
        "tim":791411006513217536,
        "birnbot":955887644578046032}
                    
# florida man stories
florida_man_data = []
with open(data_folder / "florida_man.json", "r") as file:
    florida_man_data = json.load(file)

#4chan links
with open(data_folder / "4chan_link.json", "r") as file:
    fourchan_links = json.load(file)



##### EVENTS ######

@bot.event
async def on_ready():
    log("Bot is ready!")
    user = await bot.fetch_user(user_id["thimo"])
    await user.send("Bot Ready!")

    # clear temp folder
    for file in temp_folder.iterdir():
        file.unlink()


@bot.event
async def on_voice_state_update(member, before, after):
    pass


@bot.event
async def on_message(message):
    global standby_mode
    
    if (message.author == bot.user):
        return
    
    is_command = message.content[0] == "."

    if standby_mode:
        if message.content.startswith(".standby"):
            standby_mode = False
            await message.channel.send(f"standby mode: {standby_mode}")
        return

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


    #if someone sends dm
    if (message.channel.type == discord.ChannelType.private): 
        user_is_thimo = message.author.id == user_id["thimo"]
        log_message = f"{message.author}: {message.content}"

        #send to thimo
        if not user_is_thimo:
            user = await bot.fetch_user(user_id["thimo"])
            await user.send(f"```{log_message}```")
            chat_logger.info(log_message)


    #execute command
    if is_command:
        await bot.process_commands(message)


@bot.event
async def on_presence_update(before, after):

    if before.id == bot.user.id:
        return



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
    
    
@bot.command(name='download_audio', help=' - download audio of a YT video (.download_audio [URL] [mp3/wav])')
async def download_audio(ctx, url="", extension="mp3"):
    if url == "":
        await ctx.send("please provide a link (.download_audio <https://www.youtube.com/watch?v=dQw4w9WgXcQ>)")
        return
    
    extension = extension.replace(".", "")
    if extension not in ["mp3", "wav"]:
        await ctx.send("extension has to be either 'mp3' or 'wav'.\nTry webm extension with .download_audio [URL] mp3")
        return
    
    start_time = time.time()
    file_path, error_msg = await bot.loop.run_in_executor(None, yt_dl.download_yt_audio, url, temp_folder, extension)
    duration = int(time.time() - start_time)
    file_name = file_path.split("/")[-1]
    if file_path == "error":
        await ctx.send("error occured: " + error_msg)
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
        await ctx.send("please provide a link (.download_video <https://www.youtube.com/watch?v=dQw4w9WgXcQ>)")
        return
    
    extension = extension.replace(".", "")
    if extension not in ["mp4"]:
        await ctx.send("extension can only be 'mp4'. \nTry webm extension with .download_video [URL] mp4")
        return
    
    start_time = time.time()
    file_path, error_msg = await bot.loop.run_in_executor(None, yt_dl.download_yt_video, url, temp_folder, extension)
    duration = int(time.time() - start_time)
    file_name = file_path.split("/")[-1]
    if file_path == "error":
        await ctx.send("error occured: " + error_msg)
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


# @bot.command(name='pull_update', help=' - pulls the latest update from github (.pull_update [yes/no])')
# async def pull_update(ctx, restart_after="no"):
#     if ctx.author.id == user_id["thimo"]:
#         await ctx.send("pulling update...")
#         log("pulling update...")
#         code = os.system("git pull")
#         #TODO: maybe run "git reset --hard" if pull fails
#         await ctx.send(f"update completed! exitcode: {code}")
#         if restart_after.lower() == "yes":
#             await restart(ctx)


# @bot.command(name='shutdown', help=' - shuts down server (.shutdown yes)')
# async def shutdown(ctx, confirmation=""):
#     if ctx.author.id == user_id["thimo"]:
#         if confirmation.lower() == "yes":
#             await ctx.send("shutting down...")
#             log("shutting down server...")
#             os.system("sudo shutdown -h 0")
#             return
#         await ctx.send("confirm with '.shutdown yes'")


# @bot.command(name='reboot', help=' - reboot server (.reboot yes)')
# async def reboot(ctx, confirmation=""):
#     if ctx.author.id == user_id["thimo"]:
#         if confirmation.lower() == "yes":
#             await ctx.send("rebooting...")
#             log("rebooting server...")
#             os.system("sudo reboot")
#             return
#         await ctx.send("confirm with '.reboot yes'")




@bot.command(name='thumbnail', help=' - get thumbnail of a YouTube video (.thumbnail [link])')
async def thumbnail(ctx, link=""):
    if link == "":
        await ctx.send("please provide a link (Bsp: .thumbnail <https://www.youtube.com/watch?v=dQw4w9WgXcQ>)")
        return

    url, error_msg = yt_dl.get_yt_thumbnail(link)
    if url == "error":
        await ctx.send("error occured: " + error_msg)
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

    sleep_between_images = 1

    for number in range(amount):
        url, data, tries = await bot.loop.run_in_executor(None, rand_screenshot.get_random_screenshot)

        if url == None:
            await ctx.send(f"exceeded number of tries ({tries})! skipping this image...")
            await asyncio.sleep(sleep_between_images)
            continue
        
        msg = f"image nr.: {number+1}/{amount}, tries: {tries}, URL: {url}"
        await ctx.send(msg)

        # if "imgur" in url:
        #     await ctx.send(msg)
        # else:
        #     with open(temp_folder / "screenshot.png", 'wb') as file:
        #         file.write(data)
        #     await ctx.send(msg, file=discord.File(temp_folder / "screenshot.png"))

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
            msg += f"**Postal**: {data['postal']}\n"
            msg += f"**Timezone**: {data['timezone']}"
            await ctx.send(msg)
        except Exception as e:
            log_error(f"error when getting ip info. {e}")
            await ctx.send(f"error occured. Error: {e}")
    else:
        await ctx.send(f"error occured. status code: {r.status_code}")



@bot.command(name='standby', help=' - toggle standby mode')
async def standby(ctx):
    global standby_mode
    standby_mode = not standby_mode
    await ctx.send(f"standby mode set to {standby_mode}")






@bot.command(name='wayback', help=' - get data from the wayback machine (.wayback [URL] [oldest/newest])')
async def wayback(ctx, url="", order="oldest"):

    if url == "":
        await ctx.send("please provide a link (.wayback https://www.google.com)")
        return
    
    if order.lower() not in ["oldest", "newest"]:
        await ctx.send("order has to be either 'oldest' or 'newest'")
        return

    result = await bot.loop.run_in_executor(None, get_archived_data, url, order)
    if not result["success"]:
        await ctx.send("Error: " + result["error"])
        return

    msg = f"Date: {result['date']}, URL: {result['url']}"
    await ctx.send(msg)


@bot.command(name='imgFromURL', help=' - get image from url (.imgFromURL [URL])')
async def imgFromURL(ctx, url=""):
    
    try:
        response = requests.get(url, headers=rand_screenshot.headers)
        if response.status_code != 200:
            await ctx.send(f"error: {response.status_code}")
            return
        if "image" not in response.headers["Content-Type"]:
            await ctx.send("not an image")
            return
        
        with open(temp_folder / "image.png", 'wb') as file:
            file.write(response.content)

        await ctx.send(file=discord.File(temp_folder / "image.png"))
        
    except Exception as e:
        await ctx.send("error occured " + str(e))
        return


# run bot
log("starting bot")
bot.run(TOKEN)
log("restarting...")
time.sleep(5+restart_delay)
