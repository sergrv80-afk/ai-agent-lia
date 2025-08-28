# 🚀 Быстрый старт AI-Ассистент

## ⚡ Быстрая установка (5 минут)

### 1. Клонирование репозитория
```bash
git clone https://github.com/sergrv80-afk/ai-agent-lia.git
cd ai-agent-lia
```

### 2. Автоматическая настройка GitHub
```bash
./setup_github.sh
```

### 3. Настройка API ключа
```bash
nano .env
# Добавьте ваш OpenAI API ключ
```

### 4. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 5. Запуск генерации статей
```bash
python3 auto_article_generator.py
```

## 🎯 Что получите

- **1,700 готовых тем** для статей
- **Автоматическая генерация** с GPT-5
- **SEO/GEO/LLM оптимизация**
- **Готовность к развертыванию** на сервере

## 📊 База тем

- **100 базовых тем** (без городов)
- **1,600 тем с городами** (16 основных городов России)
- **Автоматическое обновление** sitemap, robots.txt, ai.txt

## 🔧 Управление

```bash
# Статус
git status

# Обновление
git add . && git commit -m "Обновление" && git push

# Просмотр логов
tail -f ai_generation_log.txt
```

## 🌐 Демо

- **Локально**: http://localhost:8081
- **GitHub**: https://github.com/sergrv80-afk/ai-agent-lia

## 📞 Поддержка

При проблемах проверьте:
1. API ключ в .env файле
2. Логи: `tail -f ai_generation_log.txt`
3. Статус Git: `git status`
