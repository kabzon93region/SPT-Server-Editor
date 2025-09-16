#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Items Analyzer - Детальный анализатор параметров предметов из items.json
"""

import orjson as json
from pathlib import Path
from typing import Dict, List, Any, Set, Counter, Tuple
from collections import defaultdict
import re

class ItemsAnalyzer:
    """Детальный анализатор параметров предметов"""
    
    def __init__(self, server_path: Path):
        self.server_path = server_path
        self.items_file = server_path / "database" / "templates" / "items.json"
        self.cache_file = server_path / "modules" / "items_analysis_cache.json"
        
        # Результаты анализа
        self.analysis_results = {}
        
    def analyze_items(self):
        """Основной метод анализа предметов"""
        print("🔍 Начинаем детальный анализ предметов...")
        
        try:
            # Загружаем данные предметов
            items_data = self.load_items_data()
            if not items_data:
                print("❌ Не удалось загрузить данные предметов")
                return None
            
            print(f"📦 Загружено {len(items_data)} предметов")
            
            # Анализируем типы предметов
            print("📊 Анализируем типы предметов...")
            type_analysis = self.analyze_item_types(items_data)
            
            # Анализируем префабы
            print("🎨 Анализируем префабы...")
            prefab_analysis = self.analyze_prefabs(items_data)
            
            # Анализируем параметры детально
            print("⚙️ Анализируем параметры детально...")
            parameters_analysis = self.analyze_parameters_detailed(items_data)
            
            # Анализируем структуру данных
            print("🏗️ Анализируем структуру данных...")
            structure_analysis = self.analyze_data_structure(items_data)
            
            # Собираем результаты
            self.analysis_results = {
                'metadata': {
                    'total_items': len(items_data),
                    'analysis_date': str(Path().cwd()),
                    'items_file': str(self.items_file)
                },
                'types': type_analysis,
                'prefabs': prefab_analysis,
                'parameters': parameters_analysis,
                'structure': structure_analysis
            }
            
            # Сохраняем результаты
            self.save_analysis_results()
            
            print("✅ Анализ завершен успешно!")
            return self.analysis_results
            
        except Exception as e:
            print(f"❌ Ошибка анализа: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def load_items_data(self):
        """Загрузка данных предметов"""
        try:
            if not self.items_file.exists():
                print(f"❌ Файл не найден: {self.items_file}")
                return None
            
            with open(self.items_file, 'rb') as f:
                data = json.loads(f.read())
            
            return data
        except Exception as e:
            print(f"❌ Ошибка загрузки файла: {e}")
            return None
    
    def analyze_item_types(self, items_data):
        """Анализ типов предметов"""
        type_stats = Counter()
        type_parameters = defaultdict(set)
        
        for item_id, item_data in items_data.items():
            # Основной тип предмета
            item_type = item_data.get('_type', 'Unknown')
            type_stats[item_type] += 1
            
            # Собираем параметры для каждого типа
            if '_props' in item_data:
                for param_name in item_data['_props'].keys():
                    type_parameters[item_type].add(param_name)
        
        # Анализируем префабы по типам
        prefab_types = defaultdict(set)
        for item_id, item_data in items_data.items():
            item_type = item_data.get('_type', 'Unknown')
            prefab_path = self.extract_prefab_path(item_data)
            if prefab_path:
                prefab_type = self.extract_prefab_type(prefab_path)
                prefab_types[item_type].add(prefab_type)
        
        return {
            'type_counts': dict(type_stats),
            'type_parameters': {k: list(v) for k, v in type_parameters.items()},
            'prefab_types_by_item_type': {k: list(v) for k, v in prefab_types.items()}
        }
    
    def analyze_prefabs(self, items_data):
        """Анализ префабов предметов"""
        prefab_paths = Counter()
        prefab_categories = defaultdict(Counter)
        prefab_parameters = defaultdict(set)
        
        for item_id, item_data in items_data.items():
            prefab_path = self.extract_prefab_path(item_data)
            if prefab_path:
                prefab_paths[prefab_path] += 1
                
                # Анализируем категории префабов
                category, subcategory = self.analyze_prefab_path(prefab_path)
                prefab_categories[category][subcategory] += 1
                
                # Собираем параметры для каждого префаба
                if '_props' in item_data:
                    for param_name in item_data['_props'].keys():
                        prefab_parameters[prefab_path].add(param_name)
        
        return {
            'prefab_paths': dict(prefab_paths),
            'prefab_categories': {k: dict(v) for k, v in prefab_categories.items()},
            'prefab_parameters': {k: list(v) for k, v in prefab_parameters.items()}
        }
    
    def analyze_parameters_detailed(self, items_data):
        """Детальный анализ параметров предметов"""
        print("  🔍 Собираем все параметры...")
        
        # Собираем все параметры (включая вложенные)
        all_parameters = self.collect_all_parameters(items_data)
        
        print(f"  📊 Найдено {len(all_parameters)} уникальных параметров")
        
        # Анализируем каждый параметр детально
        parameter_details = {}
        total_items = len(items_data)
        
        for param_name in all_parameters:
            print(f"  ⚙️ Анализируем параметр: {param_name}")
            param_info = self.analyze_single_parameter(items_data, param_name, total_items)
            parameter_details[param_name] = param_info
        
        # Группируем параметры по частоте использования
        frequency_groups = self.group_parameters_by_frequency(parameter_details, total_items)
        
        return {
            'parameter_details': parameter_details,
            'frequency_groups': frequency_groups,
            'total_parameters': len(all_parameters),
            'total_items': total_items
        }
    
    def collect_all_parameters(self, items_data):
        """Сбор всех параметров (включая вложенные)"""
        all_params = set()
        
        for item_id, item_data in items_data.items():
            if '_props' in item_data:
                # Основные параметры
                for param_name in item_data['_props'].keys():
                    all_params.add(param_name)
                
                # Вложенные параметры
                for param_name, param_value in item_data['_props'].items():
                    if isinstance(param_value, dict):
                        for nested_param in param_value.keys():
                            all_params.add(f"{param_name}.{nested_param}")
                    elif isinstance(param_value, list):
                        # Анализируем элементы списка
                        for i, item in enumerate(param_value):
                            if isinstance(item, dict):
                                for nested_param in item.keys():
                                    all_params.add(f"{param_name}[{i}].{nested_param}")
        
        return sorted(all_params)
    
    def analyze_single_parameter(self, items_data, param_name, total_items):
        """Детальный анализ одного параметра"""
        usage_stats = {
            'total_usage': 0,
            'usage_by_type': defaultdict(int),
            'usage_by_prefab_category': defaultdict(int),
            'usage_by_prefab_subcategory': defaultdict(int),
            'items_without_param': 0,
            'types_without_param': set(),
            'prefab_categories_without_param': set(),
            'prefab_subcategories_without_param': set(),
            'parameter_types': set(),
            'sample_values': []
        }
        
        # Анализируем использование параметра
        for item_id, item_data in items_data.items():
            item_type = item_data.get('_type', 'Unknown')
            prefab_path = self.extract_prefab_path(item_data)
            category, subcategory = self.analyze_prefab_path(prefab_path) if prefab_path else ('unknown', 'unknown')
            
            # Проверяем наличие параметра
            has_param = self.has_parameter(item_data, param_name)
            
            if has_param:
                usage_stats['total_usage'] += 1
                usage_stats['usage_by_type'][item_type] += 1
                usage_stats['usage_by_prefab_category'][category] += 1
                usage_stats['usage_by_prefab_subcategory'][subcategory] += 1
                
                # Собираем тип параметра и примеры значений
                param_value = self.get_parameter_value(item_data, param_name)
                if param_value is not None:
                    usage_stats['parameter_types'].add(type(param_value).__name__)
                    if len(usage_stats['sample_values']) < 5:
                        usage_stats['sample_values'].append(str(param_value)[:100])
            else:
                usage_stats['items_without_param'] += 1
                usage_stats['types_without_param'].add(item_type)
                usage_stats['prefab_categories_without_param'].add(category)
                usage_stats['prefab_subcategories_without_param'].add(subcategory)
        
        # Конвертируем множества в списки для JSON
        usage_stats['types_without_param'] = list(usage_stats['types_without_param'])
        usage_stats['prefab_categories_without_param'] = list(usage_stats['prefab_categories_without_param'])
        usage_stats['prefab_subcategories_without_param'] = list(usage_stats['prefab_subcategories_without_param'])
        usage_stats['parameter_types'] = list(usage_stats['parameter_types'])
        
        # Конвертируем defaultdict в обычные dict
        usage_stats['usage_by_type'] = dict(usage_stats['usage_by_type'])
        usage_stats['usage_by_prefab_category'] = dict(usage_stats['usage_by_prefab_category'])
        usage_stats['usage_by_prefab_subcategory'] = dict(usage_stats['usage_by_prefab_subcategory'])
        
        return usage_stats
    
    def has_parameter(self, item_data, param_name):
        """Проверка наличия параметра в предмете"""
        if '_props' not in item_data:
            return False
        
        # Простой параметр
        if param_name in item_data['_props']:
            return True
        
        # Вложенный параметр (например, "Prefab.path")
        if '.' in param_name:
            parts = param_name.split('.')
            current = item_data['_props']
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return False
            return True
        
        # Параметр в массиве (например, "Requirements[0]._tpl")
        if '[' in param_name and ']' in param_name:
            param_base = param_name.split('[')[0]
            if param_base in item_data['_props']:
                param_value = item_data['_props'][param_base]
                if isinstance(param_value, list):
                    return True
        
        return False
    
    def get_parameter_value(self, item_data, param_name):
        """Получение значения параметра"""
        if '_props' not in item_data:
            return None
        
        # Простой параметр
        if param_name in item_data['_props']:
            return item_data['_props'][param_name]
        
        # Вложенный параметр
        if '.' in param_name:
            parts = param_name.split('.')
            current = item_data['_props']
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None
            return current
        
        # Параметр в массиве
        if '[' in param_name and ']' in param_name:
            param_base = param_name.split('[')[0]
            if param_base in item_data['_props']:
                param_value = item_data['_props'][param_base]
                if isinstance(param_value, list):
                    return param_value
        
        return None
    
    def group_parameters_by_frequency(self, parameter_details, total_items):
        """Группировка параметров по частоте использования"""
        groups = {
            'universal': [],      # 100% предметов
            'very_common': [],    # 90-99% предметов
            'common': [],         # 70-89% предметов
            'frequent': [],       # 50-69% предметов
            'occasional': [],     # 20-49% предметов
            'rare': [],           # 5-19% предметов
            'very_rare': []       # <5% предметов
        }
        
        for param_name, details in parameter_details.items():
            usage_percent = (details['total_usage'] / total_items) * 100
            
            if usage_percent >= 100:
                groups['universal'].append(param_name)
            elif usage_percent >= 90:
                groups['very_common'].append(param_name)
            elif usage_percent >= 70:
                groups['common'].append(param_name)
            elif usage_percent >= 50:
                groups['frequent'].append(param_name)
            elif usage_percent >= 20:
                groups['occasional'].append(param_name)
            elif usage_percent >= 5:
                groups['rare'].append(param_name)
            else:
                groups['very_rare'].append(param_name)
        
        return groups
    
    def analyze_data_structure(self, items_data):
        """Анализ структуры данных предметов"""
        structure_stats = defaultdict(int)
        required_fields = set()
        optional_fields = set()
        
        for item_id, item_data in items_data.items():
            # Анализируем основные поля
            for field in ['_id', '_name', '_parent', '_type', '_props']:
                if field in item_data:
                    structure_stats[f'has_{field}'] += 1
                    required_fields.add(field)
                else:
                    optional_fields.add(field)
            
            # Анализируем вложенную структуру
            if '_props' in item_data:
                structure_stats['has_props'] += 1
                
                # Анализируем вложенные объекты в _props
                for prop_name, prop_value in item_data['_props'].items():
                    if isinstance(prop_value, dict):
                        structure_stats[f'props_has_dict_{prop_name}'] += 1
                    elif isinstance(prop_value, list):
                        structure_stats[f'props_has_list_{prop_name}'] += 1
        
        return {
            'structure_stats': dict(structure_stats),
            'required_fields': list(required_fields),
            'optional_fields': list(optional_fields)
        }
    
    def extract_prefab_path(self, item_data):
        """Извлечение пути префаба"""
        try:
            props = item_data.get('_props', {})
            prefab = props.get('Prefab', {})
            if isinstance(prefab, dict):
                return prefab.get('path', '')
            return ''
        except:
            return ''
    
    def extract_prefab_type(self, prefab_path):
        """Извлечение типа префаба из пути"""
        try:
            # Разбираем путь: assets/content/category/subcategory/...
            parts = prefab_path.split('/')
            if len(parts) >= 4:
                return f"{parts[2]}/{parts[3]}"
            return 'unknown'
        except:
            return 'unknown'
    
    def analyze_prefab_path(self, prefab_path):
        """Анализ пути префаба"""
        try:
            parts = prefab_path.split('/')
            if len(parts) >= 4:
                return parts[2], parts[3]
            return 'unknown', 'unknown'
        except:
            return 'unknown', 'unknown'
    
    def save_analysis_results(self):
        """Сохранение результатов анализа"""
        try:
            with open(self.cache_file, 'wb') as f:
                f.write(json.dumps(self.analysis_results, option=json.OPT_INDENT_2))
            print(f"💾 Результаты сохранены в {self.cache_file}")
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
    
    def load_analysis_results(self):
        """Загрузка результатов анализа из кэша"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'rb') as f:
                    return json.loads(f.read())
            return None
        except Exception as e:
            print(f"❌ Ошибка загрузки кэша: {e}")
            return None
    
    def print_summary(self):
        """Вывод детальной сводки анализа"""
        if not self.analysis_results:
            print("❌ Нет данных для отображения")
            return
        
        print("\n" + "="*80)
        print("📊 ДЕТАЛЬНАЯ СВОДКА АНАЛИЗА ПРЕДМЕТОВ")
        print("="*80)
        
        # Общая информация
        metadata = self.analysis_results.get('metadata', {})
        print(f"📦 Всего предметов: {metadata.get('total_items', 0)}")
        
        # Типы предметов
        types = self.analysis_results.get('types', {})
        type_counts = types.get('type_counts', {})
        print(f"\n🏷️ Типы предметов ({len(type_counts)}):")
        for item_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {item_type}: {count}")
        
        # Префабы
        prefabs = self.analysis_results.get('prefabs', {})
        prefab_categories = prefabs.get('prefab_categories', {})
        print(f"\n🎨 Категории префабов ({len(prefab_categories)}):")
        for category, subcategories in prefabs.get('prefab_categories', {}).items():
            total = sum(subcategories.values())
            print(f"  {category}: {total} предметов")
            for subcat, count in sorted(subcategories.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"    - {subcat}: {count}")
        
        # Параметры по частоте использования
        parameters = self.analysis_results.get('parameters', {})
        frequency_groups = parameters.get('frequency_groups', {})
        print(f"\n⚙️ Параметры по частоте использования:")
        
        for group_name, group_params in frequency_groups.items():
            if group_params:
                print(f"\n  📊 {group_name.upper().replace('_', ' ')} ({len(group_params)} параметров):")
                for param in group_params[:10]:  # Показываем первые 10
                    param_details = parameters['parameter_details'].get(param, {})
                    usage_percent = (param_details.get('total_usage', 0) / metadata.get('total_items', 1)) * 100
                    print(f"    • {param} ({usage_percent:.1f}% предметов)")
                if len(group_params) > 10:
                    print(f"    ... и еще {len(group_params) - 10} параметров")
        
        # Детальная информация о ключевых параметрах
        print(f"\n🔍 ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О КЛЮЧЕВЫХ ПАРАМЕТРАХ:")
        print("="*80)
        
        # Показываем детали для универсальных параметров
        universal_params = frequency_groups.get('universal', [])
        if universal_params:
            print(f"\n🌐 УНИВЕРСАЛЬНЫЕ ПАРАМЕТРЫ ({len(universal_params)}):")
            for param in universal_params[:5]:  # Показываем первые 5
                self.print_parameter_details(param, parameters['parameter_details'].get(param, {}))
        
        # Показываем детали для очень частых параметров
        very_common_params = frequency_groups.get('very_common', [])
        if very_common_params:
            print(f"\n🔥 ОЧЕНЬ ЧАСТЫЕ ПАРАМЕТРЫ ({len(very_common_params)}):")
            for param in very_common_params[:3]:  # Показываем первые 3
                self.print_parameter_details(param, parameters['parameter_details'].get(param, {}))
    
    def print_parameter_details(self, param_name, param_details):
        """Вывод детальной информации о параметре"""
        if not param_details:
            return
        
        total_usage = param_details.get('total_usage', 0)
        items_without = param_details.get('items_without_param', 0)
        usage_by_type = param_details.get('usage_by_type', {})
        usage_by_category = param_details.get('usage_by_prefab_category', {})
        types_without = param_details.get('types_without_param', [])
        categories_without = param_details.get('prefab_categories_without_param', [])
        param_types = param_details.get('parameter_types', [])
        sample_values = param_details.get('sample_values', [])
        
        print(f"\n  📋 Параметр: {param_name}")
        print(f"    📊 Использование: {total_usage} предметов ({total_usage/(total_usage+items_without)*100:.1f}%)")
        print(f"    ❌ Без параметра: {items_without} предметов")
        print(f"    🏷️ Типы данных: {', '.join(param_types)}")
        
        if usage_by_type:
            print(f"    📈 По типам предметов:")
            for item_type, count in sorted(usage_by_type.items(), key=lambda x: x[1], reverse=True):
                print(f"      • {item_type}: {count}")
        
        if usage_by_category:
            print(f"    🎨 По категориям префабов:")
            for category, count in sorted(usage_by_category.items(), key=lambda x: x[1], reverse=True):
                print(f"      • {category}: {count}")
        
        if types_without:
            print(f"    🚫 Типы БЕЗ параметра: {', '.join(types_without)}")
        
        if categories_without:
            print(f"    🚫 Категории БЕЗ параметра: {', '.join(categories_without)}")
        
        if sample_values:
            print(f"    💡 Примеры значений: {', '.join(sample_values)}")

def main():
    """Главная функция для запуска анализа"""
    import sys
    from pathlib import Path
    
    # Определяем путь к серверу
    if len(sys.argv) > 1:
        server_path = Path(sys.argv[1])
    else:
        server_path = Path(__file__).parent.parent
    
    print(f"🚀 Запуск детального анализа предметов из {server_path}")
    
    # Создаем анализатор
    analyzer = ItemsAnalyzer(server_path)
    
    # Запускаем анализ
    results = analyzer.analyze_items()
    
    if results:
        # Выводим сводку
        analyzer.print_summary()
        
        print(f"\n✅ Анализ завершен! Результаты сохранены в кэш.")
        print(f"📁 Файл кэша: {analyzer.cache_file}")
    else:
        print("❌ Анализ не удался")

if __name__ == "__main__":
    main()