from consts import BOT_TOKEN
from discord.ext import commands
import discord

bot = commands.Bot(command_prefix='', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print('Bot is ready')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

def run():
    bot.run(BOT_TOKEN)
    