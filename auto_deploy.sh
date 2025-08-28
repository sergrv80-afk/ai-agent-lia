#!/bin/bash

# 🚀 Автоматическое развертывание AI-Ассистент на сервере
# Запускайте на сервере после клонирования репозитория

set -e  # Останавливаемся при ошибке

echo "🚀 Автоматическое развертывание AI-Ассистент на сервере"
echo "========================================================"

# Проверяем, что мы root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Ошибка: Запустите скрипт от имени root (sudo)"
    exit 1
fi

# Проверяем, что мы в правильной папке
if [ ! -f "auto_article_generator.py" ]; then
    echo "❌ Ошибка: Запустите скрипт из папки проекта!"
    exit 1
fi

# Переменные
DOMAIN="ai-agent-lia.ru"
PROJECT_DIR=$(pwd)
SERVICE_NAME="ai-assistant"

echo "📋 Информация о развертывании:"
echo "   Домен: $DOMAIN"
echo "   Папка проекта: $PROJECT_DIR"
echo "   Имя сервиса: $SERVICE_NAME"
echo ""

# ШАГ 1: Обновление системы
echo "🔄 ШАГ 1: Обновление системы..."
apt update && apt upgrade -y

# ШАГ 2: Установка необходимых пакетов
echo "📦 ШАГ 2: Установка пакетов..."
apt install -y python3 python3-pip python3-venv nginx git curl wget nano htop certbot python3-certbot-nginx

# ШАГ 3: Настройка Python окружения
echo "🐍 ШАГ 3: Настройка Python..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# ШАГ 4: Создание .env файла
echo "🔑 ШАГ 4: Настройка .env файла..."
if [ ! -f ".env" ]; then
    cp env.example .env
    echo "⚠️  ВАЖНО: Отредактируйте .env файл и добавьте ваш OpenAI API ключ!"
    echo "   nano .env"
    echo "   Добавьте: OPENAI_API_KEY=sk-your-key-here"
    echo ""
    read -p "Нажмите Enter после настройки .env файла..."
fi

# ШАГ 5: Настройка Nginx
echo "🌐 ШАГ 5: Настройка Nginx..."

# Создаем конфигурацию сайта
cat > /etc/nginx/sites-available/$DOMAIN << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    root $PROJECT_DIR;
    index index.html;
    
    access_log /var/log/nginx/$DOMAIN.access.log;
    error_log /var/log/nginx/$DOMAIN.error.log;
    
    location ~ \.html$ {
        try_files \$uri \$uri/ =404;
        add_header Content-Type "text/html; charset=utf-8";
    }
    
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|mp4|webm)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
}
EOF

# Активируем конфигурацию
ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Проверяем и перезапускаем Nginx
nginx -t
systemctl reload nginx
systemctl enable nginx

# ШАГ 6: Создание системного сервиса
echo "🤖 ШАГ 6: Создание системного сервиса..."

cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=AI Assistant Article Generator
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/python3 auto_article_generator.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Активируем сервис
systemctl daemon-reload
systemctl enable $SERVICE_NAME

# ШАГ 7: Настройка Cron
echo "⏰ ШАГ 7: Настройка Cron..."

# Добавляем задачу в crontab (каждый час)
(crontab -l 2>/dev/null; echo "0 * * * * cd $PROJECT_DIR && $PROJECT_DIR/venv/bin/python3 auto_article_generator.py >> $PROJECT_DIR/ai_generation_log.txt 2>&1") | crontab -

# ШАГ 8: Создание папки для логов
echo "📝 ШАГ 8: Создание папки для логов..."
mkdir -p logs
chmod 755 logs

# ШАГ 9: Настройка прав доступа
echo "🔐 ШАГ 9: Настройка прав доступа..."
chown -R root:root $PROJECT_DIR
chmod -R 755 $PROJECT_DIR
chmod 644 $PROJECT_DIR/*.py
chmod 644 $PROJECT_DIR/*.html
chmod 644 $PROJECT_DIR/*.css
chmod 644 $PROJECT_DIR/*.js

# ШАГ 10: Тестовая генерация
echo "🧪 ШАГ 10: Тестовая генерация..."
cd $PROJECT_DIR
source venv/bin/activate
python3 auto_article_generator.py

# ШАГ 11: Запуск сервиса
echo "🚀 ШАГ 11: Запуск сервиса..."
systemctl start $SERVICE_NAME

# ШАГ 12: Проверка статуса
echo "✅ ШАГ 12: Проверка статуса..."
echo ""
echo "📊 Статус сервисов:"
systemctl status nginx --no-pager -l
echo ""
systemctl status $SERVICE_NAME --no-pager -l

echo ""
echo "🎉 РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!"
echo "=================================="
echo ""
echo "🌐 Ваш сайт доступен по адресу: http://$DOMAIN"
echo "🤖 Сервис генерации статей: $SERVICE_NAME"
echo "📝 Логи генерации: $PROJECT_DIR/ai_generation_log.txt"
echo "⏰ Автогенерация: каждый час"
echo ""
echo "🔧 Команды управления:"
echo "   Статус: systemctl status $SERVICE_NAME"
echo "   Логи: journalctl -u $SERVICE_NAME -f"
echo "   Перезапуск: systemctl restart $SERVICE_NAME"
echo ""
echo "📋 Следующие шаги:"
echo "   1. Настройте DNS записи для домена $DOMAIN"
echo "   2. Получите SSL сертификат: certbot --nginx -d $DOMAIN"
echo "   3. Проверьте работу сайта в браузере"
echo "   4. Мониторьте генерацию статей"
echo ""
echo "🚀 Сайт готов к работе!"
