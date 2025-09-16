#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logging Integration - Модуль для интеграции логирования во все модули проекта
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import importlib
import inspect

# Импорт системы логирования
try:
    from modules.debug_logger import get_debug_logger, LogCategory, debug, info, warning, error, critical, trace
    from modules.debug_logger import log_function_calls, log_performance
except ImportError:
    # Заглушки
    def get_debug_logger():
        return None
    
    class LogCategory:
        SYSTEM = "SYSTEM"
        UI = "UI"
        DATABASE = "DATABASE"
        FILE_IO = "FILE_IO"
        ERROR = "ERROR"
        PERFORMANCE = "PERFORMANCE"
        CACHE = "CACHE"
        VALIDATION = "VALIDATION"
        PROCESSING = "PROCESSING"
        NETWORK = "NETWORK"
    
    def debug(msg, category=None, **kwargs): pass
    def info(msg, category=None, **kwargs): pass
    def warning(msg, category=None, **kwargs): pass
    def error(msg, category=None, **kwargs): pass
    def critical(msg, category=None, **kwargs): pass
    def trace(msg, category=None, **kwargs): pass
    
    def log_function_calls(category=None):
        def decorator(func):
            return func
        return decorator
    
    def log_performance(category=None):
        def decorator(func):
            return func
        return decorator

class LoggingIntegrator:
    """Класс для интеграции логирования в модули проекта"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.modules_path = project_root / "modules"
        self.logger = get_debug_logger()
        
        info("Инициализация LoggingIntegrator", LogCategory.SYSTEM)
        debug(f"Корневая директория проекта: {project_root}", LogCategory.SYSTEM)
        debug(f"Путь к модулям: {self.modules_path}", LogCategory.SYSTEM)
    
    def add_logging_to_module(self, module_name: str, module_path: Path) -> bool:
        """Добавление логирования в модуль"""
        try:
            info(f"Добавление логирования в модуль: {module_name}", LogCategory.SYSTEM)
            
            # Читаем содержимое файла
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем, есть ли уже логирование
            if "from modules.debug_logger import" in content:
                debug(f"Модуль {module_name} уже содержит логирование", LogCategory.SYSTEM)
                return True
            
            # Определяем категорию логирования для модуля
            category = self._get_module_category(module_name)
            
            # Добавляем импорт логирования
            logging_import = self._get_logging_import(category)
            
            # Находим место для вставки импорта
            lines = content.split('\n')
            insert_index = self._find_import_insertion_point(lines)
            
            # Вставляем импорт
            lines.insert(insert_index, logging_import)
            
            # Записываем обновленный файл
            updated_content = '\n'.join(lines)
            with open(module_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            info(f"Логирование успешно добавлено в модуль: {module_name}", LogCategory.SYSTEM)
            return True
            
        except Exception as e:
            error(f"Ошибка добавления логирования в модуль {module_name}: {e}", 
                  LogCategory.ERROR, exception=e)
            return False
    
    def _get_module_category(self, module_name: str) -> str:
        """Определение категории логирования для модуля"""
        category_map = {
            'items_manager': LogCategory.DATABASE,
            'items_database': LogCategory.DATABASE,
            'items_cache': LogCategory.CACHE,
            'trader_editor': LogCategory.DATABASE,
            'craft_manager': LogCategory.DATABASE,
            'scan_db': LogCategory.DATABASE,
            'ui_utils': LogCategory.UI,
            'hideout_areas': LogCategory.DATABASE,
            'scan_progress_window': LogCategory.UI,
            'context_menus': LogCategory.UI,
            'bulk_parameters_dialog': LogCategory.UI,
            'item_parameters_analyzer': LogCategory.VALIDATION,
            'stp_server_editor': LogCategory.SYSTEM
        }
        
        return category_map.get(module_name, LogCategory.SYSTEM)
    
    def _get_logging_import(self, category: str) -> str:
        """Получение строки импорта логирования"""
        return f'''# Импорт системы отладочного логирования
try:
    from modules.debug_logger import get_debug_logger, LogCategory, debug, info, warning, error, critical, trace
    from modules.debug_logger import log_function_calls, log_performance
except ImportError:
    # Заглушки для случая, если модуль логирования недоступен
    def get_debug_logger():
        return None
    
    class LogCategory:
        SYSTEM = "SYSTEM"
        UI = "UI"
        DATABASE = "DATABASE"
        FILE_IO = "FILE_IO"
        ERROR = "ERROR"
        PERFORMANCE = "PERFORMANCE"
        CACHE = "CACHE"
        VALIDATION = "VALIDATION"
        PROCESSING = "PROCESSING"
        NETWORK = "NETWORK"
    
    def debug(msg, category=None, **kwargs): pass
    def info(msg, category=None, **kwargs): pass
    def warning(msg, category=None, **kwargs): pass
    def error(msg, category=None, **kwargs): pass
    def critical(msg, category=None, **kwargs): pass
    def trace(msg, category=None, **kwargs): pass
    
    def log_function_calls(category=None):
        def decorator(func):
            return func
        return decorator
    
    def log_performance(category=None):
        def decorator(func):
            return func
        return decorator

'''
    
    def _find_import_insertion_point(self, lines: List[str]) -> int:
        """Поиск места для вставки импорта логирования"""
        # Ищем последний импорт
        last_import_index = -1
        for i, line in enumerate(lines):
            if line.strip().startswith(('import ', 'from ')) and not line.strip().startswith('#'):
                last_import_index = i
        
        # Если импорты найдены, вставляем после последнего
        if last_import_index >= 0:
            return last_import_index + 1
        
        # Иначе ищем место после docstring
        for i, line in enumerate(lines):
            if line.strip().startswith('"""') and i > 0:
                # Ищем закрывающую кавычку
                for j in range(i + 1, len(lines)):
                    if '"""' in lines[j]:
                        return j + 1
        
        # По умолчанию вставляем в начало
        return 0
    
    def integrate_all_modules(self) -> Dict[str, bool]:
        """Интеграция логирования во все модули проекта"""
        info("Начало интеграции логирования во все модули", LogCategory.SYSTEM)
        
        results = {}
        
        # Список модулей для интеграции
        modules_to_integrate = [
            'items_database.py',
            'items_cache.py',
            'trader_editor.py',
            'craft_manager.py',
            'scan_db.py',
            'ui_utils.py',
            'hideout_areas.py',
            'scan_progress_window.py',
            'context_menus.py'
        ]
        
        for module_name in modules_to_integrate:
            module_path = self.modules_path / module_name
            if module_path.exists():
                results[module_name] = self.add_logging_to_module(module_name, module_path)
            else:
                warning(f"Модуль не найден: {module_name}", LogCategory.SYSTEM)
                results[module_name] = False
        
        # Статистика
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        info(f"Интеграция завершена: {successful}/{total} модулей успешно", LogCategory.SYSTEM)
        
        return results
    
    def create_logging_utils(self) -> bool:
        """Создание утилит для логирования"""
        try:
            utils_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logging Utils - Утилиты для быстрого доступа к логированию
"""

# Импорт всех функций логирования
from modules.debug_logger import (
    get_debug_logger, LogCategory, debug, info, warning, error, critical, trace,
    log_function_calls, log_performance
)

# Экспорт для удобного импорта
__all__ = [
    'get_debug_logger', 'LogCategory', 'debug', 'info', 'warning', 'error', 'critical', 'trace',
    'log_function_calls', 'log_performance'
]

# Удобные функции для быстрого логирования
def log_module_init(module_name: str):
    """Логирование инициализации модуля"""
    info(f"Инициализация модуля: {module_name}", LogCategory.SYSTEM)

def log_function_entry(func_name: str, category: LogCategory = LogCategory.SYSTEM):
    """Логирование входа в функцию"""
    trace(f"Вход в функцию: {func_name}", category)

def log_function_exit(func_name: str, result: Any = None, category: LogCategory = LogCategory.SYSTEM):
    """Логирование выхода из функции"""
    if result is not None:
        trace(f"Выход из функции: {func_name}, результат: {result}", category)
    else:
        trace(f"Выход из функции: {func_name}", category)

def log_data_operation(operation: str, data_type: str, count: int = None, category: LogCategory = LogCategory.DATABASE):
    """Логирование операций с данными"""
    message = f"Операция с данными: {operation} ({data_type})"
    if count is not None:
        message += f", количество: {count}"
    info(message, category)

def log_ui_action(action: str, component: str = None, category: LogCategory = LogCategory.UI):
    """Логирование действий пользователя в UI"""
    message = f"UI действие: {action}"
    if component:
        message += f" (компонент: {component})"
    info(message, category)

def log_file_operation(operation: str, file_path: str, success: bool = True, category: LogCategory = LogCategory.FILE_IO):
    """Логирование операций с файлами"""
    status = "успешно" if success else "ошибка"
    message = f"Файловая операция: {operation} - {file_path} ({status})"
    
    if success:
        info(message, category)
    else:
        error(message, category)
'''
            
            utils_path = self.modules_path / "logging_utils.py"
            with open(utils_path, 'w', encoding='utf-8') as f:
                f.write(utils_content)
            
            info("Создан модуль logging_utils.py", LogCategory.SYSTEM)
            return True
            
        except Exception as e:
            error(f"Ошибка создания утилит логирования: {e}", LogCategory.ERROR, exception=e)
            return False

def main():
    """Главная функция для интеграции логирования"""
    project_root = Path(__file__).parent.parent
    integrator = LoggingIntegrator(project_root)
    
    # Создаем утилиты
    integrator.create_logging_utils()
    
    # Интегрируем во все модули
    results = integrator.integrate_all_modules()
    
    # Показываем результаты
    print("\nРезультаты интеграции логирования:")
    for module, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {module}")
    
    return results

if __name__ == "__main__":
    main()
