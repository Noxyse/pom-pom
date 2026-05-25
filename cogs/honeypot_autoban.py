import discord
from discord.ext import commands
import json
import os

class HoneypotAutoBan(commands.Cog):
    """Automatically bans users who get the honeypot role"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "honeypot_config.json"
        self.config = self.load_config()
    
    def load_config(self):
        """Load honeypot role configuration"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {"honeypot_role_id": None}
        return {"honeypot_role_id": None}
    
    def save_config(self):
        """Save honeypot role configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Detect when a member gets a new role and check if it's the honeypot role"""
        honeypot_role_id = self.config.get("honeypot_role_id")
        
        # If honeypot role is not configured, do nothing
        if not honeypot_role_id:
            return
        
        # Get the roles that were added
        added_roles = set(after.roles) - set(before.roles)
        
        # Check if the honeypot role was added
        for role in added_roles:
            if role.id == honeypot_role_id:
                try:
                    # Log the ban
                    print(f"🚨 HONEYPOT TRIGGERED by {after} ({after.id})")
                    
                    # Ban the user
                    await after.ban(
                        reason="Received honeypot role from onboarding - likely bot/raider",
                        delete_message_seconds=0
                    )
                    
                    print(f"🔨 Banned user: {after} ({after.id})")
                    
                except discord.Forbidden:
                    print(f"❌ Failed to ban {after} - insufficient permissions")
                except Exception as e:
                    print(f"❌ Error banning user: {e}")
                
                break  # Only need to ban once

    @commands.hybrid_command(name="set-honeypot-role", description="Set the honeypot role for auto-banning")
    @discord.app_commands.describe(role="The role that triggers an automatic ban")
    async def set_honeypot_role(self, ctx, role: discord.Role):
        """Configure which role is the honeypot"""
        # Check permissions
        if not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="Permission Denied",
                description="You need Administrator permissions to use this command!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        # Save configuration
        self.config["honeypot_role_id"] = role.id
        self.save_config()
        
        # Confirmation
        embed = discord.Embed(
            title="✅ Honeypot Role Configured",
            description=f"Users who receive the {role.mention} role will be automatically banned.",
            color=discord.Color.green()
        )
        embed.add_field(
            name="⚠️ Warning",
            value="Make sure this role is ONLY assigned through your onboarding honeypot button!",
            inline=False
        )
        
        await ctx.send(embed=embed, ephemeral=True)
        print(f"✅ Honeypot role set to '{role.name}' by {ctx.author}")

    @commands.hybrid_command(name="remove-honeypot-role", description="Remove the honeypot role configuration")
    async def remove_honeypot_role(self, ctx):
        """Remove honeypot role configuration"""
        # Check permissions
        if not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="Permission Denied",
                description="You need Administrator permissions to use this command!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        # Remove configuration
        self.config["honeypot_role_id"] = None
        self.save_config()
        
        embed = discord.Embed(
            title="✅ Honeypot Disabled",
            description="The honeypot auto-ban system has been disabled.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, ephemeral=True)
        print(f"✅ Honeypot role removed by {ctx.author}")

    @commands.hybrid_command(name="check-honeypot", description="Check current honeypot configuration")
    async def check_honeypot(self, ctx):
        """Check which role is configured as honeypot"""
        honeypot_role_id = self.config.get("honeypot_role_id")
        
        if not honeypot_role_id:
            embed = discord.Embed(
                title="Honeypot Not Configured",
                description="No honeypot role is currently set.",
                color=discord.Color.yellow()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        role = ctx.guild.get_role(honeypot_role_id)
        
        if not role:
            embed = discord.Embed(
                title="⚠️ Role Not Found",
                description=f"Honeypot role ID `{honeypot_role_id}` no longer exists.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🛡️ Honeypot Configuration",
            description=f"Auto-ban is enabled for: {role.mention}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Role Name", value=role.name, inline=True)
        embed.add_field(name="Role ID", value=f"`{role.id}`", inline=True)
        
        await ctx.send(embed=embed, ephemeral=True)

# Setup function
async def setup(bot):
    await bot.add_cog(HoneypotAutoBan(bot))
