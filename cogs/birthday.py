import asyncio
import discord
from discord.ext import commands
from datetime import datetime, timedelta
import json
import os

class BirthdayBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = os.path.join("data", "birthdays.json")
        self.user_birthdays = self.load_birthdays()
        self.test_mode = False  
        self.check_task = self.bot.loop.create_task(self.check_birthdays())

    def load_birthdays(self):
        """Load user birthdays from a JSON file."""
        try:
            with open(self.data_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_birthdays(self):
        """Save user birthdays to a JSON file."""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, "w") as f:
            json.dump(self.user_birthdays, f)

    @commands.command(name="anniv")
    async def set_birthday(self, ctx, date: str):
        """Command to store a user's birthday."""
        user_id = str(ctx.author.id)
        try:
            # Try to parse the date provided by the user
            birthday = datetime.strptime(date, "%d/%m").date()
            self.user_birthdays[user_id] = date
            self.save_birthdays()

            # Send a confirmation message
            anniv_message = await ctx.send(f"Merci ! J'ai bien enregistré ton anniversaire pour le {date}. 🎉")

            # Delete the user's !anniv command message
            await ctx.message.delete()

            # Delete the bot's confirmation message after 5 seconds
            await asyncio.sleep(5)
            await anniv_message.delete()

        except ValueError:
            # Handle incorrect date format
            await ctx.send("Le format de la date est incorrect. Utilise JJ/MM !")

    @commands.command(name="test_birthday_check")
    async def test_birthday_check(self, ctx):
        """Command to simulate a birthday check for testing."""
        # Switch to test mode
        self.test_mode = True
        await self.test_check_birthdays()
        await ctx.send("Test birthday check completed.")

    async def check_birthdays(self):
        """Background task to check and send birthday messages daily."""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            if self.test_mode:
                # Skip normal check and perform test check
                await self.test_check_birthdays()
                self.test_mode = False  # Reset test mode after check
            else:
                current_date = datetime.now().strftime("%d/%m")
                # Specify the channel ID or fetch the channel by name
                channel_id = 1295483149169459311  # Replace with your channel ID
                channel = self.bot.get_channel(channel_id)
                
                if not channel:
                    print(f"Channel with ID {channel_id} not found.")
                    return

                for user_id, birthday in self.user_birthdays.items():
                    if birthday == current_date:
                        user = self.bot.get_user(int(user_id))
                        if user:
                            try:
                                # Send the birthday message in the specified channel, mentioning the user
                                await channel.send(f"Bon anniversaire <@{user.id}> ! 🎉")  # Mention the user
                                print(f"Message sent to channel {channel.name}, mentioning {user.name}")
                            except discord.errors.Forbidden:
                                # Handle permission errors
                                print(f"Cannot send message to channel {channel.name}. Check permissions.")
            
            # Sleep until next check
            now = datetime.now()
            next_check = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            await asyncio.sleep((next_check - now).total_seconds())


    async def test_check_birthdays(self):
        """Test birthday message sending by simulating the current date."""
        await self.bot.wait_until_ready()
        print("Starting birthday check...")

        # Simulated current date for testing
        test_date = "17/01"  # Replace with today's date or any test date

        # Specify the channel ID or fetch the channel by name
        channel_id = 1295483149169459311  # Replace with your channel ID
        channel = self.bot.get_channel(channel_id)
        
        if not channel:
            print(f"Channel with ID {channel_id} not found.")
            return

        for user_id, birthday in self.user_birthdays.items():
            if birthday == test_date:
                try:
                    # Send the test message in the specified channel
                    await channel.send(f"Test: Bon anniversaire à <@{user_id}> ! 🎉")
                    print(f"Message sent to channel {channel.name}")
                except discord.errors.Forbidden:
                    # Handle permission errors
                    print(f"Cannot send message to channel {channel.name}. Check permissions.")
        
        print("Test completed.")


async def setup(bot):
    """Function to add the cog to the bot."""
    await bot.add_cog(BirthdayBot(bot))