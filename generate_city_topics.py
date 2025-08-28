#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт генерации 100 тем с городами для AI-Ассистент
Создает новые темы, добавляя к каждой существующей теме название города
"""

import csv
import os
from pathlib import Path

def generate_city_topics():
    """Генерирует темы: 100 базовых + 100 тем с каждым из 15 городов"""
    
    # Список городов (15 основных городов)
    cities = [
        "Москва",
        "Санкт-Петербург", 
        "Новосибирск",
        "Екатеринбург",
        "Казань",
        "Нижний Новгород",
        "Красноярск",
        "Челябинск",
        "Самара",
        "Уфа",
        "Ростов-на-Дону",
        "Омск",
        "Краснодар",
        "Воронеж",
        "Пермь",
        "Волгоград"
    ]
    
    # Читаем существующие темы
    input_file = "100-tem-dlya-statey.csv"
    output_file = "100-tem-s-gorodami.csv"
    
    if not os.path.exists(input_file):
        print(f"❌ Файл {input_file} не найден!")
        return
    
    topics = []
    
    # Читаем CSV файл
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Тема статьи']:  # Проверяем, что тема не пустая
                topics.append(row['Тема статьи'])
    
    print(f"📚 Загружено {len(topics)} тем из файла {input_file}")
    
    # Создаем все темы: базовые + с городами
    all_topics = []
    
    # 1. Сначала добавляем 100 базовых тем (без городов)
    for i, topic in enumerate(topics):
        all_topics.append({
            '№': i + 1,
            'Тема статьи': topic,
            'Город': 'Без города',
            'Базовая тема': topic
        })
    
    # 2. Потом добавляем темы с каждым городом
    topic_counter = len(topics) + 1
    
    for city in cities:
        for i, topic in enumerate(topics):
            # Создаем новую тему с городом
            if "в России" in topic:
                # Заменяем "в России" на город
                new_topic = topic.replace("в России", f"в {city}")
            elif "малого бизнеса" in topic:
                # Добавляем город к "малого бизнеса"
                new_topic = topic.replace("малого бизнеса", f"малого бизнеса в {city}")
            elif "малом бизнесе" in topic:
                # Добавляем город к "малом бизнесе"
                new_topic = topic.replace("малом бизнесе", f"малом бизнесе в {city}")
            elif "микробизнес" in topic:
                # Добавляем город к "микробизнес"
                new_topic = topic.replace("микробизнес", f"микробизнес в {city}")
            else:
                # Добавляем город в конец темы
                new_topic = f"{topic} в {city}"
            
            all_topics.append({
                '№': topic_counter,
                'Тема статьи': new_topic,
                'Город': city,
                'Базовая тема': topic
            })
            topic_counter += 1
    
    # Записываем результат в новый CSV файл
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['№', 'Тема статьи', 'Город', 'Базовая тема']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for topic_data in all_topics:
            writer.writerow(topic_data)
    
    print(f"✅ Создано {len(all_topics)} тем всего")
    print(f"📊 Структура:")
    print(f"   • 100 базовых тем (без городов)")
    print(f"   • {len(cities)} городов × 100 тем = {len(cities) * 100} тем с городами")
    print(f"   • Итого: {len(all_topics)} тем")
    print(f"📁 Результат сохранен в файл: {output_file}")
    
    # Показываем примеры
    print("\n🎯 Примеры базовых тем:")
    for i, topic_data in enumerate(all_topics[:3]):
        print(f"{i+1}. {topic_data['Тема статьи']}")
    
    print("\n🏙 Примеры тем с городами:")
    for i, topic_data in enumerate(all_topics[100:103]):
        print(f"{i+101}. {topic_data['Тема статьи']}")
    
    # Статистика по городам
    city_count = {}
    for topic_data in all_topics:
        city = topic_data['Город']
        city_count[city] = city_count.get(city, 0) + 1
    
    print(f"\n🏙 Статистика по городам:")
    print(f"   Без города: {city_count.get('Без города', 0)} тем")
    for city in cities[:5]:
        if city in city_count:
            print(f"   {city}: {city_count[city]} тем")
    print(f"   ... и еще {len(cities) - 5} городов")
    
    return all_topics

def create_ai_business_csv(all_topics):
    """Создает CSV файл для AI-ассистент со всеми темами"""
    
    output_file = "ai_business_3themes.csv"
    
    # Создаем простой CSV только с темами (формат для AI-ассистент)
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['Тема']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for topic_data in all_topics:
            writer.writerow({'Тема': topic_data['Тема статьи']})
    
    print(f"✅ Создан файл для AI-ассистент: {output_file}")
    print(f"📊 Количество тем: {len(all_topics)}")
    print(f"📝 Формат: готов для генерации статей")
    print(f"🎯 Структура: 100 базовых + {len(all_topics) - 100} с городами")

if __name__ == "__main__":
    print("🚀 Генерация тем с городами для AI-Ассистент")
    print("=" * 60)
    
    # Генерируем темы
    all_topics = generate_city_topics()
    
    if all_topics:
        # Создаем CSV для AI-ассистент
        create_ai_business_csv(all_topics)
        
        print("\n🎉 Генерация завершена!")
        print("📋 Файлы созданы:")
        print("   • 100-tem-s-gorodami.csv - полный список (базовые + с городами)")
        print("   • ai_business_3themes.csv - готов для генерации статей")
        
        print("\n💡 Теперь можете:")
        print("   1. Файл ai_business_3themes.csv содержит ВСЕ темы!")
        print("   2. Запустить генерацию статей с новыми темами")
        print("   3. Получить 1,600 уникальных статей!")
        print("   4. Начать с базовых тем, потом перейти к темам с городами")
    else:
        print("❌ Ошибка при генерации тем")
