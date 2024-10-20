import discord
import random
import asyncio
import time
from discord.ext import commands

class UnifiedCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lock = asyncio.Lock()
        self.cooldown_duration = 20
        self.user_cooldowns = {}
        self.allowed_channels = [1295483149169459311, 1236356278184448030, 1236385552698183854]  # Replace with your allowed channel IDs

        # Load responses from a file for auto-responses
        try:
            with open('chapo_responses.txt', 'r', encoding='utf-8') as file:
                self.responses = [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            self.responses = ['No responses found.']

    # Command for sending messages
    @commands.command(name='send')
    async def send_message_command(self, ctx, channel_id: int, *, message: str):
        async with self.lock:
            channel = self.bot.get_channel(channel_id)
            if channel is not None:
                await channel.send(message)
                await ctx.send(f'Message sent to channel {channel_id}')
            else:
                await ctx.send('Channel not found.')

    # Listener for incoming messages (auto-response logic)
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        # Check if the message is from an allowed channel
        if message.channel.id not in self.allowed_channels:
            return

        # Skip command processing if the message starts with the bot's prefix
        if message.content.startswith(self.bot.command_prefix):
            return

        current_time = time.time()
        user_id = message.author.id

        if user_id in self.user_cooldowns:
            last_response_time = self.user_cooldowns[user_id]
            if current_time - last_response_time < self.cooldown_duration:
                return

        self.user_cooldowns[user_id] = current_time

        # Auto-response logic
        response_dict = {
            'bibble':"Aucun passager clandestin ne sera admis à bord de ce train !",
            'coucou':"Oh, tu es de retour {mention} ! Pom-Pom est si heureux de te revoir !",
            'salut':"Salut {mention} ! De nouvelles aventures t'attendent !",
            'bonjour':"Bonjour {mention} ! Pom-Pom te souhaite une bonne journée !",
            'March 7th': "N'oublie pas de t'assoir si tu ne veux pas tomber. On va faire le saut !"
        }

        for keyword, response in response_dict.items():
            if keyword in message.content.lower():
                formatted_response = response.format(mention=message.author.mention)
                await message.channel.send(formatted_response)
                return

        if "^^" in message.content.lower() or "^^'" in message.content.lower():
            response = random.choice(self.responses)
            await message.channel.send(response)

        allowed_twitch_channel = 'shinya_nia'
        no_pub = "Il est interdit de faire de la pub pour d'autres chaînes !"

        if 'twitch.tv' in message.content.lower():
            if allowed_twitch_channel in message.content.lower():
                return
            else:
                await message.delete()
                warning_message = await message.channel.send(no_pub)
                await asyncio.sleep(6)
                await warning_message.delete()

        # Process other commands only once
        await self.bot.process_commands(message)

# Function to set up the cog
async def setup(bot):
    await bot.add_cog(UnifiedCog(bot))
