from discord_webhook import DiscordWebhook, DiscordEmbed
import config
import traceback
import requests


def send_webhook(added_count, removed_count, working_proxies):
    print(f"[WEBHOOK] Starting... Added: {added_count}, Removed: {removed_count}, Working: {len(working_proxies)}")
    
    if not config.DISCORD_WEBHOOK_URL or "YOUR_WEBHOOK_URL_HERE" in config.DISCORD_WEBHOOK_URL:
        print("[WEBHOOK] Not configured, skipping.")
        return
    
    try:
        webhook = DiscordWebhook(url=config.DISCORD_WEBHOOK_URL, timeout=60)
        
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
        
        if working_proxies:
            proxies_per_embed = 25
            max_embeds = 3
            for i in range(0, min(len(working_proxies), proxies_per_embed * max_embeds), proxies_per_embed):
                batch = working_proxies[i:i + proxies_per_embed]
                proxy_list = []
                for p in batch:
                    country = p.get('country', '')
                    flag = f" [{country}]" if country else ""
                    proxy_list.append(f"`{p['ip']}:{p['port']}` {p['protocol']}{flag}")
                
                embed2 = DiscordEmbed(title=f"📋 Proxies {i+1}-{min(i+proxies_per_embed, total)}", color=0x3498db)
                embed2.add_embed_field(name="", value="\n".join(proxy_list), inline=False)
                webhook.add_embed(embed2)
        
        # Send via direct requests with proxy support
        payload = webhook.get_json()
        headers = {'Content-Type': 'application/json'}
        
        # Use proxy from working proxies if available
        proxy_for_webhook = None
        if working_proxies:
            proxy_for_webhook = f"http://{working_proxies[0]['ip']}:{working_proxies[0]['port']}"
        
        proxies_dict = {'http': proxy_for_webhook, 'https': proxy_for_webhook} if proxy_for_webhook else None
        
        response = requests.post(
            config.DISCORD_WEBHOOK_URL, 
            json=payload, 
            headers=headers, 
            timeout=60,
            proxies=proxies_dict
        )
        
        if response.status_code in [200, 204]:
            print(f"[WEBHOOK] Sent successfully! Status: {response.status_code}")
        else:
            print(f"[WEBHOOK] Error: {response.status_code} - {response.text}")
        
    except Exception as e:
        print(f"[WEBHOOK] Error: {type(e).__name__}: {e}")
        traceback.print_exc()