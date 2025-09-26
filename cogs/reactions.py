import discord
from discord.ext import commands
import json
import os
from typing import Dict, Any

class ReactionRoles(commands.Cog):
    """Cog for handling reaction roles on pinned messages"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "reaction_roles.json"
        self.reaction_role_config = self.load_config()
    
    def load_config(self) -> Dict[str, Dict[str, int]]:
        """Load reaction role configuration from JSON file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Convert string keys back to integers for message IDs
                return {int(k): v for k, v in config.items()}
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error loading config file: {e}")
                return {}
        return {}
    
    def save_config(self):
        """Save reaction role configuration to JSON file"""
        try:
            # Convert integer keys to strings for JSON compatibility
            config_to_save = {str(k): v for k, v in self.reaction_role_config.items()}
            with open(self.config_file, 'w') as f:
                json.dump(config_to_save, f, indent=2)
        except Exception as e:
            print(f"Error saving config file: {e}")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Handle reaction additions"""
        # Ignore bot reactions
        if payload.user_id == self.bot.user.id:
            return
        
        message_id = payload.message_id
        emoji = str(payload.emoji)
        
        # Check if this message has reaction role configuration
        if message_id not in self.reaction_role_config:
            return
        
        # Check if this emoji has a role assigned
        if emoji not in self.reaction_role_config[message_id]:
            return
        
        role_id = self.reaction_role_config[message_id][emoji]
        
        try:
            # Get guild, member, and role
            guild = self.bot.get_guild(payload.guild_id)
            if not guild:
                print(f"Guild {payload.guild_id} not found")
                return
                
            member = guild.get_member(payload.user_id)
            if not member:
                print(f"Member {payload.user_id} not found")
                return
                
            role = guild.get_role(role_id)
            if not role:
                print(f"Role {role_id} not found")
                return
            
            # Check if member already has the role
            if role in member.roles:
                return
            
            # Add role to member
            await member.add_roles(role, reason="Reaction role assignment")
            print(f"✅ Added role '{role.name}' to {member.display_name}")
                
        except Exception as e:
            print(f"Error adding role: {e}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Handle reaction removals"""
        # Ignore bot reactions
        if payload.user_id == self.bot.user.id:
            return
        
        message_id = payload.message_id
        emoji = str(payload.emoji)
        
        # Check if this message has reaction role configuration
        if message_id not in self.reaction_role_config:
            return
        
        # Check if this emoji has a role assigned
        if emoji not in self.reaction_role_config[message_id]:
            return
        
        role_id = self.reaction_role_config[message_id][emoji]
        
        try:
            # Get guild, member, and role
            guild = self.bot.get_guild(payload.guild_id)
            if not guild:
                print(f"Guild {payload.guild_id} not found")
                return
                
            member = guild.get_member(payload.user_id)
            if not member:
                print(f"Member {payload.user_id} not found")
                return
                
            role = guild.get_role(role_id)
            if not role:
                print(f"Role {role_id} not found")
                return
            
            # Check if member doesn't have the role
            if role not in member.roles:
                return
            
            # Remove role from member
            await member.remove_roles(role, reason="Reaction role removal")
            print(f"❌ Removed role '{role.name}' from {member.display_name}")
                
        except Exception as e:
            print(f"Error removing role: {e}")

    @discord.app_commands.command(name="setup-reaction-roles", description="Setup reaction roles on pinned messages")
    @discord.app_commands.describe(channel="Channel to check for pinned messages (defaults to current channel)")
    async def setup_reaction_roles(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        """Slash command to help setup reaction roles"""
        # Check if user has administrator permissions
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="Permission Denied",
                description="You need Administrator permissions to use this command!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Use current channel if none specified
        if channel is None:
            channel = interaction.channel
        
        try:
            # Fetch pinned messages
            pinned_messages = await channel.pins()
            
            if not pinned_messages:
                embed = discord.Embed(
                    title="No Pinned Messages",
                    description=f"No pinned messages found in {channel.mention}!",
                    color=discord.Color.yellow()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Create response embed
            embed = discord.Embed(
                title="📌 Pinned Messages Found",
                description=f"Found {len(pinned_messages)} pinned message(s) in {channel.mention}:",
                color=discord.Color.blue()
            )
            
            for i, message in enumerate(pinned_messages[:5], 1):  # Limit to 5 messages
                content_preview = message.content[:100] + "..." if len(message.content) > 100 else message.content
                embed.add_field(
                    name=f"Message {i}",
                    value=f"**ID:** `{message.id}`\n**Content:** {content_preview}\n**[Jump to Message]({message.jump_url})**",
                    inline=False
                )
            
            embed.add_field(
                name="Next Steps",
                value="Use `/add-reaction-role` to configure reaction roles for these messages.",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            print(f"Error fetching pinned messages: {e}")
            embed = discord.Embed(
                title="Error",
                description="An error occurred while fetching pinned messages.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.app_commands.command(name="add-reaction-role", description="Add a reaction role configuration")
    @discord.app_commands.describe(
        message_id="The ID of the message to add reaction role to",
        emoji="The emoji to react with",
        role="The role to assign when users react"
    )
    async def add_reaction_role(self, interaction: discord.Interaction, message_id: str, emoji: str, role: discord.Role):
        """Slash command to add reaction role configurations"""
        # Check if user has administrator permissions
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="Permission Denied",
                description="You need Administrator permissions to use this command!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            message_id_int = int(message_id)
            
            # Initialize message config if it doesn't exist
            if message_id_int not in self.reaction_role_config:
                self.reaction_role_config[message_id_int] = {}
            
            # Add the emoji-role mapping
            self.reaction_role_config[message_id_int][emoji] = role.id
            
            # Save configuration
            self.save_config()
            
            embed = discord.Embed(
                title="Reaction Role Added! ✅",
                description=f"Successfully added reaction role configuration:",
                color=discord.Color.green()
            )
            embed.add_field(name="Message ID", value=f"`{message_id}`", inline=True)
            embed.add_field(name="Emoji", value=emoji, inline=True)
            embed.add_field(name="Role", value=role.mention, inline=True)
            
            # Try to add the reaction to the message
            try:
                channel = interaction.channel
                message = await channel.fetch_message(message_id_int)
                await message.add_reaction(emoji)
                embed.add_field(name="Status", value="✅ Reaction added to message", inline=False)
            except discord.NotFound:
                embed.add_field(name="Note", value="⚠️ Message not found in current channel", inline=False)
            except Exception as e:
                embed.add_field(name="Note", value="⚠️ Could not add reaction to message (you may need to add it manually)", inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            embed = discord.Embed(
                title="Invalid Message ID",
                description="Please provide a valid message ID (numbers only).",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(f"Error adding reaction role: {e}")
            embed = discord.Embed(
                title="Error",
                description="An error occurred while adding the reaction role.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.app_commands.command(name="remove-reaction-role", description="Remove a reaction role configuration")
    @discord.app_commands.describe(
        message_id="The ID of the message",
        emoji="The emoji to remove"
    )
    async def remove_reaction_role(self, interaction: discord.Interaction, message_id: str, emoji: str):
        """Remove a reaction role configuration"""
        # Check if user has administrator permissions
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="Permission Denied",
                description="You need Administrator permissions to use this command!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            message_id_int = int(message_id)
            
            if message_id_int not in self.reaction_role_config:
                embed = discord.Embed(
                    title="Configuration Not Found",
                    description="No reaction role configuration found for this message.",
                    color=discord.Color.yellow()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if emoji not in self.reaction_role_config[message_id_int]:
                embed = discord.Embed(
                    title="Emoji Not Found",
                    description="This emoji is not configured for reaction roles on this message.",
                    color=discord.Color.yellow()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Remove the configuration
            del self.reaction_role_config[message_id_int][emoji]
            
            # Remove message config if empty
            if not self.reaction_role_config[message_id_int]:
                del self.reaction_role_config[message_id_int]
            
            # Save configuration
            self.save_config()
            
            embed = discord.Embed(
                title="Reaction Role Removed! ✅",
                description=f"Successfully removed reaction role configuration for {emoji} on message `{message_id}`",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            embed = discord.Embed(
                title="Invalid Message ID",
                description="Please provide a valid message ID (numbers only).",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(f"Error removing reaction role: {e}")
            embed = discord.Embed(
                title="Error",
                description="An error occurred while removing the reaction role.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.app_commands.command(name="list-reaction-roles", description="List all configured reaction roles")
    async def list_reaction_roles(self, interaction: discord.Interaction):
        """List all configured reaction roles"""
        if not self.reaction_role_config:
            embed = discord.Embed(
                title="No Reaction Roles Configured",
                description="No reaction roles have been configured yet.",
                color=discord.Color.yellow()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📋 Configured Reaction Roles",
            color=discord.Color.blue()
        )
        
        for message_id, emoji_roles in self.reaction_role_config.items():
            field_value = ""
            for emoji, role_id in emoji_roles.items():
                role = interaction.guild.get_role(role_id)
                role_mention = role.mention if role else f"<@&{role_id}> (Role not found)"
                field_value += f"{emoji} → {role_mention}\n"
            
            embed.add_field(
                name=f"Message ID: {message_id}",
                value=field_value,
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Setup function to add the cog
async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))