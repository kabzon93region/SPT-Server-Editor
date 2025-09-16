#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Items Database - Модуль для работы с базой данных предметов из items.json
"""

import orjson as json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import time

class ItemsDatabase:
    """Класс для работы с базой данных предметов"""
    
    def __init__(self, server_path: Path):
        self.server_path = server_path
        self.items_file = server_path / "database" / "templates" / "items.json"
        self.items_data = {}
        self.last_modified = 0
        
        # Загрузка данных
        self.load_items()
    
    def load_items(self) -> bool:
        """Загрузка данных предметов из файла"""
        try:
            if not self.items_file.exists():
                print(f"Файл {self.items_file} не найден")
                return False
            
            # Проверяем время модификации файла
            current_modified = self.items_file.stat().st_mtime
            if current_modified == self.last_modified and self.items_data:
                return True  # Файл не изменился, данные уже загружены
            
            with open(self.items_file, 'rb') as f:
                self.items_data = json.loads(f.read())
            
            self.last_modified = current_modified
            print(f"Загружено {len(self.items_data)} предметов из {self.items_file}")
            return True
            
        except Exception as e:
            print(f"Ошибка загрузки файла предметов: {e}")
            self.items_data = {}
            return False
    
    def reload_items(self) -> bool:
        """Принудительная перезагрузка данных предметов"""
        self.items_data = {}
        self.last_modified = 0
        return self.load_items()
    
    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Получение предмета по ID"""
        if not self.items_data:
            self.load_items()
        
        return self.items_data.get(item_id)
    
    def get_item_name(self, item_id: str) -> str:
        """Получение названия предмета"""
        item = self.get_item(item_id)
        if not item:
            return f"Unknown Item ({item_id[:8]}...)"
        
        # Приоритет: locale.Name -> locale.ShortName -> props.Name -> _name
        if 'locale' in item and item['locale']:
            if item['locale'].get('Name'):
                return item['locale']['Name']
            elif item['locale'].get('ShortName'):
                return item['locale']['ShortName']
        
        if 'props' in item and 'Name' in item['props']:
            return item['props']['Name']
        
        return item.get('_name', f"Unknown Item ({item_id[:8]}...)")
    
    def get_item_short_name(self, item_id: str) -> str:
        """Получение короткого названия предмета"""
        item = self.get_item(item_id)
        if not item:
            return f"Unknown ({item_id[:8]}...)"
        
        # Приоритет: locale.Name -> locale.ShortName -> props.Name -> props.ShortName -> _name
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
        
        return item.get('_name', f"Unknown ({item_id[:8]}...)")
    
    def get_item_description(self, item_id: str) -> str:
        """Получение описания предмета"""
        item = self.get_item(item_id)
        if not item:
            return "No description available"
        
        if 'locale' in item and 'Description' in item['locale']:
            return item['locale']['Description']
        elif 'props' in item and 'Description' in item['props']:
            return item['props']['Description']
        
        return "No description available"
    
    def get_item_type(self, item_id: str) -> str:
        """Получение типа предмета"""
        item = self.get_item(item_id)
        if not item:
            return "Unknown"
        
        return item.get('_type', 'Unknown')
    
    def get_item_parent(self, item_id: str) -> str:
        """Получение родительского предмета"""
        item = self.get_item(item_id)
        if not item:
            return ""
        
        return item.get('_parent', '')
    
    def get_item_props(self, item_id: str) -> Dict[str, Any]:
        """Получение свойств предмета"""
        item = self.get_item(item_id)
        if not item:
            return {}
        
        return item.get('_props', {})
    
    def get_item_weight(self, item_id: str) -> float:
        """Получение веса предмета"""
        props = self.get_item_props(item_id)
        return props.get('Weight', 0.0)
    
    def get_item_size(self, item_id: str) -> tuple:
        """Получение размера предмета (ширина, высота)"""
        props = self.get_item_props(item_id)
        width = props.get('Width', 1)
        height = props.get('Height', 1)
        return (width, height)
    
    def get_item_durability(self, item_id: str) -> tuple:
        """Получение прочности предмета (текущая, максимальная)"""
        props = self.get_item_props(item_id)
        durability = props.get('Durability', 100)
        max_durability = props.get('MaxDurability', 100)
        return (durability, max_durability)
    
    def get_item_rarity(self, item_id: str) -> str:
        """Получение редкости предмета"""
        props = self.get_item_props(item_id)
        return props.get('RarityPvE', 'Unknown')
    
    def get_item_price(self, item_id: str) -> int:
        """Получение цены предмета (если есть в handbook)"""
        item = self.get_item(item_id)
        if not item:
            return 0
        
        if 'handbook' in item and 'Price' in item['handbook']:
            return item['handbook']['Price']
        
        return 0
    
    def get_item_prefab_path(self, item_id: str) -> str:
        """Получение пути к префабу предмета"""
        props = self.get_item_props(item_id)
        prefab = props.get('Prefab', {})
        return prefab.get('path', '')
    
    def get_item_prefab_type(self, item_id: str) -> str:
        """Получение типа префаба предмета (упрощенный путь)"""
        prefab_path = self.get_item_prefab_path(item_id)
        if prefab_path:
            # Убираем "assets/content/" из начала пути
            if prefab_path.startswith('assets/content/'):
                return prefab_path[15:]  # Убираем первые 15 символов
            return prefab_path
        return "Unknown"
    
    def is_weapon(self, item_id: str) -> bool:
        """Проверка, является ли предмет оружием"""
        return self.get_item_type(item_id) == "Weapon"
    
    def is_ammo(self, item_id: str) -> bool:
        """Проверка, является ли предмет боеприпасом"""
        return self.get_item_type(item_id) == "Ammo"
    
    def is_armor(self, item_id: str) -> bool:
        """Проверка, является ли предмет броней"""
        return self.get_item_type(item_id) == "Armor"
    
    def is_key(self, item_id: str) -> bool:
        """Проверка, является ли предмет ключом"""
        return self.get_item_type(item_id) == "Key"
    
    def is_container(self, item_id: str) -> bool:
        """Проверка, является ли предмет контейнером"""
        return self.get_item_type(item_id) == "Container"
    
    def is_mod(self, item_id: str) -> bool:
        """Проверка, является ли предмет модификацией"""
        return self.get_item_type(item_id) == "Mod"
    
    def get_weapon_props(self, item_id: str) -> Dict[str, Any]:
        """Получение свойств оружия"""
        if not self.is_weapon(item_id):
            return {}
        
        props = self.get_item_props(item_id)
        weapon_props = {}
        
        # Основные свойства оружия
        weapon_keys = [
            'weapClass', 'weapFireType', 'weapUseType', 'Durability', 'MaxDurability',
            'Ergonomics', 'RecoilForceBack', 'RecoilForceUp', 'AimSensitivity',
            'IronSightRange', 'EffectiveDistance', 'DurabilityBurnRatio',
            'Foldable', 'FoldedSlot', 'ReloadMode', 'BoltAction', 'BurstShotsCount'
        ]
        
        for key in weapon_keys:
            if key in props:
                weapon_props[key] = props[key]
        
        return weapon_props
    
    def get_ammo_props(self, item_id: str) -> Dict[str, Any]:
        """Получение свойств боеприпаса"""
        if not self.is_ammo(item_id):
            return {}
        
        props = self.get_item_props(item_id)
        ammo_props = {}
        
        # Основные свойства боеприпасов
        ammo_keys = [
            'Caliber', 'Damage', 'ArmorDamage', 'PenetrationPower', 'FragmentationChance',
            'InitialSpeed', 'BallisticCoeficient', 'BulletMassGram', 'BulletDiameterMilimeters',
            'ProjectileCount', 'MalfFeedChance', 'MalfMisfireChance', 'MisfireChance'
        ]
        
        for key in ammo_keys:
            if key in props:
                ammo_props[key] = props[key]
        
        return ammo_props
    
    def get_armor_props(self, item_id: str) -> Dict[str, Any]:
        """Получение свойств брони"""
        if not self.is_armor(item_id):
            return {}
        
        props = self.get_item_props(item_id)
        armor_props = {}
        
        # Основные свойства брони
        armor_keys = [
            'ArmorClass', 'ArmorMaterial', 'ArmorZone', 'DurabilityBurnModificator',
            'Durability', 'MaxDurability', 'Ergonomics', 'Weight'
        ]
        
        for key in armor_keys:
            if key in props:
                armor_props[key] = props[key]
        
        return armor_props
    
    def search_items(self, query: str, search_in: List[str] = None) -> List[Dict[str, Any]]:
        """Поиск предметов по запросу"""
        if not self.items_data:
            return []
        
        if search_in is None:
            search_in = ['name', 'short_name', 'description', 'id']
        
        query_lower = query.lower()
        results = []
        
        for item_id, item in self.items_data.items():
            match_found = False
            
            # Поиск в названиях
            if 'name' in search_in:
                name = self.get_item_name(item_id).lower()
                if query_lower in name:
                    match_found = True
            
            if 'short_name' in search_in and not match_found:
                short_name = self.get_item_short_name(item_id).lower()
                if query_lower in short_name:
                    match_found = True
            
            # Поиск в описании
            if 'description' in search_in and not match_found:
                description = self.get_item_description(item_id).lower()
                if query_lower in description:
                    match_found = True
            
            # Поиск по ID
            if 'id' in search_in and not match_found:
                if query_lower in item_id.lower():
                    match_found = True
            
            if match_found:
                results.append({
                    'id': item_id,
                    'name': self.get_item_name(item_id),
                    'short_name': self.get_item_short_name(item_id),
                    'type': self.get_item_type(item_id),
                    'rarity': self.get_item_rarity(item_id),
                    'price': self.get_item_price(item_id)
                })
        
        return results
    
    def get_items_by_type(self, item_type: str) -> List[Dict[str, Any]]:
        """Получение предметов по типу"""
        if not self.items_data:
            return []
        
        results = []
        for item_id, item in self.items_data.items():
            if item.get('_type', '').lower() == item_type.lower():
                results.append({
                    'id': item_id,
                    'name': self.get_item_name(item_id),
                    'short_name': self.get_item_short_name(item_id),
                    'type': self.get_item_type(item_id),
                    'rarity': self.get_item_rarity(item_id),
                    'price': self.get_item_price(item_id)
                })
        
        return results
    
    def get_items_by_rarity(self, rarity: str) -> List[Dict[str, Any]]:
        """Получение предметов по редкости"""
        if not self.items_data:
            return []
        
        results = []
        for item_id, item in self.items_data.items():
            props = item.get('_props', {})
            if props.get('RarityPvE', '').lower() == rarity.lower():
                results.append({
                    'id': item_id,
                    'name': self.get_item_name(item_id),
                    'short_name': self.get_item_short_name(item_id),
                    'type': self.get_item_type(item_id),
                    'rarity': self.get_item_rarity(item_id),
                    'price': self.get_item_price(item_id)
                })
        
        return results
    
    def get_items_by_caliber(self, caliber: str) -> List[Dict[str, Any]]:
        """Получение боеприпасов по калибру"""
        if not self.items_data:
            return []
        
        results = []
        for item_id, item in self.items_data.items():
            props = item.get('_props', {})
            if props.get('Caliber', '').lower() == caliber.lower():
                results.append({
                    'id': item_id,
                    'name': self.get_item_name(item_id),
                    'short_name': self.get_item_short_name(item_id),
                    'type': self.get_item_type(item_id),
                    'rarity': self.get_item_rarity(item_id),
                    'price': self.get_item_price(item_id),
                    'caliber': props.get('Caliber', '')
                })
        
        return results
    
    def get_items_by_weapon_class(self, weapon_class: str) -> List[Dict[str, Any]]:
        """Получение оружия по классу"""
        if not self.items_data:
            return []
        
        results = []
        for item_id, item in self.items_data.items():
            props = item.get('_props', {})
            if props.get('weapClass', '').lower() == weapon_class.lower():
                results.append({
                    'id': item_id,
                    'name': self.get_item_name(item_id),
                    'short_name': self.get_item_short_name(item_id),
                    'type': self.get_item_type(item_id),
                    'rarity': self.get_item_rarity(item_id),
                    'price': self.get_item_price(item_id),
                    'weapon_class': props.get('weapClass', '')
                })
        
        return results
    
    def get_all_calibers(self) -> List[str]:
        """Получение всех калибров боеприпасов"""
        if not self.items_data:
            return []
        
        calibers = set()
        for item_id, item in self.items_data.items():
            props = item.get('_props', {})
            caliber = props.get('Caliber', '')
            if caliber:
                calibers.add(caliber)
        
        return sorted(list(calibers))
    
    def get_all_weapon_classes(self) -> List[str]:
        """Получение всех классов оружия"""
        if not self.items_data:
            return []
        
        classes = set()
        for item_id, item in self.items_data.items():
            props = item.get('_props', {})
            weapon_class = props.get('weapClass', '')
            if weapon_class:
                classes.add(weapon_class)
        
        return sorted(list(classes))
    
    def get_all_item_types(self) -> List[str]:
        """Получение всех типов предметов"""
        if not self.items_data:
            return []
        
        types = set()
        for item_id, item in self.items_data.items():
            item_type = item.get('_type', '')
            if item_type:
                types.add(item_type)
        
        return sorted(list(types))
    
    def get_all_rarities(self) -> List[str]:
        """Получение всех редкостей предметов"""
        if not self.items_data:
            return []
        
        rarities = set()
        for item_id, item in self.items_data.items():
            props = item.get('_props', {})
            rarity = props.get('RarityPvE', '')
            if rarity:
                rarities.add(rarity)
        
        return sorted(list(rarities))
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Получение статистики базы данных"""
        if not self.items_data:
            return {'total_items': 0}
        
        total_items = len(self.items_data)
        
        # Подсчет по типам
        types_count = {}
        for item in self.items_data.values():
            item_type = item.get('_type', 'Unknown')
            types_count[item_type] = types_count.get(item_type, 0) + 1
        
        # Подсчет по редкости
        rarity_count = {}
        for item in self.items_data.values():
            props = item.get('_props', {})
            rarity = props.get('RarityPvE', 'Unknown')
            rarity_count[rarity] = rarity_count.get(rarity, 0) + 1
        
        # Подсчет оружия по классам
        weapon_classes = {}
        for item in self.items_data.values():
            props = item.get('_props', {})
            weapon_class = props.get('weapClass', '')
            if weapon_class:
                weapon_classes[weapon_class] = weapon_classes.get(weapon_class, 0) + 1
        
        # Подсчет боеприпасов по калибрам
        calibers = {}
        for item in self.items_data.values():
            props = item.get('_props', {})
            caliber = props.get('Caliber', '')
            if caliber:
                calibers[caliber] = calibers.get(caliber, 0) + 1
        
        return {
            'total_items': total_items,
            'types': types_count,
            'rarity': rarity_count,
            'weapon_classes': weapon_classes,
            'calibers': calibers,
            'file_path': str(self.items_file),
            'last_modified': self.last_modified
        }
    
    def save_item(self, item_id: str, item_data: Dict[str, Any]) -> bool:
        """Сохранение предмета в базу данных"""
        try:
            if not self.items_data:
                self.load_items()
            
            # Обновляем данные предмета в памяти
            self.items_data[item_id] = item_data
            
            # Создаем резервную копию
            backup_file = self.items_file.with_suffix('.json.backup')
            if self.items_file.exists():
                backup_file.write_bytes(self.items_file.read_bytes())
            
            # Сохраняем ВСЮ базу данных в файл
            with open(self.items_file, 'wb') as f:
                f.write(json.dumps(self.items_data, option=json.OPT_INDENT_2))
            
            # Обновляем время модификации
            self.last_modified = self.items_file.stat().st_mtime
            
            print(f"Предмет {item_id} сохранен в базу данных")
            return True
            
        except Exception as e:
            print(f"Ошибка сохранения предмета {item_id}: {e}")
            return False
    
    def save_item_incremental(self, item_id: str, changes: Dict[str, Any]) -> bool:
        """Инкрементальное сохранение только измененных параметров предмета"""
        try:
            if not self.items_data:
                self.load_items()
            
            if item_id not in self.items_data:
                print(f"Предмет {item_id} не найден в базе данных")
                return False
            
            # Применяем изменения к существующему предмету
            current_item = self.items_data[item_id]
            
            # Обновляем основные параметры
            for key, value in changes.items():
                if key != '_props':
                    current_item[key] = value
            
            # Обновляем _props если есть изменения
            if '_props' in changes:
                if '_props' not in current_item:
                    current_item['_props'] = {}
                
                props_changes = changes['_props']
                for prop_key, prop_value in props_changes.items():
                    current_item['_props'][prop_key] = prop_value
            
            # Создаем резервную копию
            backup_file = self.items_file.with_suffix('.json.backup')
            if self.items_file.exists():
                backup_file.write_bytes(self.items_file.read_bytes())
            
            # Сохраняем ВСЮ базу данных в файл
            with open(self.items_file, 'wb') as f:
                f.write(json.dumps(self.items_data, option=json.OPT_INDENT_2))
            
            # Обновляем время модификации
            self.last_modified = self.items_file.stat().st_mtime
            
            print(f"Инкрементальные изменения для предмета {item_id} сохранены")
            return True
            
        except Exception as e:
            print(f"Ошибка инкрементального сохранения предмета {item_id}: {e}")
            return False
    
    def save_database(self) -> bool:
        """Сохранение всей базы данных в файл"""
        try:
            if not self.items_data:
                print("Нет данных для сохранения")
                return False
            
            # Создаем резервную копию
            backup_file = self.items_file.with_suffix('.json.backup')
            if self.items_file.exists():
                backup_file.write_bytes(self.items_file.read_bytes())
            
            # Сохраняем всю базу данных
            with open(self.items_file, 'wb') as f:
                f.write(json.dumps(self.items_data, option=json.OPT_INDENT_2))
            
            # Обновляем время модификации
            self.last_modified = self.items_file.stat().st_mtime
            
            print(f"База данных сохранена: {len(self.items_data)} предметов")
            return True
            
        except Exception as e:
            print(f"Ошибка сохранения базы данных: {e}")
            return False
    
    def delete_item(self, item_id: str) -> bool:
        """Удаление предмета из базы данных"""
        try:
            if not self.items_data:
                self.load_items()
            
            if item_id not in self.items_data:
                print(f"Предмет {item_id} не найден в базе данных")
                return False
            
            # Создаем резервную копию
            backup_file = self.items_file.with_suffix('.json.backup')
            if self.items_file.exists():
                backup_file.write_bytes(self.items_file.read_bytes())
            
            # Удаляем предмет
            del self.items_data[item_id]
            
            # Сохраняем обновленные данные
            with open(self.items_file, 'wb') as f:
                f.write(json.dumps(self.items_data, option=json.OPT_INDENT_2))
            
            # Обновляем время модификации
            self.last_modified = self.items_file.stat().st_mtime
            
            print(f"Предмет {item_id} удален из базы данных")
            return True
            
        except Exception as e:
            print(f"Ошибка удаления предмета {item_id}: {e}")
            return False
    
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
    db = ItemsDatabase(server_path)
    
    print("🗄️ Items Database Manager")
    print("=" * 40)
    
    # Показываем статистику
    stats = db.get_database_stats()
    print(f"📊 Статистика базы данных:")
    print(f"   Всего предметов: {stats['total_items']}")
    print(f"   Файл: {stats['file_path']}")
    
    if stats['types']:
        print(f"   Типы предметов:")
        for item_type, count in stats['types'].items():
            print(f"     {item_type}: {count}")
    
    if stats['rarity']:
        print(f"   Редкость предметов:")
        for rarity, count in stats['rarity'].items():
            print(f"     {rarity}: {count}")
    
    if stats['weapon_classes']:
        print(f"   Классы оружия:")
        for weapon_class, count in stats['weapon_classes'].items():
            print(f"     {weapon_class}: {count}")
    
    if stats['calibers']:
        print(f"   Калибры боеприпасов:")
        for caliber, count in stats['calibers'].items():
            print(f"     {caliber}: {count}")
    
    # Тестируем поиск
    if stats['total_items'] > 0:
        print(f"\n🔍 Тест поиска:")
        test_queries = ['keycard', 'weapon', 'armor', 'food']
        for query in test_queries:
            results = db.search_items(query)
            print(f"   '{query}': {len(results)} результатов")
            
            # Показываем первые 3 результата
            for i, item in enumerate(results[:3]):
                name = db.get_display_name(item['id'], show_rarity=True, show_price=True)
                print(f"     {i+1}. {name}")
    
    # Тестируем получение конкретного предмета
    if stats['total_items'] > 0:
        print(f"\n🔍 Тест получения предмета:")
        first_item_id = list(db.items_data.keys())[0]
        item_name = db.get_item_name(first_item_id)
        item_type = db.get_item_type(first_item_id)
        item_rarity = db.get_item_rarity(first_item_id)
        print(f"   Первый предмет: {item_name} ({item_type}, {item_rarity})")

if __name__ == "__main__":
    main()
