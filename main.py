import time
import schedule
import parser
import checker
import database
import discord_bot as dw
import config


def progress_callback(idx, total, ip, port, success, ping):
    status = f"✅ {ping}ms" if success else "❌"
    print(f"[{idx+1}/{total}] {ip}:{port} - {status}")


def job():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting proxy check...")
    print("=" * 40)
    parsed_proxies = parser.parse_proxies()
    print(f"\nFound {len(parsed_proxies)} proxies from sources")
    print(f"Checking proxies... (this may take a while)\n")
    
    working_proxies = checker.check_proxies_sync(parsed_proxies, progress_callback)
    print(f"\nWorking: {len(working_proxies)} proxies")
    added, removed = database.update_proxies(config.DATABASE_FILE, parsed_proxies, working_proxies)
    print(f"Added: {added}, Removed: {removed}")
    all_working = database.get_working_proxies(config.DATABASE_FILE)
    dw.send_webhook(added, removed, all_working)
    print("Check complete\n")


def main():
    print("=== Proxy Checker Bot Started ===")
    print(f"Check interval: {config.CHECK_INTERVAL_MINUTES} minutes")
    print(f"Database: {config.DATABASE_FILE}")
    print("=" * 35)
    database.init_db(config.DATABASE_FILE)
    job()
    schedule.every(config.CHECK_INTERVAL_MINUTES).minutes.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()