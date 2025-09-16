#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hideout Areas - Модуль для работы с типами областей убежища
"""

from typing import Dict, Optional

class HideoutAreas:
    """Класс для работы с типами областей убежища"""
    
    # Словарь соответствия номеров областей их названиям
    AREA_TYPES = {
        0: "Вентиляция",
        1: "Безопасность", 
        2: "Санузел",
        3: "Склад",
        4: "Генератор",
        5: "Обогрев",
        6: "Водосборник",
        7: "Медблок",
        8: "Пищеблок",
        9: "Зона отдыха",
        10: "Верстак",
        11: "Разведцентр",
        12: "Тир",
        13: "Библиотека",
        14: "Ящик диких",
        15: "Освещение",
        16: "Уголок боевой славы",
        17: "Воздушный фильтр",
        18: "Солнечная батарея",
        19: "Самогонный аппарат",
        20: "Майнинг ферма",
        21: "Новогодняя елка",
        22: "Стена",
        23: "Тренажерный зал",
        24: "Оружейный стенд",
        25: "Что-то требующее оружейный стенд",
        26: "Стенд для брони",
        27: "Круг сектантов"
    }
    
    @classmethod
    def get_area_name(cls, area_type: int) -> str:
        """Получение названия области по номеру"""
        return cls.AREA_TYPES.get(area_type, f"Неизвестная область ({area_type})")
    
    @classmethod
    def get_area_number(cls, area_name: str) -> Optional[int]:
        """Получение номера области по названию"""
        for number, name in cls.AREA_TYPES.items():
            if name == area_name:
                return number
        return None
    
    @classmethod
    def get_all_areas(cls) -> Dict[int, str]:
        """Получение всех областей"""
        return cls.AREA_TYPES.copy()
    
    @classmethod
    def get_area_list(cls) -> list:
        """Получение списка областей для ComboBox"""
        return [f"{number}: {name}" for number, name in cls.AREA_TYPES.items()]

def main():
    """Главная функция для тестирования модуля"""
    print("🏠 Hideout Areas Test")
    print("=" * 40)
    
    # Тестируем получение названий
    test_areas = [0, 1, 10, 15, 27, 99]
    for area_type in test_areas:
        name = HideoutAreas.get_area_name(area_type)
        print(f"Область {area_type}: {name}")
    
    print("\nВсе области:")
    for number, name in HideoutAreas.get_all_areas().items():
        print(f"  {number}: {name}")

if __name__ == "__main__":
    main()
