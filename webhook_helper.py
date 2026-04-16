from discord_webhook import DiscordWebhook, DiscordEmbed
import config
import traceback
import requests
import json


def send_webhook(added_count, removed_count, working_proxies):
    print(f"[WEBHOOK] Starting... Added: {added_count}, Removed: {removed_count}, Working: {len(working_proxies)}")
    
    if not config.DISCORD_WEBHOOK_URL or "YOUR_WEBHOOK_URL_HERE" in config.DISCORD_WEBHOOK_URL:
        print("[WEBHOOK] Not configured, skipping.")
        return
    
    try:
        total = len(working_proxies)
        avg_ping = 0
        if working_proxies:
            avg_ping = sum(p.get('ping_ms', 0) for p in working_proxies) // total
        
        embeds = []
        
        embed1 = {
            "title": "🔄 Proxy Checker Update",
            "color": 65280,
            "fields": [
                {"name": "✅ Added", "value": str(added_count), "inline": True},
                {"name": "❌ Removed", "value": str(removed_count), "inline": True},
                {"name": "📊 Total Working", "value": str(total), "inline": True},
                {"name": "⚡ Avg Ping", "value": f"{avg_ping}ms", "inline": True}
            ],
            "footer": {"text": f"Checked: {total} proxies"}
        }
        embeds.append(embed1)
        
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
                
                embed2 = {
                    "title": f"📋 Proxies {i+1}-{min(i+proxies_per_embed, total)}",
                    "color": 52224,
                    "fields": [
                        {"name": "", "value": "\n".join(proxy_list), "inline": False}
                    ]
                }
                embeds.append(embed2)
        
        payload = {"embeds": embeds}
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(
            config.DISCORD_WEBHOOK_URL, 
            data=json.dumps(payload),
            headers=headers, 
            timeout=60
        )
        
        if response.status_code in [200, 204]:
            print(f"[WEBHOOK] Sent successfully! Status: {response.status_code}")
        else:
            print(f"[WEBHOOK] Error: {response.status_code} - {response.text[:100]}")
        
    except Exception as e:
        print(f"[WEBHOOK] Error: {type(e).__name__}: {e}")
        traceback.print_exc()