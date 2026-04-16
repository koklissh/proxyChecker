DISCORD_BOT_TOKEN = ""  # Bot token
DISCORD_CHANNEL_ID = 0   # Channel ID for proxy updates
CHECK_INTERVAL_MINUTES = 5
PROXY_TEST_TIMEOUT = 10
DATABASE_FILE = "proxies.db"
PROXY_SOURCES = [
    "https://ipspeed.info/ru/free-proxy.php",
    "proxifly:https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.json",
    "text:https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "text:https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
    "text:https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
]