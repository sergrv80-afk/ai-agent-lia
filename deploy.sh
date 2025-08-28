#!/bin/bash

# Скрипт автоматического развертывания AI-Ассистент
# Запускайте на сервере после клонирования репозитория

echo "🚀 Начинаем развертывание AI-Ассистент..."

# Проверяем, что мы в правильной папке
if [ ! -f "auto_article_generator.py" ]; then
    echo "❌ Ошибка: Запустите скрипт из папки проекта!"
    exit 1
fi

# Обновляем систему
echo "📦 Обновляем систему..."
sudo apt update && sudo apt upgrade -y

# Устанавливаем необходимые пакеты
echo "🔧 Устанавливаем необходимые пакеты..."
sudo apt install -y python3 python3-pip python3-venv nginx git curl

# Создаем виртуальное окружение Python
echo "🐍 Создаем виртуальное окружение Python..."
python3 -m venv venv
source venv/bin/activate

# Устанавливаем Python зависимости
echo "📚 Устанавливаем Python зависимости..."
pip install -r requirements.txt

# Создаем .env файл если его нет
if [ ! -f ".env" ]; then
    echo "🔑 Создаем .env файл..."
    cp env.example .env
    echo "⚠️  ВАЖНО: Отредактируйте .env файл и добавьте ваш OpenAI API ключ!"
    echo "   nano .env"
fi

# Создаем папку для логов
echo "📝 Создаем папку для логов..."
sudo mkdir -p /var/log
sudo touch /var/log/ai-generator.log
sudo chown $USER:$USER /var/log/ai-generator.log

# Настраиваем Nginx
echo "🌐 Настраиваем Nginx..."

# Создаем конфиг для домена
sudo tee /etc/nginx/sites-available/ai-agent-lia.ru > /dev/null <<EOF
server {
    listen 80;
    server_name ai-agent-lia.ru www.ai-agent-lia.ru;
    
    root $(pwd);
    index index.html;
    
    location / {
        try_files \$uri \$uri/ =404;
    }
    
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location ~* \.(mp4|webm)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Логи
    access_log /var/log/nginx/ai-agent-lia.ru.access.log;
    error_log /var/log/nginx/ai-agent-lia.ru.error.log;
}
EOF

# Активируем сайт
sudo ln -sf /etc/nginx/sites-available/ai-agent-lia.ru /etc/nginx/sites-enabled/

# Проверяем конфигурацию Nginx
if sudo nginx -t; then
    echo "✅ Конфигурация Nginx корректна"
    sudo systemctl reload nginx
    sudo systemctl enable nginx
else
    echo "❌ Ошибка в конфигурации Nginx"
    exit 1
fi

# Настраиваем автоматический запуск через cron
echo "⏰ Настраиваем автоматический запуск через cron..."
CRON_JOB="*/5 * * * * cd $(pwd) && source venv/bin/activate && python3 auto_article_generator.py >> /var/log/ai-generator.log 2>&1"

# Добавляем задачу в cron
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

# Проверяем, что cron задача добавлена
if crontab -l | grep -q "auto_article_generator.py"; then
    echo "✅ Cron задача добавлена успешно"
else
    echo "❌ Ошибка добавления cron задачи"
fi

# Создаем скрипт для управления сервисом
echo "🔧 Создаем скрипт управления сервисом..."
sudo tee /usr/local/bin/ai-assistant > /dev/null <<EOF
#!/bin/bash

case "\$1" in
    start)
        echo "🚀 Запускаем AI-Ассистент..."
        cd $(pwd)
        source venv/bin/activate
        python3 auto_article_generator.py
        ;;
    status)
        echo "📊 Статус AI-Ассистент:"
        echo "   Cron задачи:"
        crontab -l | grep "auto_article_generator.py"
        echo "   Последние логи:"
        tail -5 /var/log/ai-generator.log
        ;;
    logs)
        echo "📝 Логи AI-Ассистент:"
        tail -f /var/log/ai-generator.log
        ;;
    stop)
        echo "⏹ Останавливаем AI-Ассистент..."
        crontab -l | grep -v "auto_article_generator.py" | crontab -
        echo "✅ Cron задачи остановлены"
        ;;
    *)
        echo "Использование: ai-assistant {start|stop|status|logs}"
        exit 1
        ;;
esac
EOF

sudo chmod +x /usr/local/bin/ai-assistant

# Тестируем генерацию статьи
echo "🧪 Тестируем генерацию статьи..."
source venv/bin/activate
if python3 auto_article_generator.py; then
    echo "✅ Тестовая генерация прошла успешно!"
else
    echo "❌ Ошибка при тестовой генерации"
    echo "   Проверьте .env файл и API ключ"
fi

echo ""
echo "🎉 РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Отредактируйте .env файл: nano .env"
echo "2. Добавьте ваш OpenAI API ключ"
echo "3. Настройте DNS для домена ai-agent-lia.ru"
echo "4. Проверьте работу: ai-assistant status"
echo "5. Запустите автоматизацию: ai-assistant start"
echo ""
echo "🌐 Сайт будет доступен по адресу: http://ai-agent-lia.ru"
echo "📊 Логи: tail -f /var/log/ai-generator.log"
echo "🔧 Управление: ai-assistant {start|stop|status|logs}"
