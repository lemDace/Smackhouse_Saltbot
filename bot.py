import os
import discord
from discord.ext import commands
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv
import sqlite3

# --- Load environment variables ---
# First try environment (Render), then .env (local)
if not os.getenv("DISCORD_TOKEN"):
    load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("No Discord token found! Set DISCORD_TOKEN in your environment variables.")

# --- Database setup ---
DB_FILE = "saltbot.db"
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    salt REAL DEFAULT 0
)
""")
conn.commit()

# --- Bot setup ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

analyzer = SentimentIntensityAnalyzer()

# --- Helper functions ---
def get_user_salt(user_id):
    cursor.execute("SELECT salt FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0

def set_user_salt(user_id, username, salt):
    cursor.execute("""
    INSERT INTO users (id, username, salt)
    VALUES (?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET salt = excluded.salt, username = excluded.username
    """, (user_id, username, salt))
    conn.commit()

def add_user_salt(user_id, username, amount):
    current_salt = get_user_salt(user_id)
    new_salt = current_salt + amount
    set_user_salt(user_id, username, new_salt)
    return new_salt

def get_salt_rank(salt):
    if salt > 500:
        return "Salt King"
    elif salt > 300:
        return "Salt Queen"
    elif salt > 100:
        return "Salty Sweet"
    elif salt > 10:
        return "Salt Peasant"
    elif salt == 0:
        return "Sugar Babe"
    else:
        return "No Rank"

# --- Commands ---
@bot.event
async def on_ready():
    print(f"SaltBot is online as {bot.user}")

@bot.command()
async def mysalt(ctx):
    """Check your salt level and rank."""
    salt = get_user_salt(ctx.author.id)
    rank = get_salt_rank(salt)
    await ctx.send(f"{ctx.author.mention}, your salt level is {salt:.2f} — Rank: **{rank}**")

@bot.command()
async def setsalt(ctx, member: discord.Member, amount: float):
    """Admin command to set a user's salt level."""
    if ctx.author.guild_permissions.administrator:
        set_user_salt(member.id, member.name, amount)
        await ctx.send(f"{member.mention}'s salt level set to {amount}")
    else:
        await ctx.send("You do not have permission to use this command.")

@bot.command()
async def saltbothelp(ctx):
    """Show SaltBot help and rules."""
    help_text = (
        "**SaltBot Rules:**\n"
        "- Gain salt when you're salty in chat.\n"
        "- Lose salt by being nice.\n"
        "- Check your salt with `!mysalt`.\n"
        "- Admins can set salt with `!setsalt @user amount`.\n"
        "- Ranks:\n"
        "  - Salt King: > 500\n"
        "  - Salt Queen: > 300\n"
        "  - Salty Sweet: > 100\n"
        "  - Salt Peasant: > 10\n"
        "  - Sugar Babe: = 0\n"
    )
    await ctx.send(help_text)

# --- Sentiment listener ---
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Analyze sentiment
    sentiment_score = analyzer.polarity_scores(message.content)["compound"]

    if sentiment_score < -0.5:  # Very negative
        new_salt = add_user_salt(message.author.id, message.author.name, 5)
        print(f"{message.author} got saltier! New salt: {new_salt}")

    await bot.process_commands(message)

# --- Run bot ---
bot.run(DISCORD_TOKEN)
