import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

intents = discord.Intents.default()
intents.message_content = True # Reading messages
intents.reactions = True # Reading reactions
intents.guilds = True # Reading guilds
intents.members = True # Reading members

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

@bot.command()
@commands.is_owner()
async def sync(ctx):
    try:
        synced = await bot.tree.sync()
        await ctx.send(f'Synced {len(synced)} commands.')
        print(f'Synced {len(synced)} commands.')
    except Exception as e:
        await ctx.send(f'Error syncing commands: {e}')
        print(f'Error syncing commands: {e}')

load_dotenv()

discord_token = os.getenv('DISCORD_TOKEN')

bot.run(discord_token)
