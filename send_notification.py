import time
from dotenv import load_dotenv
import discord
from discord.ext import commands
import os
import asyncio

def send_notification(message, file_path=None):
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
        user = await bot.fetch_user(618140491879546881)
        await user.send(message, file=discord.File(file_path) if file_path else None)
        await bot.close()

    bot.run(TOKEN)

    async def shutdown():
        await bot.close()

    async def main():
        await asyncio.gather(
            shutdown(),
            return_exceptions=True
        )

    asyncio.run(main())
