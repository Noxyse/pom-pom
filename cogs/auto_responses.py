import random
import asyncio
from discord.ext import commands

# Define a Cog class for auto responses
class AutoResponsesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot # Storing the bot instance for later use

        # Attempt to read responses from text file
        try:
            with open('chapo_responses.txt', 'r', encoding='utf-8') as file:
                # Store each non-empty line from the file as a response
                self.responses = [line.strip() for line in file if line.strip()] 
        except FileNotFoundError:
            self.responses = ['No responses found.']

    # Listener for incoming messages
    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from bot itself to prevent loops
        if message.author == self.bot.user:
            return
        await self.bot.process_commands(message)

        # Dictionnary for different automatic responses based on keywords
        response_dict={
            'bibble':'Tu le préfères à moi, pas vrai...?',
            'salut':"Bonjour {mention} !"
        }

        # Check for keywords in the message and response accordingly
        for keyword, response in response_dict.items():
            if keyword in message.content.lower():
                formatted_response = response.format(mention=message.author.mention)
                await message.channel.send(formatted_response)
                return

        # Check if the message contains '^^' to send a random response
        if '^^' in message.content.lower():
            response = random.choice(self.responses)
            await message.channel.send(response)

        # Check for promotion of other Twitch channels
        allowed_twitch_channel = 'shinya_nia'
        no_pub = "Il est interdit de faire de la pub pour d'autres chaînes à bord de ce train !"

        # Check if the message contains a link to Twitch
        if 'twitch.tv' in message.content.lower():
            if allowed_twitch_channel in message.content.lower():
                return
            else:
                await message.delete()
                warning_message = await message.channel.send(no_pub)
                await asyncio.sleep(6)
                await warning_message.delete()

        await self.bot.process_commands(message)

# Function to set up the cog
async def setup(bot):
    await bot.add_cog(AutoResponsesCog(bot))