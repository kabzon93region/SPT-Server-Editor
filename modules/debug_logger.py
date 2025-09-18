#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Logger - Централизованная система отладочного логирования
"""

import logging
import logging.handlers
import os
import sys
import zipfile
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from enum import Enum
import json
import traceback
import inspect

# Цвета для консольного вывода
class Colors:
    """ANSI цветовые коды для консоли"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    
    # Основные цвета
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Яркие цвета
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Фоновые цвета
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

class LogLevel(Enum):
    """Уровни логирования"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    TRACE = "TRACE"  # Дополнительный уровень для детального отслеживания

class LogCategory(Enum):
    """Категории логов"""
    SYSTEM = "SYSTEM"
    DATABASE = "DATABASE"
    UI = "UI"
    FILE_IO = "FILE_IO"
    NETWORK = "NETWORK"
    CACHE = "CACHE"
    VALIDATION = "VALIDATION"
    PROCESSING = "PROCESSING"
    ERROR = "ERROR"
    PERFORMANCE = "PERFORMANCE"

class DebugLogger:
    """Централизованный отладочный логгер"""
    
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
        self.log_dir = log_dir or Path("logs")
        self.max_file_size = max_file_size
        self.max_files = max_files
        self.enable_console = enable_console
        self.enable_file = enable_file
        
        # Создаем директорию для логов
        self.log_dir.mkdir(exist_ok=True)
        
        # Настройка логирования
        self.logger = logging.getLogger("SPT_Server_Editor")
        self.logger.setLevel(logging.DEBUG)
        
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
    
    def _create_file_handler(self) -> logging.FileHandler:
        """Создание обработчика файла с ротацией"""
        log_file = self.log_dir / f"spt_editor_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Создаем кастомный обработчик с ротацией
        handler = RotatingFileHandler(
            log_file, 
            maxBytes=self.max_file_size, 
            backupCount=self.max_files,
            encoding='utf-8'
        )
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(self.formatter)
        
        return handler
    
    def _get_caller_info(self) -> Dict[str, str]:
        """Получение информации о вызывающем коде"""
        frame = inspect.currentframe().f_back.f_back  # Пропускаем _log и вызывающий метод
        return {
            'module': frame.f_globals.get('__name__', 'unknown').split('.')[-1],
            'function': frame.f_code.co_name,
            'filename': os.path.basename(frame.f_code.co_filename),
            'lineno': frame.f_lineno
        }
    
    def _colorize_message(self, level: LogLevel, message: str) -> str:
        """Цветовое выделение сообщения для консоли"""
        if not self.enable_console:
            return message
        
        color_map = {
            LogLevel.DEBUG: Colors.BRIGHT_BLUE,
            LogLevel.INFO: Colors.BRIGHT_GREEN,
            LogLevel.WARNING: Colors.BRIGHT_YELLOW,
            LogLevel.ERROR: Colors.BRIGHT_RED,
            LogLevel.CRITICAL: Colors.RED + Colors.BG_WHITE + Colors.BOLD,
            LogLevel.TRACE: Colors.BRIGHT_CYAN
        }
        
        color = color_map.get(level, Colors.WHITE)
        return f"{color}{message}{Colors.RESET}"
    
    def _log(self, level: LogLevel, message: str, category: LogCategory = LogCategory.SYSTEM, 
             extra_data: Dict[str, Any] = None, exception: Exception = None):
        """Базовый метод логирования"""
        with self.lock:
            # Получаем информацию о вызывающем коде
            caller_info = self._get_caller_info()
            
            # Формируем полное сообщение
            full_message = message
            if extra_data:
                full_message += f" | Extra: {json.dumps(extra_data, ensure_ascii=False, indent=2)}"
            
            if exception:
                full_message += f" | Exception: {str(exception)} | Traceback: {traceback.format_exc()}"
            
            # Обновляем статистику
            self.stats['total_logs'] += 1
            self.stats['by_level'][level.value] += 1
            self.stats['by_category'][category.value] += 1
            
            # Логируем
            log_level = getattr(logging, level.value) if hasattr(logging, level.value) else logging.DEBUG
            self.logger.log(
                log_level,
                full_message,
                extra={
                    'category': category.value,
                    'caller_module': caller_info['module'],
                    'caller_function': caller_info['function'],
                    'caller_filename': caller_info['filename'],
                    'caller_lineno': caller_info['lineno']
                }
            )
            
            # Цветной вывод в консоль
            if self.enable_console:
                colored_message = self._colorize_message(level, full_message)
                print(colored_message)
    
    def debug(self, message: str, category: LogCategory = LogCategory.SYSTEM, 
              extra_data: Dict[str, Any] = None):
        """Отладочное сообщение"""
        self._log(LogLevel.DEBUG, message, category, extra_data)
    
    def info(self, message: str, category: LogCategory = LogCategory.SYSTEM, 
             extra_data: Dict[str, Any] = None):
        """Информационное сообщение"""
        self._log(LogLevel.INFO, message, category, extra_data)
    
    def warning(self, message: str, category: LogCategory = LogCategory.SYSTEM, 
                extra_data: Dict[str, Any] = None):
        """Предупреждение"""
        self._log(LogLevel.WARNING, message, category, extra_data)
    
    def error(self, message: str, category: LogCategory = LogCategory.ERROR, 
              extra_data: Dict[str, Any] = None, exception: Exception = None):
        """Ошибка"""
        self._log(LogLevel.ERROR, message, category, extra_data, exception)
    
    def critical(self, message: str, category: LogCategory = LogCategory.ERROR, 
                 extra_data: Dict[str, Any] = None, exception: Exception = None):
        """Критическая ошибка"""
        self._log(LogLevel.CRITICAL, message, category, extra_data, exception)
    
    def trace(self, message: str, category: LogCategory = LogCategory.SYSTEM, 
              extra_data: Dict[str, Any] = None):
        """Детальное отслеживание"""
        self._log(LogLevel.TRACE, message, category, extra_data)
    
    def log_function_call(self, func_name: str, args: tuple = None, kwargs: dict = None, 
                         category: LogCategory = LogCategory.SYSTEM):
        """Логирование вызова функции"""
        extra_data = {
            'function': func_name,
            'args': args,
            'kwargs': kwargs
        }
        self.trace(f"Вызов функции: {func_name}", category, extra_data)
    
    def log_function_result(self, func_name: str, result: Any = None, 
                           category: LogCategory = LogCategory.SYSTEM):
        """Логирование результата функции"""
        extra_data = {
            'function': func_name,
            'result': str(result) if result is not None else None
        }
        self.trace(f"Результат функции: {func_name}", category, extra_data)
    
    def log_variable(self, var_name: str, value: Any, category: LogCategory = LogCategory.SYSTEM):
        """Логирование переменной"""
        extra_data = {
            'variable': var_name,
            'value': str(value),
            'type': type(value).__name__
        }
        self.debug(f"Переменная: {var_name} = {value}", category, extra_data)
    
    def log_data_structure(self, name: str, data: Any, category: LogCategory = LogCategory.SYSTEM):
        """Логирование структуры данных"""
        extra_data = {
            'structure': name,
            'data': data,
            'type': type(data).__name__,
            'size': len(data) if hasattr(data, '__len__') else 'N/A'
        }
        self.debug(f"Структура данных: {name}", category, extra_data)
    
    def log_performance(self, operation: str, duration: float, category: LogCategory = LogCategory.PERFORMANCE):
        """Логирование производительности"""
        extra_data = {
            'operation': operation,
            'duration_ms': round(duration * 1000, 2),
            'duration_seconds': round(duration, 4)
        }
        self.info(f"Производительность: {operation} - {duration:.4f}s", category, extra_data)
    
    def create_archive(self) -> Path:
        """Создание архива всех логов"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = self.log_dir / f"logs_archive_{timestamp}.zip"
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for log_file in self.log_dir.glob("*.log"):
                zipf.write(log_file, log_file.name)
        
        self.info(f"Создан архив логов: {archive_path}", LogCategory.SYSTEM)
        return archive_path
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики логирования"""
        uptime = datetime.now() - self.stats['start_time']
        self.stats['uptime_seconds'] = uptime.total_seconds()
        self.stats['uptime_formatted'] = str(uptime)
        return self.stats.copy()
    
    def cleanup_old_logs(self, days: int = 30):
        """Очистка старых логов"""
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        cleaned_count = 0
        
        for log_file in self.log_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_date:
                log_file.unlink()
                cleaned_count += 1
        
        self.info(f"Очищено {cleaned_count} старых логов (старше {days} дней)", LogCategory.SYSTEM)

class RotatingFileHandler(logging.handlers.RotatingFileHandler):
    """Кастомный обработчик с ротацией файлов"""
    
    def doRollover(self):
        """Переопределение метода ротации для архивации"""
        if self.stream:
            self.stream.close()
            self.stream = None
        
        # Переименовываем файлы
        for i in range(self.backupCount - 1, 0, -1):
            sfn = self.rotation_filename(f"{self.baseFilename}.{i}")
            dfn = self.rotation_filename(f"{self.baseFilename}.{i + 1}")
            if os.path.exists(sfn):
                if os.path.exists(dfn):
                    os.remove(dfn)
                os.rename(sfn, dfn)
        
        dfn = self.rotation_filename(f"{self.baseFilename}.1")
        if os.path.exists(dfn):
            os.remove(dfn)
        os.rename(self.baseFilename, dfn)
        
        # Создаем архив при ротации
        if hasattr(self, 'logger') and hasattr(self.logger, 'create_archive'):
            self.logger.create_archive()
        
        if not self.delay:
            self.stream = self._open()

# Глобальный экземпляр логгера
_debug_logger: Optional[DebugLogger] = None

def get_debug_logger() -> DebugLogger:
    """Получение глобального экземпляра логгера"""
    global _debug_logger
    if _debug_logger is None:
        _debug_logger = DebugLogger()
    return _debug_logger

def init_debug_logging(log_dir: Path = None, **kwargs) -> DebugLogger:
    """Инициализация отладочного логирования"""
    global _debug_logger
    _debug_logger = DebugLogger(log_dir, **kwargs)
    return _debug_logger

# Декораторы для автоматического логирования
def log_function_calls(category: LogCategory = LogCategory.SYSTEM):
    """Декоратор для логирования вызовов функций"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_debug_logger()
            logger.log_function_call(func.__name__, args, kwargs, category)
            try:
                result = func(*args, **kwargs)
                logger.log_function_result(func.__name__, result, category)
                return result
            except Exception as e:
                logger.error(f"Ошибка в функции {func.__name__}", category, exception=e)
                raise
        return wrapper
    return decorator

def log_performance(category: LogCategory = LogCategory.PERFORMANCE):
    """Декоратор для логирования производительности"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_debug_logger()
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                logger.log_performance(func.__name__, duration, category)
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                logger.log_performance(f"{func.__name__} (ERROR)", duration, category)
                raise
        return wrapper
    return decorator

# Удобные функции для быстрого доступа
def debug(message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs):
    """Быстрый доступ к debug"""
    get_debug_logger().debug(message, category, **kwargs)

def info(message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs):
    """Быстрый доступ к info"""
    get_debug_logger().info(message, category, **kwargs)

def warning(message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs):
    """Быстрый доступ к warning"""
    get_debug_logger().warning(message, category, **kwargs)

def error(message: str, category: LogCategory = LogCategory.ERROR, **kwargs):
    """Быстрый доступ к error"""
    get_debug_logger().error(message, category, **kwargs)

def critical(message: str, category: LogCategory = LogCategory.ERROR, **kwargs):
    """Быстрый доступ к critical"""
    get_debug_logger().critical(message, category, **kwargs)

def trace(message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs):
    """Быстрый доступ к trace"""
    get_debug_logger().trace(message, category, **kwargs)

if __name__ == "__main__":
    # Тестирование системы логирования
    logger = init_debug_logging()
    
    # Тестируем разные уровни
    logger.debug("Тестовое отладочное сообщение", LogCategory.SYSTEM)
    logger.info("Тестовое информационное сообщение", LogCategory.DATABASE)
    logger.warning("Тестовое предупреждение", LogCategory.UI)
    logger.error("Тестовая ошибка", LogCategory.ERROR)
    logger.critical("Тестовая критическая ошибка", LogCategory.ERROR)
    logger.trace("Тестовое детальное сообщение", LogCategory.PROCESSING)
    
    # Тестируем дополнительные функции
    logger.log_variable("test_var", 42, LogCategory.SYSTEM)
    logger.log_data_structure("test_list", [1, 2, 3, 4, 5], LogCategory.SYSTEM)
    logger.log_performance("test_operation", 0.123, LogCategory.PERFORMANCE)
    
    # Показываем статистику
    print("\nСтатистика логирования:")
    stats = logger.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
