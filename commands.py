# commands.py
from discord.ext import commands
from salt_logic import get_user_salt, set_user_salt, add_user_salt, get_rank_for_total, today_utc_str, current_week_bounds_utc
from database import cur, conn, get_config, save_config_key
import discord

def setup_commands(bot, config):

    @bot.command()
    async def mysalt(ctx):
        total = get_user_salt(ctx.author.id)
        rank = get_rank_for_total(total, config)
        await ctx.send(f"🧂 {ctx.author.mention}, your salt is **{total:.2f}** — Rank: **{rank}**")

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def setsalt(ctx, member: discord.Member, value: float):
        set_user_salt(member.id, value)
        await ctx.send(f"✅ Set {member.mention}'s salt to **{value:.2f}**")

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def resetsalt(ctx, member: discord.Member):
        current = get_user_salt(member.id)
        if current == 0:
            await ctx.send(f"{member.mention} already has **0.00** salt.")
            return
        set_user_salt(member.id, 0.0)
        add_user_salt(member.id, -current)
        await ctx.send(f"🧹 Reset {member.mention}'s salt to **0.00** (logged -{current:.2f} today).")

    @bot.command()
    async def saltboardtoday(ctx):
        date_str = today_utc_str()
        cur.execute("SELECT user_id, amount FROM history WHERE date = ? ORDER BY amount DESC", (date_str,))
        rows = cur.fetchall()
        if not rows:
            await ctx.send("😇 No salt recorded today.")
            return
        lines = [f"{await bot.fetch_user(int(row['user_id'])).mention}: {float(row['amount']):.2f}" for row in rows]
        await ctx.send("📅 **Today's Salt Leaderboard (UTC)**\n" + "\n".join(lines))

    @bot.command()
    async def saltboardweek(ctx):
        monday_str, sunday_str = current_week_bounds_utc()
        cur.execute("""
            SELECT user_id, SUM(amount) AS total
            FROM history
            WHERE date >= ? AND date <= ?
            GROUP BY user_id
            ORDER BY total DESC
        """, (monday_str, sunday_str))
        rows = cur.fetchall()
        if not rows:
            await ctx.send("😇 No salt recorded this week.")
            return
        lines = [f"{await bot.fetch_user(int(row['user_id'])).mention}: {float(row['total']):.2f}" for row in rows]
        await ctx.send("📆 **This Week's Salt Leaderboard (UTC)**\n" + "\n".join(lines))
