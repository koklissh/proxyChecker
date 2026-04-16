DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL_HERE"
CHECK_INTERVAL_MINUTES = 5
PROXY_TEST_TIMEOUT = 10
PROXY_TEST_URLS = [
    "http://httpbin.org/ip",
    "https://api.ipify.org?format=json"
]
DATABASE_FILE = "proxies.db"
PROXY_SOURCES = [
    "https://ipspeed.info/ru/free-proxy.php",
    # "https://free.geonix.com/ru/"  # Требует Selenium (динамическая загрузка)
]