import requests
import discord
from discord.ext import commands, tasks
import os
import keep_alive

keep_alive.keep_alive()
token = os.environ['TOKEN']
WEBHOOK_URL = os.environ['webhook']

DEFAULT_TARGET_BOT_ID = 877644741339144244  # Replace with the target bot's ID  #1175905263182688336 #877644741339144244

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True  # Ensure this intent is enabled
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print('Starting periodic checks...')
    check_target_bot_status.start()

@tasks.loop(minutes=1)  # Adjust the interval as needed
async def check_target_bot_status():
    bot_online = False
    for guild in bot.guilds:
        target_bot = discord.utils.get(guild.members, id=DEFAULT_TARGET_BOT_ID)
        if target_bot:
            presence = target_bot.status
            if presence == discord.Status.online:
                bot_online = True
                break

    if not bot_online:
        # Notify via webhook
        message = {
            "content": f"<@729429813726543975> Your bot <@{DEFAULT_TARGET_BOT_ID}> is offline."
        }
        requests.post(WEBHOOK_URL, json=message)
        print(f"The bot with ID {DEFAULT_TARGET_BOT_ID} is offline. Notification sent to webhook.")

@bot.command(name='checkstatus')
async def check_status(ctx, bot_id: int = None):
    """Check the status of a bot by its ID. If no ID is provided, use the default ID."""
    bot_id = bot_id or DEFAULT_TARGET_BOT_ID
    found = False
    for guild in bot.guilds:
        target_bot = discord.utils.get(guild.members, id=bot_id)
        if target_bot:
            presence = target_bot.status
            status = "online" if presence == discord.Status.online else "offline"
            await ctx.send(f'The bot with ID {bot_id} is {status}.')
            found = True
            break
    if not found:
        await ctx.send(f'Target bot with ID {bot_id} not found in any guilds.')

bot.run(token)
