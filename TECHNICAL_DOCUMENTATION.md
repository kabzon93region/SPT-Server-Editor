# Техническая документация SPT Server Editor

## Содержание
1. [Обзор проекта](#обзор-проекта)
2. [Архитектура системы](#архитектура-системы)
3. [Структура проекта](#структура-проекта)
4. [Основные модули](#основные-модули)
5. [Вспомогательные модули](#вспомогательные-модули)
6. [Система кэширования](#система-кэширования)
7. [Структуры данных](#структуры-данных)
8. [API и интерфейсы](#api-и-интерфейсы)
9. [Зависимости и лицензии](#зависимости-и-лицензии)
10. [Руководство разработчика](#руководство-разработчика)

---

## Обзор проекта

**SPT Server Editor** - это Python-приложение с графическим интерфейсом для редактирования серверных файлов настроек игры Escape from Tarkov в модификации SPT-AKI (Single Player Tarkov).

### Основные возможности:
- Редактирование параметров предметов
- Управление торговцами и их ассортиментом
- Настройка рецептов крафта
- Массовое изменение параметров
- Анализ и валидация данных
- Создание резервных копий

### Технологический стек:
- **Python 3.8+** - основной язык программирования
- **tkinter** - графический интерфейс
- **orjson** - быстрая обработка JSON
- **PyYAML** - работа с YAML конфигурациями
- **httpx** - HTTP клиент для API запросов

---

## Архитектура системы

### Общая архитектура
```
┌─────────────────────────────────────────────────────────────┐
│                    SPT Server Editor                       │
├─────────────────────────────────────────────────────────────┤
│  Главное окно (main.py)                                    │
│  ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐  │
│  │  Менеджер       │ │  Менеджер       │ │  Менеджер    │  │
│  │  предметов      │ │  торговцев      │ │  крафта      │  │
│  └─────────────────┘ └─────────────────┘ └──────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  Вспомогательные модули                                     │
│  ┌──────────────┐ ┌──────────────┐ ┌─────────────────────┐ │
│  │  Кэш         │ │  Валидация   │ │  UI утилиты         │ │
│  │  системы     │ │  данных      │ │                     │ │
│  └──────────────┘ └──────────────┘ └─────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  Слой данных                                                │
│  ┌──────────────┐ ┌──────────────┐ ┌─────────────────────┐ │
│  │  JSON файлы  │ │  YAML файлы  │ │  Кэш файлы          │ │
│  │  сервера     │ │  конфигов    │ │                     │ │
│  └──────────────┘ └──────────────┘ └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Принципы проектирования:
1. **Модульность** - каждый компонент имеет четко определенную ответственность
2. **Расширяемость** - легко добавлять новые модули и функции
3. **Безопасность** - создание резервных копий перед изменениями
4. **Производительность** - кэширование и оптимизированная обработка данных

---

## Структура проекта

```
SPT_Data/Server/
├── main.py                          # Точка входа в приложение
├── stp_server_editor.py             # Основная программа
├── config.yaml                      # Конфигурация приложения
├── requirements.txt                 # Зависимости Python
├── README.md                        # Описание проекта
├── LICENSE                          # Лицензия проекта
├── TECHNICAL_DOCUMENTATION.md       # Техническая документация
├── BULK_PARAMETERS_GUIDE.md         # Руководство по массовому изменению
├── modules/                         # Модули программы
│   ├── config_manager.py           # Управление конфигурацией
│   ├── context_menus.py            # Контекстные меню
│   ├── craft_manager.py            # Менеджер крафта
│   ├── dynamic_ui.py               # Динамический UI
│   ├── hideout_areas.py            # Области убежища
│   ├── items_analyzer.py           # Анализатор предметов
│   ├── items_cache.py              # Кэш предметов
│   ├── items_database.py           # База данных предметов
│   ├── items_manager.py            # Менеджер предметов
│   ├── items_search_dialog.py      # Диалог поиска предметов
│   ├── json_editor.py              # JSON редактор
│   ├── scan_db.py                  # Сканер базы данных
│   ├── scan_progress_window.py     # Окно прогресса сканирования
│   ├── scav_recipes_dialog.py      # Диалог рецептов диких
│   ├── trader_dialogs.py           # Диалоги торговцев
│   ├── trader_editor.py            # Редактор торговцев
│   ├── traders_database.py         # База данных торговцев
│   ├── ui_utils.py                 # UI утилиты
│   ├── view_detailed_analysis.py   # Просмотр анализа
│   ├── item_parameters_analyzer.py # Анализатор параметров
│   └── bulk_parameters_dialog.py   # Диалог массового изменения
├── cache/                          # Кэш файлы
│   ├── items_cache.json           # Кэш предметов
│   ├── items_readable.json        # Читаемый кэш
│   └── scan_db.log                # Лог сканирования
├── configs/                        # Конфигурационные файлы
│   ├── airdrop.json               # Настройки аирдропа
│   ├── bot.json                   # Настройки ботов
│   ├── core.json                  # Основные настройки
│   ├── trader.json                # Настройки торговцев
│   └── ...                        # Другие конфигурации
└── database/                       # База данных сервера
    ├── templates/                 # Шаблоны предметов
    │   └── items.json            # База предметов
    ├── traders/                   # Данные торговцев
    ├── hideout/                   # Данные убежища
    └── locations/                 # Данные локаций
```

---

## Основные модули

### 1. main.py
**Назначение**: Точка входа в приложение
**Основные функции**:
- Инициализация приложения
- Проверка зависимостей
- Запуск главного окна

### 2. stp_server_editor.py
**Назначение**: Основная программа с главным окном
**Основные функции**:
- Создание главного интерфейса
- Управление модулями
- Обработка событий

### 3. items_manager.py
**Назначение**: Управление предметами
**Основные функции**:
- Загрузка и сохранение предметов
- Редактирование параметров
- Массовое изменение параметров
- Поиск и фильтрация

**Ключевые классы**:
```python
class ItemsManager:
    def __init__(self, parent, server_path: Path)
    def load_items_data(self) -> bool
    def save_item(self, item_id: str, item_data: Dict) -> bool
    def search_items(self, query: str) -> List[Dict]
    def bulk_update_parameters(self, items: List[str], param: str, value: Any) -> bool
```

### 4. trader_editor.py
**Назначение**: Редактирование торговцев
**Основные функции**:
- Управление ассортиментом торговцев
- Настройка цен и валют
- Редактирование уровней лояльности
- Управление услугами

### 5. craft_manager.py
**Назначение**: Управление рецептами крафта
**Основные функции**:
- Редактирование рецептов
- Управление требованиями
- Настройка времени производства
- Валидация рецептов

---

## Вспомогательные модули

### 1. config_manager.py
**Назначение**: Управление конфигурацией приложения
**Функции**:
- Загрузка настроек из YAML
- Валидация конфигурации
- Сохранение изменений

### 2. items_cache.py
**Назначение**: Система кэширования предметов
**Функции**:
- Кэширование данных предметов
- Индексация для быстрого поиска
- Управление жизненным циклом кэша

### 3. items_analyzer.py
**Назначение**: Анализ параметров предметов
**Функции**:
- Статистический анализ параметров
- Группировка по типам и частоте использования
- Генерация отчетов

### 4. json_editor.py
**Назначение**: Редактор JSON с подсветкой синтаксиса
**Функции**:
- Редактирование JSON данных
- Подсветка синтаксиса
- Валидация JSON
- Форматирование

### 5. ui_utils.py
**Назначение**: Утилиты для пользовательского интерфейса
**Функции**:
- Создание стандартных диалогов
- Управление стилями
- Обработка событий

### 6. context_menus.py
**Назначение**: Контекстные меню для полей ввода
**Функции**:
- Стандартные операции (копировать, вставить, вырезать)
- Поддержка русской раскладки
- Автоматическая привязка к виджетам

---

## Система кэширования

### Архитектура кэша
```
┌─────────────────────────────────────────────────────────────┐
│                    Система кэширования                     │
├─────────────────────────────────────────────────────────────┤
│  items_cache.py                                             │
│  ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐  │
│  │  Полный кэш     │ │  Индексы        │ │  Метаданные  │  │
│  │  (items)        │ │  (поиск)        │ │  (статистика)│  │
│  └─────────────────┘ └─────────────────┘ └──────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  Файлы кэша                                                 │
│  ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐  │
│  │ items_cache.json│ │items_readable.json│ scan_db.log  │  │
│  │ (бинарный)      │ │ (человекочитаемый)│ (логи)       │  │
│  └─────────────────┘ └─────────────────┘ └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Ключевые компоненты:

#### ItemsCache
```python
class ItemsCache:
    def __init__(self, server_path: Path)
    def load_cache(self) -> bool
    def save_cache(self) -> bool
    def get_item(self, item_id: str) -> Optional[Dict]
    def search_items(self, query: str) -> List[Dict]
    def update_item(self, item_id: str, item_data: Dict) -> bool
    def invalidate_cache(self) -> None
```

#### Стратегии кэширования:
1. **Lazy Loading** - загрузка по требованию
2. **Write-Through** - синхронная запись
3. **TTL (Time To Live)** - автоматическое истечение
4. **LRU (Least Recently Used)** - вытеснение неиспользуемых данных

---

## Структуры данных

### 1. Структура предмета (items.json)
```json
{
  "_id": "string",           // Уникальный идентификатор
  "_name": "string",         // Название предмета
  "_parent": "string",       // ID родительского предмета
  "_type": "string",         // Тип предмета (Item, Node, etc.)
  "_props": {                // Свойства предмета
    "Weight": "number",      // Вес
    "Width": "number",       // Ширина в слотах
    "Height": "number",      // Высота в слотах
    "RarityPvE": "string",   // Редкость в PvE
    "BasePrice": "number",   // Базовая цена
    "Prefab": {              // Префаб
      "path": "string"       // Путь к префабу
    },
    "Requirements": [        // Требования для крафта
      {
        "templateId": "string",
        "count": "number",
        "type": "string"
      }
    ]
  }
}
```

### 2. Структура торговца (base.json)
```json
{
  "_id": "string",           // ID торговца
  "currency": "string",      // Валюта (RUB, USD, EUR)
  "balance_rub": "number",   // Баланс в рублях
  "balance_dol": "number",   // Баланс в долларах
  "balance_eur": "number",   // Баланс в евро
  "discount": "number",      // Скидка
  "availableInRaid": "boolean", // Доступен в рейде
  "loyaltyLevels": {         // Уровни лояльности
    "0": {
      "minLevel": "number",
      "minSalesSum": "number",
      "minStanding": "number"
    }
  },
  "insurance": {             // Страховка
    "availability": "boolean",
    "max_return_hour": "number",
    "min_payment": "number"
  }
}
```

### 3. Структура рецепта крафта (production.json)
```json
{
  "scavRecipes": [           // Рецепты ящика диких
    {
      "_id": "string",       // ID рецепта
      "productionTime": "number", // Время производства (сек)
      "requirements": [      // Требования
        {
          "templateId": "string",
          "count": "number",
          "type": "string"
        }
      ],
      "endProducts": {       // Продукты по редкости
        "Common": {
          "min": "number",
          "max": "number"
        },
        "Rare": {
          "min": "number",
          "max": "number"
        },
        "Superrare": {
          "min": "number",
          "max": "number"
        }
      }
    }
  ]
}
```

---

## API и интерфейсы

### 1. ItemsDatabase API
```python
class ItemsDatabase:
    def load_items(self) -> bool
    def save_item(self, item_id: str, item_data: Dict) -> bool
    def get_item(self, item_id: str) -> Optional[Dict]
    def search_items(self, query: str) -> List[Dict]
    def get_items_by_type(self, item_type: str) -> List[Dict]
    def validate_item(self, item_data: Dict) -> Tuple[bool, List[str]]
```

### 2. TradersDatabase API
```python
class TradersDatabase:
    def load_all_traders(self) -> bool
    def get_trader_info(self, trader_id: str) -> Dict
    def save_trader_base(self, trader_id: str, base_data: Dict) -> bool
    def get_trader_assort(self, trader_id: str) -> List[Dict]
    def update_trader_assort(self, trader_id: str, assort: List[Dict]) -> bool
```

### 3. ItemsCache API
```python
class ItemsCache:
    def get_item(self, item_id: str) -> Optional[Dict]
    def search_items(self, query: str) -> List[Dict]
    def update_item(self, item_id: str, item_data: Dict) -> bool
    def invalidate_cache(self) -> None
    def get_cache_stats(self) -> Dict
```

---

## Зависимости и лицензии

### Основные зависимости:

#### 1. orjson (MIT License)
- **Версия**: 3.9.10+
- **Назначение**: Быстрая обработка JSON
- **Лицензия**: MIT License
- **Использование**: Парсинг и сериализация JSON файлов

#### 2. PyYAML (MIT License)
- **Версия**: 6.0+
- **Назначение**: Работа с YAML конфигурациями
- **Лицензия**: MIT License
- **Использование**: Загрузка конфигурационных файлов

#### 3. httpx (BSD License)
- **Версия**: 0.24.0+
- **Назначение**: HTTP клиент для API запросов
- **Лицензия**: BSD License
- **Использование**: Сканирование базы данных через API

#### 4. tkinter (Python Standard Library)
- **Версия**: Встроен в Python
- **Назначение**: Графический интерфейс
- **Лицензия**: Python Software Foundation License
- **Использование**: Создание пользовательского интерфейса

### Лицензионная совместимость:
Все используемые библиотеки имеют совместимые лицензии (MIT, BSD, PSF), что позволяет использовать их в коммерческих и некоммерческих проектах.

---

## Руководство разработчика

### Требования к окружению:
- Python 3.8 или выше
- Windows 10/11 (рекомендуется)
- 4 GB RAM (минимум)
- 1 GB свободного места на диске

### Установка и настройка:

#### 1. Клонирование репозитория:
```bash
git clone <repository-url>
cd SPT_Data/Server
```

#### 2. Установка зависимостей:
```bash
pip install -r requirements.txt
```

#### 3. Запуск приложения:
```bash
python main.py
```

### Стандарты кодирования:

#### 1. Стиль кода (PEP 8):
- Отступы: 4 пробела
- Максимальная длина строки: 120 символов
- Именование: snake_case для переменных и функций, PascalCase для классов

#### 2. Документирование:
```python
def function_name(param1: str, param2: int) -> bool:
    """Краткое описание функции.
    
    Подробное описание функции, включая детали
    реализации и примеры использования.
    
    Args:
        param1 (str): Описание первого параметра
        param2 (int): Описание второго параметра
        
    Returns:
        bool: Описание возвращаемого значения
        
    Raises:
        ValueError: Описание исключения
        FileNotFoundError: Описание исключения
        
    Example:
        >>> result = function_name("test", 42)
        >>> print(result)
        True
    """
    # Реализация функции
    pass
```

#### 3. Обработка ошибок:
```python
try:
    # Код, который может вызвать исключение
    result = risky_operation()
except SpecificException as e:
    # Обработка конкретного исключения
    logger.error(f"Ошибка в операции: {e}")
    return None
except Exception as e:
    # Общая обработка исключений
    logger.error(f"Неожиданная ошибка: {e}")
    raise
```

### Добавление новых модулей:

#### 1. Структура модуля:
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name - Краткое описание модуля
"""

import tkinter as tk
from pathlib import Path
from typing import Dict, List, Any, Optional

class ModuleClass:
    """Описание класса модуля"""
    
    def __init__(self, parent, server_path: Path):
        """Инициализация модуля"""
        self.parent = parent
        self.server_path = server_path
        # Инициализация компонентов
    
    def method_name(self, param: str) -> bool:
        """Описание метода"""
        # Реализация метода
        pass

def main():
    """Главная функция для тестирования"""
    # Код тестирования

if __name__ == "__main__":
    main()
```

#### 2. Интеграция с главным приложением:
```python
# В stp_server_editor.py
from modules.new_module import NewModule

class MainApplication:
    def __init__(self):
        # Инициализация
        self.new_module = None
    
    def open_new_module(self):
        """Открытие нового модуля"""
        if not self.new_module:
            self.new_module = NewModule(self.window, self.server_path)
```

### Тестирование:

#### 1. Unit тесты:
```python
import unittest
from modules.items_manager import ItemsManager

class TestItemsManager(unittest.TestCase):
    def setUp(self):
        """Настройка тестов"""
        self.manager = ItemsManager(None, Path("test_server"))
    
    def test_load_items(self):
        """Тест загрузки предметов"""
        result = self.manager.load_items_data()
        self.assertTrue(result)
    
    def test_save_item(self):
        """Тест сохранения предмета"""
        test_item = {"_id": "test", "_name": "Test Item"}
        result = self.manager.save_item("test", test_item)
        self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()
```

#### 2. Интеграционные тесты:
```python
def test_full_workflow():
    """Тест полного рабочего процесса"""
    # 1. Загрузка данных
    # 2. Редактирование
    # 3. Сохранение
    # 4. Проверка результата
    pass
```

### Отладка и профилирование:

#### 1. Логирование:
```python
import logging

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Использование
logger.info("Информационное сообщение")
logger.warning("Предупреждение")
logger.error("Ошибка")
```

#### 2. Профилирование производительности:
```python
import cProfile
import pstats

def profile_function():
    """Профилирование функции"""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Код для профилирования
    your_function()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats()
```

### Развертывание:

#### 1. Создание исполняемого файла:
```bash
# Установка PyInstaller
pip install pyinstaller

# Создание исполняемого файла
pyinstaller --onefile --windowed main.py
```

#### 2. Создание установщика:
```bash
# Установка NSIS (Windows)
# Создание скрипта установщика
```

---

## Заключение

SPT Server Editor представляет собой комплексное решение для редактирования серверных файлов Escape from Tarkov. Архитектура приложения построена на принципах модульности, расширяемости и безопасности, что обеспечивает удобство разработки и поддержки.

Данная документация служит руководством для разработчиков, желающих внести свой вклад в проект, а также для пользователей, стремящихся понять внутреннее устройство приложения.

---

**Версия документации**: 1.0  
**Дата последнего обновления**: 2024  
**Автор**: AI Assistant  
**Лицензия**: MIT License
