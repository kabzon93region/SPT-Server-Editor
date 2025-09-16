#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
View Detailed Analysis - Просмотр детального анализа параметров предметов
"""

import orjson as json
from pathlib import Path
from typing import Dict, List, Any
import sys

def load_analysis_results(cache_file: Path = None):
    """Загрузка результатов анализа из кэша"""
    if cache_file is None:
        cache_file = Path(__file__).parent / "items_analysis_cache.json"
    
    try:
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                return json.loads(f.read())
        return None
    except Exception as e:
        print(f"❌ Ошибка загрузки кэша: {e}")
        return None

def print_parameter_summary(results: Dict[str, Any]):
    """Вывод сводки по параметрам"""
    if not results:
        print("❌ Нет данных для отображения")
        return
    
    parameters = results.get('parameters', {})
    frequency_groups = parameters.get('frequency_groups', {})
    parameter_details = parameters.get('parameter_details', {})
    metadata = results.get('metadata', {})
    total_items = metadata.get('total_items', 0)
    
    print("\n" + "="*100)
    print("📊 ДЕТАЛЬНАЯ СВОДКА ПАРАМЕТРОВ ПРЕДМЕТОВ")
    print("="*100)
    print(f"📦 Всего предметов: {total_items}")
    print(f"⚙️ Всего параметров: {parameters.get('total_parameters', 0)}")
    
    # Группировка по частоте использования
    print(f"\n📈 ГРУППИРОВКА ПАРАМЕТРОВ ПО ЧАСТОТЕ ИСПОЛЬЗОВАНИЯ:")
    print("-" * 100)
    
    for group_name, group_params in frequency_groups.items():
        if group_params:
            group_name_ru = {
                'universal': '🌐 УНИВЕРСАЛЬНЫЕ (100%)',
                'very_common': '🔥 ОЧЕНЬ ЧАСТЫЕ (90-99%)',
                'common': '📊 ЧАСТЫЕ (70-89%)',
                'frequent': '📈 РАСПРОСТРАНЕННЫЕ (50-69%)',
                'occasional': '🔍 СЛУЧАЙНЫЕ (20-49%)',
                'rare': '⚠️ РЕДКИЕ (5-19%)',
                'very_rare': '💎 ОЧЕНЬ РЕДКИЕ (<5%)'
            }.get(group_name, group_name.upper())
            
            print(f"\n{group_name_ru} ({len(group_params)} параметров):")
            
            # Показываем первые 20 параметров в группе
            for i, param in enumerate(group_params[:20]):
                param_details = parameter_details.get(param, {})
                usage_percent = (param_details.get('total_usage', 0) / total_items) * 100
                usage_count = param_details.get('total_usage', 0)
                without_count = param_details.get('items_without_param', 0)
                
                print(f"  {i+1:2d}. {param:<40} | {usage_percent:5.1f}% ({usage_count:4d}/{total_items}) | Без: {without_count:4d}")
            
            if len(group_params) > 20:
                print(f"  ... и еще {len(group_params) - 20} параметров")

def print_parameter_details(results: Dict[str, Any], param_name: str):
    """Вывод детальной информации о конкретном параметре"""
    if not results:
        print("❌ Нет данных для отображения")
        return
    
    parameters = results.get('parameters', {})
    parameter_details = parameters.get('parameter_details', {})
    metadata = results.get('metadata', {})
    total_items = metadata.get('total_items', 0)
    
    if param_name not in parameter_details:
        print(f"❌ Параметр '{param_name}' не найден в результатах анализа")
        return
    
    details = parameter_details[param_name]
    
    print(f"\n{'='*100}")
    print(f"📋 ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О ПАРАМЕТРЕ: {param_name}")
    print(f"{'='*100}")
    
    # Основная статистика
    total_usage = details.get('total_usage', 0)
    items_without = details.get('items_without_param', 0)
    usage_percent = (total_usage / total_items) * 100
    
    print(f"📊 ОСНОВНАЯ СТАТИСТИКА:")
    print(f"  • Использование: {total_usage:,} предметов ({usage_percent:.1f}%)")
    print(f"  • Без параметра: {items_without:,} предметов ({100-usage_percent:.1f}%)")
    print(f"  • Типы данных: {', '.join(details.get('parameter_types', []))}")
    
    # Использование по типам предметов
    usage_by_type = details.get('usage_by_type', {})
    if usage_by_type:
        print(f"\n📈 ИСПОЛЬЗОВАНИЕ ПО ТИПАМ ПРЕДМЕТОВ:")
        for item_type, count in sorted(usage_by_type.items(), key=lambda x: x[1], reverse=True):
            type_percent = (count / total_items) * 100
            print(f"  • {item_type:<15}: {count:4,} предметов ({type_percent:5.1f}%)")
    
    # Использование по категориям префабов
    usage_by_category = details.get('usage_by_prefab_category', {})
    if usage_by_category:
        print(f"\n🎨 ИСПОЛЬЗОВАНИЕ ПО КАТЕГОРИЯМ ПРЕФАБОВ:")
        for category, count in sorted(usage_by_category.items(), key=lambda x: x[1], reverse=True):
            category_percent = (count / total_items) * 100
            print(f"  • {category:<20}: {count:4,} предметов ({category_percent:5.1f}%)")
    
    # Использование по подкатегориям префабов
    usage_by_subcategory = details.get('usage_by_prefab_subcategory', {})
    if usage_by_subcategory:
        print(f"\n🔍 ИСПОЛЬЗОВАНИЕ ПО ПОДКАТЕГОРИЯМ ПРЕФАБОВ:")
        for subcategory, count in sorted(usage_by_subcategory.items(), key=lambda x: x[1], reverse=True):
            subcategory_percent = (count / total_items) * 100
            print(f"  • {subcategory:<25}: {count:4,} предметов ({subcategory_percent:5.1f}%)")
    
    # Типы предметов БЕЗ параметра
    types_without = details.get('types_without_param', [])
    if types_without:
        print(f"\n🚫 ТИПЫ ПРЕДМЕТОВ БЕЗ ПАРАМЕТРА:")
        for item_type in types_without:
            print(f"  • {item_type}")
    
    # Категории префабов БЕЗ параметра
    categories_without = details.get('prefab_categories_without_param', [])
    if categories_without:
        print(f"\n🚫 КАТЕГОРИИ ПРЕФАБОВ БЕЗ ПАРАМЕТРА:")
        for category in categories_without:
            print(f"  • {category}")
    
    # Подкатегории префабов БЕЗ параметра
    subcategories_without = details.get('prefab_subcategories_without_param', [])
    if subcategories_without:
        print(f"\n🚫 ПОДКАТЕГОРИИ ПРЕФАБОВ БЕЗ ПАРАМЕТРА:")
        for subcategory in subcategories_without:
            print(f"  • {subcategory}")
    
    # Примеры значений
    sample_values = details.get('sample_values', [])
    if sample_values:
        print(f"\n💡 ПРИМЕРЫ ЗНАЧЕНИЙ:")
        for i, value in enumerate(sample_values[:10], 1):
            print(f"  {i:2d}. {value}")
        if len(sample_values) > 10:
            print(f"  ... и еще {len(sample_values) - 10} примеров")

def print_parameter_search(results: Dict[str, Any], search_term: str):
    """Поиск параметров по названию"""
    if not results:
        print("❌ Нет данных для отображения")
        return
    
    parameters = results.get('parameters', {})
    parameter_details = parameters.get('parameter_details', {})
    metadata = results.get('metadata', {})
    total_items = metadata.get('total_items', 0)
    
    # Поиск параметров, содержащих поисковый термин
    matching_params = []
    for param_name in parameter_details.keys():
        if search_term.lower() in param_name.lower():
            matching_params.append(param_name)
    
    if not matching_params:
        print(f"❌ Параметры, содержащие '{search_term}', не найдены")
        return
    
    print(f"\n🔍 НАЙДЕННЫЕ ПАРАМЕТРЫ (содержат '{search_term}'):")
    print("-" * 100)
    
    # Сортируем по частоте использования
    matching_params.sort(key=lambda x: parameter_details[x].get('total_usage', 0), reverse=True)
    
    for i, param_name in enumerate(matching_params, 1):
        details = parameter_details[param_name]
        usage_count = details.get('total_usage', 0)
        usage_percent = (usage_count / total_items) * 100
        
        print(f"{i:2d}. {param_name:<50} | {usage_percent:5.1f}% ({usage_count:4,}/{total_items})")

def print_parameter_statistics(results: Dict[str, Any]):
    """Вывод статистики по параметрам"""
    if not results:
        print("❌ Нет данных для отображения")
        return
    
    parameters = results.get('parameters', {})
    parameter_details = parameters.get('parameter_details', {})
    metadata = results.get('metadata', {})
    total_items = metadata.get('total_items', 0)
    
    print(f"\n📊 СТАТИСТИКА ПО ПАРАМЕТРАМ:")
    print("-" * 100)
    
    # Статистика по типам данных
    type_stats = {}
    for param_name, details in parameter_details.items():
        param_types = details.get('parameter_types', [])
        for param_type in param_types:
            type_stats[param_type] = type_stats.get(param_type, 0) + 1
    
    print(f"\n🏷️ РАСПРЕДЕЛЕНИЕ ПО ТИПАМ ДАННЫХ:")
    for param_type, count in sorted(type_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {param_type:<15}: {count:4,} параметров")
    
    # Статистика по частоте использования
    usage_stats = {
        'universal': 0,      # 100%
        'very_common': 0,    # 90-99%
        'common': 0,         # 70-89%
        'frequent': 0,       # 50-69%
        'occasional': 0,     # 20-49%
        'rare': 0,           # 5-19%
        'very_rare': 0      # <5%
    }
    
    for param_name, details in parameter_details.items():
        usage_percent = (details.get('total_usage', 0) / total_items) * 100
        
        if usage_percent >= 100:
            usage_stats['universal'] += 1
        elif usage_percent >= 90:
            usage_stats['very_common'] += 1
        elif usage_percent >= 70:
            usage_stats['common'] += 1
        elif usage_percent >= 50:
            usage_stats['frequent'] += 1
        elif usage_percent >= 20:
            usage_stats['occasional'] += 1
        elif usage_percent >= 5:
            usage_stats['rare'] += 1
        else:
            usage_stats['very_rare'] += 1
    
    print(f"\n📈 РАСПРЕДЕЛЕНИЕ ПО ЧАСТОТЕ ИСПОЛЬЗОВАНИЯ:")
    for group, count in usage_stats.items():
        group_name = {
            'universal': 'Универсальные (100%)',
            'very_common': 'Очень частые (90-99%)',
            'common': 'Частые (70-89%)',
            'frequent': 'Распространенные (50-69%)',
            'occasional': 'Случайные (20-49%)',
            'rare': 'Редкие (5-19%)',
            'very_rare': 'Очень редкие (<5%)'
        }[group]
        print(f"  • {group_name:<25}: {count:4,} параметров")

def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Просмотр детального анализа параметров предметов')
    parser.add_argument('--cache', type=str, help='Путь к файлу кэша анализа')
    parser.add_argument('--param', type=str, help='Название параметра для детального просмотра')
    parser.add_argument('--search', type=str, help='Поиск параметров по названию')
    parser.add_argument('--stats', action='store_true', help='Показать статистику по параметрам')
    
    args = parser.parse_args()
    
    # Загружаем результаты анализа
    cache_file = Path(args.cache) if args.cache else None
    results = load_analysis_results(cache_file)
    
    if not results:
        print("❌ Не удалось загрузить результаты анализа")
        return
    
    # Выполняем запрошенное действие
    if args.param:
        print_parameter_details(results, args.param)
    elif args.search:
        print_parameter_search(results, args.search)
    elif args.stats:
        print_parameter_statistics(results)
    else:
        print_parameter_summary(results)

if __name__ == "__main__":
    main()