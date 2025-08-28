#!/bin/bash

# Скрипт настройки GitHub репозитория для AI-Ассистент
# Запускайте после клонирования репозитория

echo "🚀 Настройка GitHub репозитория AI-Ассистент"
echo "=============================================="

# Проверяем, что мы в правильной папке
if [ ! -f "auto_article_generator.py" ]; then
    echo "❌ Ошибка: Запустите скрипт из папки проекта!"
    exit 1
fi

# Инициализируем Git репозиторий
echo "📁 Инициализация Git репозитория..."
git init

# Добавляем удаленный репозиторий
echo "🔗 Добавление удаленного репозитория..."
git remote add origin https://github.com/sergrv80-afk/ai-agent-lia.git

# Создаем .env файл из примера
if [ ! -f ".env" ]; then
    echo "🔑 Создание .env файла..."
    cp env.example .env
    echo "⚠️  ВАЖНО: Отредактируйте .env файл и добавьте ваш OpenAI API ключ!"
    echo "   nano .env"
fi

# Добавляем все файлы в Git
echo "📝 Добавление файлов в Git..."
git add .

# Первый коммит
echo "💾 Создание первого коммита..."
git commit -m "Initial commit: AI-Ассистент проект с 1,700 темами

- Автоматическая генерация статей с GPT-5
- SEO/GEO/LLM оптимизация
- База из 1,700 тем (100 базовых + 1,600 с городами)
- Готов для развертывания на сервере"

# Переименовываем ветку в main
echo "🌿 Переименование ветки в main..."
git branch -M main

# Отправляем в GitHub
echo "🚀 Отправка в GitHub..."
git push -u origin main

echo ""
echo "🎉 GitHub репозиторий настроен!"
echo "📋 Следующие шаги:"
echo "   1. Отредактируйте .env файл: nano .env"
echo "   2. Добавьте ваш OpenAI API ключ"
echo "   3. Проверьте репозиторий: https://github.com/sergrv80-afk/ai-agent-lia"
echo ""
echo "🔧 Для обновления кода:"
echo "   git add . && git commit -m 'Обновление' && git push"
