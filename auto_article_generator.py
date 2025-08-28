#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоматический генератор статей AI-Ассистент
Генерирует статьи каждые 5 минут, читая темы из CSV файла
Тематика: AI-ассистенты, чат-боты, автоматизация продаж
База тем: 1,700 тем (100 базовых + 1,600 с городами)
"""

import csv
import time
import json
import os
from datetime import datetime
from pathlib import Path
from article_agent import ArticleAgent

class AutoArticleGenerator:
    def __init__(self):
        self.csv_file = "ai_business_3themes.csv"  # Теперь содержит 1,700 тем (100 базовых + 1,600 с городами)
        self.progress_file = "ai_topic_progress.json"
        self.log_file = "ai_generation_log.txt"
        self.article_agent = ArticleAgent()
        self.current_topic_index = 0
        self.topics = []
        
    def load_topics_from_csv(self):
        """Загружает темы из CSV файла"""
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                # Пропускаем заголовок
                next(reader)
                self.topics = [row[0] for row in reader if row[0].strip()]
            
            print(f"✅ Загружено {len(self.topics)} тем из CSV файла")
            for i, topic in enumerate(self.topics):
                print(f"   {i+1}. {topic}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка загрузки CSV: {e}")
            return False
    
    def load_progress(self):
        """Загружает прогресс из файла"""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_topic_index = data.get('current_index', 0)
                    print(f"📊 Загружен прогресс: тема {self.current_topic_index + 1}")
            else:
                self.current_topic_index = 0
                print("🆕 Прогресс не найден, начинаем с первой темы")
        except Exception as e:
            print(f"⚠️ Ошибка загрузки прогресса: {e}")
            self.current_topic_index = 0
    
    def save_progress(self):
        """Сохраняет текущий прогресс"""
        try:
            progress_data = {
                'current_index': self.current_topic_index,
                'last_updated': datetime.now().isoformat(),
                'total_topics': len(self.topics)
            }
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Ошибка сохранения прогресса: {e}")
    
    def log_generation(self, topic, status, details=""):
        """Логирует процесс генерации"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {status}: {topic}"
        if details:
            log_entry += f" - {details}"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"⚠️ Ошибка записи лога: {e}")
        
        print(log_entry)
    
    def get_next_topic(self):
        """Получает следующую тему по кругу"""
        if not self.topics:
            return None
        
        topic = self.topics[self.current_topic_index]
        print(f"🎯 Текущая тема ({self.current_topic_index + 1}/{len(self.topics)}): {topic}")
        return topic
    
    def generate_article(self, topic):
        """Генерирует статью по теме"""
        try:
            print(f"🚀 Начинаю генерацию статьи по теме: {topic}")
            
            # Генерируем статью через article_agent
            result = self.article_agent.create_article_by_topic(topic)
            
            if result.get("success"):
                filename = result.get("filename", "неизвестно")
                self.log_generation(topic, "✅ УСПЕХ", f"Файл: {filename}")
                return True
            else:
                error = result.get("error", "неизвестная ошибка")
                self.log_generation(topic, "❌ ОШИБКА", error)
                return False
                
        except Exception as e:
            self.log_generation(topic, "❌ ИСКЛЮЧЕНИЕ", str(e))
            return False
    
    def run_auto_generation(self):
        """Основной цикл автоматической генерации (запускается cron каждые 5 минут)"""
        print("🤖 АВТОМАТИЧЕСКИЙ ГЕНЕРАТОР СТАТЕЙ AI-АССИСТЕНТ ЗАПУЩЕН")
        print("🎯 Тематика: AI-ассистенты, чат-боты, автоматизация продаж")
        print("=" * 50)
        
        # Загружаем темы
        if not self.load_topics_from_csv():
            print("❌ Не удалось загрузить темы. Завершение работы.")
            return
        
        # Загружаем прогресс
        self.load_progress()
        
        print(f"📚 Всего тем: {len(self.topics)}")
        print("=" * 50)
        
        try:
            # Получаем текущую тему
            topic = self.get_next_topic()
            if not topic:
                print("❌ Нет тем для генерации")
                return
            
            # Генерируем статью
            success = self.generate_article(topic)
            
            # Переходим к следующей теме
            self.current_topic_index = (self.current_topic_index + 1) % len(self.topics)
            self.save_progress()
            
            if success:
                print(f"✅ Статья сгенерирована! Следующая тема: {self.current_topic_index + 1}")
            else:
                print(f"⚠️ Ошибка генерации")
            
            print("✅ Генерация завершена. Cron запустит следующий запуск через 5 минут.")
                
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            self.save_progress()

def main():
    """Главная функция для AI-Ассистент"""
    print("🚀 Запуск генератора статей для AI-Ассистент")
    print("📁 Рабочая папка:", os.getcwd())
    print("📋 CSV файл:", "ai_business_3themes.csv")
    print("=" * 50)
    
    generator = AutoArticleGenerator()
    generator.run_auto_generation()

if __name__ == "__main__":
    main()
