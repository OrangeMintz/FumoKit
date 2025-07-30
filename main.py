import os
import discord
import logging
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

token = os.getenv('DISCORD_TOKEN')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
GUILD_IDs = [766446271396839435, 1112358527160291328]

# INTENTS
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# EVENTS
@bot.event
async def on_ready():
    # synced = await bot.tree.sync()
    print(f"Hello! We have logged in as {bot.user.name}")

@bot.event
async def setup_hook():
    await bot.load_extension('cogs.cmds')
    await bot.load_extension('cogs.fg_cmds')
    
    # For debug syncing commands 
    for guild_id in GUILD_IDs:
        try:
            guild = discord.Object(id=guild_id)
            synced = await bot.tree.sync(guild=guild)
            print(f"Synced {len(synced)} commands to the guild {guild_id}")
        except Exception as e:
            print(f'Failed to sync commands to guild {e}')

bot.run(token, log_handler=handler, log_level=logging.DEBUG)