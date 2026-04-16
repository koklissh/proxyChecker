import sqlite3
import time
from datetime import datetime


def init_db(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proxies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            port INTEGER NOT NULL,
            protocol TEXT,
            country TEXT,
            ping_ms INTEGER,
            last_checked TIMESTAMP,
            is_working INTEGER DEFAULT 0,
            UNIQUE(ip, port, protocol)
        )
    ''')
    conn.commit()
    return conn


def get_all_proxies(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('SELECT ip, port, protocol, country, ping_ms, is_working FROM proxies')
    rows = cursor.fetchall()
    conn.close()
    return [{'ip': r[0], 'port': r[1], 'protocol': r[2], 'country': r[3], 'ping_ms': r[4], 'is_working': r[5]} for r in rows]


def get_working_proxies(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('SELECT ip, port, protocol, country, ping_ms FROM proxies WHERE is_working = 1 ORDER BY ping_ms')
    rows = cursor.fetchall()
    conn.close()
    return [{'ip': r[0], 'port': r[1], 'protocol': r[2], 'country': r[3], 'ping_ms': r[4]} for r in rows]


def update_proxies(db_file, new_proxies, working_proxies):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    working_set = {(p['ip'], p['port'], p['protocol']) for p in working_proxies}
    all_current = {(p['ip'], p['port'], p['protocol']) for p in get_all_proxies(db_file)}
    new_set = {(p['ip'], p['port'], p['protocol']) for p in new_proxies}
    added = new_set - all_current
    removed = all_current - working_set
    cursor.execute('UPDATE proxies SET is_working = 0')
    for p in working_proxies:
        cursor.execute('''
            INSERT OR REPLACE INTO proxies (ip, port, protocol, country, ping_ms, last_checked, is_working)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        ''', (p['ip'], p['port'], p['protocol'], p.get('country', ''), p.get('ping_ms', 0), datetime.now()))
    conn.commit()
    conn.close()
    return len(added), len(removed)


if __name__ == "__main__":
    conn = init_db("proxies.db")
    print("Database initialized")
    conn.close()