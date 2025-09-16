#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Config Manager - Модуль для работы с конфигурацией
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    def __init__(self, config_file: Path = None):
        if config_file is None:
            config_file = Path(__file__).parent.parent / "config.yaml"
        
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации из файла"""
        if not self.config_file.exists():
            # Возвращаем конфигурацию по умолчанию
            return self.get_default_config()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Ошибка загрузки конфигурации: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Получение конфигурации по умолчанию"""
        return {
            'scanner': {
                'api_base_url': 'https://db.sp-tarkov.com/api/item',
                'request_delay': 0.3,
                'request_timeout': 10.0,
                'max_connections': 10,
                'max_keepalive_connections': 5
            },
            'cache': {
                'cache_lifetime_days': 7,
                'cache_directory': 'cache',
                'items_cache_file': 'items_cache.json',
                'readable_cache_file': 'items_readable.json'
            },
            'ui': {
                'default_window_size': {'width': 800, 'height': 600},
                'min_window_size': {'width': 600, 'height': 400},
                'theme': 'clam',
                'fonts': {
                    'title': ['Arial', 16, 'bold'],
                    'header': ['Arial', 12, 'bold'],
                    'info': ['Arial', 10],
                    'code': ['Consolas', 9]
                }
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(levelname)s - %(message)s',
                'scanner_log_file': 'cache/scan_db.log'
            },
            'performance': {
                'use_orjson': True,
                'use_httpx': True,
                'cache_search_results': True,
                'max_search_results': 1000
            },
            'security': {
                'verify_ssl': True,
                'user_agent': 'SPT-Server-Editor/1.0',
                'max_response_size': 10485760
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получение значения конфигурации по ключу"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Установка значения конфигурации"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_config(self) -> None:
        """Сохранение конфигурации в файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")
    
    def get_scanner_config(self) -> Dict[str, Any]:
        """Получение конфигурации сканера"""
        return self.get('scanner', {})
    
    def get_cache_config(self) -> Dict[str, Any]:
        """Получение конфигурации кэша"""
        return self.get('cache', {})
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Получение конфигурации интерфейса"""
        return self.get('ui', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Получение конфигурации логирования"""
        return self.get('logging', {})
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Получение конфигурации производительности"""
        return self.get('performance', {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """Получение конфигурации безопасности"""
        return self.get('security', {})

def main():
    """Главная функция для тестирования модуля"""
    config = ConfigManager()
    
    print("🔧 Config Manager Test")
    print("=" * 40)
    
    print(f"API URL: {config.get('scanner.api_base_url')}")
    print(f"Request delay: {config.get('scanner.request_delay')}s")
    print(f"Cache lifetime: {config.get('cache.cache_lifetime_days')} days")
    print(f"Window size: {config.get('ui.default_window_size')}")
    print(f"Use orjson: {config.get('performance.use_orjson')}")
    print(f"User agent: {config.get('security.user_agent')}")

if __name__ == "__main__":
    main()
