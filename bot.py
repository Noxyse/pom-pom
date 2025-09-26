import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

intents = discord.Intents.default()
intents.message_content = True # Reading messages
intents.reactions = True # Reading reactions
intents.guilds = True # Reading guilds

bot = commands.Bot(command_prefix='!', intents=intents) # Creating bot intent

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Asynchronous setup hook for cog loading
async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'Loaded {filename}')
            except Exception as e:
                print(f'Failed to load {filename}: {e}')

@bot.event
async def setup_hook():
    await load_cogs()

load_dotenv()

discord_token = os.getenv('DISCORD_TOKEN')

bot.run(discord_token)
