
import discord
import pytz
from discord.ext import commands
from datetime import datetime
from decouple import config


#my bot key from config
botKey = config('BOT_TOKEN')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)

# Dictionary to store the last join time for each member
last_join_times = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_voice_state_update(member, before, after):
    # This event is triggered when a member's voice state changes
    
    # Check if the member has joined a voice channel
    if before.channel != after.channel:
        text_channel_id = int(config('TEXT_CHANNEL_ID'))  # config text channel id
        text_channel = bot.get_channel(text_channel_id)

        if text_channel:
            # Get the current time in the 'Europe/Helsinki' timezone (Finnish time)
            finnish_timezone = pytz.timezone('Europe/Helsinki')
            current_time = datetime.now(finnish_timezone).strftime("%Y-%m-%d %H:%M")

            if before.channel is None:
                # Member joined a voice channel
                await text_channel.send(f'{member.name} has joined {after.channel.name} at time: {current_time}')
    
    # Update the last join time, regardless of whether they joined a voice channel
    last_join_times[member.id] = datetime.now(finnish_timezone)

@bot.command()
async def last_joined(ctx, *, member_name=None):
    if member_name is None:
        # Display a list of all members in the dictionary
        member_list = "\n".join([f'{ctx.guild.get_member(member_id).name}: {last_join_time.strftime("%Y-%m-%d %H:%M")}' for member_id, last_join_time in last_join_times.items()])
        await ctx.send(f'Last join times for members:\n{member_list}')
    else:
        # Display the last join time for the specified member
        member = discord.utils.find(lambda m: m.name == member_name, ctx.guild.members)

        if member:
            member_id = member.id
            if member_id in last_join_times:
                last_join_time = last_join_times[member_id]
                await ctx.send(f'{member.name} last joined a voice channel at: {last_join_time.strftime("%Y-%m-%d %H:%M")}')
            else:
                await ctx.send(f'{member.name} has not joined a voice channel recently.')
        else:
            await ctx.send(f'Member "{member_name}" not found in this server.')

# Run the bot using your bot token
bot.run(botKey)
