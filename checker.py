import asyncio
import aiohttp
import time
import config


async def check_proxy(session, proxy, test_urls):
    ip = proxy['ip']
    port = proxy['port']
    protocol = proxy['protocol'].lower()
    proxy_url = f"{protocol}://{ip}:{port}"
    start_time = time.time()
    for url in test_urls:
        try:
            async with session.get(url, proxy=proxy_url, timeout=config.PROXY_TEST_TIMEOUT) as response:
                if response.status == 200:
                    ping_ms = int((time.time() - start_time) * 1000)
                    return {'ip': ip, 'port': port, 'protocol': proxy['protocol'], 'country': proxy.get('country', ''), 'ping_ms': ping_ms}
        except Exception:
            continue
    return None


async def check_all_proxies(proxies):
    test_urls = config.PROXY_TEST_URLS
    connector = aiohttp.TCPConnector(limit=100)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [check_proxy(session, p, test_urls) for p in proxies]
        results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]


def check_proxies_sync(proxies):
    return asyncio.run(check_all_proxies(proxies))


if __name__ == "__main__":
    test_proxies = [{'ip': '8.8.8.8', 'port': 53, 'protocol': 'HTTP', 'country': 'US'}]
    results = check_proxies_sync(test_proxies)
    print(f"Working: {len(results)}")