from dotenv import load_dotenv
import discord
from discord.ext import commands
import os

def send_notification(message:str, file_path=None):
    message = message[-2000:]

    if file_path and not os.path.exists(file_path):
        file_path = None

    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    intents = discord.Intents.all()
    intents.members = True
    bot = commands.Bot(command_prefix='.', intents=intents)

    @bot.event
    async def on_message(message):
        return

    @bot.event
    async def on_ready():
        try:
            user = await bot.fetch_user(618140491879546881)
            await user.send(message, file=discord.File(file_path) if file_path else None)
        except Exception as e:
            print(e)
        await bot.close()

    bot.run(TOKEN)