
import discord
import pytz
from discord.ext import commands
from datetime import datetime
from decouple import config

#Bot key from config
botKey = config('BOT_TOKEN')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)

last_join_times = {}    # Dictionary to store the last join time for each member

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_voice_state_update(member, before, after): # This event is triggered when a member's voice state changes
    
    if member.bot: # Check if the member is a bot and exclude them
        return

    if before.channel != after.channel: # Check if the member has joined a voice channel
        text_channel_id = int(config('TEXT_CHANNEL_ID'))  # config text channel id
        text_channel = bot.get_channel(text_channel_id)

        if text_channel:
            finnish_timezone = pytz.timezone('Europe/Helsinki') # Get the current time in the 'Europe/Helsinki' timezone (Finnish time)
            current_time = datetime.now(finnish_timezone)

            if before.channel is None:
                # Member joined a voice channel
                await text_channel.send(f'{member.display_name} has joined {after.channel.name} at time: {current_time.strftime("%Y-%m-%d %H:%M")}')
                last_join_times[member.id] = current_time  # Update the last join time

            elif after.channel is None: # Member left a voice channel
                if member.id in last_join_times:
                    last_join_time = last_join_times[member.id]
                    duration = current_time - last_join_time
                    formatted_duration = format_duration(duration)
                    last_join_times[member.id] = (current_time, formatted_duration)  # Update last join time and duration
                    await text_channel.send(f'{member.display_name} has left {before.channel.name} after {formatted_duration}')
                else:
                    await text_channel.send(f'Error: {member.display_name} left without a recorded join time.')

    last_join_times[member.id] = datetime.now(finnish_timezone)     # Update the last join time, regardless of whether they joined or left a voice channel


def format_duration(duration):
    seconds = duration.total_seconds()

    if seconds < 60:
        return f'{int(seconds)} seconds'
    elif seconds < 3600:
        minutes = seconds / 60
        return f'{int(minutes)} minutes'
    else:
        hours = seconds / 3600
        minutes = (seconds % 3600) / 60
        if minutes > 0:
            return f'{int(hours)} hours {int(minutes)} minutes'
        else:
            return f'{int(hours)} hours'


@bot.command()
async def last_joined(ctx, *, member_name=None):    # Display a list of all members in the dictionary
    if member_name is None:
        member_list = "\n".join([f'{ctx.guild.get_member(member_id).display_name}: {last_join_time.strftime("%Y-%m-%d %H:%M")}' for member_id, last_join_time in last_join_times.items()])
        await ctx.send(f'Last join times for members:\n{member_list}')

    else:   # Display the last join time for the specified member
        member = discord.utils.find(lambda m: m.display_name == member_name, ctx.guild.members)

        if member:
            member_id = member.id
            if member_id in last_join_times:
                last_join_time = last_join_times[member_id]
                await ctx.send(f'{member.display_name} last joined a voice channel at: {last_join_time.strftime("%Y-%m-%d %H:%M")}')
            else:
                await ctx.send(f'{member.display_name} has not joined a voice channel recently.')
        else:
            await ctx.send(f'Member "{member_name}" not found in this server.')

# Run the bot using your bot token
bot.run(botKey)
