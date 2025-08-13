# bot.py
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from database import setup_tables, seed_config, get_config
from salt_logic import rebuild_regexes, calculate_salt, add_user_salt
from commands import setup_commands

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN not found in .env")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Setup DB
setup_tables()
seed_config()
CONFIG = get_config()
rebuild_regexes(CONFIG)

# Register commands
setup_commands(bot, CONFIG)

@bot.event
async def on_ready():
    print(f"✅ SaltBot is online as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    salt_inc = calculate_salt(message.content, len(message.mentions), CONFIG)
    if salt_inc > 0:
        add_user_salt(message.author.id, salt_inc)
    await bot.process_commands(message)

bot.run(TOKEN)
