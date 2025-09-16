#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Item Parameters Analyzer - Модуль для анализа параметров предметов
"""

import orjson as json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Set
from collections import defaultdict, Counter
import re

class ItemParametersAnalyzer:
    """Класс для анализа параметров предметов и их валидации"""
    
    def __init__(self, server_path: Path):
        self.server_path = server_path
        self.items_file = server_path / "database" / "templates" / "items.json"
        self.items_data = {}
        self.parameter_analysis = {}
        
        # Загрузка данных
        self.load_items()
        self.analyze_parameters()
    
    def load_items(self) -> bool:
        """Загрузка данных предметов"""
        try:
            if not self.items_file.exists():
                print(f"Файл {self.items_file} не найден")
                return False
            
            with open(self.items_file, 'rb') as f:
                self.items_data = json.loads(f.read())
            
            print(f"Загружено {len(self.items_data)} предметов для анализа параметров")
            return True
            
        except Exception as e:
            print(f"Ошибка загрузки файла предметов: {e}")
            self.items_data = {}
            return False
    
    def analyze_parameters(self):
        """Анализ всех параметров предметов"""
        if not self.items_data:
            return
        
        print("Анализ параметров предметов...")
        
        # Счетчики для каждого параметра
        parameter_values = defaultdict(Counter)
        parameter_types = {}
        parameter_locations = defaultdict(set)
        
        # Анализируем каждый предмет
        for item_id, item in self.items_data.items():
            # Анализируем основные поля
            for key, value in item.items():
                if key.startswith('_'):  # Основные поля предмета
                    self._analyze_parameter(key, value, parameter_values, parameter_types, parameter_locations, item_id)
            
            # Анализируем _props
            if '_props' in item and isinstance(item['_props'], dict):
                for prop_key, prop_value in item['_props'].items():
                    self._analyze_parameter(f"_props.{prop_key}", prop_value, parameter_values, parameter_types, parameter_locations, item_id)
            
            # Анализируем locale
            if 'locale' in item and isinstance(item['locale'], dict):
                for locale_key, locale_value in item['locale'].items():
                    self._analyze_parameter(f"locale.{locale_key}", locale_value, parameter_values, parameter_types, parameter_locations, item_id)
        
        # Сохраняем результаты анализа
        self.parameter_analysis = {
            'parameter_values': dict(parameter_values),
            'parameter_types': parameter_types,
            'parameter_locations': {k: list(v) for k, v in parameter_locations.items()}
        }
        
        print(f"Анализ завершен. Найдено {len(parameter_types)} уникальных параметров")
    
    def _analyze_parameter(self, param_name: str, value: Any, parameter_values: Dict, parameter_types: Dict, parameter_locations: Dict, item_id: str):
        """Анализ одного параметра"""
        # Определяем тип значения
        value_type = type(value).__name__
        
        # Обновляем счетчик типов
        if param_name not in parameter_types:
            parameter_types[param_name] = value_type
        elif parameter_types[param_name] != value_type:
            # Если тип изменился, отмечаем как mixed
            parameter_types[param_name] = "mixed"
        
        # Добавляем значение в счетчик
        if isinstance(value, (str, int, float, bool)):
            parameter_values[param_name][str(value)] += 1
        elif isinstance(value, list):
            parameter_values[param_name][f"list[{len(value)}]"] += 1
        elif isinstance(value, dict):
            parameter_values[param_name][f"dict[{len(value)}]"] += 1
        else:
            parameter_values[param_name][str(type(value).__name__)] += 1
        
        # Записываем местоположение параметра
        parameter_locations[param_name].add(item_id)
    
    def get_available_parameters(self) -> List[str]:
        """Получение списка всех доступных параметров"""
        return sorted(self.parameter_analysis.get('parameter_types', {}).keys())
    
    def get_parameter_type(self, parameter: str) -> str:
        """Получение типа параметра"""
        return self.parameter_analysis.get('parameter_types', {}).get(parameter, 'unknown')
    
    def get_parameter_values(self, parameter: str, limit: int = 50) -> List[str]:
        """Получение возможных значений параметра"""
        values = self.parameter_analysis.get('parameter_values', {}).get(parameter, Counter())
        
        # Возвращаем наиболее частые значения
        most_common = values.most_common(limit)
        return [str(value) for value, count in most_common]
    
    def get_parameter_usage_count(self, parameter: str) -> int:
        """Получение количества использований параметра"""
        return len(self.parameter_analysis.get('parameter_locations', {}).get(parameter, []))
    
    def validate_parameter_value(self, parameter: str, value: str) -> tuple[bool, str]:
        """Валидация значения параметра"""
        param_type = self.get_parameter_type(parameter)
        
        if param_type == 'unknown':
            return False, f"Параметр '{parameter}' не найден в базе данных"
        
        try:
            # Преобразуем строку в нужный тип
            if param_type == 'int':
                int(value)
            elif param_type == 'float':
                float(value)
            elif param_type == 'bool':
                if value.lower() not in ['true', 'false', '1', '0', 'yes', 'no']:
                    return False, f"Булево значение должно быть true/false, 1/0, yes/no"
            elif param_type == 'str':
                # Строка всегда валидна
                pass
            elif param_type == 'mixed':
                # Для смешанных типов пробуем разные варианты
                try:
                    int(value)
                except ValueError:
                    try:
                        float(value)
                    except ValueError:
                        if value.lower() not in ['true', 'false', '1', '0', 'yes', 'no']:
                            # Считаем строкой
                            pass
            
            return True, "OK"
            
        except ValueError as e:
            return False, f"Неверный формат значения для типа {param_type}: {str(e)}"
    
    def get_parameter_info(self, parameter: str) -> Dict[str, Any]:
        """Получение подробной информации о параметре"""
        param_type = self.get_parameter_type(parameter)
        values = self.get_parameter_values(parameter, 20)
        usage_count = self.get_parameter_usage_count(parameter)
        
        return {
            'parameter': parameter,
            'type': param_type,
            'usage_count': usage_count,
            'sample_values': values,
            'is_common': usage_count > len(self.items_data) * 0.1  # Используется в >10% предметов
        }
    
    def get_common_parameters(self) -> List[Dict[str, Any]]:
        """Получение наиболее часто используемых параметров"""
        parameters = []
        
        for param in self.get_available_parameters():
            info = self.get_parameter_info(param)
            if info['is_common']:
                parameters.append(info)
        
        # Сортируем по частоте использования
        parameters.sort(key=lambda x: x['usage_count'], reverse=True)
        return parameters
    
    def get_parameter_categories(self) -> Dict[str, List[str]]:
        """Группировка параметров по категориям"""
        categories = {
            'Основные': [],
            'Свойства': [],
            'Локализация': [],
            'Оружие': [],
            'Боеприпасы': [],
            'Броня': [],
            'Контейнеры': [],
            'Прочее': []
        }
        
        for param in self.get_available_parameters():
            if param.startswith('_id') or param.startswith('_name') or param.startswith('_parent') or param.startswith('_type'):
                categories['Основные'].append(param)
            elif param.startswith('_props.'):
                prop_name = param.replace('_props.', '')
                if any(weapon_prop in prop_name.lower() for weapon_prop in ['weap', 'recoil', 'ergonomics', 'durability', 'damage']):
                    categories['Оружие'].append(param)
                elif any(ammo_prop in prop_name.lower() for ammo_prop in ['caliber', 'penetration', 'fragmentation', 'ballistic']):
                    categories['Боеприпасы'].append(param)
                elif any(armor_prop in prop_name.lower() for armor_prop in ['armor', 'class', 'material', 'zone']):
                    categories['Броня'].append(param)
                elif any(container_prop in prop_name.lower() for container_prop in ['grid', 'size', 'width', 'height']):
                    categories['Контейнеры'].append(param)
                else:
                    categories['Свойства'].append(param)
            elif param.startswith('locale.'):
                categories['Локализация'].append(param)
            else:
                categories['Прочее'].append(param)
        
        # Удаляем пустые категории
        return {k: v for k, v in categories.items() if v}
    
    def suggest_parameter_value(self, parameter: str, partial_value: str = "") -> List[str]:
        """Предложение значений для параметра на основе частичного ввода"""
        all_values = self.get_parameter_values(parameter, 100)
        
        if not partial_value:
            return all_values[:10]
        
        partial_lower = partial_value.lower()
        suggestions = []
        
        for value in all_values:
            if partial_lower in value.lower():
                suggestions.append(value)
                if len(suggestions) >= 10:
                    break
        
        return suggestions
    
    def get_parameter_statistics(self) -> Dict[str, Any]:
        """Получение статистики по параметрам"""
        total_parameters = len(self.get_available_parameters())
        common_parameters = len(self.get_common_parameters())
        
        type_counts = Counter(self.parameter_analysis.get('parameter_types', {}).values())
        
        return {
            'total_parameters': total_parameters,
            'common_parameters': common_parameters,
            'type_distribution': dict(type_counts),
            'total_items': len(self.items_data)
        }

def main():
    """Главная функция для тестирования модуля"""
    from pathlib import Path
    
    server_path = Path(__file__).parent.parent
    analyzer = ItemParametersAnalyzer(server_path)
    
    print("🔍 Item Parameters Analyzer")
    print("=" * 50)
    
    # Показываем статистику
    stats = analyzer.get_parameter_statistics()
    print(f"📊 Статистика параметров:")
    print(f"   Всего параметров: {stats['total_parameters']}")
    print(f"   Часто используемых: {stats['common_parameters']}")
    print(f"   Всего предметов: {stats['total_items']}")
    
    print(f"\n📈 Распределение по типам:")
    for param_type, count in stats['type_distribution'].items():
        print(f"   {param_type}: {count}")
    
    # Показываем категории
    print(f"\n📂 Категории параметров:")
    categories = analyzer.get_parameter_categories()
    for category, params in categories.items():
        print(f"   {category}: {len(params)} параметров")
        if len(params) <= 5:  # Показываем все если мало
            for param in params:
                print(f"     - {param}")
        else:  # Показываем первые 5
            for param in params[:5]:
                print(f"     - {param}")
            print(f"     ... и еще {len(params) - 5}")
    
    # Показываем часто используемые параметры
    print(f"\n⭐ Часто используемые параметры:")
    common_params = analyzer.get_common_parameters()[:10]
    for param_info in common_params:
        print(f"   {param_info['parameter']} ({param_info['type']}) - {param_info['usage_count']} использований")
    
    # Тестируем валидацию
    print(f"\n✅ Тест валидации:")
    test_params = ['_props.Weight', '_props.RarityPvE', '_props.Durability']
    test_values = ['1.5', 'Common', '100']
    
    for param, value in zip(test_params, test_values):
        is_valid, message = analyzer.validate_parameter_value(param, value)
        status = "✓" if is_valid else "✗"
        print(f"   {status} {param} = '{value}' -> {message}")

if __name__ == "__main__":
    main()
