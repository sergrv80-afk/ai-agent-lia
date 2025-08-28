#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import openai
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv(override=True)

class ArticleAgent:
    def __init__(self):
        self.project_root = Path(__file__).parent
        # Читаем API ключ из переменных окружения
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ OPENAI_API_KEY не найден в переменных окружения. Проверьте файл .env")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.MODEL = "gpt-5-mini"

        # AI-Ассистент: используем gpt-5-mini для генерации статей
        # self.MODEL = "gpt-5"  # для продакшена можно переключить на gpt-5

        # Responses API: без ограничений на длину вывода
        # self.max_output_tokens = None  # убираем ограничение

        self.article_template = self._load_article_template()

    def _load_article_template(self):
        p = self.project_root / "AI_ARTICLE_TEMPLATE.html"
        if p.exists():
            template = p.read_text(encoding="utf-8")
            # Автоматически обновляем версии в шаблоне для AI-Ассистент
            return self._update_template_versions(template)
        return """<!DOCTYPE html> ... базовый HTML-шаблон AI-Ассистент ... """

    def _generate_target_audience(self, topic: str) -> str:
        """Автогенерация ЦА на основе темы (специализированная для AI-автоматизации)."""
        return (
            "владельцы и руководители бизнеса, маркетологи, IT-директора, которые хотят автоматизировать продажи и лидогенерацию с помощью AI-ассистентов"
        )

    def _generate_keywords(self, topic: str) -> str:
        """Автогенерация ключевых слов из темы + базовые термины для AI-Ассистент."""
        base = re.sub(r"\s+", ", ", topic.strip())
        extra = "AI-ассистент, автоматизация продаж, лидогенерация, чат-бот, GPT, нейросети, CRM, Bitrix24"
        return f"{base}, {extra}"

    def _run_full_geo_optimization(self, article_filename: str):
        """Запускает полную ГИБРИДНУЮ GEO-оптимизацию с GPT-5."""
        try:
            from geo_hybrid_agent import GEOHybridAgent
            print("🚀 Запускаю ГИБРИДНУЮ GEO-оптимизацию с GPT-5...")
            
            # Создаем гибридного агента оптимизации
            hybrid_agent = GEOHybridAgent()
            
            # Запускаем гибридную оптимизацию (анализ + GPT-5 планирование + применение)
            result = hybrid_agent.run_hybrid_optimization(article_filename)
            
            if result.get("success"):
                print(f"✅ Гибридная GEO-оптимизация с GPT-5 завершена!")
                print(f"📊 SEO score: {result['analysis']['seo_analysis']['score']}%")
                print(f"🤖 LLM score: {result['analysis']['llm_analysis']['score']}%")
                print(f"📝 Структура score: {result['analysis']['content_analysis']['score']}%")
                print(f"🖼 Изображения score: {result['analysis']['image_analysis']['score']}%")
                
                # Показываем результаты GPT-5 оптимизации
                if result.get('gpt_plan', {}).get('success'):
                    gpt_data = result['gpt_plan']['data']
                    print(f"🤖 GPT-5 план применен:")
                    print(f"   - Приоритет: {gpt_data.get('priority', 'не указан')}")
                    print(f"   - Meta улучшения: {'Да' if 'meta_improvements' in gpt_data else 'Нет'}")
                    print(f"   - Контент улучшения: {'Да' if 'content_improvements' in gpt_data else 'Нет'}")
                    print(f"   - Технические улучшения: {'Да' if 'technical_improvements' in gpt_data else 'Нет'}")
                else:
                    print("⚠️ GPT-5 план не получен, использована оптимизация по правилам")
                
                print(f"📋 Отчет сохранен: {result['report_path']}")
            else:
                print(f"⚠️  Гибридная GEO-оптимизация не выполнена: {result.get('error')}")
                
        except Exception as e:
            print(f"⚠️  Не удалось запустить гибридную GEO-оптимизацию: {str(e)}")
            print("💡 Попробуйте запустить вручную: python3 geo_hybrid_agent.py <статья>")

    def create_article_by_topic(self, topic: str) -> dict:
        """Создает статью, принимая только тему. Остальные параметры генерируются автоматически."""
        print(f"🎯 Создаю статью по теме: '{topic}'")
        print("📋 Автоматически генерирую: целевая аудитория, имя файла, ключевые слова")
        print("🚀 После создания выполнится ГИБРИДНАЯ GEO-оптимизация с GPT-5")
        
        target_audience = self._generate_target_audience(topic)
        filename = self._generate_filename(topic)
        keywords = self._generate_keywords(topic)
        result = self.create_article(topic, target_audience, filename, keywords)
        if result.get("success"):
            # Сначала полная GEO-оптимизация (все 14 шагов), затем обновление файлов
            self._run_full_geo_optimization(filename)
            self._run_automation(filename)
        return result

    def _update_template_versions(self, template: str) -> str:
        """Автоматически обновляет версии файлов в шаблоне из index.html"""
        try:
            index_path = self.project_root / "index.html"
            if not index_path.exists():
                print("⚠️  index.html не найден, используем базовые версии")
                return template
            
            with open(index_path, 'r', encoding='utf-8') as f:
                index_content = f.read()
            
            # Получаем актуальные версии
            css_match = re.search(r'href="/assets/css/styles\.css\?v=(\d+)"', index_content)
            js_match = re.search(r'src="/js/app\.js\?v=(\d+)"', index_content)
            widget_match = re.search(r'src="/js/sv-video-widget\.js\?v=(\d+)"', index_content)
            
            if css_match:
                css_version = css_match.group(1)
                template = re.sub(r'href="/assets/css/styles\.css\?v=\d+"', f'href="/assets/css/styles.css?v={css_version}"', template)
                print(f"🎨 CSS версия обновлена до v{css_version}")
            
            if js_match:
                js_version = js_match.group(1)
                template = re.sub(r'src="/js/app\.js\?v=\d+"', f'src="/js/app.js?v={js_version}"', template)
                print(f"⚡ JS версия обновлена до v{js_version}")
            
            if widget_match:
                widget_version = widget_match.group(1)
                template = re.sub(r'src="/js/sv-video-widget\.js\?v=\d+"', f'src="/js/sv-video-widget.js?v={widget_version}"', template)
                print(f"🎥 Видео-виджет версия обновлена до v{widget_version}")
            
            return template
            
        except Exception as e:
            print(f"⚠️  Ошибка обновления версий: {str(e)}")
            return template

    def _validate_html_structure(self, html_content: str) -> dict:
        """Валидирует структуру HTML статьи"""
        validation = {
            "success": True,
            "errors": [],
            "warnings": [],
            "checks": {}
        }
        
        try:
            # Проверяем DOCTYPE
            if not html_content.strip().startswith('<!DOCTYPE html'):
                validation["errors"].append("❌ Отсутствует DOCTYPE html")
                validation["success"] = False
            else:
                validation["checks"]["doctype"] = "✅ DOCTYPE html присутствует"
            
            # Проверяем обязательные теги
            required_tags = ['<html', '<head', '<title', '<body', '</html>']
            for tag in required_tags:
                if tag not in html_content:
                    validation["errors"].append(f"❌ Отсутствует тег: {tag}")
                    validation["success"] = False
                else:
                    validation["checks"][f"tag_{tag}"] = f"✅ Тег {tag} присутствует"
            
            # Проверяем H1 заголовок
            h1_count = len(re.findall(r'<h1[^>]*>.*?</h1>', html_content, re.DOTALL))
            if h1_count == 0:
                validation["errors"].append("❌ Отсутствует H1 заголовок")
                validation["success"] = False
            elif h1_count > 1:
                validation["warnings"].append(f"⚠️  Найдено {h1_count} H1 заголовков (должен быть один)")
            else:
                validation["checks"]["h1"] = "✅ H1 заголовок: один на странице"
            
            # Проверяем H2 заголовки
            h2_count = len(re.findall(r'<h2[^>]*>.*?</h2>', html_content, re.DOTALL))
            if h2_count < 4:
                validation["warnings"].append(f"⚠️  H2 заголовков: {h2_count} (рекомендуется минимум 4)")
            else:
                validation["checks"]["h2"] = f"✅ H2 заголовки: {h2_count} (достаточно)"
            
            # Проверяем FAQ блок
            if re.search(r'<section[^>]*id="faq"[^>]*>', html_content):
                validation["checks"]["faq"] = "✅ FAQ блок присутствует"
            else:
                validation["warnings"].append("⚠️  FAQ блок отсутствует")
            
            # Проверяем CTA блоки
            cta_count = len(re.findall(r'class="[^"]*cta[^"]*"', html_content))
            if cta_count >= 2:
                validation["checks"]["cta"] = f"✅ CTA блоки: {cta_count} (достаточно)"
            else:
                validation["warnings"].append(f"⚠️  CTA блоков: {cta_count} (рекомендуется минимум 2)")
            
            # Проверяем видео-виджет
            if 'sv-video-widget.js' in html_content:
                validation["checks"]["video_widget"] = "✅ Видео-виджет подключен"
            else:
                validation["warnings"].append("⚠️  Видео-виджет не подключен")
            
        except Exception as e:
            validation["errors"].append(f"❌ Ошибка валидации HTML: {str(e)}")
            validation["success"] = False
        
        return validation

    def _validate_json_ld(self, html_content: str) -> dict:
        """Валидирует JSON-LD схемы в статье"""
        validation = {
            "success": True,
            "errors": [],
            "warnings": [],
            "checks": {}
        }
        
        try:
            # Ищем JSON-LD блоки
            json_ld_blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html_content, re.DOTALL)
            
            if not json_ld_blocks:
                validation["errors"].append("❌ JSON-LD схемы не найдены")
                validation["success"] = False
                return validation
            
            validation["checks"]["json_ld_count"] = f"✅ Найдено {len(json_ld_blocks)} JSON-LD блоков"
            
            for i, block in enumerate(json_ld_blocks):
                try:
                    # Парсим JSON
                    json_data = json.loads(block.strip())
                    
                    # Проверяем обязательные поля для Article
                    if json_data.get("@type") == "Article":
                        required_fields = ["@context", "@type", "headline", "author", "datePublished"]
                        missing_fields = [field for field in required_fields if field not in json_data]
                        
                        if missing_fields:
                            validation["warnings"].append(f"⚠️  Article схема #{i+1}: отсутствуют поля: {', '.join(missing_fields)}")
                        else:
                            validation["checks"][f"article_{i+1}"] = f"✅ Article схема #{i+1}: валидна"
                    
                    # Проверяем обязательные поля для FAQPage
                    elif json_data.get("@type") == "FAQPage":
                        if "mainEntity" not in json_data:
                            validation["errors"].append(f"❌ FAQPage схема #{i+1}: отсутствует mainEntity")
                            validation["success"] = False
                        else:
                            questions = json_data["mainEntity"]
                            if not isinstance(questions, list) or len(questions) < 6:
                                validation["warnings"].append(f"⚠️  FAQPage схема #{i+1}: недостаточно вопросов (найдено {len(questions) if isinstance(questions, list) else 0})")
                            else:
                                validation["checks"][f"faq_{i+1}"] = f"✅ FAQPage схема #{i+1}: {len(questions)} вопросов"
                    
                    # Проверяем Organization
                    elif json_data.get("@type") == "Organization":
                        validation["checks"][f"organization_{i+1}"] = f"✅ Organization схема #{i+1}: присутствует"
                    
                    else:
                        validation["checks"][f"other_{i+1}"] = f"ℹ️  Схема #{i+1}: тип {json_data.get('@type', 'неизвестен')}"
                        
                except json.JSONDecodeError as e:
                    validation["errors"].append(f"❌ Схема #{i+1}: ошибка JSON - {str(e)}")
                    validation["success"] = False
                except Exception as e:
                    validation["errors"].append(f"❌ Схема #{i+1}: ошибка валидации - {str(e)}")
                    validation["success"] = False
            
        except Exception as e:
            validation["errors"].append(f"❌ Ошибка валидации JSON-LD: {str(e)}")
            validation["success"] = False
        
        return validation

    def create_article(self, topic: str, target_audience: str,
                       article_filename: str, keywords: str = "") -> dict:
        try:
            prompt = f"""
Создай SEO + GEO/LLMO оптимизированную статью для SmartVizitka на тему: "{topic}"

Целевая аудитория: {target_audience}
Ключевые слова: {keywords or 'автоматизация, AI, нейросети, бизнес, CRM'}

## 🎯 ЦЕЛЕВАЯ АУДИТОРИЯ SMARTVIZITKA:

### **1. Сегменты бизнеса:**
• Салоны красоты и барбершопы — мастера, студии с 1–10 сотрудников
• Медицинские и оздоровительные услуги — стоматологии, массажисты, клиники
• Фитнес и спорт — тренеры, залы, секции
• Образование и репетиторы — частные школы, курсы, репетиторы
• Бытовые и сервисные услуги — автомойки, ремонт, клининг, прокат
• Досуг и развлечения — студии танца, квесты, кружки

### **2. Размер бизнеса:**
• Индивидуальные предприниматели и малые компании (1–30 сотрудников)
• Без выделенного IT-отдела, ограниченный бюджет

### **3. Боли и потребности:**
• Постоянные «пустые окна» и неявки клиентов
• Хаос в записях (блокнот, Excel, телефонные звонки)
• Нет прозрачности в финансах и загрузке
• Нужно больше клиентов, но нет времени и бюджета на маркетинг
• Желание удерживать существующих клиентов, запускать акции и бонусы

### **4. Ценности и мотивация:**
• Простота: «чтобы всё работало сразу, без программиста»
• Доступность: бесплатно/дешево, без подписок
• Гибкость: записи 24/7, уведомления, аналитика «в одном окне»
• Рост дохода: больше записей, меньше неявок, возврат клиентов

### **5. Поведенческие особенности:**
• Активные пользователи WhatsApp, Instagram, Telegram
• Решают вопросы быстро (без долгого чтения инструкций)
• Готовы пробовать новое, если «бесплатно и без риска»

**Используй эти данные для создания релевантного контента, который точно попадет в боли и потребности целевой аудитории!**

**🎯 ГЛАВНОЕ ПРАВИЛО: Статья должна быть ПОЛЕЗНОЙ для читателя - давать реальные знания, инструменты и понимание, а не только рассказывать о SmartVizitka. Читатель должен получить практическую ценность от прочтения!**

Используй этот HTML-шаблон и замени все заглушки:

{self.article_template}

**⚠️ КРИТИЧЕСКИ ВАЖНО: В шаблоне есть комментарии-инструкции для каждого раздела. СЛЕДУЙ ИМ СТРОГО!**
**Каждый раздел должен давать читателю РЕАЛЬНУЮ ПОЛЬЗУ, а не быть рекламой SmartVizitka!**

## 🎯 ОБЯЗАТЕЛЬНЫЕ ТРЕБОВАНИЯ:

### **1. Структура контента:**
- **4 раздела (H2)** с четкой логикой
- **FAQ блок** с 6 вопросами и ответами
- **Каждый раздел** должен следовать структуре: БОЛЬ → РЕШЕНИЕ → РЕЗУЛЬТАТ → ЦЕННОСТЬ (описывать естественно, без явных слов "боль", "решение", "результат")

### **2. Мета-теги (обязательно):**
- Title: "{topic} - SmartVizitka" (60-70 символов)
- Description: SEO-описание (150-160 символов)
- Keywords: ключевые слова через запятую
- Author: SmartVizitka
- Robots: index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1
- Canonical: ссылка на статью
- OpenGraph: title, description, type=article, image, url, locale, site_name, article:published_time, article:modified_time, article:author, article:section, article:tag
- Twitter: card=summary_large_image, site, creator, title, description, image

### **3. JSON-LD схемы (обязательно):**
- **Article**: headline, description, image, keywords, author, publisher, datePublished, dateModified, articleSection, articleBody
- **WebSite**: name, url, description, potentialAction (SearchAction)
- **BreadcrumbList**: itemListElement с навигацией (Главная → Статьи → [Тема статьи])
- **FAQPage**: mainEntity с 6 вопросами

### **4. CTA блоки:**
- **После каждого раздела** (4 CTA)
- **Главный CTA в конце** статьи
- **Все ссылки** ведут на главную страницу (/)

### **5. SEO-оптимизация:**
- Используй ключевые слова в **H1, H2 заголовках**
- **H1** - только один на странице
- **H2** - минимум 4, максимум 6
- **Внутренние ссылки** на главную страницу

### **6. Контент:**
- **Раздел 1**: Проблемы и боли целевой аудитории (описывать естественно, без явных слов "боль", "решение", "результат")
- **Раздел 2**: Как AI-технологии решают эти проблемы (описывать процесс и технологии)
- **Раздел 3**: Конкретные результаты и преимущества (цифры, кейсы, метрики)
- **Раздел 4**: Практическое применение и внедрение (пошагово, с примерами)

### **7. FAQ вопросы (для LLM поиска):**
- **Вопрос 1**: Что такое [тема статьи] для бизнеса?
- **Вопрос 2**: Как работает [тема статьи] в [отрасли]?
- **Вопрос 3**: Какие преимущества [темы статьи] перед традиционными методами?
- **Вопрос 4**: Сколько стоит внедрение [темы статьи]?
- **Вопрос 5**: Как внедрить [тему статьи] в бизнес?
- **Вопрос 6**: Есть ли поддержка при использовании [темы статьи]?

**ВАЖНО:** FAQ вопросы должны быть конкретными и содержать ключевые слова для лучшего попадания в ответы LLM при поиске информации.

### **8. Качество контента (ОБЯЗАТЕЛЬНО):**
- **Статья должна быть ИНФОРМАТИВНОЙ** - давать реальные знания, а не только рекламу
- **Практическая польза** - читатель должен получить конкретные инструменты и понимание
- **НЕ должно быть прямой рекламы SmartVizitka** - упоминания только в контексте решения проблем
- **Объективная информация** - честно рассказывать о возможностях и ограничениях
- **Кейсы и примеры** - реальные истории успеха и применения
- **Пошаговые инструкции** - конкретные действия, которые можно применить
- **Экспертное мнение** - глубокое понимание темы, а не поверхностная информация

## ⚠️ ВАЖНО:
- Верни ПОЛНЫЙ HTML-код от <!DOCTYPE html> до </html>
- НЕ изменяй структуру шаблона
- Замени ВСЕ заглушки на реальный контент, включая:
  * ЗАГОЛОВОК_СТАТЬИ
  * ОПИСАНИЕ_СТАТЬИ
  * КЛЮЧЕВЫЕ_СЛОВА_СТАТЬИ
  * НАЗВАНИЕ_ФАЙЛА
  * СОДЕРЖИМОЕ_СТАТЬИ_ДЛЯ_JSON_LD
- Сохрани все CSS классы и атрибуты
- Видео-виджет уже подключен - НЕ трогай его
- Все даты используй в формате ISO 8601: 2025-01-01T00:00:00+03:00
"""

            # Responses API: messages → input
            msgs = [
                {"role": "system", "content": "Ты эксперт по созданию SEO + GEO/LLMO оптимизированных HTML-статей. Твоя задача - создавать качественные, валидные HTML-страницы с правильной структурой, мета-тегами и JSON-LD схемами. КРИТИЧЕСКИ ВАЖНО: статьи должны быть ИНФОРМАТИВНЫМИ и давать реальную практическую пользу читателю, а не быть прямой рекламой. Отвечай ТОЛЬКО валидным HTML-кодом, без пояснений."},
                {"role": "user", "content": prompt},
            ]

            print(f"🔧 Отправляю запрос к модели {self.MODEL}...")
            
            resp = self.client.responses.create(
                model=self.MODEL,
                input=msgs,
                # max_output_tokens убран - без ограничений
            )
            
            print(f"🔧 Получен ответ от API")

            # Проверяем ответ
            if not hasattr(resp, 'output_text') or not resp.output_text:
                return {
                    "success": False,
                    "error": "GPT не вернул содержимое статьи",
                    "message": "Ошибка: GPT не сгенерировал содержимое"
                }

            article_content = resp.output_text

            # Проверяем, что это похоже на HTML
            if not article_content.strip().startswith('<!DOCTYPE html'):
                return {
                    "success": False,
                    "error": "GPT вернул не HTML",
                    "message": "Ошибка: GPT вернул не HTML-код"
                }

            # Валидируем созданную статью
            print("🔍 Выполняю валидацию созданной статьи...")
            
            html_validation = self._validate_html_structure(article_content)
            json_ld_validation = self._validate_json_ld(article_content)
            
            # Выводим результаты валидации
            print("\n📊 Результаты валидации HTML:")
            for check in html_validation["checks"].values():
                print(f"   {check}")
            
            if html_validation["warnings"]:
                print("\n⚠️  Предупреждения HTML:")
                for warning in html_validation["warnings"]:
                    print(f"   {warning}")
            
            if html_validation["errors"]:
                print("\n❌ Ошибки HTML:")
                for error in html_validation["errors"]:
                    print(f"   {error}")
            
            print("\n📊 Результаты валидации JSON-LD:")
            for check in json_ld_validation["checks"].values():
                print(f"   {check}")
            
            if json_ld_validation["warnings"]:
                print("\n⚠️  Предупреждения JSON-LD:")
                for warning in json_ld_validation["warnings"]:
                    print(f"   {warning}")
            
            if json_ld_validation["errors"]:
                print("\n❌ Ошибки JSON-LD:")
                for error in json_ld_validation["errors"]:
                    print(f"   {error}")
            
            # Проверяем общий результат валидации
            overall_success = html_validation["success"] and json_ld_validation["success"]
            
            if not overall_success:
                print("\n⚠️  Статья создана, но есть критические ошибки валидации!")
                print("   Рекомендуется проверить и исправить перед публикацией.")
            else:
                print("\n✅ Валидация пройдена успешно! Статья готова к публикации.")

            # Сохраняем
            article_path = self.project_root / article_filename
            article_path.write_text(article_content, encoding="utf-8")

            return {
                "success": True,
                "filename": article_filename,
                "path": str(article_path),
                "message": f"Статья '{topic}' сохранена в {article_filename}",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Ошибка при создании статьи: {str(e)}"
            }

    def _generate_filename(self, topic: str) -> str:
        # Транслитерация RU → латиница + слаг
        ru = "абвгдеёжзийклмнопрстуфхцчшщьыъэюя"
        tr = ["a","b","v","g","d","e","e","zh","z","i","y","k","l","m","n","o","p","r","s","t","u","f","h","c","ch","sh","sch","","","e","yu","ya"]
        mapping = {ru[i]: tr[i] for i in range(len(tr))}
        def translit(s: str) -> str:
            out = []
            for ch in s.lower():
                if ch in mapping:
                    out.append(mapping[ch])
                elif ch.isalnum() or ch in [' ', '-', '_']:
                    out.append(ch)
                else:
                    out.append(' ')
            return ''.join(out)
        base = translit(topic)
        base = re.sub(r'\s+', '-', base)
        base = re.sub(r'[^a-z0-9\-]', '', base).strip('-')
        if not base:
            from datetime import datetime
            base = 'article-' + datetime.now().strftime('%Y%m%d-%H%M')
        if not base.endswith('.html'):
            base += '.html'
        return base

    def run_interactive(self):
        """
        Интерактивный режим работы агента для AI-Ассистент
        """
        print("🤖 AI-Ассистент Article Agent")
        print("=" * 50)
        print("Автоматическое создание SEO + GEO/LLMO оптимизированных статей")
        print("Тематика: AI-ассистенты, чат-боты, автоматизация продаж")
        print("Использует GPT-5 с Responses API")
        print("=" * 50)
        
        while True:
            print("\n📝 Введите данные для создания статьи:")
            topic = input("🎯 Тема статьи: ").strip()
            if not topic:
                print("❌ Тема не может быть пустой!")
                continue
            print(f"\n🚀 Создаю статью '{topic}' по одной теме (остальное автоматически)...")
            print("⏳ Это может занять 1-2 минуты...")
            result = self.create_article_by_topic(topic)
            if result.get("success"):
                print(f"✅ {result['message']}")
            else:
                print(f"❌ {result.get('message') or result.get('error')}")
            continue_confirm = input("\n🔄 Создать еще одну статью? (y/n): ").strip().lower()
            if continue_confirm != 'y':
                break
        
        print("\n🎉 Работа агента завершена!")

    def _run_automation(self, article_filename: str):
        """
        Запускает автоматическое обновление файлов (после GEO-оптимизации)
        """
        try:
            print("🔄 Запускаю автоматическое обновление файлов...")
            
            # Импортируем и запускаем автоматизацию
            from auto_article_updater import ArticleUpdater
            
            updater = ArticleUpdater()
            updater.update_all_files(article_filename)
            
            print("✅ Автоматизация завершена!")
            
        except Exception as e:
            print(f"❌ Ошибка автоматизации: {str(e)}")
            print("💡 Попробуйте запустить вручную: python3 auto_article_updater.py <статья>")

    def test_agent_functionality(self):
        """Тестирует основные функции агента"""
        print("🧪 Тестирование функциональности агента...")
        print("=" * 50)
        
        test_results = {
            "template_loading": False,
            "version_updating": False,
            "html_validation": False,
            "json_ld_validation": False
        }
        
        try:
            # Тест 1: Загрузка шаблона
            print("1️⃣ Тестирую загрузку шаблона...")
            template = self._load_article_template()
            if template and "<!DOCTYPE html>" in template:
                test_results["template_loading"] = True
                print("   ✅ Шаблон загружен успешно")
            else:
                print("   ❌ Ошибка загрузки шаблона")
            
            # Тест 2: Обновление версий
            print("2️⃣ Тестирую обновление версий...")
            updated_template = self._update_template_versions(template)
            if updated_template != template:
                test_results["version_updating"] = True
                print("   ✅ Версии обновлены")
            else:
                print("   ⚠️  Версии не изменились (возможно, уже актуальны)")
            
            # Тест 3: Валидация HTML
            print("3️⃣ Тестирую валидацию HTML...")
            html_validation = self._validate_html_structure(template)
            if html_validation["success"]:
                test_results["html_validation"] = True
                print("   ✅ HTML валидация прошла")
            else:
                print(f"   ❌ HTML валидация не прошла: {len(html_validation['errors'])} ошибок")
            
            # Тест 4: Валидация JSON-LD
            print("4️⃣ Тестирую валидацию JSON-LD...")
            json_ld_validation = self._validate_json_ld(template)
            if json_ld_validation["success"]:
                test_results["json_ld_validation"] = True
                print("   ✅ JSON-LD валидация прошла")
            else:
                print(f"   ❌ JSON-LD валидация не прошла: {len(json_ld_validation['errors'])} ошибок")
            
        except Exception as e:
            print(f"   ❌ Ошибка тестирования: {str(e)}")
        
        # Итоговый результат
        print("\n📊 Результаты тестирования:")
        print("=" * 50)
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ ПРОШЕЛ" if result else "❌ НЕ ПРОШЕЛ"
            print(f"   {test_name}: {status}")
        
        print(f"\n🎯 Итого: {passed_tests}/{total_tests} тестов пройдено")
        
        if passed_tests == total_tests:
            print("🎉 Все тесты пройдены! Агент работает корректно.")
            return True
        else:
            print("⚠️  Некоторые тесты не пройдены. Проверьте настройки.")
            return False

def main():
    """Основная функция для AI-Ассистент"""
    print("🚀 AI-Ассистент Article Agent")
    print("📁 Рабочая папка:", os.getcwd())
    print("📋 Шаблон:", "AI_ARTICLE_TEMPLATE.html")
    print("=" * 50)
    
    # Создаем и запускаем агента
    agent = ArticleAgent()
    
    # Проверяем аргументы командной строки
    import sys
    if len(sys.argv) > 1:
        # Специальная команда для тестирования
        if sys.argv[1] == "test":
            print("🧪 Запуск тестирования агента...")
            agent.test_agent_functionality()
            return
        
        # Режим командной строки (поддержка: 1 аргумент — только тема; старый формат — 3+ аргумента)
        if len(sys.argv) == 2:
            topic = sys.argv[1]
            print(f"🚀 Создаю статью по теме (single-arg): '{topic}'...")
            result = agent.create_article_by_topic(topic)
            if result.get("success"):
                print(f"✅ {result['message']}")
            else:
                print(f"❌ {result.get('message') or result.get('error')}")
        elif len(sys.argv) >= 4:
            topic = sys.argv[1]
            target_audience = sys.argv[2]
            filename = sys.argv[3]
            keywords = sys.argv[4] if len(sys.argv) > 4 else ""
            
            print(f"🚀 Создаю статью '{topic}'...")
            result = agent.create_article(topic, target_audience, filename, keywords)
            
            if result["success"]:
                print(f"✅ {result['message']}")
                
                # Сначала полная GEO-оптимизация (все 14 шагов), затем автоматизация
                print("🚀 Автоматически запускаю полную GEO-оптимизацию (все 14 шагов)...")
                agent._run_full_geo_optimization(filename)
                
                print("🔄 Автоматически запускаю обновление файлов...")
                agent._run_automation(filename)
            else:
                print(f"❌ {result['message']}")
        else:
            print("❌ Использование:")
            print("   python article_agent.py 'Тема'                             # новый режим: только тема")
            print("   python article_agent.py 'Тема' 'Аудитория' 'filename.html' [ключевые_слова]")
            print("   python article_agent.py test  # для тестирования")
            print("")
            print("💡 Примеры тем для AI-Ассистент:")
            print("   python article_agent.py 'Чат-бот для бизнеса'")
            print("   python article_agent.py 'Использование GPT для бизнеса'")
            print("   python article_agent.py 'Нейросети для бизнеса'")
    else:
        # Интерактивный режим
        agent.run_interactive()

if __name__ == "__main__":
    main()
