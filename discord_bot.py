import discord
from discord.ext import commands
import asyncio
import sqlite3
import config as cfg

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

DB_FILE = cfg.DATABASE_FILE


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
    
    proxies_per_msg = 25
    for i in range(0, min(len(working), 75), proxies_per_msg):
        batch = working[i:i + proxies_per_msg]
        proxy_list = []
        for p in batch:
            country = p.get('country', '')
            flag = f" [{country}]" if country else ""
            proxy_list.append(f"`{p['ip']}:{p['port']}` {p['protocol']}{flag}")
        
        embed2 = discord.Embed(
            title=f"📋 Proxies {i+1}-{min(i+proxies_per_msg, total)}", 
            color=0x3498db,
            description="\n".join(proxy_list)
        )
        await ctx.send(embed=embed2)
    
    await ctx.send(f"✅ Отправлено {total} прокси!")


@bot.command(name="check")
async def trigger_check(ctx):
    await ctx.send("🔄 Запускаю проверку прокси...")
    import parser
    import checker
    import database
    
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
    embed.add_field(name="📁 Total in DB", value=str(total), inline=True)
    embed.add_field(name="❌ Not Working", value=str(total - working), inline=True)
    await ctx.send(embed=embed)


@bot.command(name="helpp")
async def helpp(ctx):
    embed = discord.Embed(title="📖 Proxy Bot Commands", color=0x3498db)
    embed.add_field(name="!proxies", value="Показать рабочие прокси", inline=False)
    embed.add_field(name="!check", value="Запустить проверку прокси", inline=False)
    embed.add_field(name="!stats", value="Показать статистику", inline=False)
    embed.add_field(name="!helpp", value="Показать эту справку", inline=False)
    await ctx.send(embed=embed)


if __name__ == "__main__":
    print(f"Starting Discord bot...")
    print(f"Bot token: {cfg.DISCORD_BOT_TOKEN[:20]}..." if cfg.DISCORD_BOT_TOKEN else "No token!")
    bot.run(cfg.DISCORD_BOT_TOKEN)