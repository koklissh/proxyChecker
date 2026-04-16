from discord_webhook import DiscordWebhook, DiscordEmbed
import config


def send_webhook(added_count, removed_count, working_proxies):
    if not config.DISCORD_WEBHOOK_URL or "YOUR_WEBHOOK_URL_HERE" in config.DISCORD_WEBHOOK_URL:
        print("Discord webhook not configured. Skipping notification.")
        return
    
    webhook = DiscordWebhook(url=config.DISCORD_WEBHOOK_URL)
    
    total = len(working_proxies)
    avg_ping = 0
    if working_proxies:
        avg_ping = sum(p.get('ping_ms', 0) for p in working_proxies) // total
    
    embed = DiscordEmbed(title="🔄 Proxy Checker Update", color=0x00ff00)
    embed.add_embed_field(name="✅ Added", value=str(added_count), inline=True)
    embed.add_embed_field(name="❌ Removed", value=str(removed_count), inline=True)
    embed.add_embed_field(name="📊 Total Working", value=str(total), inline=True)
    embed.add_embed_field(name="⚡ Avg Ping", value=f"{avg_ping}ms", inline=True)
    embed.set_footer(text=f"Checked: {total} proxies")
    webhook.add_embed(embed)
    
    proxies_per_embed = 25
    for i in range(0, len(working_proxies), proxies_per_embed):
        batch = working_proxies[i:i + proxies_per_embed]
        proxy_list = []
        for p in batch:
            country = p.get('country', '')
            flag = f" {country}" if country else ""
            proxy_list.append(f"`{p['ip']}:{p['port']}` ({p['protocol']}){flag}")
        
        embed2 = DiscordEmbed(title=f"📋 Working Proxies ({i+1}-{min(i+proxies_per_embed, total)})", color=0x3498db)
        embed2.add_embed_field(name="Proxies", value="\n".join(proxy_list), inline=False)
        webhook.add_embed(embed2)
    
    try:
        webhook.execute()
        print(f"Webhook sent: {total} proxies")
    except Exception as e:
        print(f"Webhook error: {e}")