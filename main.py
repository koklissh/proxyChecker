import time
import schedule
import threading
import asyncio
import sqlite3
import parser
import checker
import database
import webhook_helper as dw
import config

import discord
from discord.ext import commands


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

DB_FILE = config.DATABASE_FILE


def progress_callback(idx, total, ip, port, success, ping):
    status = f"✅ {ping}ms" if success else "❌"
    print(f"[{idx+1}/{total}] {ip}:{port} - {status}")


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


def job():
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting proxy check...")
    print("=" * 40)
    parsed_proxies = parser.parse_proxies()
    print(f"\nFound {len(parsed_proxies)} proxies from sources")
    print(f"Checking proxies... (this may take a while)\n")
    
    working_proxies = checker.check_proxies_sync(parsed_proxies, progress_callback)
    print(f"\nWorking: {len(working_proxies)} proxies")
    added, removed = database.update_proxies(config.DATABASE_FILE, parsed_proxies, working_proxies)
    print(f"Added: {added}, Removed: {removed}")
    all_working = database.get_working_proxies(config.DATABASE_FILE)
    dw.send_webhook(added, removed, all_working)
    print("Check complete\n")


def get_working_proxies():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT ip, port, protocol, country, ping_ms FROM proxies WHERE is_working = 1 ORDER BY ping_ms')
    rows = cursor.fetchall()
    conn.close()
    return [{'ip': r[0], 'port': r[1], 'protocol': r[2], 'country': r[3], 'ping_ms': r[4]} for r in rows]


@bot.command(name="proxies")
async def send_proxies(ctx):
    await ctx.send("🔄 Получаю рабочие прокси...")
    working = get_working_proxies()
    
    if not working:
        await ctx.send("❌ Нет рабочих прокси!")
        return
    
    total = len(working)
    avg_ping = sum(p.get('ping_ms', 0) for p in working) // total
    
    embed = discord.Embed(title="🔄 Proxy Checker", color=0x00ff00)
    embed.add_field(name="📊 Total Working", value=str(total), inline=True)
    embed.add_field(name="⚡ Avg Ping", value=f"{avg_ping}ms", inline=True)
    await ctx.send(embed=embed)
    
    for i in range(0, min(len(working), 75), 25):
        batch = working[i:i + 25]
        proxy_list = [f"`{p['ip']}:{p['port']}` {p['protocol']}" for p in batch]
        embed2 = discord.Embed(title=f"📋 Proxies {i+1}-{min(i+25, total)}", color=0x3498db, description="\n".join(proxy_list))
        await ctx.send(embed=embed2)


@bot.command(name="check")
async def trigger_check(ctx):
    await ctx.send("🔄 Запускаю проверку прокси...")
    parsed = parser.parse_proxies()
    await ctx.send(f"Найдено {len(parsed)} прокси, проверяю...")
    working = checker.check_proxies_sync(parsed)
    database.update_proxies(DB_FILE, parsed, working)
    await ctx.send(f"✅ Проверка завершена! Рабочих: {len(working)}")


@bot.command(name="stats")
async def stats(ctx):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM proxies WHERE is_working = 1')
    working = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM proxies')
    total = cursor.fetchone()[0]
    conn.close()
    
    embed = discord.Embed(title="📊 Proxy Stats", color=0x00ff00)
    embed.add_field(name="✅ Working", value=str(working), inline=True)
    embed.add_field(name="📁 Total", value=str(total), inline=True)
    await ctx.send(embed=embed)


@bot.command(name="helpp")
async def helpp(ctx):
    embed = discord.Embed(title="📖 Commands", color=0x3498db)
    embed.add_field(name="!proxies", value="Рабочие прокси", inline=False)
    embed.add_field(name="!check", value="Проверить прокси", inline=False)
    embed.add_field(name="!stats", value="Статистика", inline=False)
    await ctx.send(embed=embed)


def run_bot():
    if config.DISCORD_BOT_TOKEN:
        print(f"\n[Discord Bot] Starting with token {config.DISCORD_BOT_TOKEN[:20]}...")
        bot.run(config.DISCORD_BOT_TOKEN)
    else:
        print("\n[Discord Bot] Token not configured, skipping...")


def main():
    print("=" * 50)
    print("  Proxy Checker Bot + Discord Bot")
    print("=" * 50)
    print(f"Check interval: {config.CHECK_INTERVAL_MINUTES} min")
    print(f"Database: {config.DATABASE_FILE}")
    print(f"Discord Bot: {'Enabled' if config.DISCORD_BOT_TOKEN else 'Disabled'}")
    print("=" * 50)
    
    database.init_db(config.DATABASE_FILE)
    
    job()
    schedule.every(config.CHECK_INTERVAL_MINUTES).minutes.do(job)
    
    scheduler_thread = threading.Thread(target=run_schedule, daemon=True)
    scheduler_thread.start()
    
    if config.DISCORD_BOT_TOKEN:
        run_bot()
    else:
        while True:
            time.sleep(60)


if __name__ == "__main__":
    main()