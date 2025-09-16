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

# Импорт утилит для UI
# Утилиты для работы с пользовательским интерфейсом
try:
    # Импортируем функции для настройки окна и стилей
    from modules.ui_utils import setup_resizable_window, apply_modern_style, center_window, setup_auto_scaling
except ImportError:
    # Если утилиты недоступны, создаем заглушки
    # Это обеспечивает работу приложения даже без модуля ui_utils
    
    def setup_resizable_window(window, title, width=1200, height=800, min_width=800, min_height=600, fullscreen=True):
        """
        Заглушка для настройки масштабируемого окна
        
        Args:
            window: Объект окна tkinter
            title: Заголовок окна
            width: Ширина окна
            height: Высота окна
            min_width: Минимальная ширина
            min_height: Минимальная высота
            fullscreen: Включить полноэкранный режим
        """
        window.title(title)                                    # Устанавливаем заголовок окна
        window.geometry(f"{width}x{height}")                   # Устанавливаем размер окна
        window.minsize(min_width, min_height)                  # Устанавливаем минимальный размер
        window.resizable(True, True)                           # Разрешаем изменение размера
        if fullscreen:                                         # Если включен полноэкранный режим
            window.state('normal')                             # Устанавливаем нормальное состояние
    
    def apply_modern_style():
        """Заглушка для применения современного стиля"""
        style = ttk.Style()                                    # Создаем объект стиля
        try:
            style.theme_use('clam')                            # Пытаемся использовать тему 'clam'
        except:
            pass                                               # Игнорируем ошибки
    
    def center_window(window, width, height):
        """
        Заглушка для центрирования окна на экране
        
        Args:
            window: Объект окна tkinter
            width: Ширина окна
            height: Высота окна
        """
        screen_width = window.winfo_screenwidth()              # Получаем ширину экрана
        screen_height = window.winfo_screenheight()            # Получаем высоту экрана
        x = (screen_width - width) // 2                        # Вычисляем позицию X для центрирования
        y = (screen_height - height) // 2                      # Вычисляем позицию Y для центрирования
        window.geometry(f"{width}x{height}+{x}+{y}")           # Устанавливаем размер и позицию окна
    
    def setup_auto_scaling(parent):
        """Заглушка для настройки автоматического масштабирования"""
        pass  # Ничего не делаем

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
    
    def setup_styles(self):
        """
        Настройка стилей интерфейса
        
        Этот метод настраивает внешний вид всех элементов интерфейса,
        включая шрифты, отступы и цвета для различных типов виджетов.
        """
        style = ttk.Style()  # Создаем объект для работы со стилями
        style.theme_use('clam')  # Используем тему 'clam' как основу
        
        # Настройка стилей для различных типов меток (Label)
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))    # Стиль для заголовков
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))   # Стиль для подзаголовков
        style.configure('Info.TLabel', font=('Arial', 10))             # Стиль для информационного текста
        
        # Настройка стилей для кнопок
        style.configure('Module.TButton', padding=(10, 5))  # Стиль для кнопок модулей (больше отступы)
        style.configure('Action.TButton', padding=(5, 2))   # Стиль для кнопок действий (меньше отступы)
    
    def check_items_cache(self):
        """
        Проверка справочника предметов и предложение обновления
        
        Этот метод проверяет наличие и актуальность кэша предметов.
        Если кэш отсутствует или устарел, предлагает пользователю обновить его.
        """
        # Определяем пути к файлам кэша предметов
        readable_cache_file = self.server_path / "cache" / "items_readable.json"  # Читаемый кэш
        full_cache_file = self.server_path / "cache" / "items_cache.json"         # Полный кэш
        
        # Выбираем файл для проверки (приоритет отдается читаемому кэшу)
        cache_file = None
        if readable_cache_file.exists() and readable_cache_file.stat().st_size > 0:  # Если читаемый кэш существует и не пустой
            cache_file = readable_cache_file
        elif full_cache_file.exists() and full_cache_file.stat().st_size > 0:        # Если полный кэш существует и не пустой
            cache_file = full_cache_file
        
        # Инициализируем переменные для проверки необходимости обновления
        should_offer_update = False  # Флаг необходимости обновления
        reason = ""                  # Причина обновления
        
        if not cache_file or not cache_file.exists():  # Если кэш не найден
            # Справочник не существует
            should_offer_update = True
            reason = "Справочник предметов не найден"
            print(f"INFO: Предложение обновления - {reason}")
        else:
            # Справочник существует, проверяем дату последнего обновления
            try:
                # Получаем время последней модификации файла
                mod_time = cache_file.stat().st_mtime  # Время модификации в секундах с эпохи Unix
                last_update = datetime.fromtimestamp(mod_time)  # Преобразуем в объект datetime
                
                # Проверяем возраст справочника (30 дней)
                days_old = (datetime.now() - last_update).days
                
                if days_old > 30:
                    # Справочник устарел
                    should_offer_update = True
                    reason = f"Справочник предметов не обновлялся {days_old} дней"
                    print(f"INFO: Предложение обновления - {reason}")
                else:
                    print(f"INFO: Справочник актуален (обновлялся {days_old} дней назад), обновление не предлагается")
            except Exception as e:
                # Ошибка при проверке файла
                should_offer_update = True
                reason = f"Ошибка при проверке справочника: {str(e)}"
                print(f"ERROR: {reason}")
        
        # Предлагаем обновление только если нужно
        if should_offer_update:
            if "не найден" in reason:
                message = f"{reason}.\n\nХотите запустить сканер для создания справочника?\nЭто может занять несколько минут."
                title = "Справочник предметов не найден"
            else:
                # Получаем информацию о последнем обновлении для устаревшего справочника
                try:
                    mod_time = cache_file.stat().st_mtime
                    last_update = datetime.fromtimestamp(mod_time)
                    last_update_str = last_update.strftime('%d.%m.%Y %H:%M')
                except:
                    last_update_str = "неизвестно"
                
                message = f"{reason}.\nПоследнее обновление: {last_update_str}\n\nХотите обновить справочник?\nЭто может занять несколько минут."
                title = "Справочник предметов устарел"
            
            result = messagebox.askyesno(title, message, icon='question')
            
            if result:
                self.launch_scanner()
                return
    
    def launch_scanner(self):
        """Запуск сканера с окном прогресса"""
        try:
            from modules.scan_progress_window import ScanProgressWindow
            
            def on_scan_complete():
                """Обработка завершения сканирования"""
                self.update_cache_status()
                messagebox.showinfo("Сканирование завершено", 
                                  "Справочник предметов успешно обновлен!")
                # Показываем основное окно обратно
                self.root.deiconify()
            
            # Скрываем основное окно
            self.root.withdraw()
            
            # Создаем окно прогресса
            progress_window = ScanProgressWindow(self.root, self.server_path, on_scan_complete)
            
            # Добавляем обработчик закрытия окна сканера
            def on_scanner_close():
                # Показываем основное окно обратно
                self.root.deiconify()
                # Уничтожаем окно сканера
                progress_window.destroy()
            
            # Привязываем обработчик к закрытию окна сканера
            progress_window.protocol("WM_DELETE_WINDOW", on_scanner_close)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при запуске сканера: {str(e)}")
            # Показываем основное окно обратно в случае ошибки
            self.root.deiconify()
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="SPT Server Editor", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Информация о сервере
        info_frame = ttk.LabelFrame(main_frame, text="Информация о сервере", padding="10")
        info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.server_path_label = ttk.Label(info_frame, text=f"Путь к серверу: {self.server_path}")
        self.server_path_label.grid(row=0, column=0, sticky=tk.W)
        
        self.database_status_label = ttk.Label(info_frame, text="", style='Info.TLabel')
        self.database_status_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        self.cache_status_label = ttk.Label(info_frame, text="", style='Info.TLabel')
        self.cache_status_label.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        
        # Модули
        modules_frame = ttk.LabelFrame(main_frame, text="Модули редактирования", padding="10")
        modules_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # Создание фрейма для кнопок модулей
        self.modules_container = ttk.Frame(modules_frame)
        self.modules_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        modules_frame.columnconfigure(0, weight=1)
        modules_frame.rowconfigure(0, weight=1)
        self.modules_container.columnconfigure(0, weight=1)
        
        
        # Кнопки управления
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(control_frame, text="Обновить модули", command=self.load_modules, style='Action.TButton').grid(row=0, column=0, padx=(0, 10))
        ttk.Button(control_frame, text="Обновить справочник", command=self.launch_scanner, style='Action.TButton').grid(row=0, column=1, padx=(0, 10))
        ttk.Button(control_frame, text="Открыть папку сервера", command=self.open_server_folder, style='Action.TButton').grid(row=0, column=2, padx=(0, 10))
        ttk.Button(control_frame, text="О программе", command=self.show_about, style='Action.TButton').grid(row=0, column=3)
        
        # Проверка базы данных
        self.check_database()
        
        # Обновление информации о справочнике
        self.update_cache_status()
    
    def check_database(self):
        """Проверка наличия файлов базы данных"""
        required_files = [
            "database/hideout/production.json",
            "database/templates/items.json",
            "database/server.json"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.server_path / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.database_status_label.config(text=f"⚠️ Отсутствуют файлы: {', '.join(missing_files)}", foreground='red')
        else:
            self.database_status_label.config(text="✅ База данных найдена", foreground='green')
    
    def update_cache_status(self):
        """Обновление информации о справочнике предметов"""
        # Проверяем оба файла кэша
        readable_cache_file = self.server_path / "cache" / "items_readable.json"
        full_cache_file = self.server_path / "cache" / "items_cache.json"
        
        # Выбираем файл для отображения (приоритет readable)
        cache_file = None
        if readable_cache_file.exists() and readable_cache_file.stat().st_size > 0:
            cache_file = readable_cache_file
        elif full_cache_file.exists() and full_cache_file.stat().st_size > 0:
            cache_file = full_cache_file
        
        if not cache_file:
            self.cache_status_label.config(text="❌ Справочник предметов не найден", foreground='red')
        else:
            try:
                # Получаем время модификации файла
                mod_time = cache_file.stat().st_mtime
                last_update = datetime.fromtimestamp(mod_time)
                
                # Получаем размер файла
                file_size = cache_file.stat().st_size
                size_mb = file_size / (1024 * 1024)
                
                # Проверяем возраст справочника
                days_old = (datetime.now() - last_update).days
                
                # Определяем тип файла
                file_type = "читаемый" if cache_file.name == "items_readable.json" else "полный"
                
                if days_old > 7:
                    status_text = f"⚠️ Справочник устарел ({days_old} дней) - {last_update.strftime('%d.%m.%Y %H:%M')} ({size_mb:.1f} MB, {file_type})"
                    color = 'orange'
                else:
                    status_text = f"✅ Справочник актуален - {last_update.strftime('%d.%m.%Y %H:%M')} ({size_mb:.1f} MB, {file_type})"
                    color = 'green'
                
                self.cache_status_label.config(text=status_text, foreground=color)
                
            except Exception as e:
                self.cache_status_label.config(text=f"❌ Ошибка чтения справочника: {str(e)}", foreground='red')
    
    def load_modules(self):
        """Загрузка доступных модулей"""
        # Очистка существующих кнопок
        for widget in self.modules_container.winfo_children():
            widget.destroy()
        
        # Список модулей
        modules = [
            {
                "name": "Сканер базы данных",
                "description": "Сбор данных о предметах с онлайн базы",
                "file": "scan_db.py",
                "icon": "🔍"
            },
            {
                "name": "Менеджер крафта",
                "description": "Редактирование рецептов крафта в убежище",
                "file": "craft_manager.py",
                "icon": "🔨"
            },
            {
                "name": "Менеджер предметов",
                "description": "Управление предметами - создание, редактирование, массовые операции",
                "file": "items_manager.py",
                "icon": "📦"
            },
            {
                "name": "Редактор торговцев",
                "description": "Управление торговцами - создание, редактирование, настройка",
                "file": "trader_editor.py",
                "icon": "🏪"
            },
            {
                "name": "Конфигурация ботов",
                "description": "Настройка поведения и характеристик ботов",
                "file": "bot_config.py",
                "icon": "🤖"
            }
        ]
        
        # Настройка равномерного распределения строк для модулей
        for i in range(len(modules)):
            self.modules_container.rowconfigure(i, weight=1)
        
        # Создание кнопок модулей
        for i, module in enumerate(modules):
            module_frame = ttk.Frame(self.modules_container)
            # Равномерные отступы для всех модулей
            if i == 0:
                # Первый модуль - отступ только снизу
                module_frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=5)
            elif i == len(modules) - 1:
                # Последний модуль - отступ только сверху
                module_frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=(8, 0), padx=5)
            else:
                # Средние модули - отступы сверху и снизу
                module_frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=(8, 8), padx=5)
            
            module_frame.columnconfigure(1, weight=1)
            
            # Иконка и название
            icon_label = ttk.Label(module_frame, text=module["icon"], font=('Arial', 16))
            icon_label.grid(row=0, column=0, rowspan=2, padx=(0, 10), sticky=tk.W)
            
            # Название с учетом статуса
            name_text = module["name"]
            if module.get("status") == "development":
                name_text += " (в разработке)"
                name_style = 'Header.TLabel'
            else:
                name_style = 'Header.TLabel'
            
            name_label = ttk.Label(module_frame, text=name_text, style=name_style)
            name_label.grid(row=0, column=1, sticky=tk.W)
            
            # Описание с учетом статуса
            desc_text = module["description"]
            if module.get("status") == "development":
                desc_text += " - Модуль находится в разработке"
                desc_style = 'Info.TLabel'
            else:
                desc_style = 'Info.TLabel'
            
            desc_label = ttk.Label(module_frame, text=desc_text, style=desc_style)
            desc_label.grid(row=1, column=1, sticky=tk.W)
            
            # Применяем красный цвет для модулей в разработке
            if module.get("status") == "development":
                name_label.config(foreground='red')
                desc_label.config(foreground='red')
            
            # Кнопка запуска
            if module["file"] in ["craft_manager.py", "trader_editor.py", "scan_db.py", "items_manager.py"]:
                # Для реализованных модулей создаем кнопку
                # Используем замыкание с параметром по умолчанию для избежания проблем с lambda
                def make_launch_command(file_name):
                    return lambda: self.launch_module(file_name)
                
                launch_btn = ttk.Button(module_frame, text="Запустить", 
                                      command=make_launch_command(module["file"]),
                                      style='Module.TButton')
                launch_btn.grid(row=0, column=2, rowspan=2, padx=(10, 0), sticky=tk.E)
            elif module.get("status") == "development":
                # Для модулей в разработке - неактивная кнопка
                launch_btn = ttk.Button(module_frame, text="В разработке", 
                                      command=lambda: messagebox.showinfo("Информация", "Модуль находится в разработке"),
                                      style='Module.TButton', state='disabled')
                launch_btn.grid(row=0, column=2, rowspan=2, padx=(10, 0), sticky=tk.E)
            else:
                # Для остальных модулей - заглушка
                launch_btn = ttk.Button(module_frame, text="Не реализован", 
                                      command=lambda: messagebox.showinfo("Информация", "Модуль не реализован"),
                                      style='Module.TButton', state='disabled')
                launch_btn.grid(row=0, column=2, rowspan=2, padx=(10, 0), sticky=tk.E)
    
    def launch_module(self, module_file):
        """Запуск модуля"""
        try:
            module_path = self.server_path / "modules" / module_file
            if module_path.exists():
                # Добавляем путь к модулям в sys.path ПЕРЕД импортом
                modules_path = str(self.server_path / "modules")
                if modules_path not in sys.path:
                    sys.path.insert(0, modules_path)
                
                if module_file == "craft_manager.py":
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("craft_manager", module_path)
                    craft_manager = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(craft_manager)
                    
                    # Создание нового окна для модуля
                    module_window = tk.Toplevel(self.root)
                    
                    # Скрываем основное окно
                    self.root.withdraw()
                    
                    # Создаем экземпляр модуля
                    craft_manager_instance = craft_manager.CraftManager(module_window, self.server_path)
                    
                    # Добавляем обработчик закрытия модуля
                    def on_module_close():
                        # Показываем основное окно обратно
                        self.root.deiconify()
                        # Уничтожаем окно модуля
                        module_window.destroy()
                    
                    # Привязываем обработчик к закрытию окна модуля
                    module_window.protocol("WM_DELETE_WINDOW", on_module_close)
                    
                elif module_file == "items_manager.py":
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("items_manager", module_path)
                    items_manager = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(items_manager)
                    
                    # Создание нового окна для модуля
                    module_window = tk.Toplevel(self.root)
                    
                    # Скрываем основное окно
                    self.root.withdraw()
                    
                    # Создаем экземпляр модуля
                    items_manager_instance = items_manager.ItemsManager(module_window, self.server_path)
                    
                    # Добавляем обработчик закрытия модуля
                    def on_module_close():
                        # Показываем основное окно обратно
                        self.root.deiconify()
                        # Уничтожаем окно модуля
                        module_window.destroy()
                    
                    # Привязываем обработчик к закрытию окна модуля
                    module_window.protocol("WM_DELETE_WINDOW", on_module_close)
                    
                elif module_file == "trader_editor.py":
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("trader_editor", module_path)
                    trader_editor = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(trader_editor)
                    
                    # Создание нового окна для модуля
                    module_window = tk.Toplevel(self.root)
                    
                    # Скрываем основное окно
                    self.root.withdraw()
                    
                    # Создаем экземпляр модуля
                    trader_editor_instance = trader_editor.TraderEditor(module_window, self.server_path)
                    
                    # Добавляем обработчик закрытия модуля
                    def on_module_close():
                        # Показываем основное окно обратно
                        self.root.deiconify()
                        # Уничтожаем окно модуля
                        module_window.destroy()
                    
                    # Привязываем обработчик к закрытию окна модуля
                    module_window.protocol("WM_DELETE_WINDOW", on_module_close)
                    
                elif module_file == "scan_db.py":
                    # Запуск сканера с окном прогресса
                    self.launch_scanner()
                else:
                    messagebox.showinfo("Информация", f"Модуль {module_file} не реализован")
            else:
                messagebox.showerror("Ошибка", f"Файл модуля {module_file} не найден")
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            messagebox.showerror("Ошибка", f"Ошибка при запуске модуля: {str(e)}\n\nДетали:\n{error_details}")
    
    def open_server_folder(self):
        """Открытие папки сервера в проводнике"""
        try:
            os.startfile(str(self.server_path))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть папку: {str(e)}")
    
    def show_about(self):
        """Показ информации о программе"""
        about_text = """
SPT Server Editor v1.0

Программа для редактирования настроек сервера 
Escape from Tarkov (SPT-AKI).

Возможности:
• Редактирование рецептов крафта
• Настройка предметов и торговцев
• Конфигурация ботов
• И многое другое...

Разработано для SPT-AKI Community
        """
        messagebox.showinfo("О программе", about_text)

@log_function_calls(LogCategory.SYSTEM)
@log_performance(LogCategory.PERFORMANCE)
def main():
    """Главная функция"""
    info("Запуск главной функции приложения", LogCategory.SYSTEM)
    
    try:
        root = tk.Tk()
        info("Создан корневой Tkinter объект", LogCategory.UI)
        
        app = SPTEditor(root)
        info("Создан экземпляр SPTEditor", LogCategory.SYSTEM)
        
        info("Запуск главного цикла приложения", LogCategory.UI)
        root.mainloop()
        
        info("Приложение завершено", LogCategory.SYSTEM)
        
    except Exception as e:
        critical(f"Критическая ошибка в главной функции: {e}", LogCategory.ERROR, exception=e)
        raise

if __name__ == "__main__":
    main()
