# 🚀 Пошаговое развертывание AI-Ассистент на сервере

## 📋 План развертывания

1. **Подготовка сервера** (VPS/хостинг)
2. **Настройка домена** (DNS записи)
3. **Установка проекта** (клонирование + настройка)
4. **Настройка веб-сервера** (Nginx)
5. **Запуск автоматизации** (генерация статей)
6. **Мониторинг и управление**

---

## 🖥️ ШАГ 1: ПОДГОТОВКА СЕРВЕРА

### 1.1 Требования к серверу
- **ОС**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **RAM**: минимум 2GB (рекомендуется 4GB+)
- **CPU**: 2 ядра+
- **Диск**: 20GB+ свободного места
- **Доступ**: SSH доступ с правами root/sudo

### 1.2 Подключение к серверу
```bash
# Подключение по SSH
ssh root@YOUR_SERVER_IP

# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка базовых пакетов
sudo apt install -y curl wget git nano htop
```

---

## 🌐 ШАГ 2: НАСТРОЙКА ДОМЕНА

### 2.1 DNS записи (в панели регистратора домена)
```
Тип: A
Имя: @ (или оставить пустым)
Значение: YOUR_SERVER_IP
TTL: 300

Тип: A  
Имя: www
Значение: YOUR_SERVER_IP
TTL: 300
```

### 2.2 Проверка DNS
```bash
# На сервере проверить резолвинг
nslookup ai-agent-lia.ru
dig ai-agent-lia.ru

# Должен показать ваш IP адрес
```

---

## 📥 ШАГ 3: УСТАНОВКА ПРОЕКТА

### 3.1 Клонирование репозитория
```bash
# Переходим в домашнюю директорию
cd ~

# Клонируем проект
git clone https://github.com/sergrv80-afk/ai-agent-lia.git

# Переходим в папку проекта
cd ai-agent-lia

# Проверяем файлы
ls -la
```

### 3.2 Настройка Python окружения
```bash
# Устанавливаем Python 3.8+
sudo apt install -y python3 python3-pip python3-venv

# Создаем виртуальное окружение
python3 -m venv venv

# Активируем окружение
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt

# Проверяем установку
python3 --version
pip list
```

### 3.3 Настройка API ключа
```bash
# Копируем пример .env файла
cp env.example .env

# Редактируем .env файл
nano .env

# Добавляем ваш OpenAI API ключ:
OPENAI_API_KEY=sk-your-api-key-here
PROJECT_NAME=AI-Ассистент
PROJECT_DOMAIN=ai-agent-lia.ru
MAIN_SITE_URL=https://ai.call-intellect.ru
GENERATION_INTERVAL_MINUTES=60
MAX_ARTICLES_PER_DAY=10
SERVER_PORT=8081
LOG_LEVEL=INFO
```

---

## 🌐 ШАГ 4: НАСТРОЙКА ВЕБ-СЕРВЕРА (Nginx)

### 4.1 Установка Nginx
```bash
# Устанавливаем Nginx
sudo apt install -y nginx

# Запускаем Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Проверяем статус
sudo systemctl status nginx
```

### 4.2 Создание конфигурации сайта
```bash
# Создаем конфигурацию для вашего домена
sudo nano /etc/nginx/sites-available/ai-agent-lia.ru
```

### 4.3 Конфигурация Nginx (вставить в файл)
```nginx
server {
    listen 80;
    server_name ai-agent-lia.ru www.ai-agent-lia.ru;
    
    # Корневая директория сайта
    root /root/ai-agent-lia;
    index index.html;
    
    # Логи
    access_log /var/log/nginx/ai-agent-lia.ru.access.log;
    error_log /var/log/nginx/ai-agent-lia.ru.error.log;
    
    # Обработка HTML файлов
    location ~ \.html$ {
        try_files $uri $uri/ =404;
        add_header Content-Type "text/html; charset=utf-8";
    }
    
    # Статические файлы
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|mp4|webm)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Безопасность
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # Gzip сжатие
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
}
```

### 4.4 Активация конфигурации
```bash
# Создаем символическую ссылку
sudo ln -s /etc/nginx/sites-available/ai-agent-lia.ru /etc/nginx/sites-enabled/

# Убираем дефолтный сайт
sudo rm /etc/nginx/sites-enabled/default

# Проверяем конфигурацию
sudo nginx -t

# Перезапускаем Nginx
sudo systemctl reload nginx

# Проверяем статус
sudo systemctl status nginx
```

---

## 🔒 ШАГ 5: НАСТРОЙКА SSL (HTTPS)

### 5.1 Установка Certbot
```bash
# Устанавливаем Certbot
sudo apt install -y certbot python3-certbot-nginx

# Получаем SSL сертификат
sudo certbot --nginx -d ai-agent-lia.ru -d www.ai-agent-lia.ru

# Автоматическое обновление сертификата
sudo crontab -e

# Добавляем строку:
0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 🤖 ШАГ 6: ЗАПУСК АВТОМАТИЗАЦИИ

### 6.1 Создание системного сервиса
```bash
# Создаем файл сервиса
sudo nano /etc/systemd/system/ai-assistant.service
```

### 6.2 Конфигурация сервиса (вставить в файл)
```ini
[Unit]
Description=AI Assistant Article Generator
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/ai-agent-lia
Environment=PATH=/root/ai-agent-lia/venv/bin
ExecStart=/root/ai-agent-lia/venv/bin/python3 auto_article_generator.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 6.3 Активация сервиса
```bash
# Перезагружаем systemd
sudo systemctl daemon-reload

# Включаем автозапуск
sudo systemctl enable ai-assistant

# Запускаем сервис
sudo systemctl start ai-assistant

# Проверяем статус
sudo systemctl status ai-assistant

# Смотрим логи
sudo journalctl -u ai-assistant -f
```

### 6.4 Настройка Cron для регулярной генерации
```bash
# Открываем crontab
crontab -e

# Добавляем строку (каждый час):
0 * * * * cd /root/ai-agent-lia && /root/ai-agent-lia/venv/bin/python3 auto_article_generator.py >> /root/ai-agent-lia/ai_generation_log.txt 2>&1
```

---

## 📊 ШАГ 7: МОНИТОРИНГ И УПРАВЛЕНИЕ

### 7.1 Команды управления
```bash
# Статус сервиса
sudo systemctl status ai-assistant

# Запуск/остановка
sudo systemctl start ai-assistant
sudo systemctl stop ai-assistant
sudo systemctl restart ai-assistant

# Просмотр логов
sudo journalctl -u ai-assistant -f
tail -f /root/ai-agent-lia/ai_generation_log.txt

# Проверка генерации статей
ls -la /root/ai-agent-lia/*.html | wc -l
```

### 7.2 Проверка работы сайта
```bash
# Проверка доступности
curl -I http://ai-agent-lia.ru
curl -I https://ai-agent-lia.ru

# Проверка Nginx
sudo nginx -t
sudo systemctl status nginx

# Проверка портов
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```

---

## 🚨 УСТРАНЕНИЕ ПРОБЛЕМ

### Проблема: Сайт не открывается
```bash
# Проверяем статус Nginx
sudo systemctl status nginx

# Проверяем логи
sudo tail -f /var/log/nginx/error.log

# Проверяем права доступа
ls -la /root/ai-agent-lia/
```

### Проблема: Статьи не генерируются
```bash
# Проверяем API ключ
cat /root/ai-agent-lia/.env

# Проверяем логи генерации
tail -f /root/ai-agent-lia/ai_generation_log.txt

# Проверяем статус сервиса
sudo systemctl status ai-assistant
```

### Проблема: Ошибки Python
```bash
# Активируем виртуальное окружение
cd /root/ai-agent-lia
source venv/bin/activate

# Проверяем зависимости
pip list

# Тестируем генерацию
python3 auto_article_generator.py
```

---

## ✅ ПРОВЕРКА РАБОТЫ

### 7.1 Проверочный список
- [ ] Домен резолвится на IP сервера
- [ ] Сайт открывается по HTTP
- [ ] Сайт открывается по HTTPS
- [ ] Nginx работает без ошибок
- [ ] Сервис ai-assistant запущен
- [ ] Статьи генерируются автоматически
- [ ] Cron задачи работают
- [ ] Логи обновляются

### 7.2 Тестовая генерация
```bash
# Переходим в папку проекта
cd /root/ai-agent-lia

# Активируем окружение
source venv/bin/activate

# Запускаем тестовую генерацию
python3 auto_article_generator.py

# Проверяем результат
ls -la *.html
```

---

## 🎯 РЕЗУЛЬТАТ

После выполнения всех шагов у вас будет:
- **Рабочий сайт** на домене ai-agent-lia.ru
- **Автоматическая генерация** статей каждый час
- **1,700 готовых тем** для статей
- **SEO оптимизация** и обновление sitemap
- **Мониторинг** и управление через systemd

**🚀 Сайт готов к работе и автоматической генерации контента!**
