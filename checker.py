import asyncio
import socket
import time
import config


async def check_proxy_port(proxy, progress_callback=None, index=0, total=0):
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
        if progress_callback:
            progress_callback(index, total, ip, port, True, ping_ms)
        return {
            'ip': ip,
            'port': port,
            'protocol': proxy['protocol'],
            'country': proxy.get('country', ''),
            'ping_ms': ping_ms
        }
    except Exception as e:
        if progress_callback:
            progress_callback(index, total, ip, port, False, 0)
        return None


async def check_all_proxies(proxies, progress_callback=None):
    total = len(proxies)
    tasks = [check_proxy_port(p, progress_callback, i, total) for i, p in enumerate(proxies)]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]


def check_proxies_sync(proxies, progress_callback=None):
    return asyncio.run(check_all_proxies(proxies, progress_callback))


if __name__ == "__main__":
    test_proxies = [{'ip': '8.8.8.8', 'port': 53, 'protocol': 'HTTP', 'country': 'US'}]
    
    def progress(idx, total, ip, port, success, ping):
        status = f"✅ {ping}ms" if success else "❌"
        print(f"[{idx+1}/{total}] {ip}:{port} - {status}")
    
    results = check_proxies_sync(test_proxies, progress)
    print(f"Working: {len(results)}")