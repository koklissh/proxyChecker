DISCORD_WEBHOOK_URL = "https://discordapp.com/api/webhooks/1494444287637848275/SI-ky6Hfu64tijB6L0C5T8LBk_qdd3mYLmmpYw1mvtfNhoGDcrPMrJTZG11KLl6DXYK9"
DISCORD_BOT_TOKEN = ""  # Bot token for Discord bot (get from Discord Developer Portal)
CHECK_INTERVAL_MINUTES = 5
PROXY_TEST_TIMEOUT = 10
PROXY_TEST_URLS = [
    "http://httpbin.org/ip",
    "https://api.ipify.org?format=json"
]
DATABASE_FILE = "proxies.db"
PROXY_SOURCES = [
    "https://ipspeed.info/ru/free-proxy.php",
    "proxifly:https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.json",
    "text:https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "text:https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
    "text:https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
]