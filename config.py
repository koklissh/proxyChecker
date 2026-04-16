# Discord Bot Token (get from https://discord.com/developers/applications)
DISCORD_BOT_TOKEN = ""

# Discord Channel ID for auto-send proxies (right click channel -> copy ID)
DISCORD_CHANNEL_ID = 0

# Check interval in minutes
CHECK_INTERVAL_MINUTES = 5

# Proxy socket timeout in seconds
PROXY_TEST_TIMEOUT = 10

# Database file
DATABASE_FILE = "proxies.db"

# Proxy sources
PROXY_SOURCES = [
    "https://ipspeed.info/ru/free-proxy.php",
    "proxifly:https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.json",
    "text:https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "text:https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
    "text:https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
]