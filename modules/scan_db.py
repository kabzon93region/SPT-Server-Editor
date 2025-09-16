#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Scanner - Модуль для сбора данных о предметах с онлайн базы SPT-Tarkov
"""

import requests
import orjson as json  # Используем orjson для ускорения JSON операций
import time
import os
import random
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import logging
import httpx  # Используем httpx для улучшения HTTP запросов

class DatabaseScanner:
    def __init__(self, server_path: Path):
        self.server_path = server_path
        self.cache_dir = server_path / "cache"
        self.items_cache_file = self.cache_dir / "items_cache.json"
        self.api_base_url = "https://db.sp-tarkov.com/api/item"
        
        # Переменные для управления сканированием
        self.is_paused = False
        self.is_cancelled = False
        self.progress_callback: Optional[Callable] = None
        self.status_callback: Optional[Callable] = None
        
        # Создание папки кэша
        self.cache_dir.mkdir(exist_ok=True)
        
        # Настройка логирования
        self.setup_logging()
        
        # Загрузка существующего кэша
        self.items_cache = self.load_cache()
        
        # Настройка сессии для запросов (requests для совместимости)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SPT-Server-Editor/1.0',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        
        # Настройка httpx клиента для улучшенных HTTP запросов
        self.httpx_client = httpx.Client(
            headers={
                'User-Agent': 'SPT-Server-Editor/1.0',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9'
            },
            timeout=10.0,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
    
    def setup_logging(self):
        """Настройка логирования"""
        log_file = self.cache_dir / "scan_db.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_cache(self) -> Dict[str, Any]:
        """Загрузка кэша предметов"""
        if self.items_cache_file.exists():
            try:
                with open(self.items_cache_file, 'rb') as f:
                    cache = json.loads(f.read())
                self.logger.info(f"Загружен кэш: {len(cache)} предметов")
                return cache
            except Exception as e:
                self.logger.error(f"Ошибка загрузки кэша: {e}")
                return {}
        return {}
    
    def save_cache(self):
        """Сохранение кэша"""
        try:
            with open(self.items_cache_file, 'wb') as f:
                f.write(json.dumps(self.items_cache, option=json.OPT_INDENT_2))
            self.logger.info(f"Кэш сохранен: {len(self.items_cache)} предметов")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения кэша: {e}")
    
    def get_item_from_api(self, item_id: str, max_retries: int = 10) -> Optional[Dict[str, Any]]:
        """Получение данных предмета с API с повторными попытками"""
        url = f"{self.api_base_url}?id={item_id}&locale=en"
        
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"Запрос к API (попытка {attempt + 1}/{max_retries}): {url}")
                
                # Используем httpx для улучшенной производительности
                response = self.httpx_client.get(url)
                response.raise_for_status()
                
                # Используем orjson для ускорения парсинга JSON
                data = json.loads(response.content)
                
                if 'item' in data and 'locale' in data:
                    # Объединяем данные предмета с локализацией
                    item_data = {
                        'id': item_id,
                        'name': data['item'].get('_name', ''),
                        'parent': data['item'].get('_parent', ''),
                        'type': data['item'].get('_type', ''),
                        'props': data['item'].get('_props', {}),
                        'locale': data['locale'],
                        'handbook': data.get('handbook', {}),
                        'last_updated': int(time.time())
                    }
                    
                    self.logger.info(f"Получены данные предмета: {item_id}")
                    return item_data
                else:
                    self.logger.warning(f"Неполные данные для предмета: {item_id}")
                    return None
                    
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                self.logger.warning(f"Ошибка запроса для предмета {item_id} (попытка {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    # Ждем 3 секунды перед следующей попыткой
                    self.logger.info(f"Повторная попытка через 3 секунды...")
                    time.sleep(3)
                else:
                    self.logger.error(f"Не удалось получить данные для {item_id} после {max_retries} попыток")
                    return None
                    
            except json.JSONDecodeError as e:
                self.logger.error(f"Ошибка парсинга JSON для предмета {item_id}: {e}")
                return None
                
            except Exception as e:
                self.logger.error(f"Неожиданная ошибка для предмета {item_id}: {e}")
                return None
        
        return None
    
    def scan_item(self, item_id: str, force_update: bool = False) -> Optional[Dict[str, Any]]:
        """Сканирование одного предмета"""
        # Проверяем кэш
        if not force_update and item_id in self.items_cache:
            cached_item = self.items_cache[item_id]
            # Проверяем возраст кэша (24 часа)
            if time.time() - cached_item.get('last_updated', 0) < 86400:
                self.logger.debug(f"Используем кэшированные данные для {item_id}")
                return cached_item
        
        # Получаем данные с API
        self.logger.debug(f"Запрос данных с API для {item_id}")
        item_data = self.get_item_from_api(item_id)
        if item_data:
            self.logger.debug(f"Получены данные для {item_id}: {item_data.get('name', 'Unknown')}")
            self.items_cache[item_id] = item_data
            self.save_cache()
            return item_data
        else:
            self.logger.warning(f"Не удалось получить данные для {item_id}")
        
        return None
    
    def scan_items_batch(self, item_ids: List[str], delay_range: tuple = (0.3, 0.8)) -> Dict[str, Any]:
        """Сканирование нескольких предметов с случайной задержкой и поддержкой паузы/отмены"""
        results = {}
        total = len(item_ids)
        
        self.logger.info(f"Начинаем сканирование {total} предметов")
        
        for i, item_id in enumerate(item_ids, 1):
            # Проверяем на отмену
            if self.is_cancelled:
                self.logger.info("Сканирование отменено пользователем")
                break
            
            # Обработка паузы
            while self.is_paused and not self.is_cancelled:
                time.sleep(0.1)
            
            if self.is_cancelled:
                break
            
            # Обновляем прогресс
            if self.progress_callback:
                self.progress_callback(i, total)
            
            if self.status_callback:
                self.status_callback(f"Сканирование {i}/{total}: {item_id}")
            
            self.logger.info(f"Сканирование {i}/{total}: {item_id}")
            
            item_data = self.scan_item(item_id)
            if item_data:
                results[item_id] = item_data
                # Сохраняем в кэш
                self.items_cache[item_id] = item_data
            else:
                self.logger.warning(f"Не удалось получить данные для {item_id}")
            
            # Случайная задержка между запросами
            if i < total and not self.is_cancelled:
                delay = random.uniform(delay_range[0], delay_range[1])
                time.sleep(delay)
        
        if self.is_cancelled:
            self.logger.info(f"Сканирование отменено: {len(results)}/{total} предметов")
        else:
            self.logger.info(f"Сканирование завершено: {len(results)}/{total} предметов")
        
        return results
    
    def get_item_display_name(self, item_id: str) -> str:
        """Получение отображаемого названия предмета"""
        if item_id in self.items_cache:
            item = self.items_cache[item_id]
            # Приоритет: locale.Name > props.Name > _name
            if 'locale' in item and 'Name' in item['locale']:
                return item['locale']['Name']
            elif 'props' in item and 'Name' in item['props']:
                return item['props']['Name']
            elif 'name' in item:
                return item['name']
        
        return f"Unknown Item ({item_id[:8]}...)"
    
    def get_item_short_name(self, item_id: str) -> str:
        """Получение короткого названия предмета"""
        if item_id in self.items_cache:
            item = self.items_cache[item_id]
            # Приоритет: locale.ShortName > props.ShortName
            if 'locale' in item and 'ShortName' in item['locale']:
                return item['locale']['ShortName']
            elif 'props' in item and 'ShortName' in item['props']:
                return item['props']['ShortName']
        
        return f"Unknown ({item_id[:8]}...)"
    
    def get_item_description(self, item_id: str) -> str:
        """Получение описания предмета"""
        if item_id in self.items_cache:
            item = self.items_cache[item_id]
            if 'locale' in item and 'Description' in item['locale']:
                return item['locale']['Description']
            elif 'props' in item and 'Description' in item['props']:
                return item['props']['Description']
        
        return "No description available"
    
    def get_item_price(self, item_id: str) -> int:
        """Получение цены предмета"""
        if item_id in self.items_cache:
            item = self.items_cache[item_id]
            if 'handbook' in item and 'Price' in item['handbook']:
                return item['handbook']['Price']
        
        return 0
    
    def get_item_rarity(self, item_id: str) -> str:
        """Получение редкости предмета"""
        if item_id in self.items_cache:
            item = self.items_cache[item_id]
            if 'props' in item and 'RarityPvE' in item['props']:
                return item['props']['RarityPvE']
        
        return "Unknown"
    
    def extract_item_ids_from_items_file(self) -> List[str]:
        """Извлечение ID предметов из файла items.json"""
        item_ids = set()
        
        try:
            items_file = self.server_path / "database" / "templates" / "items.json"
            if items_file.exists():
                with open(items_file, 'rb') as f:
                    data = json.loads(f.read())
                
                # items.json содержит объект с ключами-ID предметов
                for item_id in data.keys():
                    if item_id and len(item_id) > 10:  # Проверяем что это валидный ID
                        item_ids.add(item_id)
                
                self.logger.info(f"Найдено {len(item_ids)} уникальных ID предметов в items.json")
                return list(item_ids)
            else:
                self.logger.warning("Файл items.json не найден")
                return []
                
        except Exception as e:
            self.logger.error(f"Ошибка при извлечении ID предметов из items.json: {e}")
            return []
    
    def extract_item_ids_from_recipes(self) -> List[str]:
        """Извлечение ID предметов из рецептов крафта"""
        item_ids = set()
        
        try:
            production_file = self.server_path / "database" / "hideout" / "production.json"
            if production_file.exists():
                with open(production_file, 'rb') as f:
                    data = json.loads(f.read())
                
                recipes = data.get('recipes', [])
                for recipe in recipes:
                    # ID конечного продукта
                    end_product = recipe.get('endProduct')
                    if end_product:
                        item_ids.add(end_product)
                    
                    # ID предметов в требованиях
                    requirements = recipe.get('requirements', [])
                    for req in requirements:
                        if req.get('type') == 'Item':
                            template_id = req.get('templateId')
                            if template_id:
                                item_ids.add(template_id)
                        elif req.get('type') == 'Tool':
                            template_id = req.get('templateId')
                            if template_id:
                                item_ids.add(template_id)
                
                self.logger.info(f"Найдено {len(item_ids)} уникальных ID предметов в рецептах")
                return list(item_ids)
            else:
                self.logger.warning("Файл production.json не найден")
                return []
                
        except Exception as e:
            self.logger.error(f"Ошибка при извлечении ID предметов: {e}")
            return []
    
    def remove_duplicates(self):
        """Удаление дублей предметов по ID, сохраняя наиболее полное описание"""
        if not self.items_cache:
            return
        
        original_count = len(self.items_cache)
        duplicates_removed = 0
        
        # Группируем предметы по ID
        items_by_id = {}
        for item_id, item_data in self.items_cache.items():
            if item_id not in items_by_id:
                items_by_id[item_id] = []
            items_by_id[item_id].append(item_data)
        
        # Очищаем кэш
        self.items_cache = {}
        
        # Для каждого ID выбираем наиболее полное описание
        for item_id, items in items_by_id.items():
            if len(items) == 1:
                # Только один предмет с этим ID
                self.items_cache[item_id] = items[0]
            else:
                # Несколько предметов с одинаковым ID - выбираем наиболее полный
                duplicates_removed += len(items) - 1
                
                # Критерии для выбора наиболее полного описания:
                # 1. Наличие locale.Name
                # 2. Наличие handbook.Price
                # 3. Наличие props.RarityPvE
                # 4. Больше всего заполненных полей
                
                best_item = None
                best_score = -1
                
                for item in items:
                    score = 0
                    
                    # Проверяем наличие важных полей
                    if 'locale' in item and 'Name' in item['locale'] and item['locale']['Name']:
                        score += 10
                    if 'handbook' in item and 'Price' in item['handbook'] and item['handbook']['Price'] > 0:
                        score += 8
                    if 'props' in item and 'RarityPvE' in item['props'] and item['props']['RarityPvE']:
                        score += 6
                    if 'locale' in item and 'ShortName' in item['locale'] and item['locale']['ShortName']:
                        score += 4
                    if 'locale' in item and 'Description' in item['locale'] and item['locale']['Description']:
                        score += 3
                    
                    # Подсчитываем общее количество заполненных полей
                    for key, value in item.items():
                        if value and value != "" and value != 0:
                            score += 1
                    
                    if score > best_score:
                        best_score = score
                        best_item = item
                
                self.items_cache[item_id] = best_item
                self.logger.debug(f"Выбран наиболее полный вариант для {item_id} (оценка: {best_score})")
        
        self.logger.info(f"Удалено дублей: {duplicates_removed}, осталось предметов: {len(self.items_cache)}")
        
        # Сохраняем обновленный кэш
        self.save_cache()
    
    def scan_all_items(self, delay_range: tuple = (0.3, 0.8)) -> Dict[str, Any]:
        """Сканирование всех предметов из items.json и рецептов"""
        # Сбрасываем флаги управления
        self.is_paused = False
        self.is_cancelled = False
        
        # Получаем ID из items.json
        items_ids = self.extract_item_ids_from_items_file()
        
        # Получаем ID из рецептов
        recipe_ids = self.extract_item_ids_from_recipes()
        
        # Объединяем все ID
        all_item_ids = list(set(items_ids + recipe_ids))
        
        if not all_item_ids:
            self.logger.warning("Не найдено ID предметов для сканирования")
            return {}
        
        self.logger.info(f"Всего найдено {len(all_item_ids)} уникальных ID предметов")
        
        # Сканируем все предметы
        self.scan_items_batch(all_item_ids, delay_range)
        
        # Удаляем дубли только если сканирование не было отменено
        if not self.is_cancelled:
            self.remove_duplicates()
        
        # Сохраняем кэш
        self.save_cache()
        
        return self.items_cache
    
    def scan_all_recipe_items(self, delay: float = 0.5) -> Dict[str, Any]:
        """Сканирование всех предметов из рецептов (устаревший метод)"""
        item_ids = self.extract_item_ids_from_recipes()
        if not item_ids:
            self.logger.warning("Не найдено ID предметов для сканирования")
            return {}
        
        return self.scan_items_batch(item_ids, delay)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Получение статистики кэша"""
        total_items = len(self.items_cache)
        
        # Подсчет по типам
        types_count = {}
        for item in self.items_cache.values():
            item_type = item.get('type', 'Unknown')
            types_count[item_type] = types_count.get(item_type, 0) + 1
        
        # Подсчет по редкости
        rarity_count = {}
        for item in self.items_cache.values():
            if 'props' in item and 'RarityPvE' in item['props']:
                rarity = item['props']['RarityPvE']
                rarity_count[rarity] = rarity_count.get(rarity, 0) + 1
        
        return {
            'total_items': total_items,
            'types': types_count,
            'rarity': rarity_count,
            'cache_file_size': self.items_cache_file.stat().st_size if self.items_cache_file.exists() else 0
        }
    
    def clear_cache(self):
        """Очистка кэша"""
        self.items_cache = {}
        if self.items_cache_file.exists():
            self.items_cache_file.unlink()
        self.logger.info("Кэш очищен")
    
    def export_cache_to_readable(self, output_file: Optional[Path] = None):
        """Экспорт кэша в читаемый формат"""
        if output_file is None:
            output_file = self.cache_dir / "items_readable.json"
        
        self.logger.info(f"Экспорт кэша в читаемый формат: {len(self.items_cache)} предметов")
        
        readable_data = {}
        for item_id, item in self.items_cache.items():
            readable_data[item_id] = {
                'id': item_id,
                'name': self.get_item_display_name(item_id),
                'short_name': self.get_item_short_name(item_id),
                'description': self.get_item_description(item_id),
                'price': self.get_item_price(item_id),
                'rarity': self.get_item_rarity(item_id),
                'type': item.get('type', 'Unknown'),
                'last_updated': item.get('last_updated', 0)
            }
        
        try:
            # Используем orjson для ускорения записи JSON
            with open(output_file, 'wb') as f:
                f.write(json.dumps(readable_data, option=json.OPT_INDENT_2))
            self.logger.info(f"Кэш экспортирован в {output_file} ({len(readable_data)} предметов)")
        except Exception as e:
            self.logger.error(f"Ошибка экспорта кэша: {e}")
    
    def pause_scanning(self):
        """Приостановка сканирования"""
        self.is_paused = True
        self.logger.info("Сканирование приостановлено")
    
    def resume_scanning(self):
        """Возобновление сканирования"""
        self.is_paused = False
        self.logger.info("Сканирование возобновлено")
    
    def cancel_scanning(self):
        """Отмена сканирования"""
        self.is_cancelled = True
        self.logger.info("Сканирование отменено")
    
    def set_progress_callback(self, callback: Callable):
        """Установка callback для обновления прогресса"""
        self.progress_callback = callback
    
    def set_status_callback(self, callback: Callable):
        """Установка callback для обновления статуса"""
        self.status_callback = callback
    
    def close(self):
        """Закрытие ресурсов"""
        if hasattr(self, 'httpx_client'):
            self.httpx_client.close()
        if hasattr(self, 'session'):
            self.session.close()

def main():
    """Главная функция для тестирования модуля"""
    import sys
    from pathlib import Path
    
    # Определяем путь к серверу
    if len(sys.argv) > 1:
        server_path = Path(sys.argv[1])
    else:
        server_path = Path(__file__).parent.parent
    
    scanner = DatabaseScanner(server_path)
    
    print("🔍 SPT Database Scanner")
    print("=" * 40)
    
    # Показываем статистику кэша
    stats = scanner.get_cache_stats()
    print(f"📊 Статистика кэша:")
    print(f"   Всего предметов: {stats['total_items']}")
    print(f"   Размер файла: {stats['cache_file_size']} байт")
    
    if stats['types']:
        print(f"   Типы предметов:")
        for item_type, count in stats['types'].items():
            print(f"     {item_type}: {count}")
    
    if stats['rarity']:
        print(f"   Редкость предметов:")
        for rarity, count in stats['rarity'].items():
            print(f"     {rarity}: {count}")
    
    print("\n🚀 Начинаем сканирование всех предметов...")
    
    # Сканируем все предметы из items.json и рецептов
    results = scanner.scan_all_items(delay_range=(0.3, 0.8))
    
    print(f"\n✅ Сканирование завершено!")
    print(f"   Обработано: {len(results)} предметов")
    
    # Экспортируем в читаемый формат
    scanner.export_cache_to_readable()
    
    # Показываем примеры
    print(f"\n📋 Примеры найденных предметов:")
    for i, (item_id, item_data) in enumerate(list(results.items())[:5]):
        name = scanner.get_item_display_name(item_id)
        short_name = scanner.get_item_short_name(item_id)
        price = scanner.get_item_price(item_id)
        rarity = scanner.get_item_rarity(item_id)
        print(f"   {i+1}. {name} ({short_name}) - {price}₽ ({rarity})")
    
    # Закрываем ресурсы
    scanner.close()

if __name__ == "__main__":
    main()
