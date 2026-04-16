import requests
from bs4 import BeautifulSoup
import config
import re
import json


def parse_ipspeed(html):
    proxies = []
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', class_='table')
    if not table:
        table = soup.find('table')
    if not table:
        print("Table not found in HTML")
        return proxies
    rows = table.find_all('tr')[1:]
    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 6:
            continue
        try:
            country = cells[1].get_text(strip=True)
            ip = cells[2].get_text(strip=True)
            port = cells[3].get_text(strip=True)
            protocol_cell = cells[4]
            protocols_raw = protocol_cell.get_text(strip=True)
            protocols = protocols_raw.split('<br>') if '<br>' in protocols_raw else [protocols_raw]
            for protocol in protocols:
                protocol = protocol.strip()
                if protocol and protocol not in ['ms']:
                    proxies.append({
                        'ip': ip,
                        'port': int(port),
                        'protocol': protocol.upper(),
                        'country': country
                    })
        except Exception as e:
            print(f"  Error: {e}")
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
    except Exception as e:
        print(f"Error parsing proxifly: {e}")
    return proxies


def parse_proxies():
    proxies = []
    for url in config.PROXY_SOURCES:
        try:
            print(f"Fetching {url}...")
            if url.startswith('proxifly:'):
                json_url = url.replace('proxifly:', '')
                response = requests.get(json_url, timeout=30, headers={
                    'User-Agent': 'Mozilla/5.0'
                })
                proxies_ext = parse_proxifly(response.text)
                print(f"Parsed {len(proxies_ext)} from proxifly")
                proxies.extend(proxies_ext)
            elif 'ipspeed' in url:
                response = requests.get(url, timeout=30, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                response.encoding = 'utf-8'
                proxies_ext = parse_ipspeed(response.text)
                print(f"Parsed {len(proxies_ext)} from ipspeed")
                proxies.extend(proxies_ext)
        except Exception as e:
            print(f"Error parsing {url}: {e}")
    return proxies


if __name__ == "__main__":
    proxies = parse_proxies()
    print(f"Found {len(proxies)} proxies")
    for p in proxies[:5]:
        print(p)