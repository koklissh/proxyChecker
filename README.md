# Proxy Checker Bot

Бот для сбора и проверки бесплатных прокси с отправкой в Discord.

## ОДНОЙ КОМАНДОЙ (Ubuntu 22.04):

```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv git -y && cd /opt && sudo git clone https://github.com/koklissh/damp.git proxy-checker && cd /opt/proxy-checker && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && nano config.py
```

## ИЛИ пошагово:

```bash
# 1. Установка
sudo apt update && sudo apt install python3 python3-pip python3-venv git -y

# 2. Клонирование
cd /opt
sudo git clone https://github.com/koklissh/damp.git proxy-checker
cd /opt/proxy-checker

# 3. Запуск
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
nano config.py  # Вставь Discord Webhook URL
python3 main.py
```

## Cron (автозапуск каждые 5 минут):
```bash
crontab -e
*/5 * * * * cd /opt/proxy-checker && /opt/proxy-checker/venv/bin/python3 main.py >> /var/log/proxy-checker.log 2>&1
```