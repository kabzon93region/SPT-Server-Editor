# 🔍 Руководство по системе отладочного логирования

## Обзор

Система отладочного логирования SPT Server Editor предоставляет централизованное, цветное, многопоточное логирование с архивацией и детальной аналитикой для всего проекта.

## 🚀 Возможности

### ✨ Основные функции
- **Цветной вывод в консоль** - разные цвета для разных уровней логирования
- **Сохранение в файл** - автоматическая ротация файлов логов
- **Архивация** - автоматическое создание ZIP архивов при ротации
- **Многопоточность** - потокобезопасное логирование
- **Категоризация** - логирование по категориям (SYSTEM, DATABASE, UI, etc.)
- **Детальная информация** - автоматическое определение вызывающего кода
- **Производительность** - измерение времени выполнения функций
- **Статистика** - подробная статистика использования

### 🎨 Цветовая схема
- **DEBUG** - Синий (BRIGHT_BLUE)
- **INFO** - Зеленый (BRIGHT_GREEN)
- **WARNING** - Желтый (BRIGHT_YELLOW)
- **ERROR** - Красный (BRIGHT_RED)
- **CRITICAL** - Красный на белом фоне (RED + BG_WHITE + BOLD)
- **TRACE** - Голубой (BRIGHT_CYAN)

## 📁 Структура файлов

```
modules/
├── debug_logger.py          # Основной модуль логирования
├── logging_integration.py   # Интеграция в модули проекта
└── logging_utils.py         # Утилиты для быстрого доступа

logs/                        # Директория логов
├── spt_editor_20250917.log  # Текущий файл лога
├── spt_editor_20250917.log.1 # Резервные копии
└── logs_archive_*.zip       # Архивы логов
```

## 🔧 Использование

### Базовое логирование

```python
from modules.debug_logger import debug, info, warning, error, critical, trace, LogCategory

# Простое логирование
info("Приложение запущено", LogCategory.SYSTEM)
debug("Отладочная информация", LogCategory.DATABASE)
warning("Предупреждение", LogCategory.UI)
error("Ошибка", LogCategory.ERROR)
critical("Критическая ошибка", LogCategory.ERROR)
trace("Детальная информация", LogCategory.PROCESSING)
```

### Логирование с дополнительными данными

```python
# С дополнительными данными
debug("Обработка данных", LogCategory.DATABASE, 
      extra_data={"count": 100, "type": "items"})

# С исключением
try:
    risky_operation()
except Exception as e:
    error("Ошибка операции", LogCategory.ERROR, exception=e)
```

### Декораторы для автоматического логирования

```python
from modules.debug_logger import log_function_calls, log_performance

@log_function_calls(LogCategory.SYSTEM)
@log_performance(LogCategory.PERFORMANCE)
def my_function(param1, param2):
    # Функция будет автоматически логироваться
    return result
```

### Специализированные функции логирования

```python
from modules.debug_logger import get_debug_logger

logger = get_debug_logger()

# Логирование переменных
logger.log_variable("user_id", 12345, LogCategory.SYSTEM)

# Логирование структур данных
logger.log_data_structure("items_list", [1, 2, 3], LogCategory.DATABASE)

# Логирование производительности
logger.log_performance("database_query", 0.123, LogCategory.PERFORMANCE)
```

## 📊 Категории логирования

| Категория | Описание | Использование |
|-----------|----------|---------------|
| `SYSTEM` | Системные сообщения | Инициализация, общие операции |
| `DATABASE` | Работа с базой данных | Запросы, операции с данными |
| `UI` | Пользовательский интерфейс | События UI, взаимодействие |
| `FILE_IO` | Файловые операции | Чтение, запись файлов |
| `NETWORK` | Сетевые операции | HTTP запросы, API |
| `CACHE` | Кэширование | Операции с кэшем |
| `VALIDATION` | Валидация данных | Проверка входных данных |
| `PROCESSING` | Обработка данных | Массовые операции |
| `ERROR` | Ошибки | Исключения, ошибки |
| `PERFORMANCE` | Производительность | Измерение времени |

## ⚙️ Конфигурация

### Инициализация логгера

```python
from modules.debug_logger import init_debug_logging

logger = init_debug_logging(
    log_dir=Path("logs"),           # Директория для логов
    max_file_size=10 * 1024 * 1024, # Максимальный размер файла (10MB)
    max_files=10,                   # Количество резервных файлов
    enable_console=True,            # Включить вывод в консоль
    enable_file=True                # Включить сохранение в файл
)
```

### Настройка уровней логирования

```python
# Установка уровня логирования
logger.logger.setLevel(logging.DEBUG)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 📈 Статистика и мониторинг

### Получение статистики

```python
stats = logger.get_stats()
print(f"Всего логов: {stats['total_logs']}")
print(f"По уровням: {stats['by_level']}")
print(f"По категориям: {stats['by_category']}")
print(f"Время работы: {stats['uptime_formatted']}")
```

### Создание архива

```python
# Создание архива всех логов
archive_path = logger.create_archive()
print(f"Архив создан: {archive_path}")
```

### Очистка старых логов

```python
# Очистка логов старше 30 дней
logger.cleanup_old_logs(days=30)
```

## 🔄 Интеграция в модули

### Автоматическая интеграция

```python
from modules.logging_integration import LoggingIntegrator

# Интеграция во все модули проекта
integrator = LoggingIntegrator(project_root)
results = integrator.integrate_all_modules()
```

### Ручная интеграция

```python
# Добавление в начало модуля
from modules.debug_logger import get_debug_logger, LogCategory, debug, info, warning, error

# В функциях и методах
def my_function():
    info("Начало выполнения функции", LogCategory.SYSTEM)
    try:
        # код функции
        info("Функция выполнена успешно", LogCategory.SYSTEM)
    except Exception as e:
        error("Ошибка в функции", LogCategory.ERROR, exception=e)
```

## 🎯 Лучшие практики

### 1. Используйте подходящие категории
```python
# ✅ Хорошо
info("Загружен предмет", LogCategory.DATABASE)
debug("Обновлен UI", LogCategory.UI)

# ❌ Плохо
info("Загружен предмет", LogCategory.SYSTEM)  # Неправильная категория
```

### 2. Логируйте важные события
```python
# ✅ Хорошо
info("Пользователь вошел в систему", LogCategory.SYSTEM)
error("Ошибка подключения к базе данных", LogCategory.DATABASE)

# ❌ Плохо
debug("i = 1")  # Избыточное логирование
```

### 3. Используйте дополнительные данные
```python
# ✅ Хорошо
info("Обработано предметов", LogCategory.DATABASE, 
     extra_data={"count": len(items), "duration": 0.123})

# ❌ Плохо
info("Обработано предметов")  # Недостаточно информации
```

### 4. Обрабатывайте исключения
```python
# ✅ Хорошо
try:
    risky_operation()
except Exception as e:
    error("Ошибка операции", LogCategory.ERROR, exception=e)
    # Обработка ошибки

# ❌ Плохо
try:
    risky_operation()
except:
    pass  # Игнорирование ошибок
```

## 🐛 Отладка

### Включение детального логирования

```python
# Установка уровня DEBUG для детального логирования
logger.logger.setLevel(logging.DEBUG)

# Использование TRACE для максимальной детализации
trace("Детальная информация", LogCategory.SYSTEM)
```

### Просмотр логов в реальном времени

```bash
# Windows
Get-Content logs\spt_editor_*.log -Wait

# Linux/Mac
tail -f logs/spt_editor_*.log
```

## 📋 Примеры использования

### Логирование в классе

```python
class ItemsManager:
    def __init__(self):
        self.logger = get_debug_logger()
        info("Инициализация ItemsManager", LogCategory.SYSTEM)
    
    def load_items(self):
        info("Начало загрузки предметов", LogCategory.DATABASE)
        try:
            items = self.load_from_file()
            info("Предметы загружены", LogCategory.DATABASE, 
                 extra_data={"count": len(items)})
            return items
        except Exception as e:
            error("Ошибка загрузки предметов", LogCategory.DATABASE, exception=e)
            raise
```

### Логирование производительности

```python
@log_performance(LogCategory.PERFORMANCE)
def process_large_dataset(data):
    start_time = time.time()
    # Обработка данных
    result = process_data(data)
    duration = time.time() - start_time
    
    info("Обработка завершена", LogCategory.PROCESSING,
         extra_data={"items": len(data), "duration": duration})
    return result
```

### Логирование UI событий

```python
def on_button_click(self):
    info("Кнопка нажата", LogCategory.UI, 
         extra_data={"button": "save", "user": self.current_user})
    
    try:
        self.save_data()
        info("Данные сохранены", LogCategory.UI)
    except Exception as e:
        error("Ошибка сохранения", LogCategory.UI, exception=e)
```

## 🔧 Устранение неполадок

### Проблема: Логи не отображаются в консоли
**Решение:** Проверьте, что `enable_console=True` при инициализации

### Проблема: Логи не сохраняются в файл
**Решение:** Проверьте права доступа к директории `logs/` и `enable_file=True`

### Проблема: Слишком много логов
**Решение:** Увеличьте уровень логирования или используйте более специфичные категории

### Проблема: Медленная работа
**Решение:** Отключите детальное логирование в продакшене, используйте `logging.INFO` или выше

## 📚 Дополнительные ресурсы

- [Техническая документация](TECHNICAL_DOCUMENTATION.md)
- [Руководство разработчика](DEVELOPER_GUIDE.md)
- [Тестовый скрипт](test_debug_logging.py)

---

**Примечание:** Система логирования автоматически интегрирована во все модули проекта. Для отключения логирования в продакшене измените уровень логирования на `logging.WARNING` или выше.
