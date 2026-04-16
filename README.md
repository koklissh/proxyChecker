# Proxy Checker Bot

Бот для сбора, проверки бесплатных прокси и отправки в Discord.

## Установка

```bash
# Ubuntu 22.04
sudo apt update && sudo apt install python3 python3-pip python3-venv git -y

cd /opt
sudo git clone https://github.com/koklissh/proxyChecker.git proxy-checker
cd /opt/proxy-checker

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Настройка

Отредактируй `config.py`:
```python
# Discord Webhook URL (для уведомлений)
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/..."

# Discord Bot Token (для команд бота)
DISCORD_BOT_TOKEN = "MTQ4Mzg2OTg3NDIzNjQyODQwOA.GP49SC..."
```

## Запуск

```bash
# Режим 1: Проверка прокси +Webhook (каждые 5 минут)
python3 main.py

# Режим 2: Discord бот с командами (отдельный терминал)
python3 discord_bot.py
```

## Команды Discord бота

- `!proxies` — показать рабочие прокси
- `!check` — запустить проверку прокси
- `!stats` — статистика базы данных

## Автозапуск

```bash
crontab -e
*/5 * * * * cd /opt/proxy-checker && /opt/proxy-checker/venv/bin/python3 main.py >> /var/log/proxy-checker.log 2>&1
```

## Структура

```
proxy-checker/
├── main.py           # Скрипт проверки прокси + webhook
├── discord_bot.py    # Discord бот с командами
├── parser.py         # Парсинг прокси с сайтов
├── checker.py        # Проверка прокси (socket ping)
├── database.py       # SQLite база данных
├── webhook_helper.py # Отправка в Discord
├── config.py         # Настройки
└── requirements.txt  # Зависимости
```