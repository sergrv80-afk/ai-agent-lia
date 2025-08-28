# AI-Ассистент - Автоматическая генерация статей

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?style=for-the-badge&logo=github)](https://github.com/sergrv80-afk/ai-agent-lia)
[![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5-orange?style=for-the-badge&logo=openai)](https://openai.com)

## 🎯 Описание проекта

Автоматическая система генерации SEO-оптимизированных статей для AI-ассистентов, чат-ботов и автоматизации продаж.

**🌐 GitHub**: https://github.com/sergrv80-afk/ai-agent-lia

## 🚀 Возможности

- **Автоматическая генерация статей** с помощью GPT-5
- **SEO/GEO/LLM оптимизация** согласно гайду 2025
- **Гибридная оптимизация** с использованием GPT-5 планирования
- **Автоматическое обновление** sitemap, robots.txt, ai.txt
- **Видео-виджет** для увеличения конверсии

## 📁 Структура проекта

```
lia/
├── index.html                 # Главная страница
├── AI_ARTICLE_TEMPLATE.html   # Шаблон для статей
├── auto_article_generator.py  # Основной генератор
├── article_agent.py          # Агент создания статей
├── geo_hybrid_agent.py      # GEO-оптимизация с GPT-5
├── auto_article_updater.py  # Обновление файлов
├── ai_business_3themes.csv  # 1,700 тем (100 базовых + 1,600 с городами)
├── requirements.txt          # Python зависимости
├── .env                     # API ключи (не в Git)
├── js/                      # JavaScript файлы
├── assets/                  # Изображения и стили
├── .well-known/            # AI.txt файл
├── auto_deploy.sh          # Автоматическое развертывание на сервере
├── SERVER_DEPLOYMENT_GUIDE.md # Подробная инструкция по развертыванию
├── QUICK_DEPLOY.md         # Быстрое развертывание
└── QUICK_START.md          # Быстрый старт для разработчиков
```

## 🛠 Установка и запуск

### 🖥️ На сервере (продакшн)
```bash
# 1. Клонируем проект
git clone https://github.com/sergrv80-afk/ai-agent-lia.git
cd ai-agent-lia

# 2. Автоматическое развертывание
chmod +x auto_deploy.sh
./auto_deploy.sh

# 3. Настраиваем API ключ
nano .env

# 4. Получаем SSL сертификат
certbot --nginx -d ai-agent-lia.ru
```

**📖 Подробная инструкция**: [SERVER_DEPLOYMENT_GUIDE.md](SERVER_DEPLOYMENT_GUIDE.md)  
**⚡ Быстрое развертывание**: [QUICK_DEPLOY.md](QUICK_DEPLOY.md)

### Локально (для разработки)

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/sergrv80-afk/ai-agent-lia.git
cd ai-agent-lia
```

2. **Создайте .env файл:**
```bash
cp .env.example .env
# Отредактируйте .env и добавьте ваш OpenAI API ключ
```

3. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

4. **Запустите локальный сервер:**
```bash
python3 -m http.server 8081
```

5. **Откройте в браузере:**
```
http://localhost:8081/
```

### На сервере (продакшн)

1. **Подключитесь к серверу:**
```bash
ssh root@your-server-ip
```

2. **Клонируйте репозиторий:**
```bash
git clone https://github.com/your-username/ai-assistant-lia.git
cd ai-assistant-lia
```

3. **Настройте .env:**
```bash
nano .env
# Добавьте ваш OpenAI API ключ
```

4. **Установите зависимости:**
```bash
pip3 install -r requirements.txt
```

5. **Настройте Nginx:**
```bash
# Создайте конфиг для домена
sudo nano /etc/nginx/sites-available/ai-agent-lia.ru
```

6. **Запустите автоматизацию:**
```bash
# Ручной запуск
python3 auto_article_generator.py

# Автоматический запуск через cron
crontab -e
# Добавьте: */5 * * * * cd /path/to/ai-assistant-lia && python3 auto_article_generator.py
```

## 🔑 Настройка API ключей

Создайте файл `.env` в корне проекта:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## 📊 Автоматизация

### Cron задачи

Для автоматического запуска генерации статей каждые 5 минут:

```bash
crontab -e
```

Добавьте строку:
```cron
*/5 * * * * cd /path/to/ai-assistant-lia && python3 auto_article_generator.py >> /var/log/ai-generator.log 2>&1
```

### Мониторинг

Проверьте логи:
```bash
tail -f /var/log/ai-generator.log
```

## 🌐 Настройка домена

1. **В DNS провайдере создайте A-запись:**
   - **Тип**: A
   - **Имя**: @ (или ai-agent-lia)
   - **Значение**: IP-адрес вашего сервера

2. **Подождите 15-60 минут** для распространения DNS

3. **Проверьте настройки:**
```bash
nslookup ai-agent-lia.ru
```

## 🔧 Nginx конфигурация

Создайте файл `/etc/nginx/sites-available/ai-agent-lia.ru`:

```nginx
server {
    listen 80;
    server_name ai-agent-lia.ru www.ai-agent-lia.ru;
    
    root /var/www/ai-assistant-lia;
    index index.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location ~* \.(mp4|webm)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Активируйте сайт:
```bash
sudo ln -s /etc/nginx/sites-available/ai-agent-lia.ru /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 📈 Мониторинг и аналитика

### Логи генерации
- `ai_generation_log.txt` - основной лог
- `hybrid_optimization_report_*.md` - отчеты оптимизации

### SEO отчеты
- `SEO_ОТЧЕТ_*.md` - комплексные SEO отчеты

## 🚨 Устранение неполадок

### Проблема: Статьи не генерируются
**Решение:** Проверьте API ключ в .env файле

### Проблема: Ошибки Nginx
**Решение:** Проверьте конфигурацию и права доступа

### Проблема: Cron не работает
**Решение:** Проверьте пути и права на выполнение

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `tail -f /var/log/ai-generator.log`
2. Проверьте статус сервисов: `sudo systemctl status nginx`
3. Проверьте права доступа к файлам

## 📄 Лицензия

Проект создан для автоматизации генерации контента.
