import asyncio
import socket
import time
import config


async def check_proxy_port(proxy):
    ip = proxy['ip']
    port = proxy['port']
    start_time = time.time()
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port),
            timeout=config.PROXY_TEST_TIMEOUT
        )
        writer.close()
        await writer.wait_closed()
        ping_ms = int((time.time() - start_time) * 1000)
        return {
            'ip': ip,
            'port': port,
            'protocol': proxy['protocol'],
            'country': proxy.get('country', ''),
            'ping_ms': ping_ms
        }
    except Exception:
        return None


async def check_all_proxies(proxies):
    tasks = [check_proxy_port(p) for p in proxies]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]


def check_proxies_sync(proxies):
    return asyncio.run(check_all_proxies(proxies))


if __name__ == "__main__":
    test_proxies = [{'ip': '8.8.8.8', 'port': 53, 'protocol': 'HTTP', 'country': 'US'}]
    results = check_proxies_sync(test_proxies)
    print(f"Working: {len(results)}")