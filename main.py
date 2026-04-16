import asyncio
import time
import schedule
import sqlite3
import parser
import checker
import database
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


async def job_async():
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting proxy check...")
    print("=" * 40)
    
    parsed_proxies = await parser.parse_proxies()
    print(f"\nFound {len(parsed_proxies)} proxies")
    print(f"Checking proxies...\n")
    
    working_proxies = await checker.check_proxies_async(parsed_proxies, progress_callback)
    print(f"\nWorking: {len(working_proxies)} proxies")
    
    added, removed = database.update_proxies(config.DATABASE_FILE, parsed_proxies, working_proxies)
    print(f"Added: {added}, Removed: {removed}")
    print("Check complete\n")
    
    await send_proxies_to_channel(working_proxies)
    
    return len(working_proxies)


async def send_proxies_to_channel(working_proxies):
    channel = bot.get_channel(config.DISCORD_CHANNEL_ID) if config.DISCORD_CHANNEL_ID else None
    
    if not channel:
        print("[Discord] Channel ID not set, skipping...")
        return
    
    if not working_proxies:
        await channel.send("❌ Нет рабочих прокси!")
        return
    
    total = len(working_proxies)
    avg_ping = sum(p.get('ping_ms', 0) for p in working_proxies) // total
    
    embed = discord.Embed(title="🔄 Proxy Checker Update", color=0x00ff00)
    embed.add_field(name="📊 Total Working", value=str(total), inline=True)
    embed.add_field(name="⚡ Avg Ping", value=f"{avg_ping}ms", inline=True)
    embed.add_field(name="⏰ Updated", value=time.strftime("%H:%M"), inline=True)
    await channel.send(embed=embed)
    
    for i in range(0, min(len(working_proxies), 75), 25):
        batch = working_proxies[i:i + 25]
        proxy_list = [f"`{p['ip']}:{p['port']}` {p['protocol']}" for p in batch]
        embed2 = discord.Embed(
            title=f"📋 Proxies {i+1}-{min(i+25, total)}", 
            color=0x3498db, 
            description="\n".join(proxy_list)
        )
        await channel.send(embed=embed2)
    
    print(f"[Discord] Sent {total} proxies to channel")


def job():
    asyncio.get_event_loop().run_until_complete(job_async())


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


def get_working_proxies():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT ip, port, protocol, country, ping_ms FROM proxies WHERE is_working = 1 ORDER BY ping_ms')
    rows = cursor.fetchall()
    conn.close()
    return [{'ip': r[0], 'port': r[1], 'protocol': r[2], 'country': r[3], 'ping_ms': r[4]} for r in rows]


@bot.command(name="proxies")
async def send_proxies(ctx):
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
    parsed = await parser.parse_proxies()
    await ctx.send(f"Найдено {len(parsed)} прокси, проверяю...")
    working = await checker.check_proxies_async(parsed)
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


async def start_bot_and_check():
    if config.DISCORD_BOT_TOKEN:
        print(f"\n[Discord] Starting bot...")
        asyncio.create_task(bot.start(config.DISCORD_BOT_TOKEN))
        await asyncio.sleep(3)
        
        print("[Discord] Bot started, running proxy check...")
        await job_async()
        
        schedule.every(config.CHECK_INTERVAL_MINUTES).minutes.do(job)
        
        while True:
            schedule.run_pending()
            await asyncio.sleep(1)
    else:
        print("[Discord] Token not configured!")
        job()
        while True:
            schedule.run_pending()
            time.sleep(1)


def main():
    print("=" * 50)
    print("  Proxy Checker Bot")
    print("=" * 50)
    print(f"Check interval: {config.CHECK_INTERVAL_MINUTES} min")
    print(f"Database: {config.DATABASE_FILE}")
    print("=" * 50)
    
    database.init_db(config.DATABASE_FILE)
    
    asyncio.run(start_bot_and_check())


if __name__ == "__main__":
    main()