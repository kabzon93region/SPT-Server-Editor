# Руководство разработчика SPT Server Editor

## Содержание
1. [Введение](#введение)
2. [Настройка окружения разработки](#настройка-окружения-разработки)
3. [Архитектура и принципы](#архитектура-и-принципы)
4. [Стандарты кодирования](#стандарты-кодирования)
5. [Создание новых модулей](#создание-новых-модулей)
6. [Тестирование](#тестирование)
7. [Отладка и профилирование](#отладка-и-профилирование)
8. [Документирование](#документирование)
9. [Контрибьюция](#контрибьюция)
10. [Развертывание](#развертывание)

---

## Введение

SPT Server Editor - это Python-приложение для редактирования серверных файлов Escape from Tarkov. Данное руководство предназначено для разработчиков, желающих внести свой вклад в проект или создать форк.

### Цели проекта:
- Предоставить удобный интерфейс для редактирования игровых данных
- Обеспечить безопасность и стабильность операций
- Поддерживать расширяемость и модульность
- Обеспечить высокую производительность

---

## Настройка окружения разработки

### Системные требования:
- **ОС**: Windows 10/11 (рекомендуется), Linux, macOS
- **Python**: 3.8 или выше
- **RAM**: 4 GB (минимум), 8 GB (рекомендуется)
- **Диск**: 1 GB свободного места

### Установка Python:
```bash
# Windows (через Chocolatey)
choco install python

# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install python3 python3-pip python3-venv

# macOS (через Homebrew)
brew install python
```

### Настройка виртуального окружения:
```bash
# Создание виртуального окружения
python -m venv venv

# Активация (Windows)
venv\Scripts\activate

# Активация (Linux/macOS)
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### Настройка IDE:
#### Visual Studio Code:
```json
{
    "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true
}
```

#### PyCharm:
1. Открыть проект
2. Настроить интерпретатор Python (venv)
3. Включить линтеры (pylint, flake8)
4. Настроить форматирование (black)

### Установка инструментов разработки:
```bash
# Линтеры и форматтеры
pip install black flake8 pylint isort

# Тестирование
pip install pytest pytest-cov

# Документирование
pip install sphinx sphinx-rtd-theme

# Отладка
pip install ipdb
```

---

## Архитектура и принципы

### Принципы проектирования:

#### 1. Модульность
Каждый модуль должен иметь единственную ответственность:
```python
# ✅ Хорошо - модуль отвечает только за кэширование
class ItemsCache:
    def get_item(self, item_id: str) -> Optional[Dict]:
        pass
    
    def update_item(self, item_id: str, item_data: Dict) -> bool:
        pass

# ❌ Плохо - модуль делает слишком много
class ItemsManager:
    def get_item(self, item_id: str) -> Optional[Dict]:
        pass
    
    def send_email(self, message: str) -> bool:  # Не относится к предметам
        pass
```

#### 2. Расширяемость
Используйте интерфейсы и абстрактные классы:
```python
from abc import ABC, abstractmethod

class DatabaseInterface(ABC):
    @abstractmethod
    def load_data(self) -> bool:
        pass
    
    @abstractmethod
    def save_data(self, data: Dict) -> bool:
        pass

class ItemsDatabase(DatabaseInterface):
    def load_data(self) -> bool:
        # Реализация для предметов
        pass
    
    def save_data(self, data: Dict) -> bool:
        # Реализация для предметов
        pass
```

#### 3. Безопасность
Всегда создавайте резервные копии:
```python
def save_item(self, item_id: str, item_data: Dict) -> bool:
    try:
        # Создание резервной копии
        backup_file = self.get_backup_path(item_id)
        if self.item_file.exists():
            backup_file.write_bytes(self.item_file.read_bytes())
        
        # Сохранение данных
        with open(self.item_file, 'wb') as f:
            f.write(json.dumps(item_data, option=json.OPT_INDENT_2))
        
        return True
    except Exception as e:
        # Восстановление из резервной копии
        self.restore_from_backup(backup_file)
        raise
```

### Паттерны проектирования:

#### 1. Singleton (для конфигурации)
```python
class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

#### 2. Observer (для событий UI)
```python
class EventManager:
    def __init__(self):
        self._observers = []
    
    def subscribe(self, observer):
        self._observers.append(observer)
    
    def notify(self, event):
        for observer in self._observers:
            observer.update(event)
```

#### 3. Factory (для создания модулей)
```python
class ModuleFactory:
    @staticmethod
    def create_module(module_type: str, parent, server_path: Path):
        if module_type == "items":
            return ItemsManager(parent, server_path)
        elif module_type == "traders":
            return TradersManager(parent, server_path)
        else:
            raise ValueError(f"Unknown module type: {module_type}")
```

---

## Стандарты кодирования

### 1. PEP 8 Compliance
```python
# ✅ Хорошо
def calculate_item_weight(item_data: Dict[str, Any]) -> float:
    """Calculate total weight of an item including attachments."""
    base_weight = item_data.get('Weight', 0.0)
    attachments_weight = sum(
        attachment.get('Weight', 0.0) 
        for attachment in item_data.get('Attachments', [])
    )
    return base_weight + attachments_weight

# ❌ Плохо
def calcweight(d):
    w=d.get('Weight',0)
    a=sum(x.get('Weight',0)for x in d.get('Attachments',[]))
    return w+a
```

### 2. Типизация
```python
from typing import Dict, List, Optional, Union, Tuple, Any
from pathlib import Path

def process_items(
    items: List[Dict[str, Any]], 
    filter_func: Optional[callable] = None
) -> Tuple[List[Dict[str, Any]], int]:
    """Process items with optional filtering.
    
    Args:
        items: List of item dictionaries
        filter_func: Optional function to filter items
        
    Returns:
        Tuple of (filtered_items, total_count)
    """
    if filter_func:
        filtered = [item for item in items if filter_func(item)]
    else:
        filtered = items
    
    return filtered, len(filtered)
```

### 3. Обработка ошибок
```python
def load_config_file(file_path: Path) -> Dict[str, Any]:
    """Load configuration file with proper error handling."""
    try:
        if not file_path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if not isinstance(config, dict):
            raise ValueError("Config file must contain a dictionary")
        
        return config
        
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in config file: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to load config: {e}")
```

### 4. Логирование
```python
import logging

logger = logging.getLogger(__name__)

def save_item_data(item_id: str, item_data: Dict[str, Any]) -> bool:
    """Save item data with logging."""
    logger.info(f"Saving item data for {item_id}")
    
    try:
        # Логика сохранения
        result = perform_save(item_id, item_data)
        
        if result:
            logger.info(f"Successfully saved item {item_id}")
        else:
            logger.warning(f"Failed to save item {item_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error saving item {item_id}: {e}", exc_info=True)
        return False
```

---

## Создание новых модулей

### 1. Структура модуля
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name - Краткое описание модуля

Подробное описание назначения модуля и его основных функций.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)

class ModuleClass:
    """Основной класс модуля.
    
    Описание назначения класса и его основных возможностей.
    """
    
    def __init__(self, parent: tk.Widget, server_path: Path):
        """Инициализация модуля.
        
        Args:
            parent: Родительский виджет
            server_path: Путь к серверу SPT
        """
        self.parent = parent
        self.server_path = server_path
        self.data = {}
        
        # Инициализация компонентов
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self) -> None:
        """Настройка пользовательского интерфейса."""
        # Создание UI компонентов
        pass
    
    def _load_data(self) -> bool:
        """Загрузка данных модуля.
        
        Returns:
            True если данные загружены успешно
        """
        try:
            # Логика загрузки
            return True
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            return False
    
    def save_data(self) -> bool:
        """Сохранение данных модуля.
        
        Returns:
            True если данные сохранены успешно
        """
        try:
            # Логика сохранения
            return True
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
            return False

def main():
    """Главная функция для тестирования модуля."""
    root = tk.Tk()
    root.withdraw()
    
    server_path = Path(__file__).parent.parent
    module = ModuleClass(root, server_path)
    
    root.mainloop()

if __name__ == "__main__":
    main()
```

### 2. Интеграция с главным приложением
```python
# В stp_server_editor.py
from modules.new_module import ModuleClass

class MainApplication:
    def __init__(self):
        # ... существующий код ...
        self.new_module = None
    
    def open_new_module(self):
        """Открытие нового модуля."""
        try:
            if not self.new_module:
                self.new_module = ModuleClass(self.window, self.server_path)
            else:
                self.new_module.dialog.lift()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть модуль: {e}")
```

### 3. Создание диалогов
```python
class ModuleDialog:
    """Диалог модуля."""
    
    def __init__(self, parent: tk.Widget, title: str):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрирование диалога
        self._center_dialog()
        
        # Создание интерфейса
        self._create_widgets()
        
        # Обработка закрытия
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _center_dialog(self):
        """Центрирование диалога на экране."""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_widgets(self):
        """Создание виджетов диалога."""
        # Реализация интерфейса
        pass
    
    def _on_closing(self):
        """Обработка закрытия диалога."""
        self.dialog.destroy()
```

---

## Тестирование

### 1. Unit тесты
```python
import unittest
from unittest.mock import Mock, patch
from pathlib import Path
from modules.items_manager import ItemsManager

class TestItemsManager(unittest.TestCase):
    """Тесты для ItemsManager."""
    
    def setUp(self):
        """Настройка тестов."""
        self.server_path = Path("test_server")
        self.manager = ItemsManager(None, self.server_path)
    
    def test_load_items_data_success(self):
        """Тест успешной загрузки данных предметов."""
        with patch.object(self.manager, 'items_file') as mock_file:
            mock_file.exists.return_value = True
            mock_file.read_bytes.return_value = b'{"test": "data"}'
            
            result = self.manager.load_items_data()
            
            self.assertTrue(result)
            self.assertEqual(self.manager.items_data, {"test": "data"})
    
    def test_load_items_data_file_not_found(self):
        """Тест загрузки при отсутствии файла."""
        with patch.object(self.manager, 'items_file') as mock_file:
            mock_file.exists.return_value = False
            
            result = self.manager.load_items_data()
            
            self.assertFalse(result)
    
    def test_save_item_success(self):
        """Тест успешного сохранения предмета."""
        test_item = {"_id": "test", "_name": "Test Item"}
        
        with patch.object(self.manager, 'items_file') as mock_file:
            mock_file.exists.return_value = True
            mock_file.write_bytes.return_value = None
            
            result = self.manager.save_item("test", test_item)
            
            self.assertTrue(result)
            mock_file.write_bytes.assert_called_once()
    
    def test_search_items(self):
        """Тест поиска предметов."""
        self.manager.items_data = {
            "item1": {"_name": "Test Item 1"},
            "item2": {"_name": "Another Item"},
            "item3": {"_name": "Test Item 2"}
        }
        
        results = self.manager.search_items("Test")
        
        self.assertEqual(len(results), 2)
        self.assertIn("item1", [r["_id"] for r in results])
        self.assertIn("item3", [r["_id"] for r in results])

if __name__ == "__main__":
    unittest.main()
```

### 2. Интеграционные тесты
```python
class TestIntegration(unittest.TestCase):
    """Интеграционные тесты."""
    
    def setUp(self):
        """Настройка тестов."""
        self.test_server_path = Path("test_server")
        self.test_server_path.mkdir(exist_ok=True)
        
        # Создание тестовых файлов
        self._create_test_files()
    
    def tearDown(self):
        """Очистка после тестов."""
        import shutil
        if self.test_server_path.exists():
            shutil.rmtree(self.test_server_path)
    
    def _create_test_files(self):
        """Создание тестовых файлов."""
        # Создание items.json
        items_data = {
            "test_item": {
                "_id": "test_item",
                "_name": "Test Item",
                "_type": "Item",
                "_props": {
                    "Weight": 1.0,
                    "Width": 1,
                    "Height": 1
                }
            }
        }
        
        items_file = self.test_server_path / "database" / "templates" / "items.json"
        items_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(items_file, 'wb') as f:
            f.write(json.dumps(items_data, option=json.OPT_INDENT_2))
    
    def test_full_workflow(self):
        """Тест полного рабочего процесса."""
        # 1. Загрузка данных
        manager = ItemsManager(None, self.test_server_path)
        self.assertTrue(manager.load_items_data())
        
        # 2. Редактирование
        item_data = manager.get_item("test_item")
        item_data["_props"]["Weight"] = 2.0
        
        # 3. Сохранение
        self.assertTrue(manager.save_item("test_item", item_data))
        
        # 4. Проверка результата
        manager.load_items_data()  # Перезагрузка
        updated_item = manager.get_item("test_item")
        self.assertEqual(updated_item["_props"]["Weight"], 2.0)
```

### 3. Тестирование UI
```python
class TestUI(unittest.TestCase):
    """Тесты пользовательского интерфейса."""
    
    def setUp(self):
        """Настройка тестов."""
        self.root = tk.Tk()
        self.root.withdraw()  # Скрываем главное окно
    
    def tearDown(self):
        """Очистка после тестов."""
        self.root.destroy()
    
    def test_dialog_creation(self):
        """Тест создания диалога."""
        dialog = ModuleDialog(self.root, "Test Dialog")
        
        self.assertIsInstance(dialog.dialog, tk.Toplevel)
        self.assertEqual(dialog.dialog.title(), "Test Dialog")
        
        dialog.dialog.destroy()
    
    def test_button_click(self):
        """Тест нажатия кнопки."""
        dialog = ModuleDialog(self.root, "Test Dialog")
        
        # Симуляция нажатия кнопки
        with patch.object(dialog, 'on_button_click') as mock_click:
            dialog.button.invoke()
            mock_click.assert_called_once()
        
        dialog.dialog.destroy()
```

### 4. Запуск тестов
```bash
# Запуск всех тестов
python -m pytest

# Запуск с покрытием
python -m pytest --cov=modules

# Запуск конкретного теста
python -m pytest tests/test_items_manager.py::TestItemsManager::test_load_items_data_success

# Запуск с подробным выводом
python -m pytest -v

# Запуск с остановкой на первой ошибке
python -m pytest -x
```

---

## Отладка и профилирование

### 1. Логирование
```python
import logging
import sys
from pathlib import Path

def setup_logging(log_level: str = "INFO") -> None:
    """Настройка системы логирования."""
    
    # Создание логгера
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Обработчик для файла
    file_handler = logging.FileHandler('debug.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Добавление обработчиков
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# Использование
setup_logging("DEBUG")
logger = logging.getLogger(__name__)

def process_data(data: Dict[str, Any]) -> bool:
    """Обработка данных с логированием."""
    logger.debug(f"Processing data: {data}")
    
    try:
        # Логика обработки
        result = perform_processing(data)
        
        logger.info(f"Data processed successfully: {result}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing data: {e}", exc_info=True)
        return False
```

### 2. Отладка с помощью pdb
```python
import pdb

def debug_function(data: Dict[str, Any]) -> bool:
    """Функция с точками останова."""
    
    # Установка точки останова
    pdb.set_trace()
    
    # Логика функции
    result = process_data(data)
    
    # Еще одна точка останова
    pdb.set_trace()
    
    return result

# Команды pdb:
# n - следующая строка
# s - войти в функцию
# c - продолжить выполнение
# l - показать код
# p variable - показать переменную
# pp variable - красиво показать переменную
# q - выйти
```

### 3. Профилирование производительности
```python
import cProfile
import pstats
import io
from contextlib import contextmanager

@contextmanager
def profile_context():
    """Контекстный менеджер для профилирования."""
    profiler = cProfile.Profile()
    profiler.enable()
    
    try:
        yield profiler
    finally:
        profiler.disable()

def profile_function():
    """Профилирование функции."""
    with profile_context() as profiler:
        # Код для профилирования
        result = expensive_operation()
    
    # Анализ результатов
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats()
    
    print(s.getvalue())

# Профилирование с сохранением в файл
def profile_to_file():
    """Профилирование с сохранением в файл."""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Код для профилирования
    result = expensive_operation()
    
    profiler.disable()
    profiler.dump_stats('profile.prof')
    
    # Анализ файла
    ps = pstats.Stats('profile.prof')
    ps.sort_stats('cumulative')
    ps.print_stats(20)  # Топ 20 функций
```

### 4. Мониторинг памяти
```python
import tracemalloc
import psutil
import os

def monitor_memory():
    """Мониторинг использования памяти."""
    
    # Запуск трассировки памяти
    tracemalloc.start()
    
    # Выполнение кода
    result = process_large_dataset()
    
    # Получение статистики памяти
    current, peak = tracemalloc.get_traced_memory()
    
    print(f"Current memory usage: {current / 1024 / 1024:.2f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.2f} MB")
    
    # Остановка трассировки
    tracemalloc.stop()
    
    # Дополнительная информация
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    print(f"RSS: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"VMS: {memory_info.vms / 1024 / 1024:.2f} MB")
```

---

## Документирование

### 1. Docstrings (Google Style)
```python
def calculate_item_stats(
    item_data: Dict[str, Any], 
    include_attachments: bool = True
) -> Dict[str, Union[int, float]]:
    """Calculate comprehensive statistics for an item.
    
    This function calculates various statistics for an item including
    weight, dimensions, and value. It can optionally include statistics
    from attached items.
    
    Args:
        item_data: Dictionary containing item data with required keys:
            - Weight: Base weight of the item
            - Width: Width in inventory slots
            - Height: Height in inventory slots
            - BasePrice: Base price of the item
            - Attachments: List of attached items (optional)
        include_attachments: Whether to include attached items in calculations
        
    Returns:
        Dictionary containing calculated statistics:
            - total_weight: Total weight including attachments
            - total_value: Total value including attachments
            - slot_count: Number of inventory slots occupied
            - attachment_count: Number of attachments
            
    Raises:
        KeyError: If required keys are missing from item_data
        ValueError: If item_data contains invalid values
        TypeError: If item_data is not a dictionary
        
    Example:
        >>> item_data = {
        ...     'Weight': 2.5,
        ...     'Width': 2,
        ...     'Height': 3,
        ...     'BasePrice': 1000,
        ...     'Attachments': [{'Weight': 0.5, 'BasePrice': 100}]
        ... }
        >>> stats = calculate_item_stats(item_data)
        >>> print(stats['total_weight'])
        3.0
        
    Note:
        This function assumes that all weight values are in kilograms
        and all price values are in the same currency.
    """
    # Реализация функции
    pass
```

### 2. Комментарии в коде
```python
def process_items_batch(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process a batch of items for bulk operations."""
    
    processed_items = []
    
    # Обработка каждого предмета в батче
    for item in items:
        try:
            # Валидация обязательных полей
            if not self._validate_required_fields(item):
                logger.warning(f"Skipping item {item.get('_id', 'unknown')}: missing required fields")
                continue
            
            # Нормализация данных предмета
            normalized_item = self._normalize_item_data(item)
            
            # Применение бизнес-правил
            processed_item = self._apply_business_rules(normalized_item)
            
            # Добавление метаданных обработки
            processed_item['_processed_at'] = datetime.now().isoformat()
            processed_item['_processed_by'] = 'batch_processor'
            
            processed_items.append(processed_item)
            
        except Exception as e:
            # Логирование ошибки, но продолжение обработки остальных предметов
            logger.error(f"Error processing item {item.get('_id', 'unknown')}: {e}")
            continue
    
    return processed_items
```

### 3. README для модуля
```markdown
# Module Name

Краткое описание назначения модуля.

## Функции

- Основная функция 1
- Основная функция 2
- Основная функция 3

## Использование

```python
from modules.module_name import ModuleClass

# Создание экземпляра
module = ModuleClass(parent, server_path)

# Использование
result = module.some_method()
```

## API Reference

### ModuleClass

#### `__init__(parent, server_path)`
Инициализация модуля.

**Параметры:**
- `parent`: Родительский виджет
- `server_path`: Путь к серверу SPT

#### `some_method() -> bool`
Описание метода.

**Возвращает:**
- `bool`: Результат операции

## Примеры

### Пример 1: Базовое использование
```python
# Код примера
```

### Пример 2: Расширенное использование
```python
# Код примера
```

## Требования

- Python 3.8+
- tkinter
- pathlib

## Лицензия

MIT License
```

---

## Контрибьюция

### 1. Процесс контрибьюции

#### Шаг 1: Форк репозитория
```bash
# Создание форка на GitHub
# Клонирование форка
git clone https://github.com/your-username/spt-server-editor.git
cd spt-server-editor
```

#### Шаг 2: Создание ветки для фичи
```bash
git checkout -b feature/new-feature-name
```

#### Шаг 3: Разработка
```bash
# Внесение изменений
# Тестирование
python -m pytest
# Форматирование кода
black modules/
# Проверка линтера
flake8 modules/
```

#### Шаг 4: Коммит
```bash
git add .
git commit -m "feat: add new feature

- Добавлена новая функция X
- Исправлена ошибка Y
- Обновлена документация

Closes #123"
```

#### Шаг 5: Push и Pull Request
```bash
git push origin feature/new-feature-name
# Создание Pull Request на GitHub
```

### 2. Стандарты коммитов
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Типы:**
- `feat`: Новая функция
- `fix`: Исправление бага
- `docs`: Изменения в документации
- `style`: Форматирование кода
- `refactor`: Рефакторинг
- `test`: Добавление тестов
- `chore`: Обслуживание

**Примеры:**
```
feat(items): add bulk parameter update functionality

- Implemented bulk parameter update dialog
- Added validation for parameter values
- Created backup system for changes

Closes #45
```

### 3. Code Review Checklist
- [ ] Код соответствует стандартам PEP 8
- [ ] Добавлены тесты для новой функциональности
- [ ] Обновлена документация
- [ ] Нет критических уязвимостей безопасности
- [ ] Производительность не ухудшена
- [ ] Обратная совместимость сохранена

---

## Развертывание

### 1. Создание исполняемого файла

#### PyInstaller
```bash
# Установка PyInstaller
pip install pyinstaller

# Создание исполняемого файла
pyinstaller --onefile --windowed --name "SPT Server Editor" main.py

# Создание с дополнительными файлами
pyinstaller --onefile --windowed --add-data "configs;configs" --add-data "images;images" main.py
```

#### cx_Freeze
```python
# setup.py
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["tkinter", "orjson", "yaml"],
    "include_files": ["configs/", "images/"],
    "excludes": ["test", "unittest"]
}

setup(
    name="SPT Server Editor",
    version="1.0.0",
    description="Editor for SPT server files",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base="Win32GUI")]
)
```

### 2. Создание установщика

#### NSIS (Windows)
```nsis
; installer.nsi
!define APPNAME "SPT Server Editor"
!define COMPANYNAME "SPT Community"
!define DESCRIPTION "Editor for SPT server files"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0

!include "MUI2.nsh"

Name "${APPNAME}"
OutFile "SPT_Server_Editor_Setup.exe"
InstallDir "$PROGRAMFILES\${APPNAME}"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "Russian"

Section "Install"
    SetOutPath $INSTDIR
    File "SPT_Server_Editor.exe"
    File "LICENSE"
    File "README.md"
    
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\SPT_Server_Editor.exe"
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\SPT_Server_Editor.exe"
    
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\SPT_Server_Editor.exe"
    Delete "$INSTDIR\LICENSE"
    Delete "$INSTDIR\README.md"
    Delete "$INSTDIR\uninstall.exe"
    
    Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
    Delete "$DESKTOP\${APPNAME}.lnk"
    
    RMDir "$SMPROGRAMS\${APPNAME}"
    RMDir "$INSTDIR"
    
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
SectionEnd
```

### 3. Автоматизация сборки

#### GitHub Actions
```yaml
# .github/workflows/build.yml
name: Build and Release

on:
  push:
    tags:
      - 'v*'
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Run tests
      run: |
        python -m pytest tests/
    
    - name: Build executable
      run: |
        pyinstaller --onefile --windowed --name "SPT Server Editor" main.py
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v2
      with:
        name: SPT-Server-Editor
        path: dist/
```

---

## Заключение

Данное руководство предоставляет полную информацию для разработчиков, желающих внести свой вклад в проект SPT Server Editor. Следование описанным стандартам и практикам обеспечит высокое качество кода и удобство разработки.

### Полезные ресурсы:
- [Python PEP 8](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [pytest Documentation](https://docs.pytest.org/)
- [Sphinx Documentation](https://www.sphinx-doc.org/)

### Контакты:
- GitHub Issues: [ссылка на репозиторий]
- Discord: [ссылка на сервер]
- Email: [контактный email]

---

**Версия руководства**: 1.0  
**Дата последнего обновления**: 2024  
**Автор**: AI Assistant  
**Лицензия**: MIT License
