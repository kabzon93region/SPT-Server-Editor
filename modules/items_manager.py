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

# Импорт системы отладочного логирования
# Система логирования используется для отслеживания работы модуля
try:
    # Импортируем основные функции логирования
    from modules.debug_logger import get_debug_logger, LogCategory, debug, info, warning, error, critical, trace
    # Импортируем декораторы для автоматического логирования
    from modules.debug_logger import log_function_calls, log_performance
except ImportError:
    # Если модуль логирования недоступен, создаем заглушки
    # Это обеспечивает работу модуля даже без системы логирования
    
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
        CACHE = "CACHE"          # Кэширование
        VALIDATION = "VALIDATION"    # Валидация данных
    
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

# Импорт модулей проекта
# Импортируем необходимые модули для работы с предметами
try:
    from modules.items_database import ItemsDatabase      # Модуль для работы с базой данных предметов
    from modules.items_cache import ItemsCache            # Модуль для работы с кэшем предметов
    from modules.hideout_areas import HideoutAreas        # Модуль для работы с зонами убежища
    from modules.context_menus import setup_context_menus_for_module  # Модуль для настройки контекстных меню
except ImportError:
    # Если модули не найдены, добавляем путь к модулям в sys.path
    # Это необходимо для корректного импорта при запуске из разных директорий
    import sys
    from pathlib import Path
    modules_path = str(Path(__file__).parent)  # Получаем путь к директории модулей
    if modules_path not in sys.path:           # Если путь не в sys.path
        sys.path.insert(0, modules_path)       # Добавляем его в начало списка
    
    # Повторный импорт после добавления пути
    from items_database import ItemsDatabase
    from items_cache import ItemsCache
    from hideout_areas import HideoutAreas
    from context_menus import setup_context_menus_for_module

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
        
        # Инициализация модулей
        info("Инициализация модулей базы данных", LogCategory.DATABASE)
        self.items_db = ItemsDatabase(server_path)
        self.items_cache = ItemsCache(server_path)
        self.hideout_areas = HideoutAreas()
        
        # Используем переданное окно напрямую
        self.window = parent_window
        self.window.title("Менеджер предметов")
        self.window.geometry("1000x700")
        self.window.minsize(800, 600)
        
        info("Настройка окна менеджера предметов", LogCategory.UI)
        
        # Добавляем поддержку управления окном
        try:
            from modules.ui_utils import add_module_window_controls, create_window_control_buttons
            add_module_window_controls(self.window)
            debug("Добавлены элементы управления окном", LogCategory.UI)
        except Exception as e:
            error(f"Ошибка добавления управления окном: {e}", LogCategory.UI, exception=e)
        
        # Переменные для статистики
        self.items_statistics = {}
        self.prefab_statistics = {}
        
        debug("Инициализированы переменные статистики", LogCategory.SYSTEM)
        
        # Создание интерфейса
        self.create_widgets()
        self.load_statistics()
        
        # Настройка контекстных меню
        setup_context_menus_for_module(self)
        
        # Обработка закрытия окна
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Создание интерфейса"""
        # Главный фрейм - используем content_container если он есть
        parent_container = getattr(self.window, 'content_container', self.window)
        main_frame = ttk.Frame(parent_container)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок с предупреждением о разработке
        self.create_header(main_frame)
        
        # Статистика предметов
        self.create_statistics_section(main_frame)
        
        # Кнопки интерфейсов
        self.create_interface_buttons(main_frame)
        
        # Информационная панель
        self.create_info_panel(main_frame)
    
    def create_header(self, parent):
        """Создание заголовка с предупреждением"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Заголовок
        title_label = ttk.Label(header_frame, text="Менеджер предметов", 
                               font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Статус модуля
        status_label = ttk.Label(header_frame, text="✅ АКТИВЕН", 
                                font=("Arial", 12, "bold"), foreground="green")
        status_label.pack(side=tk.RIGHT)
    
    def create_statistics_section(self, parent):
        """Создание секции статистики"""
        stats_frame = ttk.LabelFrame(parent, text="Статистика предметов", padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Создание notebook для разных видов статистики
        notebook = ttk.Notebook(stats_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка "По типам"
        self.create_types_tab(notebook)
        
        # Вкладка "По путям префабов"
        self.create_prefabs_tab(notebook)
        
        # Вкладка "Общая статистика"
        self.create_general_tab(notebook)
    
    def create_types_tab(self, notebook):
        """Создание вкладки статистики по типам"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="По типам")
        
        # Treeview для типов предметов
        columns = ("type", "count", "percentage")
        self.types_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        self.types_tree.heading("type", text="Тип предмета")
        self.types_tree.heading("count", text="Количество")
        self.types_tree.heading("percentage", text="Процент")
        
        self.types_tree.column("type", width=300)
        self.types_tree.column("count", width=100)
        self.types_tree.column("percentage", width=100)
        
        # Прокрутка
        scrollbar_y = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.types_tree.yview)
        self.types_tree.configure(yscrollcommand=scrollbar_y.set)
        
        # Размещение
        self.types_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_prefabs_tab(self, notebook):
        """Создание вкладки статистики по путям префабов"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="По путям префабов")
        
        # Treeview для путей префабов
        columns = ("path_category", "path_subcategory", "count", "percentage")
        self.prefabs_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        self.prefabs_tree.heading("path_category", text="Категория пути")
        self.prefabs_tree.heading("path_subcategory", text="Подкатегория")
        self.prefabs_tree.heading("count", text="Количество")
        self.prefabs_tree.heading("percentage", text="Процент")
        
        self.prefabs_tree.column("path_category", width=200)
        self.prefabs_tree.column("path_subcategory", width=200)
        self.prefabs_tree.column("count", width=100)
        self.prefabs_tree.column("percentage", width=100)
        
        # Прокрутка
        scrollbar_y = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.prefabs_tree.yview)
        self.prefabs_tree.configure(yscrollcommand=scrollbar_y.set)
        
        # Размещение
        self.prefabs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_general_tab(self, notebook):
        """Создание вкладки общей статистики"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Общая статистика")
        
        # Информационные метки
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.total_items_label = ttk.Label(info_frame, text="Всего предметов: 0", 
                                          font=("Arial", 12, "bold"))
        self.total_items_label.pack(anchor=tk.W, pady=5)
        
        self.unique_types_label = ttk.Label(info_frame, text="Уникальных типов: 0", 
                                           font=("Arial", 12))
        self.unique_types_label.pack(anchor=tk.W, pady=5)
        
        self.unique_prefabs_label = ttk.Label(info_frame, text="Уникальных префабов: 0", 
                                             font=("Arial", 12))
        self.unique_prefabs_label.pack(anchor=tk.W, pady=5)
        
        # Дополнительная информация
        details_frame = ttk.LabelFrame(frame, text="Детали", padding=10)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.details_text = tk.Text(details_frame, height=10, wrap=tk.WORD)
        details_scrollbar = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scrollbar.set)
        
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_interface_buttons(self, parent):
        """Создание кнопок для открытия интерфейсов"""
        buttons_frame = ttk.LabelFrame(parent, text="Интерфейсы", padding=10)
        buttons_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Создание кнопок в сетке
        buttons_grid = ttk.Frame(buttons_frame)
        buttons_grid.pack(fill=tk.X)
        
        # Кнопка поиска и редактирования
        search_btn = ttk.Button(buttons_grid, text="🔍 Поиск и редактирование предметов", 
                               command=self.open_search_interface)
        search_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # Кнопка массового изменения
        bulk_btn = ttk.Button(buttons_grid, text="⚡ Массовое изменение параметров", 
                             command=self.open_bulk_interface)
        bulk_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Кнопка создания предметов
        create_btn = ttk.Button(buttons_grid, text="➕ Создание (дублирование) предметов", 
                               command=self.open_create_interface, state="disabled")
        create_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        # Настройка растягивания колонок
        buttons_grid.columnconfigure(0, weight=1)
        buttons_grid.columnconfigure(1, weight=1)
        buttons_grid.columnconfigure(2, weight=1)
    
    def create_info_panel(self, parent):
        """Создание информационной панели"""
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill=tk.X)
        
        # Статус загрузки
        self.status_label = ttk.Label(info_frame, text="Статистика загружена")
        self.status_label.pack(side=tk.LEFT)
        
        # Кнопка обновления
        refresh_btn = ttk.Button(info_frame, text="🔄 Обновить статистику", 
                                command=self.load_statistics)
        refresh_btn.pack(side=tk.RIGHT)
    
    def load_statistics(self):
        """Загрузка и анализ статистики предметов"""
        try:
            self.status_label.config(text="Загрузка статистики...")
            self.window.update()
            
            # Получение всех предметов
            items_data = self.items_db.items_data
            total_items = len(items_data)
            
            if total_items == 0:
                self.status_label.config(text="Нет данных о предметах")
                return
            
            # Анализ по типам
            type_counter = Counter()
            prefab_counter = Counter()
            prefab_categories = defaultdict(lambda: defaultdict(int))
            
            for item_id, item_data in items_data.items():
                # Анализ типа
                item_type = item_data.get("_type", "Unknown")
                type_counter[item_type] += 1
                
                # Анализ пути префаба
                prefab_path = self.extract_prefab_path(item_data)
                if prefab_path:
                    prefab_counter[prefab_path] += 1
                    
                    # Разбор пути на категории
                    path_parts = prefab_path.split("/")
                    if len(path_parts) >= 4:  # assets/content/category/subcategory/...
                        category = path_parts[2] if len(path_parts) > 2 else "unknown"
                        subcategory = path_parts[3] if len(path_parts) > 3 else "unknown"
                        prefab_categories[category][subcategory] += 1
            
            # Сохранение статистики
            self.items_statistics = {
                'total': total_items,
                'by_type': dict(type_counter),
                'by_prefab': dict(prefab_counter),
                'prefab_categories': dict(prefab_categories)
            }
            
            # Обновление интерфейса
            self.update_types_display()
            self.update_prefabs_display()
            self.update_general_display()
            
            self.status_label.config(text=f"Статистика загружена: {total_items} предметов")
            
        except Exception as e:
            self.status_label.config(text=f"Ошибка загрузки: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить статистику: {str(e)}")
    
    def extract_prefab_path(self, item_data):
        """Извлечение пути префаба из данных предмета"""
        try:
            props = item_data.get("_props", {})
            prefab = props.get("Prefab", {})
            if isinstance(prefab, dict):
                return prefab.get("path", "")
            return ""
        except:
            return ""
    
    def update_types_display(self):
        """Обновление отображения статистики по типам"""
        # Очистка таблицы
        for item in self.types_tree.get_children():
            self.types_tree.delete(item)
        
        # Получение данных
        type_stats = self.items_statistics.get('by_type', {})
        total_items = self.items_statistics.get('total', 1)
        
        # Сортировка по количеству
        sorted_types = sorted(type_stats.items(), key=lambda x: x[1], reverse=True)
        
        # Заполнение таблицы
        for item_type, count in sorted_types:
            percentage = (count / total_items) * 100
            self.types_tree.insert('', 'end', values=(
                item_type,
                str(count),
                f"{percentage:.1f}%"
            ))
    
    def update_prefabs_display(self):
        """Обновление отображения статистики по путям префабов"""
        # Очистка таблицы
        for item in self.prefabs_tree.get_children():
            self.prefabs_tree.delete(item)
        
        # Получение данных
        prefab_categories = self.items_statistics.get('prefab_categories', {})
        total_items = self.items_statistics.get('total', 1)
        
        # Сортировка и заполнение
        for category, subcategories in prefab_categories.items():
            for subcategory, count in subcategories.items():
                percentage = (count / total_items) * 100
                self.prefabs_tree.insert('', 'end', values=(
                    category,
                    subcategory,
                    str(count),
                    f"{percentage:.1f}%"
                ))
    
    def update_general_display(self):
        """Обновление общей статистики"""
        total_items = self.items_statistics.get('total', 0)
        unique_types = len(self.items_statistics.get('by_type', {}))
        unique_prefabs = len(self.items_statistics.get('by_prefab', {}))
        
        # Обновление меток
        self.total_items_label.config(text=f"Всего предметов: {total_items}")
        self.unique_types_label.config(text=f"Уникальных типов: {unique_types}")
        self.unique_prefabs_label.config(text=f"Уникальных префабов: {unique_prefabs}")
        
        # Детальная информация
        details = []
        details.append("=== СТАТИСТИКА ПРЕДМЕТОВ ===\n")
        details.append(f"Всего предметов в базе: {total_items}")
        details.append(f"Уникальных типов: {unique_types}")
        details.append(f"Уникальных префабов: {unique_prefabs}\n")
        
        # Топ-5 типов
        type_stats = self.items_statistics.get('by_type', {})
        sorted_types = sorted(type_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        details.append("Топ-5 типов предметов:")
        for i, (item_type, count) in enumerate(sorted_types, 1):
            percentage = (count / total_items) * 100
            details.append(f"  {i}. {item_type}: {count} ({percentage:.1f}%)")
        
        details.append("\n")
        
        # Топ-5 категорий префабов
        prefab_categories = self.items_statistics.get('prefab_categories', {})
        category_totals = {cat: sum(subcats.values()) for cat, subcats in prefab_categories.items()}
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        details.append("Топ-5 категорий префабов:")
        for i, (category, count) in enumerate(sorted_categories, 1):
            percentage = (count / total_items) * 100
            details.append(f"  {i}. {category}: {count} ({percentage:.1f}%)")
        
        # Обновление текста
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, "\n".join(details))
    
    def open_search_interface(self):
        """Открытие интерфейса поиска и редактирования"""
        try:
            from modules.items_search_dialog import ItemsSearchDialog
            ItemsSearchDialog(self.window, self.server_path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть интерфейс поиска: {str(e)}")
    
    def open_bulk_interface(self):
        """Открытие интерфейса массового изменения"""
        try:
            info("Попытка открытия интерфейса массового изменения", LogCategory.UI)
            from modules.bulk_parameters_dialog import BulkParametersDialog
            debug("Модуль BulkParametersDialog импортирован", LogCategory.UI)
            
            try:
                bulk_dialog = BulkParametersDialog(self.window, self.server_path)
                info("Интерфейс массового изменения открыт успешно", LogCategory.UI)
            except Exception as e:
                error(f"Ошибка создания BulkParametersDialog: {e}", LogCategory.ERROR, exception=e)
                messagebox.showerror("Ошибка", f"Не удалось создать диалог массового изменения:\n{str(e)}")
                raise
                
        except ImportError as e:
            error(f"Ошибка импорта BulkParametersDialog: {e}", LogCategory.ERROR, exception=e)
            messagebox.showerror("Ошибка", f"Не удалось загрузить модуль массового изменения:\n{str(e)}")
        except Exception as e:
            error(f"Неожиданная ошибка при открытии интерфейса массового изменения: {e}", LogCategory.ERROR, exception=e)
            messagebox.showerror("Ошибка", f"Неожиданная ошибка при открытии интерфейса массового изменения:\n{str(e)}")
    
    def open_create_interface(self):
        """Открытие интерфейса создания предметов"""
        messagebox.showinfo("В разработке", "Интерфейс создания и дублирования предметов будет реализован в следующих версиях")
    
    def on_closing(self):
        """Обработка закрытия окна"""
        # Окно управляется основной программой, просто очищаем содержимое
        for widget in self.window.winfo_children():
            widget.destroy()

def main():
    """Главная функция для тестирования модуля"""
    root = tk.Tk()
    root.withdraw()  # Скрываем главное окно
    
    server_path = Path(__file__).parent.parent
    manager = ItemsManager(root, server_path)
    
    root.mainloop()

if __name__ == "__main__":
    main()
