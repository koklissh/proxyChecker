import aiohttp
from bs4 import BeautifulSoup
import config
import json


async def fetch_url(session, url, headers=None):
    if headers is None:
        headers = {'User-Agent': 'Mozilla/5.0'}
    async with session.get(url, timeout=aiohttp.ClientTimeout(total=30), headers=headers) as response:
        return await response.text()


def parse_ipspeed(html):
    proxies = []
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', class_='table')
    if not table:
        table = soup.find('table')
    if not table:
        return proxies
    rows = table.find_all('tr')[1:]
    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 6:
            continue
        try:
            country = cells[1].get_text(strip=True)
            ip = cells[2].get_text(strip=True)
            port_raw = cells[3].get_text(strip=True)
            try:
                port = int(port_raw)
            except ValueError:
                continue
            protocol = cells[4].get_text(strip=True).replace(' ms', '').strip()
            if not protocol:
                protocol = 'HTTP'
            proxies.append({
                'ip': ip,
                'port': port,
                'protocol': protocol.upper(),
                'country': country
            })
        except Exception:
            continue
    return proxies


def parse_proxifly(data):
    proxies = []
    try:
        if isinstance(data, str):
            data = json.loads(data)
        for item in data:
            try:
                proxies.append({
                    'ip': item.get('ip', ''),
                    'port': item.get('port', 0),
                    'protocol': item.get('protocol', 'SOCKS5').upper(),
                    'country': item.get('geolocation', {}).get('country', '')
                })
            except Exception:
                continue
    except Exception:
        pass
    return proxies


def parse_text_list(text, protocol='HTTP'):
    proxies = []
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' in line:
            parts = line.split(':')
            if len(parts) >= 2:
                try:
                    ip = parts[0].strip()
                    port = int(parts[1].strip())
                    proxies.append({'ip': ip, 'port': port, 'protocol': protocol.upper(), 'country': ''})
                except ValueError:
                    continue
    return proxies


async def parse_proxies():
    all_proxies = []
    seen = set()
    
    async with aiohttp.ClientSession() as session:
        for url in config.PROXY_SOURCES:
            try:
                print(f"Fetching {url}...")
                
                if url.startswith('proxifly:'):
                    json_url = url.replace('proxifly:', '')
                    text = await fetch_url(session, json_url)
                    proxies_ext = parse_proxifly(text)
                    print(f"  Parsed {len(proxies_ext)} from proxifly")
                    
                elif url.startswith('text:'):
                    text_url = url.replace('text:', '')
                    protocol = 'HTTP'
                    if 'socks5' in text_url:
                        protocol = 'SOCKS5'
                    elif 'socks4' in text_url:
                        protocol = 'SOCKS4'
                    text = await fetch_url(session, text_url)
                    proxies_ext = parse_text_list(text, protocol)
                    print(f"  Parsed {len(proxies_ext)} from {protocol} list")
                    
                elif 'ipspeed' in url:
                    text = await fetch_url(session, url, {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
                    proxies_ext = parse_ipspeed(text)
                    print(f"  Parsed {len(proxies_ext)} from ipspeed")
                else:
                    continue
                
                for p in proxies_ext:
                    key = (p['ip'], p['port'], p['protocol'].upper())
                    if key not in seen:
                        seen.add(key)
                        all_proxies.append(p)
                        
            except Exception as e:
                print(f"Error parsing {url}: {e}")
    
    print(f"Total unique proxies: {len(all_proxies)}")
    return all_proxies


if __name__ == "__main__":
    import asyncio
    proxies = asyncio.run(parse_proxies())
    print(f"Found {len(proxies)} proxies")
    for p in proxies[:5]:
        print(p)