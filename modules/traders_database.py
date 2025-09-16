#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Traders Database - Модуль для работы с базой данных торговцев
"""

import orjson as json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import time

class TradersDatabase:
    """Класс для работы с базой данных торговцев"""
    
    def __init__(self, server_path: Path):
        self.server_path = server_path
        self.trader_config_file = server_path / "configs" / "trader.json"
        self.traders_dir = server_path / "database" / "traders"
        
        # Загрузка данных
        self.trader_config = {}
        self.traders_data = {}
        self.load_trader_config()
        self.load_all_traders()
    
    def load_trader_config(self) -> bool:
        """Загрузка конфигурации торговцев"""
        try:
            if not self.trader_config_file.exists():
                print(f"Файл {self.trader_config_file} не найден")
                return False
            
            with open(self.trader_config_file, 'rb') as f:
                self.trader_config = json.loads(f.read())
            
            print(f"Загружена конфигурация торговцев из {self.trader_config_file}")
            return True
            
        except Exception as e:
            print(f"Ошибка загрузки конфигурации торговцев: {e}")
            self.trader_config = {}
            return False
    
    def load_all_traders(self) -> bool:
        """Загрузка данных всех торговцев"""
        try:
            if not self.traders_dir.exists():
                print(f"Папка {self.traders_dir} не найдена")
                return False
            
            self.traders_data = {}
            
            for trader_dir in self.traders_dir.iterdir():
                if trader_dir.is_dir():
                    trader_id = trader_dir.name
                    trader_data = self.load_trader_data(trader_id)
                    if trader_data:
                        self.traders_data[trader_id] = trader_data
            
            print(f"Загружено {len(self.traders_data)} торговцев")
            return True
            
        except Exception as e:
            print(f"Ошибка загрузки торговцев: {e}")
            self.traders_data = {}
            return False
    
    def load_trader_data(self, trader_id: str) -> Optional[Dict[str, Any]]:
        """Загрузка данных конкретного торговца"""
        try:
            trader_dir = self.traders_dir / trader_id
            trader_data = {}
            
            # Загружаем base.json
            base_file = trader_dir / "base.json"
            if base_file.exists():
                with open(base_file, 'rb') as f:
                    trader_data['base'] = json.loads(f.read())
            
            # Загружаем assort.json
            assort_file = trader_dir / "assort.json"
            if assort_file.exists():
                with open(assort_file, 'rb') as f:
                    trader_data['assort'] = json.loads(f.read())
            
            # Загружаем questassort.json
            questassort_file = trader_dir / "questassort.json"
            if questassort_file.exists():
                with open(questassort_file, 'rb') as f:
                    trader_data['questassort'] = json.loads(f.read())
            
            # Загружаем dialogue.json
            dialogue_file = trader_dir / "dialogue.json"
            if dialogue_file.exists():
                with open(dialogue_file, 'rb') as f:
                    trader_data['dialogue'] = json.loads(f.read())
            
            # Загружаем services.json
            services_file = trader_dir / "services.json"
            if services_file.exists():
                with open(services_file, 'rb') as f:
                    trader_data['services'] = json.loads(f.read())
            
            return trader_data
            
        except Exception as e:
            print(f"Ошибка загрузки торговца {trader_id}: {e}")
            return None
    
    def get_trader_name(self, trader_id: str) -> str:
        """Получение имени торговца по ID"""
        # Словарь соответствия ID и имен
        trader_names = {
            "54cb50c76803fa8b248b4571": "Прапор",
            "54cb57776803fa99248b456e": "Терапевт",
            "579dc571d53a0658a154fbec": "Забор",
            "58330581ace78e27b8b10cee": "Лыжник",
            "5935c25fb3acc3127c3d8cd9": "Миротворец",
            "5a7c2eca46aef81a7ca2145d": "Механик",
            "5ac3b934156ae10c4430e83c": "Рэгмен",
            "5c0647fdd443bc2504c2d371": "Егерь",
            "656f0f98d80a697f855d34b1": "БТР",
            "6617beeaa9cfa777ca915b7c": "Реф",
            "ragfair": "Барахолка"
        }
        
        return trader_names.get(trader_id, f"Неизвестный торговец ({trader_id[:8]}...)")
    
    def get_trader_id_by_name(self, name: str) -> Optional[str]:
        """Получение ID торговца по имени"""
        name_to_id = {
            "Прапор": "54cb50c76803fa8b248b4571",
            "Терапевт": "54cb57776803fa99248b456e",
            "Забор": "579dc571d53a0658a154fbec",
            "Лыжник": "58330581ace78e27b8b10cee",
            "Миротворец": "5935c25fb3acc3127c3d8cd9",
            "Механик": "5a7c2eca46aef81a7ca2145d",
            "Рэгмен": "5ac3b934156ae10c4430e83c",
            "Егерь": "5c0647fdd443bc2504c2d371",
            "БТР": "656f0f98d80a697f855d34b1",
            "Реф": "6617beeaa9cfa777ca915b7c",
            "Барахолка": "ragfair"
        }
        
        return name_to_id.get(name)
    
    def get_trader_base_info(self, trader_id: str) -> Dict[str, Any]:
        """Получение базовой информации о торговце"""
        if trader_id not in self.traders_data:
            return {}
        
        base = self.traders_data[trader_id].get('base', {})
        
        return {
            'id': trader_id,
            'name': self.get_trader_name(trader_id),
            'currency': base.get('currency', 'RUB'),
            'balance_rub': base.get('balance_rub', 0),
            'balance_dol': base.get('balance_dol', 0),
            'balance_eur': base.get('balance_eur', 0),
            'discount': base.get('discount', 0),
            'available_in_raid': base.get('availableInRaid', False),
            'buyer_up': base.get('buyer_up', False),
            'customization_seller': base.get('customization_seller', False),
            'grid_height': base.get('gridHeight', 120)
        }
    
    def get_trader_insurance_info(self, trader_id: str) -> Dict[str, Any]:
        """Получение информации о страховке торговца"""
        if trader_id not in self.traders_data:
            return {}
        
        base = self.traders_data[trader_id].get('base', {})
        insurance = base.get('insurance', {})
        
        return {
            'availability': insurance.get('availability', False),
            'max_return_hour': insurance.get('max_return_hour', 0),
            'max_storage_time': insurance.get('max_storage_time', 0),
            'min_payment': insurance.get('min_payment', 0),
            'min_return_hour': insurance.get('min_return_hour', 0),
            'excluded_category': insurance.get('excluded_category', [])
        }
    
    def get_trader_loyalty_levels(self, trader_id: str) -> Dict[str, Any]:
        """Получение уровней лояльности торговца"""
        if trader_id not in self.traders_data:
            return {}
        
        base = self.traders_data[trader_id].get('base', {})
        loyalty_levels = base.get('loyaltyLevels', {})
        
        return loyalty_levels
    
    def get_trader_assort_count(self, trader_id: str) -> int:
        """Получение количества предметов в ассортименте"""
        if trader_id not in self.traders_data:
            return 0
        
        assort = self.traders_data[trader_id].get('assort', {})
        items = assort.get('items', [])
        
        return len(items)
    
    def get_trader_quest_assort_count(self, trader_id: str) -> int:
        """Получение количества предметов в квестовом ассортименте"""
        if trader_id not in self.traders_data:
            return 0
        
        questassort = self.traders_data[trader_id].get('questassort', {})
        
        total = 0
        for status in ['started', 'success', 'fail']:
            if status in questassort:
                total += len(questassort[status])
        
        return total
    
    def get_trader_services(self, trader_id: str) -> List[str]:
        """Получение списка услуг торговца"""
        if trader_id not in self.traders_data:
            return []
        
        services = self.traders_data[trader_id].get('services', [])
        
        if isinstance(services, list):
            return [service.get('serviceType', '') for service in services if isinstance(service, dict)]
        
        return []
    
    def get_trader_update_time(self, trader_id: str) -> Dict[str, int]:
        """Получение времени обновления торговца"""
        if 'updateTime' not in self.trader_config:
            return {'min': 3600, 'max': 3600}
        
        for trader_update in self.trader_config['updateTime']:
            if trader_update.get('traderId') == trader_id:
                return trader_update.get('seconds', {'min': 3600, 'max': 3600})
        
        return {'min': 3600, 'max': 3600}
    
    def get_all_traders_info(self) -> List[Dict[str, Any]]:
        """Получение информации о всех торговцах"""
        traders_info = []
        
        for trader_id in self.traders_data.keys():
            base_info = self.get_trader_base_info(trader_id)
            base_info['assort_count'] = self.get_trader_assort_count(trader_id)
            base_info['quest_assort_count'] = self.get_trader_quest_assort_count(trader_id)
            base_info['services'] = self.get_trader_services(trader_id)
            base_info['update_time'] = self.get_trader_update_time(trader_id)
            
            traders_info.append(base_info)
        
        return traders_info
    
    def get_trader_config_info(self) -> Dict[str, Any]:
        """Получение информации о конфигурации торговцев"""
        return {
            'update_time_default': self.trader_config.get('updateTimeDefault', 3600),
            'traders_reset_from_server_start': self.trader_config.get('tradersResetFromServerStart', True),
            'purchases_are_found_in_raid': self.trader_config.get('purchasesAreFoundInRaid', False),
            'trader_price_multiplier': self.trader_config.get('traderPriceMultipler', 1.0),
            'fence_settings': self.trader_config.get('fence', {})
        }
    
    def save_trader_base(self, trader_id: str, base_data: Dict[str, Any]) -> bool:
        """Сохранение базовых данных торговца"""
        try:
            if trader_id not in self.traders_data:
                return False
            
            # Создаем резервную копию
            trader_dir = self.traders_dir / trader_id
            base_file = trader_dir / "base.json"
            backup_file = trader_dir / "base.json.backup"
            
            if base_file.exists():
                backup_file.write_bytes(base_file.read_bytes())
            
            # Сохраняем обновленные данные
            with open(base_file, 'wb') as f:
                f.write(json.dumps(base_data, option=json.OPT_INDENT_2))
            
            # Обновляем кэш
            self.traders_data[trader_id]['base'] = base_data
            
            print(f"Базовые данные торговца {trader_id} сохранены")
            return True
            
        except Exception as e:
            print(f"Ошибка сохранения базовых данных торговца {trader_id}: {e}")
            return False
    
    def save_trader_config(self) -> bool:
        """Сохранение конфигурации торговцев"""
        try:
            # Создаем резервную копию
            backup_file = self.trader_config_file.with_suffix('.json.backup')
            if self.trader_config_file.exists():
                backup_file.write_bytes(self.trader_config_file.read_bytes())
            
            # Сохраняем обновленные данные
            with open(self.trader_config_file, 'wb') as f:
                f.write(json.dumps(self.trader_config, option=json.OPT_INDENT_2))
            
            print(f"Конфигурация торговцев сохранена")
            return True
            
        except Exception as e:
            print(f"Ошибка сохранения конфигурации торговцев: {e}")
            return False
    
    def get_trader_statistics(self) -> Dict[str, Any]:
        """Получение статистики торговцев"""
        total_traders = len(self.traders_data)
        
        # Подсчет по валютам
        currencies = {}
        for trader_id in self.traders_data.keys():
            base_info = self.get_trader_base_info(trader_id)
            currency = base_info.get('currency', 'RUB')
            currencies[currency] = currencies.get(currency, 0) + 1
        
        # Подсчет по услугам
        services_count = {}
        for trader_id in self.traders_data.keys():
            services = self.get_trader_services(trader_id)
            for service in services:
                services_count[service] = services_count.get(service, 0) + 1
        
        # Общий ассортимент
        total_assort = sum(self.get_trader_assort_count(trader_id) for trader_id in self.traders_data.keys())
        total_quest_assort = sum(self.get_trader_quest_assort_count(trader_id) for trader_id in self.traders_data.keys())
        
        return {
            'total_traders': total_traders,
            'currencies': currencies,
            'services': services_count,
            'total_assort_items': total_assort,
            'total_quest_assort_items': total_quest_assort,
            'config_file': str(self.trader_config_file),
            'traders_dir': str(self.traders_dir)
        }
    
    def format_currency(self, amount: int, currency: str) -> str:
        """Форматирование валюты для отображения"""
        if currency == "RUB":
            if amount >= 1000000:
                return f"{amount // 1000000}M ₽"
            elif amount >= 1000:
                return f"{amount // 1000}K ₽"
            else:
                return f"{amount} ₽"
        elif currency == "USD":
            if amount >= 1000000:
                return f"${amount // 1000000}M"
            elif amount >= 1000:
                return f"${amount // 1000}K"
            else:
                return f"${amount}"
        elif currency == "EUR":
            if amount >= 1000000:
                return f"€{amount // 1000000}M"
            elif amount >= 1000:
                return f"€{amount // 1000}K"
            else:
                return f"€{amount}"
        else:
            return f"{amount} {currency}"

def main():
    """Главная функция для тестирования модуля"""
    from pathlib import Path
    
    server_path = Path(__file__).parent.parent
    db = TradersDatabase(server_path)
    
    print("🏪 Traders Database Manager")
    print("=" * 40)
    
    # Показываем статистику
    stats = db.get_trader_statistics()
    print(f"📊 Статистика торговцев:")
    print(f"   Всего торговцев: {stats['total_traders']}")
    print(f"   Всего предметов в ассортименте: {stats['total_assort_items']}")
    print(f"   Всего предметов в квестовом ассортименте: {stats['total_quest_assort_items']}")
    
    if stats['currencies']:
        print(f"   Валюты:")
        for currency, count in stats['currencies'].items():
            print(f"     {currency}: {count}")
    
    if stats['services']:
        print(f"   Услуги:")
        for service, count in stats['services'].items():
            print(f"     {service}: {count}")
    
    # Показываем информацию о торговцах
    print(f"\n🏪 Информация о торговцах:")
    traders_info = db.get_all_traders_info()
    for trader in traders_info:
        print(f"   {trader['name']} ({trader['currency']}): {db.format_currency(trader['balance_rub'], 'RUB')} | Ассортимент: {trader['assort_count']} | Квестовый: {trader['quest_assort_count']}")

if __name__ == "__main__":
    main()
