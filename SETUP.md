# Proxy Checker Bot - Инструкция по запуску

## Команды для Ubuntu Server 22.04

```bash
# 1. Обновление системы
sudo apt update && sudo apt upgrade -y

# 2. Установка Python и Git
sudo apt install python3 python3-pip python3-venv git -y

# 3. Создание директории и клонирование
cd /opt
sudo mkdir proxy-checker
cd proxy-checker

# 4. Копирование файлов (через SFTP или git)
# Скопируй все файлы из папки DiscordBot1 в эту директорию

# ИЛИ если есть доступ к GitHub:
sudo git clone https://github.com/koklissh/damp.git .
# (сначала создай пустой репозиторий на GitHub)

# 5. Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# 6. Установка зависимостей
pip install -r requirements.txt

# 7. Настройка webhook
nano config.py
# Вставь свой Discord Webhook URL

# 8. Запуск
python3 main.py
```

## Настройка Discord Webhook

1. Открой Discord → Настройки сервера → Интеграции → Создать вебхук
2. Скопируй URL
3. Вставь в config.py: `DISCORD_WEBHOOK_URL = "твой_url"`

## Автозапуск (каждые 5 минут)

```bash
crontab -e
# Добавить строку:
*/5 * * * * cd /opt/proxy-checker && /opt/proxy-checker/venv/bin/python3 main.py >> /var/log/proxy-checker.log 2>&1
```

## Проверка работы

```bash
# Запуск вручную для теста
source venv/bin/activate
python3 main.py

# Просмотр логов
tail -f /var/log/proxy-checker.log
```

## Структура проекта

```
/opt/proxy-checker/
├── config.py           # Конфигурация (Webhook URL)
├── parser.py          # Парсинг прокси с ipspeed.info
├── checker.py         # Асинхронная проверка прокси
├── database.py        # SQLite база данных
├── discord_webhook.py # Отправка в Discord
├── main.py            # Главный файл + планировщик
├── requirements.txt   # Зависимости
└── README.md          # Этот файл
```

## Что делает бот

1. Каждые 5 минут парсит прокси с ipspeed.info
2. Проверяет каждый прокси на работоспособность
3. Сохраняет рабочие прокси в базу SQLite
4. Отправляет список рабочих прокси в Discord через Webhook