import requests
from bs4 import BeautifulSoup
import config
import re


def parse_ipspeed(html):
    proxies = []
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', class_='table')
    if not table:
        table = soup.find('table')
    if not table:
        print("Table not found in HTML")
        return proxies
    print(f"Found table: {table.get('class')}")
    rows = table.find_all('tr')[1:]
    print(f"Found {len(rows)} rows")
    for i, row in enumerate(rows):
        cells = row.find_all('td')
        print(f"Row {i}: {len(cells)} cells")
    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 6:
            continue
        try:
            print(f"Processing row with {len(cells)} cells")
            country = cells[1].get_text(strip=True)
            ip = cells[2].get_text(strip=True)
            port = cells[3].get_text(strip=True)
            print(f"  Country: '{country}', IP: '{ip}', Port: '{port}'")
            protocol_cell = cells[4]
            protocols = [p.get_text(strip=True) for p in protocol_cell.find_all('br')]
            if not protocols:
                protocols = [protocol_cell.get_text(strip=True)]
            print(f"  Protocols: {protocols}")
            for protocol in protocols:
                if protocol:
                    proxies.append({
                        'ip': ip,
                        'port': int(port),
                        'protocol': protocol.upper(),
                        'country': country
                    })
        except Exception as e:
            print(f"  Error: {e}")
    return proxies


def parse_geonix(html):
    proxies = []
    soup = BeautifulSoup(html, 'html.parser')
    proxy_items = soup.find_all('li', class_=re.compile(r'proxy-list__item'))
    if not proxy_items:
        for item in soup.find_all('div', class_=re.compile(r'proxy')):
            ip_elem = item.find('span', class_=re.compile(r'ip'))
            port_elem = item.find('span', class_=re.compile(r'port'))
            if ip_elem and port_elem:
                ip = ip_elem.get_text(strip=True)
                port = port_elem.get_text(strip=True)
                protocol = 'HTTPS'
                country = item.get('data-country', '')
                proxies.append({
                    'ip': ip,
                    'port': int(port),
                    'protocol': protocol,
                    'country': country
                })
    for item in proxy_items:
        try:
            ip_elem = item.find('span', class_='ip')
            port_elem = item.find('span', class_='port')
            if not ip_elem or not port_elem:
                text = item.get_text()
                match = re.search(r'(\d+\.\d+\.\d+\.\d+):(\d+)', text)
                if match:
                    ip, port = match.groups()
                else:
                    continue
            else:
                ip = ip_elem.get_text(strip=True)
                port = port_elem.get_text(strip=True)
            protocol = 'HTTPS'
            country = ''
            type_elem = item.find('span', class_=re.compile(r'type|type_'))
            if type_elem:
                protocol = type_elem.get_text(strip=True).upper()
            proxies.append({
                'ip': ip,
                'port': int(port),
                'protocol': protocol,
                'country': country
            })
        except (ValueError, AttributeError):
            continue
    return proxies


def parse_proxies():
    proxies = []
    for url in config.PROXY_SOURCES:
        try:
            print(f"Fetching {url}...")
            response = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            print(f"Response status: {response.status_code}, length: {len(response.text)}")
            response.encoding = 'utf-8'
            if 'ipspeed' in url:
                proxies_ext = parse_ipspeed(response.text)
                print(f"Parsed {len(proxies_ext)} from ipspeed")
                proxies.extend(proxies_ext)
            elif 'geonix' in url:
                proxies_ext = parse_geonix(response.text)
                print(f"Parsed {len(proxies_ext)} from geonix")
                proxies.extend(proxies_ext)
        except Exception as e:
            print(f"Error parsing {url}: {e}")
    return proxies


if __name__ == "__main__":
    proxies = parse_proxies()
    print(f"Found {len(proxies)} proxies")
    for p in proxies[:5]:
        print(p)