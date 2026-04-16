from discord_webhook import DiscordWebhook, DiscordEmbed
import config


def send_webhook(added_count, removed_count, working_proxies):
    if not config.DISCORD_WEBHOOK_URL or config.DISCORD_WEBHOOK_URL == "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL_HERE":
        print("Discord webhook not configured. Skipping notification.")
        return
    webhook = DiscordWebhook(url=config.DISCORD_WEBHOOK_URL)
    embed = DiscordEmbed(title="🔄 Proxy Checker Update", color=0x00ff00)
    embed.add_embed_field(name="✅ Added", value=str(added_count), inline=True)
    embed.add_embed_field(name="❌ Removed", value=str(removed_count), inline=True)
    embed.add_embed_field(name="📊 Total Working", value=str(len(working_proxies)), inline=True)
    if working_proxies:
        proxy_list = []
        for p in working_proxies[:50]:
            proxy_list.append(f"`{p['ip']}:{p['port']}` ({p['protocol']})")
        embed.add_embed_field(name="Working Proxies", value="\n".join(proxy_list) + ("\n... and more" if len(working_proxies) > 50 else ""), inline=False)
    embed.set_footer(text=f"Updated: {working_proxies[0]['ping_ms']}ms avg" if working_proxies else "No working proxies")
    webhook.add_embed(embed)
    webhook.execute()


if __name__ == "__main__":
    test_proxies = [{'ip': '8.8.8.8', 'port': 53, 'protocol': 'HTTP', 'country': 'US', 'ping_ms': 50}]
    send_webhook(1, 0, test_proxies)