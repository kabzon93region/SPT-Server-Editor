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

# Инициализация логирования loguru
# Система логирования должна быть инициализирована до импорта других модулей
try:
    # Импортируем необходимые функции из модуля логирования loguru
    from modules.loguru_logger import init_loguru_logging, LogCategory, error, critical, info
    
    # Инициализируем систему логирования с настройками:
    loguru_logger = init_loguru_logging(
        log_dir=current_dir / "logs",           # Директория для сохранения логов
        max_file_size=10 * 1024 * 1024,        # Максимальный размер файла лога (10MB)
        max_files=10                            # Количество резервных файлов логов
    )
    
    # Логируем успешную инициализацию приложения
    info("SPT Server Editor запускается", LogCategory.SYSTEM)
    
except Exception as e:
    # Если не удалось инициализировать логирование, выводим ошибку в консоль
    print(f"Ошибка инициализации логирования: {e}")
    loguru_logger = None  # Устанавливаем логгер в None для проверок

# Глобальная обработка исключений
def handle_exception(exc_type, exc_value, exc_traceback):
    """Глобальная обработка необработанных исключений"""
    if loguru_logger:
        critical(f"Необработанное исключение: {exc_type.__name__}: {exc_value}", 
                LogCategory.ERROR, exception=exc_value)
    else:
        print(f"Необработанное исключение: {exc_type.__name__}: {exc_value}")
        import traceback
        traceback.print_exception(exc_type, exc_value, exc_traceback)

# Устанавливаем глобальный обработчик исключений
sys.excepthook = handle_exception

# Импорт и запуск основного модуля приложения
try:
    # Импортируем главную функцию из основного модуля приложения
    from stp_server_editor import main
    
    # Проверяем, что скрипт запущен напрямую (а не импортирован)
    if __name__ == "__main__":
        # Логируем запуск главного приложения, если логгер доступен
        if loguru_logger:
            info("Запуск главного приложения", LogCategory.SYSTEM)
        
        # Запускаем главную функцию приложения
        main()
        
except ImportError as e:
    # Обработка ошибки импорта модулей
    error_msg = f"Ошибка импорта: {e}"
    
    # Логируем критическую ошибку, если логгер доступен
    if loguru_logger:
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
    if loguru_logger:
        critical(error_msg, LogCategory.SYSTEM, exception=e)
    else:
        # Иначе выводим в консоль
        print(error_msg)
    
    # Ждем подтверждения пользователя перед выходом
    input("Нажмите Enter для выхода...")
    sys.exit(1)  # Завершаем программу с кодом ошибки
