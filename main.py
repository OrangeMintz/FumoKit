import os
import discord
import logging
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

token = os.getenv('DISCORD_TOKEN')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# INTENTS
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# EVENTS
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Hello! We have logged in as {bot.user.name}")

@bot.event
async def setup_hook():
    await bot.load_extension('cogs.cmds')

bot.run(token, log_handler=handler, log_level=logging.DEBUG)