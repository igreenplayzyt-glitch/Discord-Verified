import discord
from discord.ext import commands
import os

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Configuration
VERIFICATION_CHANNEL_ID = 1402708945407316090  # Set this to your verification channel ID
VERIFIED_ROLE_NAME = "Verified"  # Name of the role to assign
VERIFICATION_MESSAGE_ID = None  # Set this to your verification message ID

@bot.event
async def on_ready():
    print(f'{bot.user} has logged in!')
    print(f'Bot is ready and connected to {len(bot.guilds)} guilds')

@bot.event
async def on_reaction_add(reaction, user):
    # Ignore bot reactions
    if user.bot:
        return
    
    # Check if reaction is ✅
    if str(reaction.emoji) != '✅':
        return
    
    # Get the guild
    guild = reaction.message.guild
    if not guild:
        return
    
    # Find the verified role
    verified_role = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
    if not verified_role:
        # Create the role if it doesn't exist
        try:
            verified_role = await guild.create_role(
                name=VERIFIED_ROLE_NAME,
                color=discord.Color.green(),
                reason="Verification role created by bot"
            )
            print(f"Created role: {VERIFIED_ROLE_NAME}")
        except discord.Forbidden:
            print("Bot doesn't have permission to create roles")
            return
    
    # Get the member
    member = guild.get_member(user.id)
    if not member:
        return
    
    # Check if user already has the role
    if verified_role in member.roles:
        print(f"{member.display_name} already has the verified role")
        return
    
    # Add the verified role
    try:
        await member.add_roles(verified_role, reason="User verified via reaction")
        print(f"Verified {member.display_name}")
        
        # Optional: Send a DM to the user
        try:
            await user.send(f"Welcome to {guild.name}! You have been verified.")
        except discord.Forbidden:
            pass  # User has DMs disabled
            
    except discord.Forbidden:
        print("Bot doesn't have permission to assign roles")
    except Exception as e:
        print(f"Error assigning role: {e}")

@bot.event
async def on_reaction_remove(reaction, user):
    # Ignore bot reactions
    if user.bot:
        return
    
    # Check if reaction is ✅
    if str(reaction.emoji) != '✅':
        return
    
    # Get the guild
    guild = reaction.message.guild
    if not guild:
        return
    
    # Find the verified role
    verified_role = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
    if not verified_role:
        return
    
    # Get the member
    member = guild.get_member(user.id)
    if not member:
        return
    
    # Remove the verified role if they have it
    if verified_role in member.roles:
        try:
            await member.remove_roles(verified_role, reason="User removed verification reaction")
            print(f"Removed verification from {member.display_name}")
        except discord.Forbidden:
            print("Bot doesn't have permission to remove roles")
        except Exception as e:
            print(f"Error removing role: {e}")

@bot.command(name='setup_verification')
@commands.has_permissions(administrator=True)
async def setup_verification(ctx):
    """Set up a verification message in the current channel"""
    embed = discord.Embed(
        title="Server Verification",
        description="React with ✅ to verify yourself and gain access to the server!",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="Instructions",
        value="Click the ✅ reaction below to get verified",
        inline=False
    )
    
    message = await ctx.send(embed=embed)
    await message.add_reaction('✅')
    
    await ctx.send(f"Verification message created! Message ID: {message.id}")

@bot.command(name='verify_user')
@commands.has_permissions(manage_roles=True)
async def verify_user(ctx, member: discord.Member):
    """Manually verify a user"""
    verified_role = discord.utils.get(ctx.guild.roles, name=VERIFIED_ROLE_NAME)
    
    if not verified_role:
        verified_role = await ctx.guild.create_role(
            name=VERIFIED_ROLE_NAME,
            color=discord.Color.green(),
            reason="Verification role created by bot"
        )
    
    if verified_role in member.roles:
        await ctx.send(f"{member.display_name} is already verified!")
        return
    
    await member.add_roles(verified_role, reason=f"Manually verified by {ctx.author}")
    await ctx.send(f"✅ {member.display_name} has been verified!")

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("Please set the DISCORD_BOT_TOKEN environment variable")
        print("You can do this in the Secrets tab of your Repl")
    else:
        bot.run(token)
