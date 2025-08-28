#!/usr/bin/env python3
"""
GEO-гибридный агент оптимизации для AI-Ассистент
Объединяет возможности:
- geo_optimization_agent.py (правила + анализ)
- geo_llm_agent.py (GPT-5 планирование)
- Автоматическое применение изменений
Тематика: AI-ассистенты, чат-боты, автоматизация продаж
"""

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
load_dotenv()

class GEOHybridAgent:
    def __init__(self):
        self.project_root = Path(__file__).parent
        # Читаем API ключ из переменных окружения
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ OPENAI_API_KEY не найден в переменных окружения. Проверьте файл .env")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.MODEL = "gpt-5"  # Используем GPT-5 для планирования
        
        # SEO элементы для проверки
        self.required_seo_elements = {
            "meta": ["title", "description", "keywords", "author", "robots", "canonical"],
            "opengraph": ["og:title", "og:description", "og:type", "og:url", "og:image", "og:locale", "og:site_name"],
            "twitter": ["twitter:card", "twitter:site", "twitter:creator", "twitter:title", "twitter:description", "twitter:image"],
            "json_ld": ["Article", "WebSite", "BreadcrumbList"]
        }
        
        # LLM-friendly элементы
        self.llm_optimization_elements = [
            "FAQ блоки", "HowTo инструкции", "Структурированные списки",
            "Семантические заголовки", "Контентные выводы", "Локальные ключевые слова"
        ]

    def run_hybrid_optimization(self, article_path: str) -> Dict:
        """Запускает гибридную оптимизацию: анализ + GPT-5 планирование + применение"""
        try:
            print(f"🚀 Запускаю ГИБРИДНУЮ GEO-оптимизацию для: {article_path}")
            
            # 1. Анализируем статью через правила (быстро)
            print("📊 Этап 1: Анализ статьи через правила...")
            analysis = self.analyze_article(article_path)
            if not analysis["success"]:
                return analysis
            
            # 2. Планируем оптимизацию через GPT-5 (умно)
            print("🤖 Этап 2: GPT-5 планирование оптимизации...")
            llm_plan = self._request_gpt_optimization_plan(article_path, analysis)
            if not llm_plan.get("success"):
                print(f"⚠️ GPT-5 планирование не удалось: {llm_plan.get('error')}")
                print("🔄 Продолжаем с оптимизацией по правилам...")
                llm_plan = {"success": False, "data": {}}
            
            # 3. Применяем GPT-5 план (если есть)
            if llm_plan.get("success"):
                print("🔧 Этап 3: Применение GPT-5 плана...")
                gpt_result = self._apply_gpt_plan(article_path, llm_plan["data"])
                if gpt_result.get("success"):
                    print("✅ GPT-5 план применен успешно!")
                else:
                    print(f"⚠️ Ошибка применения GPT-5 плана: {gpt_result.get('error')}")
            
            # 4. Дополнительная оптимизация по правилам
            print("🔧 Этап 4: Дополнительная оптимизация по правилам...")
            optimization_result = self.optimize_article(article_path)
            
            # 5. Создаем комплексный отчет
            print("📋 Этап 5: Создание комплексного отчета...")
            report = self._create_hybrid_report(analysis, llm_plan, optimization_result)
            
            # 6. Сохраняем отчет
            report_path = self.project_root / f"hybrid_optimization_report_{Path(article_path).stem}.md"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"✅ Гибридная оптимизация завершена! Отчет сохранен: {report_path}")
            
            return {
                "success": True,
                "article_path": article_path,
                "analysis": analysis,
                "gpt_plan": llm_plan,
                "optimization": optimization_result,
                "report_path": str(report_path),
                "summary": f"Статья оптимизирована гибридным методом. SEO: {analysis['seo_analysis']['score']}%, LLM: {analysis['llm_analysis']['score']}%"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Ошибка гибридной оптимизации: {str(e)}"}

    def _request_gpt_optimization_plan(self, article_path: str, analysis: Dict) -> Dict:
        """Запрашивает план оптимизации у GPT-5"""
        try:
            # Читаем содержимое статьи
            article_file = self.project_root / article_path
            with open(article_file, 'r', encoding='utf-8') as f:
                article_content = f.read()
            
            # Собираем контекст для GPT-5
            context = self._collect_context_for_gpt(article_path, analysis, article_content)
            
            # Формируем промпт для GPT-5
            system_prompt = (
                "Ты эксперт по SEO и LLM-оптимизации. Проанализируй статью и создай план оптимизации. "
                "Верни ТОЛЬКО валидный JSON без пояснений."
            )
            
            user_prompt = self._build_gpt_prompt(context, analysis)
            
            # Отправляем запрос к GPT-5 через Responses API
            response = self.client.responses.create(
                model=self.MODEL,
                input=f"{system_prompt}\n\n{user_prompt}",
                reasoning={"effort": "medium"},   # minimal|low|medium|high
                text={"verbosity": "medium"}     # low|medium|high
            )
            
            # Парсим ответ
            gpt_response = response.output_text.strip()
            
            print(f"🤖 GPT-5 ответ получен (длина: {len(gpt_response)} символов)")
            print(f"📝 Первые 200 символов: {gpt_response[:200]}...")
            
            # Убираем возможные кодовые блоки
            gpt_response = re.sub(r'^```[a-zA-Z]*\n|\n```$', '', gpt_response)
            
            # Ищем JSON в ответе
            json_match = re.search(r'\{.*\}', gpt_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                print(f"🔍 Найден JSON (длина: {len(json_str)} символов)")
                print(f"📋 JSON: {json_str[:300]}...")
                
                try:
                    # Парсим JSON
                    plan = json.loads(json_str)
                    print("✅ JSON успешно распарсен")
                    return {"success": True, "data": plan}
                except json.JSONDecodeError as e:
                    print(f"❌ Ошибка парсинга JSON: {e}")
                    print(f"🔍 Проблемный JSON: {json_str}")
                    return {"success": False, "error": f"Ошибка парсинга JSON: {str(e)}"}
            else:
                print("❌ JSON не найден в ответе GPT-5")
                print(f"🔍 Полный ответ GPT-5: {gpt_response}")
                return {"success": False, "error": "JSON не найден в ответе GPT-5"}
            
        except Exception as e:
            return {"success": False, "error": f"Ошибка GPT-5 планирования: {str(e)}"}

    def _collect_context_for_gpt(self, article_path: str, analysis: Dict, article_content: str) -> Dict:
        """Собирает контекст для GPT-5"""
        context = {
            "article_path": article_path,
            "article_content": article_content[:15000],  # Ограничиваем размер
            "seo_analysis": analysis.get("seo_analysis", {}),
            "llm_analysis": analysis.get("llm_analysis", {}),
            "content_analysis": analysis.get("content_analysis", {}),
            "image_analysis": analysis.get("image_analysis", {}),
            "recommendations": analysis.get("recommendations", [])
        }
        return context

    def _build_gpt_prompt(self, context: Dict, analysis: Dict) -> str:
        """Строит промпт для GPT-5"""
        return f"""
Ты эксперт по SEO и LLM-оптимизации. Проанализируй статью и создай план оптимизации.

ВАЖНО: Верни ТОЛЬКО валидный JSON без пояснений, комментариев или дополнительного текста.

ТЕКУЩИЙ АНАЛИЗ:
- SEO Score: {analysis.get('seo_analysis', {}).get('score', 0)}%
- LLM Score: {analysis.get('llm_analysis', {}).get('score', 0)}%
- Структура Score: {analysis.get('content_analysis', {}).get('score', 0)}%
- Изображения Score: {analysis.get('image_analysis', {}).get('score', 0)}%

РЕКОМЕНДАЦИИ: {', '.join(analysis.get('recommendations', [])[:5])}

СОЗДАЙ ПЛАН ОПТИМИЗАЦИИ В JSON ФОРМАТЕ:

{{
  "meta_improvements": {{
    "title": "улучшенный заголовок статьи",
    "description": "улучшенное meta описание",
    "keywords": "ключевые слова через запятую"
  }},
  "content_improvements": {{
    "faq_questions": [
      {{
        "question": "Вопрос 1",
        "answer": "Ответ 1"
      }},
      {{
        "question": "Вопрос 2", 
        "answer": "Ответ 2"
      }}
    ],
    "summary_text": "краткий вывод раздела",
    "internal_links": [
      {{
        "text": "текст ссылки",
        "url": "/#section"
      }}
    ]
  }},
  "technical_improvements": {{
    "alt_tags": [
      {{
        "src_pattern": "часть src",
        "alt": "описание изображения"
      }}
    ],
    "json_ld_schemas": ["Article", "FAQPage"]
  }},
  "priority": "high",
  "estimated_impact": "описание ожидаемого эффекта"
}}

ПРАВИЛА:
1. JSON должен быть полностью валидным
2. Все скобки должны быть закрыты
3. Используй русский язык для контента
4. Будь конкретным и практичным
5. Не добавляй текст вне JSON
"""

    def _apply_gpt_plan(self, article_path: str, plan: Dict) -> Dict:
        """Применяет план оптимизации от GPT-5"""
        try:
            article_file = self.project_root / article_path
            
            # Создаем backup
            backup_path = article_file.with_suffix('.gpt.backup.html')
            with open(article_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            optimized_content = original_content
            applied_changes = []
            
            # Применяем улучшения meta тегов
            if "meta_improvements" in plan:
                meta_changes = self._apply_meta_improvements(optimized_content, plan["meta_improvements"])
                if meta_changes["changes"] > 0:
                    optimized_content = meta_changes["content"]
                    applied_changes.append(f"Meta теги: {meta_changes['changes']} изменений")
            
            # Применяем улучшения контента
            if "content_improvements" in plan:
                content_changes = self._apply_content_improvements(optimized_content, plan["content_improvements"])
                if content_changes["changes"] > 0:
                    optimized_content = content_changes["content"]
                    applied_changes.append(f"Контент: {content_changes['changes']} улучшений")
            
            # Применяем технические улучшения
            if "technical_improvements" in plan:
                tech_changes = self._apply_technical_improvements(optimized_content, plan["technical_improvements"])
                if tech_changes["changes"] > 0:
                    optimized_content = tech_changes["content"]
                    applied_changes.append(f"Технические: {tech_changes['changes']} улучшений")
            
            # Сохраняем оптимизированную статью
            with open(article_file, 'w', encoding='utf-8') as f:
                f.write(optimized_content)
            
            return {
                "success": True,
                "backup_path": str(backup_path),
                "changes_applied": applied_changes,
                "total_changes": len(applied_changes)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Ошибка применения GPT-5 плана: {str(e)}"}

    def _apply_meta_improvements(self, content: str, meta_plan: Dict) -> Dict:
        """Применяет улучшения meta тегов"""
        changes = 0
        
        # Обновляем title
        if "title" in meta_plan and meta_plan["title"]:
            title_pattern = r'<title>(.*?)</title>'
            if re.search(title_pattern, content):
                content = re.sub(title_pattern, f'<title>{meta_plan["title"]}</title>', content)
                changes += 1
        
        # Обновляем description
        if "description" in meta_plan and meta_plan["description"]:
            desc_pattern = r'<meta name="description" content="[^"]*"'
            if re.search(desc_pattern, content):
                content = re.sub(desc_pattern, f'<meta name="description" content="{meta_plan["description"]}"', content)
                changes += 1
        
        return {"content": content, "changes": changes}

    def _apply_content_improvements(self, content: str, content_plan: Dict) -> Dict:
        """Применяет улучшения контента"""
        changes = 0
        
        # Добавляем FAQ блоки
        if "faq_questions" in content_plan and content_plan["faq_questions"]:
            faq_html = self._generate_faq_html(content_plan["faq_questions"])
            if faq_html:
                content = self._insert_faq_section(content, faq_html)
                changes += 1
        
        # Добавляем контентный вывод
        if "summary_text" in content_plan and content_plan["summary_text"]:
            summary_html = self._generate_summary_html(content_plan["summary_text"])
            if summary_html:
                content = self._insert_summary_section(content, summary_html)
                changes += 1
        
        return {"content": content, "changes": changes}

    def _apply_technical_improvements(self, content: str, tech_plan: Dict) -> Dict:
        """Применяет технические улучшения"""
        changes = 0
        
        # Обновляем alt теги изображений
        if "alt_tags" in tech_plan and tech_plan["alt_tags"]:
            for alt_item in tech_plan["alt_tags"]:
                if "src_pattern" in alt_item and "alt" in alt_item:
                    content = self._update_image_alt(content, alt_item["src_pattern"], alt_item["alt"])
                    changes += 1
        
        return {"content": content, "changes": changes}

    def _generate_faq_html(self, faq_items: List[Dict]) -> str:
        """Генерирует HTML для FAQ блока"""
        if not faq_items:
            return ""
        
        faq_html = [
            '<section id="faq" class="alt">',
            '  <div class="container">',
            '    <h2 class="h2">Часто задаваемые вопросы</h2>',
            '    <div class="faq-grid">'
        ]
        
        for item in faq_items[:6]:  # Максимум 6 вопросов
            question = item.get("question", "Вопрос")
            answer = item.get("answer", "Ответ")
            faq_html.extend([
                '      <article class="faq-item">',
                f'        <h3>{question}</h3>',
                f'        <p>{answer}</p>',
                '      </article>'
            ])
        
        faq_html.extend(['    </div>', '  </div>', '</section>'])
        return '\n'.join(faq_html)

    def _generate_summary_html(self, summary_text: str) -> str:
        """Генерирует HTML для контентного вывода"""
        return f'''
<!-- ============== КОНТЕНТНЫЙ ВЫВОД ============== -->
<section class="content-summary-section">
  <div class="container">
    <div class="content-summary" style="background: var(--bg-alt); padding: 32px; border-radius: 20px; margin: 48px 0; text-align: center;">
      <h2 class="h2">📋 Краткий вывод</h2>
      <p style="font-size: 18px; line-height: 1.6; margin: 24px 0; color: var(--text);">
        {summary_text}
      </p>
      <div style="display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; margin-top: 24px;">
        <a href="/#signup" class="btn btn-primary">Получить CRM бесплатно</a>
        <a href="/#ai-team" class="btn btn-ghost">Узнать про AI-команду</a>
      </div>
    </div>
  </div>
</section>'''

    def _insert_faq_section(self, content: str, faq_html: str) -> str:
        """Вставляет FAQ секцию перед футером"""
        footer_marker = r'<!-- ============== FOOTER ============== -->'
        if re.search(footer_marker, content):
            return re.sub(footer_marker, f'{faq_html}\n\n{footer_marker}', content, count=1)
        return content

    def _insert_summary_section(self, content: str, summary_html: str) -> str:
        """Вставляет контентный вывод перед FAQ"""
        faq_marker = r'<!-- ============== FAQ SECTION ============== -->'
        if re.search(faq_marker, content):
            return re.sub(faq_marker, f'{summary_html}\n\n{faq_marker}', content, count=1)
        return content

    def _update_image_alt(self, content: str, src_pattern: str, alt_text: str) -> str:
        """Обновляет alt тег изображения"""
        img_pattern = rf'<img([^>]*?)src="[^"]*{re.escape(src_pattern)}[^"]*"([^>]*?)>'
        
        def replace_img(match):
            img_attrs = match.group(1) + match.group(2)
            if 'alt=' in img_attrs:
                return re.sub(r'alt="[^"]*"', f'alt="{alt_text}"', match.group(0))
            else:
                return match.group(0)[:-1] + f' alt="{alt_text}">'
        
        return re.sub(img_pattern, replace_img, content)

    def analyze_article(self, article_path: str) -> Dict:
        """Анализирует созданную статью и выявляет недостающие SEO элементы"""
        try:
            article_file = self.project_root / article_path
            if not article_file.exists():
                return {"success": False, "error": f"Файл {article_path} не найден"}
            
            with open(article_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"🔍 Анализирую статью: {article_path}")
            
            # Анализ SEO элементов
            seo_analysis = self._analyze_seo_elements(content)
            
            # Анализ LLM-оптимизации
            llm_analysis = self._analyze_llm_optimization(content)
            
            # Анализ структуры контента
            content_analysis = self._analyze_content_structure(content)
            
            # Анализ изображений
            image_analysis = self._analyze_images(content)
            
            return {
                "success": True,
                "article_path": article_path,
                "seo_analysis": seo_analysis,
                "llm_analysis": llm_analysis,
                "content_analysis": content_analysis,
                "image_analysis": image_analysis,
                "recommendations": self._generate_recommendations(seo_analysis, llm_analysis, content_analysis, image_analysis)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Ошибка анализа: {str(e)}"}

    def _analyze_seo_elements(self, content: str) -> Dict:
        """Анализирует наличие SEO элементов"""
        analysis = {
            "meta_tags": {},
            "opengraph": {},
            "twitter": {},
            "json_ld": {},
            "score": 0,
            "missing": []
        }
        
        # Проверка meta тегов
        for tag in self.required_seo_elements["meta"]:
            if tag == "title":
                pattern = r'<title>(.*?)</title>'
            elif tag == "description":
                pattern = r'<meta name="description" content="(.*?)"'
            elif tag == "keywords":
                pattern = r'<meta name="keywords" content="(.*?)"'
            elif tag == "author":
                pattern = r'<meta name="author" content="(.*?)"'
            elif tag == "robots":
                pattern = r'<meta name="robots" content="(.*?)"'
            elif tag == "canonical":
                pattern = r'<link rel="canonical" href="(.*?)"'
            
            match = re.search(pattern, content)
            if match:
                analysis["meta_tags"][tag] = {"found": True, "value": match.group(1)}
            else:
                analysis["meta_tags"][tag] = {"found": False, "value": None}
                analysis["missing"].append(f"meta:{tag}")
        
        # Проверка OpenGraph тегов
        for tag in self.required_seo_elements["opengraph"]:
            pattern = rf'<meta property="{tag}" content="(.*?)"'
            match = re.search(pattern, content)
            if match:
                analysis["opengraph"][tag] = {"found": True, "value": match.group(1)}
            else:
                analysis["opengraph"][tag] = {"found": False, "value": None}
                analysis["missing"].append(f"og:{tag}")
        
        # Проверка Twitter тегов
        for tag in self.required_seo_elements["twitter"]:
            pattern = rf'<meta name="{tag}" content="(.*?)"'
            match = re.search(pattern, content)
            if match:
                analysis["twitter"][tag] = {"found": True, "value": match.group(1)}
            else:
                analysis["twitter"][tag] = {"found": False, "value": None}
                analysis["missing"].append(f"og:{tag}")
        
        # Проверка JSON-LD схем
        json_ld_pattern = r'<script type="application/ld\+json">(.*?)</script>'
        json_ld_blocks = re.findall(json_ld_pattern, content, re.DOTALL)
        
        for block in json_ld_blocks:
            try:
                data = json.loads(block)
                if "@type" in data:
                    schema_type = data["@type"]
                    analysis["json_ld"][schema_type] = {"found": True, "data": data}
            except json.JSONDecodeError:
                continue
        
        # Подсчет score
        total_elements = len(self.required_seo_elements["meta"]) + len(self.required_seo_elements["opengraph"]) + len(self.required_seo_elements["twitter"])
        found_elements = sum(1 for tag in analysis["meta_tags"].values() if tag["found"])
        found_elements += sum(1 for tag in analysis["opengraph"].values() if tag["found"])
        found_elements += sum(1 for tag in analysis["twitter"].values() if tag["found"])
        
        analysis["score"] = round((found_elements / total_elements) * 100, 1)
        
        return analysis

    def _analyze_llm_optimization(self, content: str) -> Dict:
        """Анализирует LLM-оптимизацию контента"""
        analysis = {
            "faq_blocks": 0,
            "howto_instructions": 0,
            "structured_lists": 0,
            "semantic_headings": 0,
            "content_summaries": 0,
            "local_keywords": 0,
            "score": 0
        }
        
        # Подсчет FAQ блоков
        faq_pattern = r'<(?:article|div)[^>]*class="faq-item"[^>]*>'
        analysis["faq_blocks"] = len(re.findall(faq_pattern, content))
        
        # Подсчет HowTo инструкций
        howto_pattern = r'<ol>|<ul>|<li>'
        analysis["howto_instructions"] = len(re.findall(howto_pattern, content))
        
        # Подсчет структурированных списков
        list_pattern = r'<ul[^>]*>.*?</ul>|<ol[^>]*>.*?</ol>'
        analysis["structured_lists"] = len(re.findall(list_pattern, content, re.DOTALL))
        
        # Подсчет семантических заголовков
        heading_pattern = r'<h[1-6][^>]*>.*?</h[1-6]>'
        analysis["semantic_headings"] = len(re.findall(heading_pattern, content))
        
        # Подсчет контентных выводов
        summary_pattern = r'<p[^>]*>.*?(?:в итоге|в результате|таким образом|итак).*?</p>'
        analysis["content_summaries"] = len(re.findall(summary_pattern, content, re.IGNORECASE))
        
        # Подсчет локальных ключевых слов
        local_keywords = ["салон красоты", "клиника", "фитнес", "образование", "автомойка", "ремонт"]
        analysis["local_keywords"] = sum(1 for keyword in local_keywords if keyword.lower() in content.lower())
        
        # Подсчет score
        max_score = 6
        current_score = sum([
            min(analysis["faq_blocks"], 2),  # Максимум 2 балла за FAQ
            min(analysis["howto_instructions"], 2),  # Максимум 2 балла за инструкции
            min(analysis["structured_lists"], 1),  # Максимум 1 балл за списки
            min(analysis["semantic_headings"], 1)  # Максимум 1 балл за заголовки
        ])
        
        analysis["score"] = round((current_score / max_score) * 100, 1)
        
        return analysis

    def _analyze_content_structure(self, content: str) -> Dict:
        """Анализирует структуру контента"""
        analysis = {
            "h1_count": 0,
            "h2_count": 0,
            "h3_count": 0,
            "paragraphs": 0,
            "images": 0,
            "links": 0,
            "cta_blocks": 0,
            "score": 0
        }
        
        # Подсчет заголовков
        analysis["h1_count"] = len(re.findall(r'<h1[^>]*>', content))
        analysis["h2_count"] = len(re.findall(r'<h2[^>]*>', content))
        analysis["h3_count"] = len(re.findall(r'<h3[^>]*>', content))
        
        # Подсчет параграфов
        analysis["paragraphs"] = len(re.findall(r'<p[^>]*>', content))
        
        # Подсчет изображений
        analysis["images"] = len(re.findall(r'<img[^>]*>', content))
        
        # Подсчет ссылок
        analysis["links"] = len(re.findall(r'<a[^>]*>', content))
        
        # Подсчет CTA блоков
        cta_pattern = r'<a[^>]*class="[^"]*btn[^"]*"[^>]*>'
        analysis["cta_blocks"] = len(re.findall(cta_pattern, content))
        
        # Подсчет score
        score = 0
        if analysis["h1_count"] == 1:  # Должен быть только один H1
            score += 20
        if 4 <= analysis["h2_count"] <= 6:  # Оптимальное количество H2
            score += 20
        if analysis["paragraphs"] >= 10:  # Достаточно контента
            score += 20
        if analysis["cta_blocks"] >= 4:  # Достаточно CTA
            score += 20
        if analysis["images"] > 0:  # Есть изображения
            score += 20
        
        analysis["score"] = score
        
        return analysis

    def _analyze_images(self, content: str) -> Dict:
        """Анализирует изображения и их оптимизацию"""
        analysis = {
            "total_images": 0,
            "with_alt": 0,
            "with_title": 0,
            "optimized": 0,
            "score": 0
        }
        
        # Поиск всех изображений
        img_pattern = r'<img[^>]*>'
        images = re.findall(img_pattern, content)
        analysis["total_images"] = len(images)
        
        if analysis["total_images"] == 0:
            analysis["score"] = 100  # Нет изображений - идеально
            return analysis
        
        for img in images:
            has_alt = 'alt=' in img
            has_title = 'title=' in img
            
            if has_alt:
                analysis["with_alt"] += 1
            if has_title:
                analysis["with_title"] += 1
            if has_alt and has_title:
                analysis["optimized"] += 1
        
        # Подсчет score
        if analysis["total_images"] > 0:
            analysis["score"] = round((analysis["optimized"] / analysis["total_images"]) * 100, 1)
        
        return analysis

    def _generate_recommendations(self, seo_analysis: Dict, llm_analysis: Dict, content_analysis: Dict, image_analysis: Dict) -> List[str]:
        """Генерирует рекомендации по улучшению"""
        recommendations = []
        
        # SEO рекомендации
        if seo_analysis["score"] < 80:
            for missing in seo_analysis["missing"][:5]:  # Максимум 5 рекомендаций
                recommendations.append(f"Добавить недостающий SEO элемент: {missing}")
        
        # LLM рекомендации
        if llm_analysis["score"] < 70:
            if llm_analysis["faq_blocks"] == 0:
                recommendations.append("Добавить FAQ блок с вопросами и ответами")
            if llm_analysis["content_summaries"] == 0:
                recommendations.append("Добавить контентные выводы в конце разделов")
            if llm_analysis["local_keywords"] < 3:
                recommendations.append("Добавить больше локальных ключевых слов")
        
        # Структурные рекомендации
        if content_analysis["score"] < 80:
            if content_analysis["h1_count"] != 1:
                recommendations.append("Должен быть только один H1 заголовок")
            if content_analysis["h2_count"] < 4:
                recommendations.append("Добавить больше H2 заголовков для структурирования")
            if content_analysis["cta_blocks"] < 4:
                recommendations.append("Добавить больше призывов к действию")
        
        # Рекомендации по изображениям
        if image_analysis["score"] < 100:
            recommendations.append("Добавить alt и title теги для изображений")
        
        return recommendations[:8]  # Максимум 8 рекомендаций

    def optimize_article(self, article_path: str) -> Dict:
        """Выполняет дополнительную оптимизацию по правилам"""
        try:
            print(f"🔧 Выполняю дополнительную оптимизацию по правилам: {article_path}")
            
            # Анализируем статью
            analysis = self.analyze_article(article_path)
            if not analysis["success"]:
                return analysis
            
            # Генерируем недостающие элементы
            optimization_result = self._generate_missing_elements(article_path, analysis)
            
            return {
                "success": True,
                "article_path": article_path,
                "analysis": analysis,
                "optimization": optimization_result,
                "elements_generated": optimization_result.get("elements_generated", [])
            }
            
        except Exception as e:
            return {"success": False, "error": f"Ошибка оптимизации: {str(e)}"}

    def _generate_missing_elements(self, article_path: str, analysis: Dict) -> Dict:
        """Генерирует недостающие SEO элементы"""
        try:
            article_file = self.project_root / article_path
            with open(article_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            optimized_content = content
            generated_elements = []
            
            # Генерируем недостающие alt теги для изображений
            if analysis["image_analysis"]["score"] < 100:
                optimized_content, alt_tags_generated = self._generate_alt_tags(optimized_content)
                if alt_tags_generated > 0:
                    generated_elements.append(f"Сгенерировано {alt_tags_generated} alt тегов")
            
            # Генерируем недостающие meta теги
            if analysis["seo_analysis"]["score"] < 100:
                optimized_content, meta_tags_generated = self._generate_missing_meta_tags(optimized_content, analysis)
                if meta_tags_generated > 0:
                    generated_elements.append(f"Сгенерировано {meta_tags_generated} meta тегов")
            
            # Генерируем LLM-оптимизированный контент
            if analysis["llm_analysis"]["score"] < 70:
                optimized_content, llm_elements_generated = self._generate_llm_optimized_content(optimized_content, analysis)
                if llm_elements_generated > 0:
                    generated_elements.append(f"Добавлено {llm_elements_generated} LLM-элементов")
            
            # Сохраняем оптимизированную статью
            backup_path = article_file.with_suffix('.rules.backup.html')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            with open(article_file, 'w', encoding='utf-8') as f:
                f.write(optimized_content)
            
            return {
                "elements_generated": generated_elements,
                "backup_created": str(backup_path),
                "content_optimized": True
            }
            
        except Exception as e:
            return {"error": f"Ошибка генерации элементов: {str(e)}"}

    def _generate_alt_tags(self, content: str) -> Tuple[str, int]:
        """Генерирует alt теги для изображений"""
        img_pattern = r'<img([^>]*?)>'
        generated_count = 0
        
        def replace_img(match):
            nonlocal generated_count
            img_attrs = match.group(1)
            
            # Если уже есть alt, не трогаем
            if 'alt=' in img_attrs:
                return match.group(0)
            
            # Генерируем alt на основе контекста
            alt_text = "SmartVizitka - Бизнес-автопилот с AI"
            new_img = f'<img{img_attrs} alt="{alt_text}">'
            generated_count += 1
            
            return new_img
        
        optimized_content = re.sub(img_pattern, replace_img, content)
        return optimized_content, generated_count

    def _generate_missing_meta_tags(self, content: str, analysis: Dict) -> Tuple[str, int]:
        """Генерирует недостающие meta теги"""
        generated_count = 0
        
        # Добавляем недостающие meta теги
        head_pattern = r'(<head[^>]*>)([\s\S]*?)(</head>)'
        head_match = re.search(head_pattern, content)
        
        if head_match:
            head_open, head_body, head_close = head_match.groups()
            
            # Добавляем keywords если нет
            if not re.search(r'<meta name="keywords"', head_body):
                keywords_meta = '  <meta name="keywords" content="SmartVizitka, CRM бесплатно, бизнес-автопилот, AI, автоматизация" />'
                head_body = head_body + '\n' + keywords_meta
                generated_count += 1
            
            # Добавляем author если нет
            if not re.search(r'<meta name="author"', head_body):
                author_meta = '  <meta name="author" content="SmartVizitka" />'
                head_body = head_body + '\n' + author_meta
                generated_count += 1
            
            # Обновляем head
            content = head_open + head_body + head_close
        
        return content, generated_count

    def _generate_llm_optimized_content(self, content: str, analysis: Dict) -> Tuple[str, int]:
        """Генерирует LLM-оптимизированный контент"""
        generated_count = 0
        
        # Добавляем контентные выводы в конце разделов
        if analysis["llm_analysis"]["content_summaries"] == 0:
            # Ищем конец последнего раздела перед FAQ и добавляем вывод
            faq_pattern = r'(<!-- ============== FAQ SECTION ============== -->)'
            
            def add_summary(match):
                nonlocal generated_count
                summary_html = '''
                <!-- ============== КОНТЕНТНЫЙ ВЫВОД ============== -->
                <section class="content-summary-section">
                  <div class="container">
                    <div class="content-summary" style="background: var(--bg-alt); padding: 32px; border-radius: 20px; margin: 48px 0; text-align: center;">
                      <h2 class="h2">📋 Краткий вывод</h2>
                      <p style="font-size: 18px; line-height: 1.6; margin: 24px 0; color: var(--text);">
                        AI-Ассистент предоставляет полный функционал автоматизации продаж и лидогенерации, позволяя бизнесу работать 24/7 без потери качества обслуживания. Интеграция с популярными платформами и CRM-системами обеспечивает seamless-внедрение в существующие бизнес-процессы.
                      </p>
                      <div style="display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; margin-top: 24px;">
                        <a href="/#trial" class="btn btn-primary">Протестировать бота</a>
                        <a href="/#contact" class="btn btn-ghost">Получить консультацию</a>
                      </div>
                    </div>
                  </div>
                </section>'''
                generated_count += 1
                return summary_html + '\n\n' + match.group(1)
            
            content = re.sub(faq_pattern, add_summary, content, count=1)
        
        return content, generated_count

    def _create_hybrid_report(self, analysis: Dict, gpt_plan: Dict, optimization: Dict) -> str:
        """Создает комплексный отчет по гибридной оптимизации"""
        report = f"""
# 🚀 Отчет по гибридной GEO-оптимизации

## 📊 Анализ статьи
- **SEO Score**: {analysis.get('seo_analysis', {}).get('score', 0)}%
- **LLM Score**: {analysis.get('llm_analysis', {}).get('score', 0)}%
- **Структура Score**: {analysis.get('content_analysis', {}).get('score', 0)}%
- **Изображения Score**: {analysis.get('image_analysis', {}).get('score', 0)}%

## 🤖 GPT-5 план оптимизации
"""
        
        if gpt_plan.get("success"):
            plan_data = gpt_plan.get("data", {})
            report += f"""
- **Приоритет**: {plan_data.get('priority', 'не указан')}
- **Ожидаемый эффект**: {plan_data.get('estimated_impact', 'не указан')}
- **Meta улучшения**: {'Да' if 'meta_improvements' in plan_data else 'Нет'}
- **Контент улучшения**: {'Да' if 'content_improvements' in plan_data else 'Нет'}
- **Технические улучшения**: {'Да' if 'technical_improvements' in plan_data else 'Нет'}
"""
        else:
            report += "- **GPT-5 план**: Не удалось получить\n"
        
        report += f"""
## 🔧 Примененные улучшения
{chr(10).join(f"- {change}" for change in optimization.get('elements_generated', []))}

## 📈 Рекомендации
{chr(10).join(f"- {rec}" for rec in analysis.get('recommendations', []))}

---
*Отчет создан гибридным GEO-агентом AI-Ассистент с GPT-5*
"""
        return report

def main():
    """Основная функция для запуска из командной строки для AI-Ассистент"""
    import sys
    
    agent = GEOHybridAgent()
    
    if len(sys.argv) < 2:
        print("🚀 GEO-гибридный агент оптимизации AI-Ассистент")
        print("🎯 Тематика: AI-ассистенты, чат-боты, автоматизация продаж")
        print("Использование:")
        print("  python3 geo_hybrid_agent.py <путь_к_статье>")
        print("  python3 geo_hybrid_agent.py hybrid <путь_к_статье>")
        return
    
    command = sys.argv[1]
    article_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if command == "hybrid" and article_path:
        print("🚀 Запускаю гибридную оптимизацию...")
        result = agent.run_hybrid_optimization(article_path)
        if result["success"]:
            print(f"✅ {result['summary']}")
        else:
            print(f"❌ Ошибка: {result['error']}")
    
    elif article_path:
        print("🚀 Запускаю гибридную оптимизацию...")
        result = agent.run_hybrid_optimization(article_path)
        if result["success"]:
            print(f"✅ {result['summary']}")
        else:
            print(f"❌ Ошибка: {result['error']}")
    
    else:
        print("❌ Неверные параметры. Используйте: hybrid <путь_к_статье> или просто <путь_к_статье>")

if __name__ == "__main__":
    main()
