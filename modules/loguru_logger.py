"""
Модуль логирования на основе loguru
Предоставляет цветное логирование с тегами и категориями
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional
from loguru import logger
import orjson as json
import traceback
from datetime import datetime
from enum import Enum
import functools


class LogLevel(Enum):
    """Уровни логирования"""
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(Enum):
    """Категории логирования"""
    SYSTEM = "SYSTEM"
    UI = "UI"
    DATABASE = "DATABASE"
    FILE = "FILE"
    NETWORK = "NETWORK"
    PERFORMANCE = "PERFORMANCE"
    ERROR = "ERROR"
    USER = "USER"
    MODULE = "MODULE"
    CRAFT = "CRAFT"
    ITEMS = "ITEMS"
    TRADER = "TRADER"


class LoguruLogger:
    """Класс для управления логированием на основе loguru"""
    
    def __init__(self, log_dir: Path, max_file_size: int = 10 * 1024 * 1024, max_files: int = 10):
        """
        Инициализация логгера
        
        Args:
            log_dir: Директория для логов
            max_file_size: Максимальный размер файла лога
            max_files: Максимальное количество файлов логов
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Удаляем все существующие обработчики
        logger.remove()
        
        # Настройка консольного вывода с цветами
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{extra[category]: <12}</cyan> | <blue>{name: <20}</blue> | <magenta>{function: <20}</magenta> | <level>{message}</level>",
            level="DEBUG",
            colorize=True,
            backtrace=True,
            diagnose=True
        )
        
        # Настройка файлового логирования
        log_file = self.log_dir / "spt_editor.log"
        logger.add(
            str(log_file),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[category]: <12} | {name: <20} | {function: <20} | {message}",
            level="DEBUG",
            rotation=max_file_size,
            retention=max_files,
            compression="zip",
            backtrace=True,
            diagnose=True
        )
        
        # Настройка логирования ошибок в отдельный файл
        error_log_file = self.log_dir / "errors.log"
        logger.add(
            str(error_log_file),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[category]: <12} | {name: <20} | {function: <20} | {message}\n{traceback}",
            level="ERROR",
            rotation=max_file_size,
            retention=max_files,
            compression="zip",
            backtrace=True,
            diagnose=True
        )
        
        # Настройка логирования производительности
        perf_log_file = self.log_dir / "performance.log"
        logger.add(
            str(perf_log_file),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[category]: <12} | {name: <20} | {function: <20} | {message}",
            level="INFO",
            filter=lambda record: record["extra"].get("category") == "PERFORMANCE",
            rotation=max_file_size,
            retention=max_files,
            compression="zip"
        )
        
        self.stats = {
            'total_logs': 0,
            'by_level': {level.value: 0 for level in LogLevel},
            'by_category': {category.value: 0 for category in LogCategory}
        }
    
    def _safe_serialize(self, obj: Any) -> str:
        """Безопасная сериализация объекта в JSON"""
        try:
            if obj is None:
                return "null"
            elif isinstance(obj, (str, int, float, bool)):
                return json.dumps(obj, ensure_ascii=False)
            elif isinstance(obj, (list, tuple)):
                return json.dumps([self._safe_serialize(item) for item in obj], ensure_ascii=False)
            elif isinstance(obj, dict):
                return json.dumps({k: self._safe_serialize(v) for k, v in obj.items()}, ensure_ascii=False)
            else:
                return f'"{str(type(obj).__name__)}"'
        except Exception:
            return f'"{str(type(obj).__name__)}"'
    
    def _log(self, level: LogLevel, message: str, category: LogCategory = LogCategory.SYSTEM, 
             extra_data: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None):
        """Базовый метод логирования"""
        # Обновляем статистику
        self.stats['total_logs'] += 1
        self.stats['by_level'][level.value] += 1
        self.stats['by_category'][category.value] += 1
        
        # Подготавливаем дополнительные данные
        extra = {
            'category': category.value,
            'timestamp': datetime.now().isoformat()
        }
        
        if extra_data:
            extra['data'] = self._safe_serialize(extra_data)
        
        if exception:
            extra['exception'] = str(exception)
            extra['traceback'] = traceback.format_exc()
        
        # Логируем с помощью loguru
        log_func = getattr(logger, level.value.lower())
        log_func(message, **extra)
    
    def trace(self, message: str, category: LogCategory = LogCategory.SYSTEM, 
              extra_data: Optional[Dict[str, Any]] = None):
        """Логирование уровня TRACE"""
        self._log(LogLevel.TRACE, message, category, extra_data)
    
    def debug(self, message: str, category: LogCategory = LogCategory.SYSTEM, 
              extra_data: Optional[Dict[str, Any]] = None):
        """Логирование уровня DEBUG"""
        self._log(LogLevel.DEBUG, message, category, extra_data)
    
    def info(self, message: str, category: LogCategory = LogCategory.SYSTEM, 
             extra_data: Optional[Dict[str, Any]] = None):
        """Логирование уровня INFO"""
        self._log(LogLevel.INFO, message, category, extra_data)
    
    def success(self, message: str, category: LogCategory = LogCategory.SYSTEM, 
                extra_data: Optional[Dict[str, Any]] = None):
        """Логирование уровня SUCCESS"""
        self._log(LogLevel.SUCCESS, message, category, extra_data)
    
    def warning(self, message: str, category: LogCategory = LogCategory.SYSTEM, 
                extra_data: Optional[Dict[str, Any]] = None):
        """Логирование уровня WARNING"""
        self._log(LogLevel.WARNING, message, category, extra_data)
    
    def error(self, message: str, category: LogCategory = LogCategory.ERROR, 
              extra_data: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None):
        """Логирование уровня ERROR"""
        self._log(LogLevel.ERROR, message, category, extra_data, exception)
    
    def critical(self, message: str, category: LogCategory = LogCategory.ERROR, 
                 extra_data: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None):
        """Логирование уровня CRITICAL"""
        self._log(LogLevel.CRITICAL, message, category, extra_data, exception)
    
    def log_function_call(self, func_name: str, args: tuple, kwargs: dict, category: LogCategory = LogCategory.SYSTEM):
        """Логирование вызова функции"""
        self.trace(f"Вызов функции: {func_name}", category, {
            'function': func_name,
            'args': self._safe_serialize(args),
            'kwargs': self._safe_serialize(kwargs)
        })
    
    def log_performance(self, operation: str, duration_ms: float, category: LogCategory = LogCategory.PERFORMANCE):
        """Логирование производительности"""
        self.info(f"Производительность: {operation} - {duration_ms:.4f}s", category, {
            'operation': operation,
            'duration_ms': duration_ms,
            'duration_seconds': duration_ms / 1000
        })
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики логирования"""
        return self.stats.copy()


# Глобальный экземпляр логгера
_logger_instance: Optional[LoguruLogger] = None


def init_loguru_logging(log_dir: Path, max_file_size: int = 10 * 1024 * 1024, max_files: int = 10) -> LoguruLogger:
    """
    Инициализация системы логирования loguru
    
    Args:
        log_dir: Директория для логов
        max_file_size: Максимальный размер файла лога
        max_files: Максимальное количество файлов логов
    
    Returns:
        LoguruLogger: Экземпляр логгера
    """
    global _logger_instance
    _logger_instance = LoguruLogger(log_dir, max_file_size, max_files)
    _logger_instance.info("LoguruLogger инициализирован", LogCategory.SYSTEM, {
        'log_dir': str(log_dir),
        'max_file_size': max_file_size
    })
    return _logger_instance


def get_loguru_logger() -> LoguruLogger:
    """Получение глобального экземпляра логгера"""
    global _logger_instance
    if _logger_instance is None:
        raise RuntimeError("Логгер не инициализирован. Вызовите init_loguru_logging() сначала.")
    return _logger_instance


# Функции для удобного использования
def trace(message: str, category: LogCategory = LogCategory.SYSTEM, extra_data: Optional[Dict[str, Any]] = None):
    """Логирование уровня TRACE"""
    get_loguru_logger().trace(message, category, extra_data)


def debug(message: str, category: LogCategory = LogCategory.SYSTEM, extra_data: Optional[Dict[str, Any]] = None):
    """Логирование уровня DEBUG"""
    get_loguru_logger().debug(message, category, extra_data)


def info(message: str, category: LogCategory = LogCategory.SYSTEM, extra_data: Optional[Dict[str, Any]] = None):
    """Логирование уровня INFO"""
    get_loguru_logger().info(message, category, extra_data)


def success(message: str, category: LogCategory = LogCategory.SYSTEM, extra_data: Optional[Dict[str, Any]] = None):
    """Логирование уровня SUCCESS"""
    get_loguru_logger().success(message, category, extra_data)


def warning(message: str, category: LogCategory = LogCategory.SYSTEM, extra_data: Optional[Dict[str, Any]] = None):
    """Логирование уровня WARNING"""
    get_loguru_logger().warning(message, category, extra_data)


def error(message: str, category: LogCategory = LogCategory.ERROR, extra_data: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None):
    """Логирование уровня ERROR"""
    get_loguru_logger().error(message, category, extra_data, exception)


def critical(message: str, category: LogCategory = LogCategory.ERROR, extra_data: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None):
    """Логирование уровня CRITICAL"""
    get_loguru_logger().critical(message, category, extra_data, exception)


def log_function_call(func_name: str, args: tuple, kwargs: dict, category: LogCategory = LogCategory.SYSTEM):
    """Логирование вызова функции"""
    get_loguru_logger().log_function_call(func_name, args, kwargs, category)


def log_performance(operation: str, duration_ms: float, category: LogCategory = LogCategory.PERFORMANCE):
    """Логирование производительности"""
    get_loguru_logger().log_performance(operation, duration_ms, category)


# Декораторы для автоматического логирования
def log_function_calls(category: LogCategory = LogCategory.SYSTEM):
    """Декоратор для логирования вызовов функций"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            log_function_call(func.__name__, args, kwargs, category)
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error(f"Ошибка в функции {func.__name__}", category, exception=e)
                raise
        return wrapper
    return decorator


def log_performance_decorator(category: LogCategory = LogCategory.PERFORMANCE):
    """Декоратор для логирования производительности функций"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                log_performance(f"{func.__name__} (SUCCESS)", duration_ms, category)
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                log_performance(f"{func.__name__} (ERROR)", duration_ms, category)
                error(f"Ошибка в функции {func.__name__}", category, exception=e)
                raise
        return wrapper
    return decorator
