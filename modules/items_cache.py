#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Items Cache - Модуль для работы с кэшем предметов
"""

import orjson as json  # Используем orjson для ускорения JSON операций
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

class ItemsCache:
    def __init__(self, server_path: Path):
        self.server_path = server_path
        self.cache_dir = server_path / "cache"
        self.items_cache_file = self.cache_dir / "items_cache.json"
        self.readable_cache_file = self.cache_dir / "items_readable.json"
        
        # Создание папки кэша
        self.cache_dir.mkdir(exist_ok=True)
        
        # Загрузка кэша
        try:
            self.cache = self.load_cache()
            # Загружаем полный кэш для доступа к данным префабов
            self.full_cache = self.load_full_cache()
        except Exception as e:
            print(f"Ошибка инициализации кэша предметов: {e}")
            self.cache = {}
            self.full_cache = {}
    
    def load_cache(self) -> Dict[str, Any]:
        """Загрузка кэша предметов"""
        # Сначала пробуем загрузить читаемый кэш
        if self.readable_cache_file.exists():
            try:
                with open(self.readable_cache_file, 'rb') as f:
                    return json.loads(f.read())
            except Exception as e:
                print(f"Ошибка загрузки читаемого кэша: {e}")
                pass
        
        # Если не получилось, загружаем полный кэш
        if self.items_cache_file.exists():
            try:
                with open(self.items_cache_file, 'rb') as f:
                    full_cache = json.loads(f.read())
                
                # Конвертируем в читаемый формат
                readable_cache = {}
                for item_id, item in full_cache.items():
                    readable_cache[item_id] = {
                        'id': item_id,
                        'name': self._extract_name(item),
                        'short_name': self._extract_short_name(item),
                        'description': self._extract_description(item),
                        'price': self._extract_price(item),
                        'rarity': self._extract_rarity(item),
                        'type': item.get('type', 'Unknown'),
                        'last_updated': item.get('last_updated', 0)
                    }
                
                return readable_cache
            except Exception:
                pass
        
        return {}
    
    def load_full_cache(self) -> Dict[str, Any]:
        """Загрузка полного кэша предметов"""
        if self.items_cache_file.exists():
            try:
                with open(self.items_cache_file, 'rb') as f:
                    return json.loads(f.read())
            except Exception as e:
                print(f"Ошибка загрузки полного кэша: {e}")
        return {}
    
    def _extract_name(self, item: Dict[str, Any]) -> str:
        """Извлечение названия предмета"""
        # Приоритет: locale.Name -> locale.ShortName -> props.Name -> name
        if 'locale' in item and item['locale']:
            if item['locale'].get('Name'):
                return item['locale']['Name']
            elif item['locale'].get('ShortName'):
                return item['locale']['ShortName']
        
        if 'props' in item and 'Name' in item['props']:
            return item['props']['Name']
        elif 'name' in item:
            return item['name']
        
        return f"Unknown Item ({item.get('id', 'N/A')[:8]}...)"
    
    def _extract_short_name(self, item: Dict[str, Any]) -> str:
        """Извлечение короткого названия предмета"""
        # Приоритет: locale.Name -> locale.ShortName -> props.Name -> props.ShortName -> name
        if 'locale' in item and item['locale']:
            if item['locale'].get('Name'):
                return item['locale']['Name']
            elif item['locale'].get('ShortName'):
                return item['locale']['ShortName']
        
        if 'props' in item:
            if 'Name' in item['props'] and item['props']['Name']:
                return item['props']['Name']
            elif 'ShortName' in item['props'] and item['props']['ShortName']:
                return item['props']['ShortName']
        
        if 'name' in item:
            return item['name']
        
        return f"Unknown ({item.get('id', 'N/A')[:8]}...)"
    
    def _extract_description(self, item: Dict[str, Any]) -> str:
        """Извлечение описания предмета"""
        if 'locale' in item and 'Description' in item['locale']:
            return item['locale']['Description']
        elif 'props' in item and 'Description' in item['props']:
            return item['props']['Description']
        return "No description available"
    
    def _extract_price(self, item: Dict[str, Any]) -> int:
        """Извлечение цены предмета"""
        if 'handbook' in item and 'Price' in item['handbook']:
            return item['handbook']['Price']
        return 0
    
    def _extract_rarity(self, item: Dict[str, Any]) -> str:
        """Извлечение редкости предмета"""
        if 'props' in item and 'RarityPvE' in item['props']:
            return item['props']['RarityPvE']
        return "Unknown"
    
    def get_item_name(self, item_id: str) -> str:
        """Получение названия предмета"""
        # Сначала пробуем читаемый кэш
        if item_id in self.cache:
            name = self.cache[item_id].get('name', f"Unknown Item ({item_id[:8]}...)")
            # Если в читаемом кэше неправильное название, пробуем полный кэш
            if name.startswith('Unknown Item ('):
                if item_id in self.full_cache:
                    return self._extract_name(self.full_cache[item_id])
            return name
        
        # Если нет в читаемом кэше, пробуем полный кэш
        if item_id in self.full_cache:
            return self._extract_name(self.full_cache[item_id])
        
        return f"Unknown Item ({item_id[:8]}...)"
    
    def get_item_short_name(self, item_id: str) -> str:
        """Получение короткого названия предмета"""
        # Сначала пробуем читаемый кэш
        if item_id in self.cache:
            short_name = self.cache[item_id].get('short_name', f"Unknown ({item_id[:8]}...)")
            # Если в читаемом кэше неправильное название, пробуем полный кэш
            if short_name.startswith('Unknown ('):
                if item_id in self.full_cache:
                    return self._extract_short_name(self.full_cache[item_id])
            return short_name
        
        # Если нет в читаемом кэше, пробуем полный кэш
        if item_id in self.full_cache:
            return self._extract_short_name(self.full_cache[item_id])
        
        return f"Unknown ({item_id[:8]}...)"
    
    def get_item_description(self, item_id: str) -> str:
        """Получение описания предмета"""
        if item_id in self.cache:
            return self.cache[item_id].get('description', "No description available")
        return "No description available"
    
    def get_item_price(self, item_id: str) -> int:
        """Получение цены предмета"""
        if item_id in self.cache:
            return self.cache[item_id].get('price', 0)
        return 0
    
    def get_item_rarity(self, item_id: str) -> str:
        """Получение редкости предмета"""
        if item_id in self.cache:
            return self.cache[item_id].get('rarity', "Unknown")
        return "Unknown"
    
    def get_item_type(self, item_id: str) -> str:
        """Получение типа предмета"""
        if item_id in self.cache:
            return self.cache[item_id].get('type', "Unknown")
        return "Unknown"
    
    def get_item_prefab_type(self, item_id: str) -> str:
        """Получение типа префаба предмета"""
        if item_id in self.full_cache:
            item = self.full_cache[item_id]
            if 'props' in item and 'Prefab' in item['props']:
                prefab_path = item['props']['Prefab'].get('path', '')
                if prefab_path:
                    # Убираем "assets/content/" из начала пути
                    if prefab_path.startswith('assets/content/'):
                        return prefab_path[15:]  # Убираем первые 15 символов
                    return prefab_path
        return "Unknown"
    
    def get_item_info(self, item_id: str) -> Dict[str, Any]:
        """Получение полной информации о предмете"""
        if item_id in self.cache:
            return self.cache[item_id].copy()
        
        return {
            'id': item_id,
            'name': f"Unknown Item ({item_id[:8]}...)",
            'short_name': f"Unknown ({item_id[:8]}...)",
            'description': "No description available",
            'price': 0,
            'rarity': "Unknown",
            'type': "Unknown",
            'last_updated': 0
        }
    
    def is_item_cached(self, item_id: str) -> bool:
        """Проверка наличия предмета в кэше"""
        return item_id in self.cache
    
    def get_cached_items_count(self) -> int:
        """Получение количества закэшированных предметов"""
        return len(self.cache)
    
    def search_items(self, query: str) -> List[Dict[str, Any]]:
        """Поиск предметов по запросу"""
        query_lower = query.lower()
        results = []
        
        for item_id, item in self.cache.items():
            name = item.get('name', '').lower()
            short_name = item.get('short_name', '').lower()
            description = item.get('description', '').lower()
            
            if (query_lower in name or 
                query_lower in short_name or 
                query_lower in description or
                query_lower in item_id.lower()):
                results.append(item)
        
        return results
    
    def get_items_by_rarity(self, rarity: str) -> List[Dict[str, Any]]:
        """Получение предметов по редкости"""
        return [item for item in self.cache.values() if item.get('rarity', '').lower() == rarity.lower()]
    
    def get_items_by_type(self, item_type: str) -> List[Dict[str, Any]]:
        """Получение предметов по типу"""
        return [item for item in self.cache.values() if item.get('type', '').lower() == item_type.lower()]
    
    def get_price_range_items(self, min_price: int = 0, max_price: int = None) -> List[Dict[str, Any]]:
        """Получение предметов в диапазоне цен"""
        results = []
        for item in self.cache.values():
            price = item.get('price', 0)
            if price >= min_price and (max_price is None or price <= max_price):
                results.append(item)
        return results
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Получение статистики кэша"""
        total_items = len(self.cache)
        
        # Подсчет по типам
        types_count = {}
        for item in self.cache.values():
            item_type = item.get('type', 'Unknown')
            types_count[item_type] = types_count.get(item_type, 0) + 1
        
        # Подсчет по редкости
        rarity_count = {}
        for item in self.cache.values():
            rarity = item.get('rarity', 'Unknown')
            rarity_count[rarity] = rarity_count.get(rarity, 0) + 1
        
        # Подсчет по ценовым диапазонам
        price_ranges = {
            '0-1000': 0,
            '1000-10000': 0,
            '10000-100000': 0,
            '100000+': 0
        }
        
        for item in self.cache.values():
            price = item.get('price', 0)
            if price < 1000:
                price_ranges['0-1000'] += 1
            elif price < 10000:
                price_ranges['1000-10000'] += 1
            elif price < 100000:
                price_ranges['10000-100000'] += 1
            else:
                price_ranges['100000+'] += 1
        
        return {
            'total_items': total_items,
            'types': types_count,
            'rarity': rarity_count,
            'price_ranges': price_ranges,
            'cache_file_size': self.readable_cache_file.stat().st_size if self.readable_cache_file.exists() else 0
        }
    
    def format_price(self, price: int) -> str:
        """Форматирование цены для отображения"""
        if price >= 1000000:
            return f"{price // 1000000}M ₽"
        elif price >= 1000:
            return f"{price // 1000}K ₽"
        else:
            return f"{price} ₽"
    
    def format_rarity(self, rarity: str) -> str:
        """Форматирование редкости для отображения"""
        rarity_colors = {
            'Common': '🟢',
            'Uncommon': '🔵', 
            'Rare': '🟡',
            'Superrare': '🟠',
            'Legendary': '🔴',
            'Epic': '🟣'
        }
        
        color = rarity_colors.get(rarity, '⚪')
        return f"{color} {rarity}"
    
    def get_display_name(self, item_id: str, show_rarity: bool = False, show_price: bool = False) -> str:
        """Получение отображаемого названия предмета с дополнительной информацией"""
        name = self.get_item_name(item_id)
        
        if show_rarity or show_price:
            parts = [name]
            
            if show_rarity:
                rarity = self.get_item_rarity(item_id)
                parts.append(self.format_rarity(rarity))
            
            if show_price:
                price = self.get_item_price(item_id)
                if price > 0:
                    parts.append(self.format_price(price))
            
            return " | ".join(parts)
        
        return name

def main():
    """Главная функция для тестирования модуля"""
    from pathlib import Path
    
    server_path = Path(__file__).parent.parent
    cache = ItemsCache(server_path)
    
    print("📦 Items Cache Manager")
    print("=" * 40)
    
    # Показываем статистику
    stats = cache.get_cache_stats()
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
    
    if stats['price_ranges']:
        print(f"   Ценовые диапазоны:")
        for range_name, count in stats['price_ranges'].items():
            print(f"     {range_name}: {count}")
    
    # Тестируем поиск
    if stats['total_items'] > 0:
        print(f"\n🔍 Тест поиска:")
        test_queries = ['keycard', 'weapon', 'armor', 'food']
        for query in test_queries:
            results = cache.search_items(query)
            print(f"   '{query}': {len(results)} результатов")
            
            # Показываем первые 3 результата
            for i, item in enumerate(results[:3]):
                name = cache.get_display_name(item['id'], show_rarity=True, show_price=True)
                print(f"     {i+1}. {name}")

if __name__ == "__main__":
    main()
