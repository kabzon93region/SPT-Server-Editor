# 📝 Документация комментариев к коду

## Обзор

Этот документ содержит подробные комментарии ко всем модулям проекта SPT Server Editor. Комментарии добавлены для улучшения читаемости кода и понимания его функциональности.

## 📁 Структура комментариев

### 1. main.py - Главная точка входа

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPT Server Editor - Главная точка входа

Этот файл является точкой входа в приложение SPT Server Editor.
Он отвечает за:
- Инициализацию системы логирования
- Импорт и запуск основного модуля приложения
- Обработку ошибок инициализации
- Предоставление пользователю информации об ошибках

Автор: SPT Server Editor Team
Версия: 1.0.0
"""

# Импорт стандартных библиотек Python
import sys  # Для работы с системными параметрами и выходом из программы
import os   # Для работы с операционной системой
from pathlib import Path  # Для работы с путями файловой системы

# Добавляем текущую директорию в путь для импорта модулей
# Это необходимо для корректного импорта модулей проекта
current_dir = Path(__file__).parent  # Получаем директорию, где находится этот файл
sys.path.insert(0, str(current_dir))  # Добавляем её в начало списка путей для поиска модулей

# Инициализация отладочного логирования
# Система логирования должна быть инициализирована до импорта других модулей
try:
    # Импортируем необходимые функции из модуля логирования
    from modules.debug_logger import init_debug_logger, LogCategory, error, critical, info
    
    # Инициализируем систему логирования с настройками:
    debug_logger = init_debug_logging(
        log_dir=current_dir / "logs",           # Директория для сохранения логов
        enable_console=True,                    # Включить вывод в консоль
        enable_file=True,                       # Включить сохранение в файл
        max_file_size=10 * 1024 * 1024,        # Максимальный размер файла лога (10MB)
        max_files=10                            # Количество резервных файлов логов
    )
    
    # Логируем успешную инициализацию приложения
    info("SPT Server Editor запускается", LogCategory.SYSTEM)
    
except Exception as e:
    # Если не удалось инициализировать логирование, выводим ошибку в консоль
    print(f"Ошибка инициализации логирования: {e}")
    debug_logger = None  # Устанавливаем логгер в None для проверок

# Импорт и запуск основного модуля приложения
try:
    # Импортируем главную функцию из основного модуля приложения
    from stp_server_editor import main
    
    # Проверяем, что скрипт запущен напрямую (а не импортирован)
    if __name__ == "__main__":
        # Логируем запуск главного приложения, если логгер доступен
        if debug_logger:
            debug_logger.info("Запуск главного приложения", LogCategory.SYSTEM)
        
        # Запускаем главную функцию приложения
        main()
        
except ImportError as e:
    # Обработка ошибки импорта модулей
    error_msg = f"Ошибка импорта: {e}"
    
    # Логируем критическую ошибку, если логгер доступен
    if debug_logger:
        critical(error_msg, LogCategory.SYSTEM, exception=e)
    else:
        # Иначе выводим в консоль
        print(error_msg)
    
    # Предоставляем пользователю инструкции по устранению проблемы
    print("Убедитесь, что все зависимости установлены:")
    print("python -m pip install -r requirements.txt")
    input("Нажмите Enter для выхода...")
    sys.exit(1)  # Завершаем программу с кодом ошибки
    
except Exception as e:
    # Обработка любых других неожиданных ошибок
    error_msg = f"Неожиданная ошибка: {e}"
    
    # Логируем критическую ошибку, если логгер доступен
    if debug_logger:
        critical(error_msg, LogCategory.SYSTEM, exception=e)
    else:
        # Иначе выводим в консоль
        print(error_msg)
    
    # Ждем подтверждения пользователя перед выходом
    input("Нажмите Enter для выхода...")
    sys.exit(1)  # Завершаем программу с кодом ошибки
```

### 2. stp_server_editor.py - Основной модуль приложения

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPT Server Editor - Основная программа для редактирования настроек сервера Escape from Tarkov

Этот модуль содержит главный класс SPTEditor, который является центральным компонентом
приложения для редактирования настроек сервера SPT-AKI (Single Player Tarkov).

Основные функции:
- Создание и управление главным окном приложения
- Инициализация всех модулей и компонентов
- Обработка пользовательского интерфейса
- Координация работы между различными модулями
- Управление состоянием приложения

Автор: SPT Server Editor Team
Версия: 1.0.0
"""

# Импорт стандартных библиотек Python
import tkinter as tk                    # Основная библиотека для создания GUI
from tkinter import ttk, messagebox, filedialog  # Дополнительные компоненты tkinter
import os                              # Для работы с операционной системой
import sys                             # Для работы с системными параметрами
import orjson as json                  # Быстрая библиотека для работы с JSON (быстрее стандартной)
from pathlib import Path               # Для работы с путями файловой системы
from datetime import datetime          # Для работы с датой и временем

# Импорт системы отладочного логирования
# Система логирования используется для отслеживания работы приложения
try:
    # Импортируем основные функции логирования
    from modules.debug_logger import get_debug_logger, LogCategory, debug, info, warning, error, critical, trace
    # Импортируем декораторы для автоматического логирования
    from modules.debug_logger import log_function_calls, log_performance
except ImportError:
    # Если модуль логирования недоступен, создаем заглушки
    # Это обеспечивает работу приложения даже без системы логирования
    
    def get_debug_logger():
        """Заглушка для получения логгера"""
        return None
    
    class LogCategory:
        """Заглушка для категорий логирования"""
        SYSTEM = "SYSTEM"        # Системные сообщения
        UI = "UI"                # Пользовательский интерфейс
        DATABASE = "DATABASE"    # Работа с базой данных
        FILE_IO = "FILE_IO"      # Файловые операции
        ERROR = "ERROR"          # Ошибки
        PERFORMANCE = "PERFORMANCE"  # Производительность
    
    # Заглушки для функций логирования - ничего не делают
    def debug(msg, category=None, **kwargs): pass      # Отладочные сообщения
    def info(msg, category=None, **kwargs): pass       # Информационные сообщения
    def warning(msg, category=None, **kwargs): pass    # Предупреждения
    def error(msg, category=None, **kwargs): pass      # Ошибки
    def critical(msg, category=None, **kwargs): pass   # Критические ошибки
    def trace(msg, category=None, **kwargs): pass      # Детальные сообщения
    
    def log_function_calls(category=None):
        """Заглушка декоратора для логирования вызовов функций"""
        def decorator(func):
            return func  # Возвращаем функцию без изменений
        return decorator
    
    def log_performance(category=None):
        """Заглушка декоратора для логирования производительности"""
        def decorator(func):
            return func  # Возвращаем функцию без изменений
        return decorator

class SPTEditor:
    """
    Главный класс приложения SPT Server Editor
    
    Этот класс является центральным компонентом приложения и отвечает за:
    - Инициализацию всех компонентов приложения
    - Создание и управление пользовательским интерфейсом
    - Координацию работы между различными модулями
    - Управление состоянием приложения
    
    Атрибуты:
        root: Главное окно tkinter
        server_path: Путь к директории сервера SPT
        database_path: Путь к директории базы данных
        modules: Словарь загруженных модулей
    """
    
    @log_function_calls(LogCategory.SYSTEM)  # Декоратор для логирования вызовов функций
    def __init__(self, root):
        """
        Инициализация главного класса приложения
        
        Args:
            root: Главное окно tkinter, переданное из main()
        """
        info("Инициализация SPTEditor", LogCategory.SYSTEM)  # Логируем начало инициализации
        self.root = root  # Сохраняем ссылку на главное окно
        
        # Определяем пути к серверу и базе данных
        self.server_path = Path(__file__).parent          # Путь к директории сервера (где находится этот файл)
        self.database_path = self.server_path / "database" # Путь к директории базы данных
        
        # Логируем пути для отладки
        debug(f"Путь к серверу: {self.server_path}", LogCategory.SYSTEM)
        debug(f"Путь к базе данных: {self.database_path}", LogCategory.DATABASE)
        
        # Настройка главного окна приложения
        info("Настройка окна приложения", LogCategory.UI)
        setup_resizable_window(self.root, "SPT Server Editor", 1000, 700, 800, 600, fullscreen=True)  # Настраиваем окно
        apply_modern_style()  # Применяем современный стиль
        center_window(self.root, 1000, 700)  # Центрируем окно на экране
        
        # Настройка стилей интерфейса
        self.setup_styles()
        
        # Проверяем наличие кэша предметов
        self.check_items_cache()
        
        # Создаем пользовательский интерфейс
        info("Создание интерфейса", LogCategory.UI)
        self.create_widgets()
        
        # Настраиваем автоматическое масштабирование
        setup_auto_scaling(self.root)
        
        # Загружаем все модули приложения
        self.load_modules()
```

### 3. modules/items_manager.py - Модуль управления предметами

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Items Manager - Модуль для работы с предметами

Этот модуль предоставляет функциональность для управления предметами в игре Escape from Tarkov.
Он включает в себя:
- Просмотр и редактирование предметов
- Поиск и фильтрацию предметов
- Статистику по предметам
- Массовое изменение параметров предметов
- Работу с кэшем предметов

Основные компоненты:
- ItemsManager: Главный класс для управления предметами
- Интерфейс для работы с базой данных предметов
- Интеграция с системой логирования

Автор: SPT Server Editor Team
Версия: 1.0.0
"""

# Импорт стандартных библиотек Python
import tkinter as tk                    # Основная библиотека для создания GUI
from tkinter import ttk, messagebox    # Дополнительные компоненты tkinter
import orjson as json                  # Быстрая библиотека для работы с JSON
from pathlib import Path               # Для работы с путями файловой системы
from typing import Dict, List, Optional, Any, Union  # Аннотации типов для лучшей читаемости кода
from collections import defaultdict, Counter  # Специальные коллекции для подсчета и группировки
import re                              # Регулярные выражения для поиска и фильтрации

class ItemsManager:
    """
    Главный класс модуля управления предметами
    
    Этот класс предоставляет полный функционал для работы с предметами в игре Escape from Tarkov.
    Он включает в себя:
    - Просмотр и редактирование предметов
    - Поиск и фильтрацию по различным критериям
    - Статистику по предметам
    - Массовое изменение параметров
    - Работу с кэшем предметов
    
    Атрибуты:
        parent_window: Родительское окно tkinter
        server_path: Путь к директории сервера SPT
        items_db: Объект для работы с базой данных предметов
        items_cache: Объект для работы с кэшем предметов
        hideout_areas: Объект для работы с зонами убежища
        window: Главное окно модуля
        items_statistics: Статистика по предметам
        prefab_statistics: Статистика по префабам
    """
    
    @log_function_calls(LogCategory.SYSTEM)  # Декоратор для логирования вызовов функций
    def __init__(self, parent_window, server_path: Path):
        """
        Инициализация менеджера предметов
        
        Args:
            parent_window: Родительское окно tkinter
            server_path: Путь к директории сервера SPT
        """
        info("Инициализация ItemsManager", LogCategory.SYSTEM)  # Логируем начало инициализации
        self.parent_window = parent_window  # Сохраняем ссылку на родительское окно
        self.server_path = server_path      # Сохраняем путь к серверу
        
        debug(f"Путь к серверу: {server_path}", LogCategory.SYSTEM)  # Логируем путь для отладки
```

### 4. modules/bulk_parameters_dialog.py - Диалог массового изменения параметров

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bulk Parameters Dialog - Диалог для массового изменения параметров предметов

Этот модуль предоставляет интерфейс для массового изменения параметров предметов.
Он включает в себя:
- Ввод списка ID предметов
- Выбор параметра для изменения
- Валидацию входных данных
- Предварительный просмотр изменений
- Логирование всех операций
- Создание резервных копий

Основные компоненты:
- BulkParametersDialog: Главный класс диалога
- Валидация параметров и значений
- Массовая обработка предметов
- Система логирования операций

Автор: SPT Server Editor Team
Версия: 1.0.0
"""

# Импорт стандартных библиотек Python
import tkinter as tk                    # Основная библиотека для создания GUI
from tkinter import ttk, messagebox, scrolledtext  # Дополнительные компоненты tkinter
from typing import Dict, List, Optional, Any, Callable  # Аннотации типов
from pathlib import Path               # Для работы с путями файловой системы
import threading                       # Для многопоточности
import time                            # Для работы со временем
from datetime import datetime          # Для работы с датой и временем

class BulkParametersDialog:
    """
    Диалог для массового изменения параметров предметов
    
    Этот класс предоставляет полный интерфейс для массового изменения параметров предметов.
    Он включает в себя:
    - Ввод списка ID предметов
    - Выбор параметра для изменения
    - Валидацию входных данных
    - Предварительный просмотр изменений
    - Массовую обработку предметов
    - Логирование всех операций
    
    Атрибуты:
        parent: Родительское окно
        server_path: Путь к серверу SPT
        on_complete: Callback функция при завершении
        items_db: Объект базы данных предметов
        analyzer: Анализатор параметров предметов
        dialog: Главное окно диалога
    """
    
    @log_function_calls(LogCategory.SYSTEM)
    def __init__(self, parent, server_path: Path, on_complete: Optional[Callable] = None):
        """
        Инициализация диалога массового изменения параметров
        
        Args:
            parent: Родительское окно
            server_path: Путь к серверу SPT
            on_complete: Callback функция при завершении
        """
        info("Инициализация BulkParametersDialog", LogCategory.SYSTEM)
        self.parent = parent
        self.server_path = server_path
        self.on_complete = on_complete
        
        debug(f"Путь к серверу: {server_path}", LogCategory.SYSTEM)
        
        # Инициализация модулей для массового изменения
        info("Инициализация модулей для массового изменения", LogCategory.DATABASE)
        self.items_db = ItemsDatabase(server_path)
        self.analyzer = ItemParametersAnalyzer(server_path)
```

### 5. modules/debug_logger.py - Система отладочного логирования

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Logger - Централизованная система отладочного логирования

Этот модуль предоставляет полнофункциональную систему логирования для всего проекта.
Он включает в себя:
- Цветной вывод в консоль
- Сохранение в файл с ротацией
- ZIP архивацию логов
- Многопоточное логирование
- Категоризацию сообщений
- Детальную статистику
- Декораторы для автоматического логирования

Основные компоненты:
- DebugLogger: Главный класс логгера
- LogLevel: Уровни логирования
- LogCategory: Категории логирования
- Colors: Цветовые коды для консоли
- Декораторы для автоматического логирования

Автор: SPT Server Editor Team
Версия: 1.0.0
"""

# Импорт стандартных библиотек Python
import logging                          # Стандартная библиотека логирования
import logging.handlers                 # Обработчики для логирования
import os                              # Для работы с файловой системой
import sys                             # Для работы с системными параметрами
import zipfile                         # Для создания ZIP архивов
import threading                       # Для многопоточности
from datetime import datetime          # Для работы с датой и временем
from pathlib import Path               # Для работы с путями файловой системы
from typing import Any, Dict, List, Optional, Union  # Аннотации типов
from enum import Enum                  # Для создания перечислений
import json                            # Для работы с JSON
import traceback                       # Для работы с трассировкой стека
import inspect                         # Для интроспекции кода

class LogLevel(Enum):
    """Уровни логирования"""
    DEBUG = "DEBUG"        # Отладочные сообщения
    INFO = "INFO"          # Информационные сообщения
    WARNING = "WARNING"    # Предупреждения
    ERROR = "ERROR"        # Ошибки
    CRITICAL = "CRITICAL"  # Критические ошибки
    TRACE = "TRACE"        # Детальные сообщения

class LogCategory(Enum):
    """Категории логирования"""
    SYSTEM = "SYSTEM"          # Системные сообщения
    DATABASE = "DATABASE"      # Работа с базой данных
    UI = "UI"                  # Пользовательский интерфейс
    FILE_IO = "FILE_IO"        # Файловые операции
    NETWORK = "NETWORK"        # Сетевые операции
    CACHE = "CACHE"            # Кэширование
    VALIDATION = "VALIDATION"  # Валидация данных
    PROCESSING = "PROCESSING"  # Обработка данных
    ERROR = "ERROR"            # Ошибки
    PERFORMANCE = "PERFORMANCE"  # Производительность

class DebugLogger:
    """
    Централизованный отладочный логгер
    
    Этот класс предоставляет полнофункциональную систему логирования с:
    - Цветным выводом в консоль
    - Сохранением в файл с автоматической ротацией
    - ZIP архивацией при ротации
    - Многопоточным логированием
    - Категоризацией сообщений
    - Детальной статистикой использования
    
    Атрибуты:
        log_dir: Директория для сохранения логов
        max_file_size: Максимальный размер файла лога
        max_files: Максимальное количество файлов логов
        enable_console: Включить вывод в консоль
        enable_file: Включить сохранение в файл
        logger: Объект стандартного логгера Python
        stats: Статистика использования логгера
    """
    
    def __init__(self, log_dir: Path = None, max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 max_files: int = 10, enable_console: bool = True, enable_file: bool = True):
        """
        Инициализация логгера
        
        Args:
            log_dir: Директория для логов (по умолчанию logs/)
            max_file_size: Максимальный размер файла лога в байтах
            max_files: Максимальное количество файлов логов
            enable_console: Включить вывод в консоль
            enable_file: Включить сохранение в файл
        """
        self.log_dir = log_dir or Path("logs")  # Устанавливаем директорию для логов
        self.max_file_size = max_file_size      # Максимальный размер файла
        self.max_files = max_files              # Максимальное количество файлов
        self.enable_console = enable_console    # Включить консольный вывод
        self.enable_file = enable_file          # Включить файловый вывод
        
        # Создаем директорию для логов
        self.log_dir.mkdir(exist_ok=True)
        
        # Настройка логирования
        self.logger = logging.getLogger("SPT_Server_Editor")  # Создаем логгер
        self.logger.setLevel(logging.DEBUG)                   # Устанавливаем уровень DEBUG
        
        # Очищаем существующие обработчики
        self.logger.handlers.clear()
        
        # Настройка формата
        self.formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(category)-12s | %(caller_module)-20s | %(caller_function)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Обработчик для консоли
        if self.enable_console:
            self.console_handler = logging.StreamHandler(sys.stdout)
            self.console_handler.setLevel(logging.DEBUG)
            self.console_handler.setFormatter(self.formatter)
            self.logger.addHandler(self.console_handler)
        
        # Обработчик для файла
        if self.enable_file:
            self.file_handler = self._create_file_handler()
            self.logger.addHandler(self.file_handler)
        
        # Потокобезопасность
        self.lock = threading.Lock()
        
        # Статистика
        self.stats = {
            'total_logs': 0,
            'by_level': {level.value: 0 for level in LogLevel},
            'by_category': {category.value: 0 for category in LogCategory},
            'start_time': datetime.now()
        }
        
        # Логирование инициализации
        self.info("DebugLogger инициализирован", LogCategory.SYSTEM, 
                extra_data={'log_dir': str(self.log_dir), 'max_file_size': self.max_file_size})
```

## 📋 Принципы комментирования

### 1. Структура комментариев

- **Заголовок модуля**: Описание назначения и функциональности
- **Импорты**: Объяснение назначения каждой библиотеки
- **Классы**: Подробное описание класса, его атрибутов и методов
- **Методы**: Описание параметров, возвращаемых значений и логики
- **Строки кода**: Комментарии к сложным или важным операциям

### 2. Типы комментариев

- **Docstring**: Многострочные комментарии для классов и функций
- **Inline комментарии**: Комментарии к отдельным строкам кода
- **Блочные комментарии**: Комментарии к группам связанных операций
- **TODO комментарии**: Отметки для будущих улучшений

### 3. Стиль комментирования

- Использование русского языка для лучшего понимания
- Подробное объяснение сложной логики
- Указание назначения каждой переменной
- Объяснение алгоритмов и структур данных
- Описание взаимодействия между компонентами

## 🎯 Преимущества подробного комментирования

1. **Читаемость кода**: Легче понимать назначение и логику
2. **Поддержка**: Упрощает внесение изменений и исправление ошибок
3. **Документация**: Код сам документирует себя
4. **Обучение**: Помогает новым разработчикам изучить проект
5. **Отладка**: Упрощает поиск и исправление ошибок

## 📚 Дополнительные ресурсы

- [PEP 257 - Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)
- [PEP 8 - Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

---

**Примечание**: Все комментарии написаны на русском языке для лучшего понимания русскоязычными разработчиками. Комментарии регулярно обновляются при изменении кода.
