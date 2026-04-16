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
next_check_time = time.time()


def progress_callback(idx, total, ip, port, success, ping):
    status = f"✅ {ping}ms" if success else "❌"
    print(f"[{idx+1}/{total}] {ip}:{port} - {status}")


async def job_async():
    global next_check_time
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
    
    next_check_time = time.time() + (config.CHECK_INTERVAL_MINUTES * 60)
    
    await send_proxies_to_channel(working_proxies)
    
    return len(working_proxies)


async def send_proxies_to_channel(working_proxies):
    if not config.DISCORD_CHANNEL_ID:
        print("[Discord] Channel ID not set, skipping...")
        return
    
    channel = bot.get_channel(config.DISCORD_CHANNEL_ID)
    if not channel:
        print(f"[Discord] Channel {config.DISCORD_CHANNEL_ID} not found!")
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


async def main_loop():
    global next_check_time
    
    if config.DISCORD_BOT_TOKEN:
        print(f"\n[Discord] Starting bot with token {config.DISCORD_BOT_TOKEN[:20]}...")
    
    database.init_db(config.DATABASE_FILE)
    
    print("[Proxy] Running initial check...")
    await job_async()
    next_check_time = time.time() + (config.CHECK_INTERVAL_MINUTES * 60)
    
    print(f"\n[System] Bot ready! Check interval: {config.CHECK_INTERVAL_MINUTES} minutes")
    print(f"[System] Discord: {'Enabled' if config.DISCORD_BOT_TOKEN else 'Disabled'}")
    print(f"[System] Channel ID: {config.DISCORD_CHANNEL_ID}")
    print("=" * 50)
    
    while True:
        current_time = time.time()
        
        if current_time >= next_check_time:
            print(f"\n[{time.strftime('%H:%M:%S')}] Scheduled check triggered")
            await job_async()
        
        await asyncio.sleep(10)


async def start_bot():
    if config.DISCORD_BOT_TOKEN:
        async with bot:
            await bot.start(config.DISCORD_BOT_TOKEN)
    else:
        await main_loop()


def main():
    print("=" * 50)
    print("  Proxy Checker Bot")
    print("=" * 50)
    print(f"Database: {config.DATABASE_FILE}")
    print("=" * 50)
    
    asyncio.run(start_bot())


if __name__ == "__main__":
    main()