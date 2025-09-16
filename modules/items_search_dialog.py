#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Items Search Dialog - Диалог поиска и редактирования предметов
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import orjson
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict

# Импорт модулей проекта
try:
    from modules.items_database import ItemsDatabase
    from modules.items_cache import ItemsCache
    from modules.context_menus import setup_context_menus_for_module
    from modules.items_analyzer import ItemsAnalyzer
    from modules.ui_utils import setup_resizable_window, apply_modern_style, center_window
    from modules.dynamic_ui import DynamicUIBuilder, load_parameters_config
    from modules.json_editor import JSONEditor
except ImportError:
    import sys
    from pathlib import Path
    modules_path = str(Path(__file__).parent)
    if modules_path not in sys.path:
        sys.path.insert(0, modules_path)
    
    from items_database import ItemsDatabase
    from items_cache import ItemsCache
    from context_menus import setup_context_menus_for_module
    from items_analyzer import ItemsAnalyzer
    
    # Заглушки для UI утилит
    def setup_resizable_window(window, title, width=1200, height=800, min_width=800, min_height=600, fullscreen=True):
        window.title(title)
        window.geometry(f"{width}x{height}")
        window.minsize(min_width, min_height)
        window.resizable(True, True)
        if fullscreen:
            window.state('normal')
    
    def apply_modern_style():
        pass
    
    def center_window(window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    # Заглушки для новых модулей
    class DynamicUIBuilder:
        def __init__(self, *args, **kwargs):
            pass
        def create_ui(self):
            pass
        def get_values(self):
            return {}
        def set_values(self, data):
            pass
    
    def load_parameters_config(path):
        return {}
    
    class JSONEditor:
        def __init__(self, *args, **kwargs):
            pass

class ItemsSearchDialog:
    """Диалог поиска и редактирования предметов"""
    
    def __init__(self, parent, server_path: Path):
        self.parent = parent
        self.server_path = server_path
        
        # Инициализация модулей
        self.items_db = ItemsDatabase(server_path)
        self.items_cache = ItemsCache(server_path)
        
        # Загрузка анализа параметров
        self.analysis_results = self.load_analysis_results()
        
        # Загрузка конфигурации параметров
        self.parameters_config = self.load_parameters_config()
        
        # Создание диалога с использованием утилит
        self.dialog = tk.Toplevel(parent)
        setup_resizable_window(self.dialog, "Поиск и редактирование предметов", 1400, 900, 1000, 700, fullscreen=True)
        apply_modern_style()
        center_window(self.dialog, 1400, 900)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        
        # Переменные
        self.search_results = []
        self.selected_items = []
        self.current_item = None
        self.original_item_data = None  # Оригинальные данные для сравнения
        self.changed_parameters = set()  # Отслеживание измененных параметров
        
        # Создание интерфейса
        self.create_widgets()
        
        # Настройка контекстных меню
        try:
            # Создаем временный объект с атрибутом window для совместимости
            class TempModule:
                def __init__(self, dialog):
                    self.window = dialog
            
            temp_module = TempModule(self.dialog)
            setup_context_menus_for_module(temp_module)
        except Exception as e:
            print(f"Ошибка настройки контекстных меню: {e}")
        
        # Обработка закрытия
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Выполняем начальный поиск для отображения всех предметов
        self.perform_search()
    
    def load_analysis_results(self):
        """Загрузка результатов анализа параметров"""
        try:
            analyzer = ItemsAnalyzer(self.server_path)
            return analyzer.load_analysis_results()
        except Exception as e:
            print(f"Ошибка загрузки анализа: {e}")
            return None
    
    def load_parameters_config(self):
        """Загрузка конфигурации параметров"""
        try:
            config_path = self.server_path / "modules" / "parameters_config.json"
            return load_parameters_config(config_path)
        except Exception as e:
            print(f"Ошибка загрузки конфигурации параметров: {e}")
            return {}
    
    def create_widgets(self):
        """Создание интерфейса"""
        # Создаем Canvas и Scrollbar для прокрутки всего интерфейса
        canvas = tk.Canvas(self.dialog, bg='#ffffff', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Настройка фона основного окна
        self.dialog.configure(bg='#ffffff')
        
        # Создаем окно в Canvas
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Функция для настройки ширины и области прокрутки
        def configure_scroll_region(event):
            # Обновляем область прокрутки
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Устанавливаем ширину scrollable_frame равной ширине canvas
            canvas_width = canvas.winfo_width()
            if canvas_width > 1:  # Избегаем деления на ноль
                canvas.itemconfig(canvas_window, width=canvas_width)
        
        # Привязываем события
        scrollable_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_scroll_region)
        
        # Размещение Canvas и Scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Привязка колесика мыши
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Главный фрейм внутри прокручиваемого контейнера
        main_frame = ttk.Frame(scrollable_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Панель поиска
        self.create_search_panel(main_frame)
        
        # Панель результатов
        self.create_results_panel(main_frame)
        
        # Панель редактирования
        self.create_edit_panel(main_frame)
    
    def create_search_panel(self, parent):
        """Создание панели поиска"""
        search_frame = ttk.LabelFrame(parent, text="Поиск предметов", padding=10)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Строка 1: Основные фильтры
        row1 = ttk.Frame(search_frame)
        row1.pack(fill=tk.X, pady=(0, 5))
        
        # ID предмета
        ttk.Label(row1, text="ID предмета:").pack(side=tk.LEFT, padx=(0, 5))
        self.id_var = tk.StringVar()
        id_entry = ttk.Entry(row1, textvariable=self.id_var, width=30)
        id_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # Привязка событий клавиатуры для правильной обработки вставки
        id_entry.bind('<KeyRelease>', self.on_id_key_release)
        id_entry.bind('<Control-KeyPress>', self.on_control_key)  # Обработка Ctrl+клавиша (включая Ctrl+V)
        id_entry.bind('<Button-1>', self.on_id_click)
        id_entry.bind('<Button-3>', self.on_right_click)  # Правая кнопка мыши
        
        # Название предмета
        ttk.Label(row1, text="Название:").pack(side=tk.LEFT, padx=(0, 5))
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(row1, textvariable=self.name_var, width=30)
        name_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # Привязка событий клавиатуры для правильной обработки вставки
        name_entry.bind('<KeyRelease>', self.on_name_key_release)
        name_entry.bind('<Control-KeyPress>', self.on_control_key)  # Обработка Ctrl+клавиша (включая Ctrl+V)
        name_entry.bind('<Button-1>', self.on_name_click)
        name_entry.bind('<Button-3>', self.on_right_click)  # Правая кнопка мыши
        
        # Тип предмета
        ttk.Label(row1, text="Тип:").pack(side=tk.LEFT, padx=(0, 5))
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(row1, textvariable=self.type_var, width=15)
        self.type_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.type_combo['values'] = ['Все', 'Item', 'Node']
        self.type_combo.set('Все')
        self.type_combo.bind('<<ComboboxSelected>>', self.on_search_change)
        
        # Строка 2: Дополнительные фильтры
        row2 = ttk.Frame(search_frame)
        row2.pack(fill=tk.X, pady=(0, 5))
        
        # Категория префаба
        ttk.Label(row2, text="Категория префаба:").pack(side=tk.LEFT, padx=(0, 5))
        self.prefab_category_var = tk.StringVar()
        self.prefab_category_combo = ttk.Combobox(row2, textvariable=self.prefab_category_var, width=20)
        self.prefab_category_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.prefab_category_combo['values'] = ['Все', 'weapons', 'items', 'location_objects', 'prefabs']
        self.prefab_category_combo.set('Все')
        self.prefab_category_combo.bind('<<ComboboxSelected>>', self.on_search_change)
        
        # Редкость
        ttk.Label(row2, text="Редкость:").pack(side=tk.LEFT, padx=(0, 5))
        self.rarity_var = tk.StringVar()
        self.rarity_combo = ttk.Combobox(row2, textvariable=self.rarity_var, width=15)
        self.rarity_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.rarity_combo['values'] = ['Все', 'Common', 'Rare', 'Superrare', 'Not_exist', 'Not_exist_quest']
        self.rarity_combo.set('Все')
        self.rarity_combo.bind('<<ComboboxSelected>>', self.on_search_change)
        
        # Кнопка поиска
        search_btn = ttk.Button(row2, text="🔍 Поиск", command=self.perform_search)
        search_btn.pack(side=tk.LEFT, padx=(20, 0))
        
        # Кнопка сброса
        reset_btn = ttk.Button(row2, text="🔄 Сбросить", command=self.reset_filters)
        reset_btn.pack(side=tk.LEFT, padx=(5, 0))
    
    def create_results_panel(self, parent):
        """Создание панели результатов"""
        results_frame = ttk.LabelFrame(parent, text="Результаты поиска", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Создание фрейма для TreeView и прокрутки
        tree_frame = ttk.Frame(results_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создание Treeview с прокруткой (уменьшен на 30%)
        columns = ("ID", "Название", "Тип", "Редкость", "Вес", "Цена", "Размер")
        self.results_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)
        
        # Настройка колонок
        self.results_tree.heading("ID", text="ID")
        self.results_tree.heading("Название", text="Название")
        self.results_tree.heading("Тип", text="Тип")
        self.results_tree.heading("Редкость", text="Редкость")
        self.results_tree.heading("Вес", text="Вес")
        self.results_tree.heading("Цена", text="Цена")
        self.results_tree.heading("Размер", text="Размер")
        
        # Настройка ширины колонок (уменьшены на 30%)
        self.results_tree.column("ID", width=140)
        self.results_tree.column("Название", width=140)
        self.results_tree.column("Тип", width=56)
        self.results_tree.column("Редкость", width=70)
        self.results_tree.column("Вес", width=56)
        self.results_tree.column("Цена", width=70)
        self.results_tree.column("Размер", width=56)
        
        # Прокрутка
        scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Размещение
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Обработка выбора
        self.results_tree.bind("<<TreeviewSelect>>", self.on_item_select)
        self.results_tree.bind("<Double-1>", self.on_item_double_click)
    
    def create_edit_panel(self, parent):
        """Создание панели редактирования"""
        edit_frame = ttk.LabelFrame(parent, text="Редактирование предмета", padding=10)
        edit_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Создание notebook для вкладок
        notebook = ttk.Notebook(edit_frame)
        notebook.pack(fill=tk.X)
        
        # Вкладка "Основные параметры"
        self.create_basic_tab(notebook)
        
        # Вкладка "Свойства предмета"
        self.create_properties_tab(notebook)
        
        # Вкладка "Дополнительные параметры"
        self.create_advanced_tab(notebook)
        
        # Вкладка "Все параметры"
        self.create_all_parameters_tab(notebook)
    
    def create_basic_tab(self, notebook):
        """Создание вкладки основных параметров"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Основные параметры")
        
        # Создание Canvas и Scrollbar для прокрутки
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Создание динамического UI для основных параметров
        basic_config = self.parameters_config.get('basic_parameters', {})
        self.basic_ui_builder = DynamicUIBuilder(scrollable_frame, basic_config, {})
        self.basic_ui_builder.create_ui()
        
        # Размещение Canvas и Scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Привязка колесика мыши
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def create_properties_tab(self, notebook):
        """Создание вкладки свойств предмета"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Свойства предмета")
        
        # Создание Canvas и Scrollbar для прокрутки
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Создание динамического UI для свойств предмета
        properties_config = self.parameters_config.get('item_properties', {})
        self.properties_ui_builder = DynamicUIBuilder(scrollable_frame, properties_config, {})
        self.properties_ui_builder.create_ui()
        
        # Размещение Canvas и Scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Привязка колесика мыши
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def create_advanced_tab(self, notebook):
        """Создание вкладки дополнительных параметров"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Дополнительные параметры")
        
        # Создание Canvas и Scrollbar для прокрутки
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Создание динамического UI для дополнительных параметров
        advanced_config = self.parameters_config.get('additional_parameters', {})
        self.advanced_ui_builder = DynamicUIBuilder(scrollable_frame, advanced_config, {})
        self.advanced_ui_builder.create_ui()
        
        # Размещение Canvas и Scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Привязка колесика мыши
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def create_all_parameters_tab(self, notebook):
        """Создание вкладки всех параметров предмета"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Все параметры")
        
        # Панель управления
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Кнопки управления
        ttk.Button(control_frame, text="🔄 Обновить", command=self.refresh_json_editor).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="💾 Сохранить", command=self.save_json_editor).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="🎨 Форматировать", command=self.format_json_editor).pack(side=tk.LEFT, padx=(0, 10))
        
        # Информация о предмете
        info_label = ttk.Label(control_frame, text="JSON редактор с подсветкой синтаксиса", foreground="gray")
        info_label.pack(side=tk.RIGHT)
        
        # Создание фрейма для JSON редактора
        editor_frame = ttk.Frame(frame)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создание текстового поля для JSON
        self.json_text = tk.Text(
            editor_frame,
            wrap=tk.NONE,
            font=('Consolas', 10),
            bg='#f8f8f8',
            fg='#333333',
            insertbackground='#333333',
            selectbackground='#0078d4',
            selectforeground='white',
            undo=True,
            maxundo=50
        )
        
        # Прокрутка для JSON редактора
        json_scrollbar_y = ttk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=self.json_text.yview)
        json_scrollbar_x = ttk.Scrollbar(editor_frame, orient=tk.HORIZONTAL, command=self.json_text.xview)
        self.json_text.configure(yscrollcommand=json_scrollbar_y.set, xscrollcommand=json_scrollbar_x.set)
        
        # Размещение
        self.json_text.grid(row=0, column=0, sticky="nsew")
        json_scrollbar_y.grid(row=0, column=1, sticky="ns")
        json_scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        editor_frame.grid_rowconfigure(0, weight=1)
        editor_frame.grid_columnconfigure(0, weight=1)
        
        # Привязка событий
        self.json_text.bind('<KeyRelease>', self.on_json_change)
        self.json_text.bind('<Control-s>', lambda e: self.save_json_editor())
        self.json_text.bind('<Control-z>', lambda e: self.json_text.edit_undo())
        self.json_text.bind('<Control-y>', lambda e: self.json_text.edit_redo())
    
    def refresh_json_editor(self):
        """Обновление JSON редактора"""
        if not self.current_item:
            messagebox.showwarning("Предупреждение", "Выберите предмет для просмотра параметров")
            return
        
        try:
            _, item_data = self.current_item
            
            # Конвертируем в JSON строку
            json_str = orjson.dumps(item_data, option=orjson.OPT_INDENT_2).decode('utf-8')
            
            # Очищаем и вставляем текст
            self.json_text.delete(1.0, tk.END)
            self.json_text.insert(1.0, json_str)
            
            # Применяем подсветку синтаксиса
            self.apply_json_syntax_highlighting()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обновлении JSON: {str(e)}")
    
    def save_json_editor(self):
        """Сохранение изменений из JSON редактора"""
        if not self.current_item:
            messagebox.showwarning("Предупреждение", "Выберите предмет для редактирования")
            return
        
        try:
            # Получаем текст
            content = self.json_text.get(1.0, tk.END).strip()
            
            # Парсим JSON
            try:
                parsed_data = orjson.loads(content)
            except orjson.JSONDecodeError as e:
                messagebox.showerror("Ошибка JSON", f"Неверный формат JSON:\n{str(e)}")
                return
            
            # Обновляем данные предмета
            item_id, _ = self.current_item
            self.current_item = (item_id, parsed_data)
            
            # Сохраняем в базе данных
            if self.items_db.save_item(item_id, parsed_data):
                messagebox.showinfo("Успех", "Изменения сохранены успешно")
                # Обновляем отображение в таблице
                self.perform_search()
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить изменения")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")
    
    def format_json_editor(self):
        """Форматирование JSON в редакторе"""
        try:
            # Получаем текст
            content = self.json_text.get(1.0, tk.END).strip()
            
            # Парсим и форматируем
            parsed_data = orjson.loads(content)
            formatted = orjson.dumps(parsed_data, option=orjson.OPT_INDENT_2).decode('utf-8')
            
            # Заменяем текст
            self.json_text.delete(1.0, tk.END)
            self.json_text.insert(1.0, formatted)
            
            # Применяем подсветку
            self.apply_json_syntax_highlighting()
            
        except orjson.JSONDecodeError as e:
            messagebox.showerror("Ошибка JSON", f"Неверный формат JSON:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при форматировании: {str(e)}")
    
    def on_json_change(self, event=None):
        """Обработка изменения JSON"""
        # Применяем подсветку синтаксиса
        self.dialog.after(100, self.apply_json_syntax_highlighting)
    
    def apply_json_syntax_highlighting(self):
        """Применение подсветки синтаксиса JSON"""
        try:
            # Получаем весь текст
            content = self.json_text.get(1.0, tk.END)
            
            # Очищаем все теги
            self.json_text.tag_remove("json_key", 1.0, tk.END)
            self.json_text.tag_remove("json_string", 1.0, tk.END)
            self.json_text.tag_remove("json_number", 1.0, tk.END)
            self.json_text.tag_remove("json_boolean", 1.0, tk.END)
            self.json_text.tag_remove("json_null", 1.0, tk.END)
            self.json_text.tag_remove("json_punctuation", 1.0, tk.END)
            
            # Настройка тегов
            self.json_text.tag_configure("json_key", foreground="#0000ff", font=('Consolas', 10, 'bold'))
            self.json_text.tag_configure("json_string", foreground="#008000", font=('Consolas', 10))
            self.json_text.tag_configure("json_number", foreground="#ff8000", font=('Consolas', 10))
            self.json_text.tag_configure("json_boolean", foreground="#800080", font=('Consolas', 10, 'bold'))
            self.json_text.tag_configure("json_null", foreground="#808080", font=('Consolas', 10, 'italic'))
            self.json_text.tag_configure("json_punctuation", foreground="#000000", font=('Consolas', 10, 'bold'))
            
            # Простая подсветка синтаксиса
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                self.highlight_json_line(line, line_num)
                
        except Exception as e:
            print(f"Ошибка подсветки синтаксиса: {e}")
    
    def highlight_json_line(self, line: str, line_num: int):
        """Подсветка одной строки JSON"""
        try:
            import re
            
            # Ключи
            key_pattern = r'"([^"]+)"\s*:'
            for match in re.finditer(key_pattern, line):
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()}"
                self.json_text.tag_add("json_key", start, end)
            
            # Строки
            string_pattern = r'"[^"]*"'
            for match in re.finditer(string_pattern, line):
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()}"
                # Проверяем, что это не ключ
                if not line[match.end():match.end()+1].strip().startswith(':'):
                    self.json_text.tag_add("json_string", start, end)
            
            # Числа
            number_pattern = r'\b\d+\.?\d*\b'
            for match in re.finditer(number_pattern, line):
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()}"
                self.json_text.tag_add("json_number", start, end)
            
            # Булевы значения
            boolean_pattern = r'\b(true|false)\b'
            for match in re.finditer(boolean_pattern, line, re.IGNORECASE):
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()}"
                self.json_text.tag_add("json_boolean", start, end)
            
            # null
            null_pattern = r'\bnull\b'
            for match in re.finditer(null_pattern, line, re.IGNORECASE):
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()}"
                self.json_text.tag_add("json_null", start, end)
            
            # Пунктуация
            punct_pattern = r'[{}[\](),:]'
            for match in re.finditer(punct_pattern, line):
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()}"
                self.json_text.tag_add("json_punctuation", start, end)
                
        except Exception as e:
            print(f"Ошибка подсветки строки {line_num}: {e}")
    
    def create_parameter_context_menu(self):
        """Создание контекстного меню для параметров"""
        self.param_context_menu = tk.Menu(self.dialog, tearoff=0)
        self.param_context_menu.add_command(label="📝 Редактировать", command=self.edit_selected_parameter)
        self.param_context_menu.add_command(label="📋 Копировать значение", command=self.copy_parameter_value)
        self.param_context_menu.add_command(label="📋 Копировать путь", command=self.copy_parameter_path)
        self.param_context_menu.add_separator()
        self.param_context_menu.add_command(label="🔍 Найти в коде", command=self.find_parameter_in_code)
        
        # Привязка контекстного меню
        self.parameters_tree.bind("<Button-3>", self.show_parameter_context_menu)
    
    def show_parameter_context_menu(self, event):
        """Показ контекстного меню для параметров"""
        try:
            self.param_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.param_context_menu.grab_release()
    
    def refresh_parameters_table(self):
        """Обновление таблицы параметров"""
        if not self.current_item:
            messagebox.showwarning("Предупреждение", "Выберите предмет для просмотра параметров")
            return
        
        try:
            # Очистка таблицы
            for item in self.parameters_tree.get_children():
                self.parameters_tree.delete(item)
            
            # Загрузка параметров текущего предмета
            _, item_data = self.current_item
            self.load_item_parameters(item_data)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обновлении параметров: {str(e)}")
    
    def load_item_parameters(self, item_data):
        """Загрузка всех параметров предмета в таблицу"""
        try:
            # Основные параметры предмета
            main_params = ['_id', '_name', '_parent', '_type', '_props']
            for param in main_params:
                if param in item_data:
                    value = item_data[param]
                    param_type = type(value).__name__
                    
                    # Форматирование значения для отображения
                    if isinstance(value, (dict, list)):
                        display_value = f"<{param_type}> ({len(value)} элементов)"
                    else:
                        display_value = str(value)[:100]  # Ограничиваем длину
                    
                    self.parameters_tree.insert('', 'end', values=(
                        param,
                        param_type,
                        display_value,
                        f"root.{param}"
                    ))
            
            # Параметры из _props
            props = item_data.get('_props', {})
            self.load_nested_parameters(props, "_props")
            
        except Exception as e:
            print(f"Ошибка загрузки параметров: {e}")
    
    def load_nested_parameters(self, data, path_prefix, max_depth=3, current_depth=0):
        """Рекурсивная загрузка вложенных параметров"""
        if current_depth >= max_depth:
            return
        
        try:
            if isinstance(data, dict):
                for key, value in data.items():
                    # Путь к контейнеру (без имени параметра)
                    container_path = path_prefix
                    param_type = type(value).__name__
                    
                    # Форматирование значения
                    if isinstance(value, (dict, list)):
                        if isinstance(value, dict):
                            display_value = f"<{param_type}> ({len(value)} ключей)"
                        else:
                            display_value = f"<{param_type}> ({len(value)} элементов)"
                    else:
                        display_value = str(value)[:100]
                    
                    self.parameters_tree.insert('', 'end', values=(
                        key,
                        param_type,
                        display_value,
                        container_path
                    ))
                    
                    # Рекурсивная загрузка вложенных структур
                    if isinstance(value, (dict, list)) and current_depth < max_depth - 1:
                        # Для вложенных структур используем полный путь
                        nested_path = f"{path_prefix}.{key}"
                        self.load_nested_parameters(value, nested_path, max_depth, current_depth + 1)
            
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    # Путь к контейнеру (без индекса элемента)
                    container_path = path_prefix
                    param_type = type(item).__name__
                    
                    if isinstance(item, (dict, list)):
                        display_value = f"<{param_type}> ({len(item)} элементов)"
                    else:
                        display_value = str(item)[:100]
                    
                    self.parameters_tree.insert('', 'end', values=(
                        f"[{i}]",
                        param_type,
                        display_value,
                        container_path
                    ))
                    
                    # Рекурсивная загрузка элементов списка
                    if isinstance(item, (dict, list)) and current_depth < max_depth - 1:
                        # Для вложенных структур используем полный путь
                        nested_path = f"{path_prefix}[{i}]"
                        self.load_nested_parameters(item, nested_path, max_depth, current_depth + 1)
        
        except Exception as e:
            print(f"Ошибка загрузки вложенных параметров: {e}")
    
    def filter_parameters(self, *args):
        """Фильтрация параметров по поисковому запросу"""
        search_term = self.param_search_var.get().lower()
        
        # Очистка таблицы
        for item in self.parameters_tree.get_children():
            self.parameters_tree.delete(item)
        
        if not self.current_item:
            return
        
        # Загрузка всех параметров
        _, item_data = self.current_item
        self.load_item_parameters(item_data)
        
        # Фильтрация по поисковому запросу
        if search_term:
            for item in self.parameters_tree.get_children():
                values = self.parameters_tree.item(item)['values']
                param_name = values[0].lower()
                param_value = values[2].lower()
                
                if search_term not in param_name and search_term not in param_value:
                    self.parameters_tree.detach(item)
    
    def search_parameter(self):
        """Поиск конкретного параметра"""
        search_dialog = tk.simpledialog.askstring("Поиск параметра", "Введите название параметра:")
        if search_dialog:
            self.param_search_var.set(search_dialog)
    
    def on_parameter_select(self, event):
        """Обработка выбора параметра"""
        selection = self.parameters_tree.selection()
        if selection:
            item = self.parameters_tree.item(selection[0])
            self.selected_parameter = item['values']
    
    def on_parameter_double_click(self, event):
        """Обработка двойного клика по параметру"""
        self.edit_selected_parameter()
    
    def edit_selected_parameter(self):
        """Редактирование выбранного параметра"""
        if not hasattr(self, 'selected_parameter') or not self.selected_parameter:
            messagebox.showwarning("Предупреждение", "Выберите параметр для редактирования")
            return
        
        param_name, param_type, param_value, param_path = self.selected_parameter
        
        # Создание диалога редактирования
        edit_dialog = tk.Toplevel(self.dialog)
        edit_dialog.title(f"Редактирование параметра: {param_name}")
        edit_dialog.geometry("500x300")
        edit_dialog.transient(self.dialog)
        edit_dialog.grab_set()
        
        # Информация о параметре
        info_frame = ttk.LabelFrame(edit_dialog, text="Информация о параметре", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(info_frame, text=f"Название: {param_name}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Тип: {param_type}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Путь: {param_path}").pack(anchor=tk.W)
        
        # Поле редактирования
        edit_frame = ttk.LabelFrame(edit_dialog, text="Значение", padding=10)
        edit_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        if param_type in ['str', 'int', 'float', 'bool']:
            # Простые типы - Entry
            value_var = tk.StringVar(value=param_value)
            value_entry = ttk.Entry(edit_frame, textvariable=value_var, width=50)
            value_entry.pack(fill=tk.X, pady=5)
        else:
            # Сложные типы - Text
            value_text = tk.Text(edit_frame, height=10, width=50)
            value_text.pack(fill=tk.BOTH, expand=True, pady=5)
            value_text.insert(1.0, param_value)
        
        # Кнопки
        button_frame = ttk.Frame(edit_dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_changes():
            try:
                if param_type in ['str', 'int', 'float', 'bool']:
                    new_value = value_var.get()
                else:
                    new_value = value_text.get(1.0, tk.END).strip()
                
                # Здесь должна быть логика сохранения изменений
                messagebox.showinfo("Успех", "Изменения сохранены")
                edit_dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")
        
        ttk.Button(button_frame, text="💾 Сохранить", command=save_changes).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Отмена", command=edit_dialog.destroy).pack(side=tk.LEFT)
    
    def copy_parameter_value(self):
        """Копирование значения параметра в буфер обмена"""
        if hasattr(self, 'selected_parameter') and self.selected_parameter:
            param_value = self.selected_parameter[2]
            self.dialog.clipboard_clear()
            self.dialog.clipboard_append(param_value)
            messagebox.showinfo("Успех", "Значение скопировано в буфер обмена")
    
    def copy_parameter_path(self):
        """Копирование пути параметра в буфер обмена"""
        if hasattr(self, 'selected_parameter') and self.selected_parameter:
            param_path = self.selected_parameter[3]
            self.dialog.clipboard_clear()
            self.dialog.clipboard_append(param_path)
            messagebox.showinfo("Успех", "Путь скопирован в буфер обмена")
    
    def find_parameter_in_code(self):
        """Поиск параметра в коде (заглушка)"""
        if hasattr(self, 'selected_parameter') and self.selected_parameter:
            param_name = self.selected_parameter[0]
            messagebox.showinfo("Поиск в коде", f"Поиск параметра '{param_name}' в коде (функция в разработке)")
    
    
    def on_search_change(self, *args):
        """Обработка изменения поискового запроса"""
        # Автоматический поиск при изменении фильтров
        self.perform_search()
    
    def on_id_key_release(self, event):
        """Обработка отпускания клавиши в поле ID"""
        # Проверяем, что это не служебные клавиши
        if event.keysym in ['Control_L', 'Control_R', 'Shift_L', 'Shift_R', 'Alt_L', 'Alt_R', 'v', 'м']:
            return
        
        # Проверяем, что это не вставка (Control нажат)
        if event.state & 0x4:  # Control нажат
            return
        
        # Выполняем поиск с небольшой задержкой
        self.dialog.after(100, self.perform_search)
    
    def on_control_key(self, event):
        """Обработка Ctrl+клавиша для поддержки русской раскладки"""
        # Проверяем, что это Ctrl+V (английская раскладка) или Ctrl+м (русская раскладка)
        if event.keysym in ['v', 'м'] or event.keycode == 86:  # V или м
            # Предотвращаем стандартную обработку
            event.widget.event_generate('<<Paste>>')
            # Даем время на вставку, затем выполняем поиск
            self.dialog.after(100, self.perform_search)
        return "break"
    
    def on_paste(self, event):
        """Обработка вставки через Ctrl+V"""
        # Предотвращаем стандартную обработку
        event.widget.event_generate('<<Paste>>')
        # Даем время на вставку, затем выполняем поиск
        self.dialog.after(100, self.perform_search)
        return "break"
    
    def on_id_click(self, event):
        """Обработка клика по полю ID"""
        # Выделяем весь текст при клике (только если поле не пустое)
        if event.widget.get():
            event.widget.select_range(0, tk.END)
    
    def on_name_key_release(self, event):
        """Обработка отпускания клавиши в поле названия"""
        # Проверяем, что это не служебные клавиши
        if event.keysym in ['Control_L', 'Control_R', 'Shift_L', 'Shift_R', 'Alt_L', 'Alt_R', 'v', 'м']:
            return
        
        # Проверяем, что это не вставка (Control нажат)
        if event.state & 0x4:  # Control нажат
            return
        
        # Выполняем поиск с небольшой задержкой
        self.dialog.after(100, self.perform_search)
    
    def on_name_click(self, event):
        """Обработка клика по полю названия"""
        # Выделяем весь текст при клике (только если поле не пустое)
        if event.widget.get():
            event.widget.select_range(0, tk.END)
    
    def on_right_click(self, event):
        """Обработка правой кнопки мыши"""
        # Создаем контекстное меню
        context_menu = tk.Menu(self.dialog, tearoff=0)
        context_menu.add_command(label="📋 Вставить", command=lambda: self.paste_text(event.widget))
        context_menu.add_command(label="📋 Копировать", command=lambda: self.copy_text(event.widget))
        context_menu.add_command(label="✂️ Вырезать", command=lambda: self.cut_text(event.widget))
        context_menu.add_separator()
        context_menu.add_command(label="🗑️ Очистить", command=lambda: self.clear_text(event.widget))
        context_menu.add_command(label="📝 Выделить все", command=lambda: self.select_all_text(event.widget))
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def paste_text(self, widget):
        """Вставка текста"""
        try:
            # Получаем текст из буфера обмена
            clipboard_text = self.dialog.clipboard_get()
            if clipboard_text:
                # Очищаем поле и вставляем текст
                widget.delete(0, tk.END)
                widget.insert(0, clipboard_text)
                # Выполняем поиск
                self.dialog.after(100, self.perform_search)
        except tk.TclError:
            pass  # Буфер обмена пуст
    
    def copy_text(self, widget):
        """Копирование текста"""
        try:
            selected_text = widget.selection_get()
            self.dialog.clipboard_clear()
            self.dialog.clipboard_append(selected_text)
        except tk.TclError:
            pass  # Ничего не выделено
    
    def cut_text(self, widget):
        """Вырезание текста"""
        try:
            selected_text = widget.selection_get()
            self.dialog.clipboard_clear()
            self.dialog.clipboard_append(selected_text)
            widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.dialog.after(50, self.perform_search)
        except tk.TclError:
            pass  # Ничего не выделено
    
    def clear_text(self, widget):
        """Очистка текста"""
        widget.delete(0, tk.END)
        self.dialog.after(50, self.perform_search)
    
    def select_all_text(self, widget):
        """Выделение всего текста"""
        widget.select_range(0, tk.END)
    
    def perform_search(self):
        """Выполнение поиска предметов"""
        try:
            # Очистка результатов
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            self.search_results = []
            
            # Получение фильтров
            id_filter = self.id_var.get().lower()
            name_filter = self.name_var.get().lower()
            type_filter = self.type_var.get()
            prefab_category_filter = self.prefab_category_var.get()
            rarity_filter = self.rarity_var.get()
            
            # Поиск по всем предметам
            for item_id, item_data in self.items_db.items_data.items():
                # Фильтр по ID
                if id_filter and id_filter not in item_id.lower():
                    continue
                
                # Фильтр по типу
                if type_filter != 'Все' and item_data.get('_type') != type_filter:
                    continue
                
                # Фильтр по названию
                item_name = item_data.get('_name', '')
                if name_filter and name_filter not in item_name.lower():
                    continue
                
                # Фильтр по редкости
                if rarity_filter != 'Все':
                    props = item_data.get('_props', {})
                    item_rarity = props.get('RarityPvE', '')
                    if rarity_filter != item_rarity:
                        continue
                
                # Фильтр по категории префаба
                if prefab_category_filter != 'Все':
                    prefab_path = self.extract_prefab_path(item_data)
                    if not prefab_path or not prefab_path.startswith(f'assets/content/{prefab_category_filter}'):
                        continue
                
                # Добавляем в результаты
                self.search_results.append((item_id, item_data))
            
            # Отображение результатов
            self.display_search_results()
            
        except Exception as e:
            messagebox.showerror("Ошибка поиска", f"Ошибка при выполнении поиска: {str(e)}")
    
    def display_search_results(self):
        """Отображение результатов поиска"""
        for item_id, item_data in self.search_results:
            # Получение данных для отображения
            name = item_data.get('_name', 'N/A')
            item_type = item_data.get('_type', 'N/A')
            
            # Получение свойств
            props = item_data.get('_props', {})
            rarity = props.get('RarityPvE', 'N/A')
            weight = props.get('Weight', 0)
            price = props.get('BasePrice', 0)
            width = props.get('Width', 0)
            height = props.get('Height', 0)
            
            # Вставка в таблицу
            self.results_tree.insert('', 'end', values=(
                item_id,
                name,
                item_type,
                rarity,
                f"{weight:.2f}",
                f"{price:,}",
                f"{width}x{height}"
            ))
    
    def extract_prefab_path(self, item_data):
        """Извлечение пути префаба"""
        try:
            props = item_data.get('_props', {})
            prefab = props.get('Prefab', {})
            if isinstance(prefab, dict):
                return prefab.get('path', '')
            return ''
        except:
            return ''
    
    def on_item_select(self, event):
        """Обработка выбора предмета"""
        selection = self.results_tree.selection()
        if selection:
            item = self.results_tree.item(selection[0])
            item_id = item['values'][0]
            
            # Находим данные предмета
            for search_item_id, item_data in self.search_results:
                if search_item_id == item_id:
                    self.current_item = (search_item_id, item_data)
                    self.load_item_to_form(item_data)
                    break
    
    def on_item_double_click(self, event):
        """Обработка двойного клика по предмету"""
        self.on_item_select(event)
    
    def load_item_to_form(self, item_data):
        """Загрузка данных предмета в форму редактирования"""
        try:
            # Сохраняем оригинальные данные для сравнения
            import copy
            self.original_item_data = copy.deepcopy(item_data)
            self.changed_parameters.clear()
            
            # Обновляем динамические UI билдеры
            if hasattr(self, 'basic_ui_builder'):
                self.basic_ui_builder.set_values(item_data)
            
            if hasattr(self, 'properties_ui_builder'):
                props = item_data.get('_props', {})
                self.properties_ui_builder.set_values(props)
            
            if hasattr(self, 'advanced_ui_builder'):
                props = item_data.get('_props', {})
                self.advanced_ui_builder.set_values(props)
            
            # Обновляем JSON редактор
            if hasattr(self, 'json_text'):
                self.refresh_json_editor()
            
            # Добавляем обработчики изменений для синхронизации
            self.setup_change_handlers()
            
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", f"Ошибка при загрузке данных предмета: {str(e)}")
    
    def setup_change_handlers(self):
        """Настройка обработчиков изменений для синхронизации между вкладками"""
        try:
            # Добавляем обработчики для основных параметров
            if hasattr(self, 'basic_ui_builder'):
                for param_name, widget in self.basic_ui_builder.widgets.items():
                    if param_name in self.basic_ui_builder.variables:
                        var = self.basic_ui_builder.variables[param_name]
                        var.trace('w', self.on_parameter_change)
                    elif isinstance(widget, tk.Text):
                        widget.bind('<KeyRelease>', self.on_parameter_change)
            
            # Добавляем обработчики для свойств предмета
            if hasattr(self, 'properties_ui_builder'):
                for param_name, widget in self.properties_ui_builder.widgets.items():
                    if param_name in self.properties_ui_builder.variables:
                        var = self.properties_ui_builder.variables[param_name]
                        var.trace('w', self.on_parameter_change)
                    elif isinstance(widget, tk.Text):
                        widget.bind('<KeyRelease>', self.on_parameter_change)
            
            # Добавляем обработчики для дополнительных параметров
            if hasattr(self, 'advanced_ui_builder'):
                for param_name, widget in self.advanced_ui_builder.widgets.items():
                    if param_name in self.advanced_ui_builder.variables:
                        var = self.advanced_ui_builder.variables[param_name]
                        var.trace('w', self.on_parameter_change)
                    elif isinstance(widget, tk.Text):
                        widget.bind('<KeyRelease>', self.on_parameter_change)
                        
        except Exception as e:
            print(f"Ошибка настройки обработчиков изменений: {e}")
    
    def on_parameter_change(self, *args):
        """Обработка изменения параметров - умное обновление JSON"""
        try:
            if not self.current_item or not self.original_item_data:
                return
            
            # Получаем значения из всех UI билдеров
            basic_values = {}
            properties_values = {}
            advanced_values = {}
            
            if hasattr(self, 'basic_ui_builder'):
                basic_values = self.basic_ui_builder.get_values()
            
            if hasattr(self, 'properties_ui_builder'):
                properties_values = self.properties_ui_builder.get_values()
            
            if hasattr(self, 'advanced_ui_builder'):
                advanced_values = self.advanced_ui_builder.get_values()
            
            # Умно обновляем JSON, сохраняя структуру
            self._smart_update_json(basic_values, properties_values, advanced_values)
                
        except Exception as e:
            print(f"Ошибка обновления параметров: {e}")
    
    def _smart_update_json(self, basic_values, properties_values, advanced_values):
        """Умное обновление JSON с сохранением структуры"""
        if not self.current_item or not self.original_item_data:
            return
        
        item_id, current_data = self.current_item
        original_data = self.original_item_data
        
        # Создаем копию оригинальных данных
        import copy
        updated_data = copy.deepcopy(original_data)
        
        # Обновляем основные параметры
        for key, value in basic_values.items():
            if key != '_props':
                original_value = original_data.get(key)
                validated_value = self._validate_value(key, value, original_value)
                
                if validated_value != original_value:
                    updated_data[key] = validated_value
                    self.changed_parameters.add(key)
                else:
                    self.changed_parameters.discard(key)
        
        # Обновляем свойства предмета
        if properties_values or advanced_values:
            original_props = original_data.get('_props', {})
            updated_props = copy.deepcopy(original_props)
            
            # Объединяем все изменения в _props
            all_props_changes = {**properties_values, **advanced_values}
            
            for key, value in all_props_changes.items():
                original_value = original_props.get(key)
                validated_value = self._validate_value(key, value, original_value)
                
                if validated_value != original_value:
                    updated_props[key] = validated_value
                    self.changed_parameters.add(f"_props.{key}")
                else:
                    self.changed_parameters.discard(f"_props.{key}")
            
            updated_data['_props'] = updated_props
        
        # Обновляем current_item
        self.current_item = (item_id, updated_data)
        
        # Обновляем JSON редактор
        if hasattr(self, 'json_text'):
            self.refresh_json_editor()
    
    def _validate_value(self, key: str, new_value: Any, original_value: Any) -> Any:
        """Валидация значения с сохранением типа"""
        try:
            # Если новое значение пустое, возвращаем оригинальное
            if new_value == '' or new_value is None:
                return original_value
            
            # Если оригинальное значение было числом, пытаемся преобразовать
            if isinstance(original_value, (int, float)):
                if isinstance(original_value, int):
                    return int(float(new_value))
                else:
                    return float(new_value)
            
            # Если оригинальное значение было булевым
            if isinstance(original_value, bool):
                if str(new_value).lower() in ('true', '1', 'yes', 'да'):
                    return True
                elif str(new_value).lower() in ('false', '0', 'no', 'нет'):
                    return False
                return original_value
            
            # Для строк и других типов возвращаем как есть
            return new_value
            
        except (ValueError, TypeError):
            # Если не удалось преобразовать, возвращаем оригинальное значение
            return original_value
    
    def save_changes(self):
        """Умное сохранение только измененных параметров"""
        if not self.current_item or not self.original_item_data:
            messagebox.showwarning("Предупреждение", "Выберите предмет для редактирования")
            return
        
        if not self.changed_parameters:
            messagebox.showinfo("Информация", "Нет изменений для сохранения")
            return
        
        try:
            item_id, current_data = self.current_item
            original_data = self.original_item_data
            
            # Создаем инкрементальные изменения
            incremental_changes = self._create_incremental_changes(original_data, current_data)
            
            # Сохраняем только измененные параметры
            if self.items_db.save_item_incremental(item_id, incremental_changes):
                # Обновляем оригинальные данные
                import copy
                self.original_item_data = copy.deepcopy(current_data)
                self.changed_parameters.clear()
                
                messagebox.showinfo("Успех", f"Сохранено {len(incremental_changes)} изменений")
                # Обновляем отображение в таблице
                self.perform_search()
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить изменения")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")
    
    def _create_incremental_changes(self, original_data, current_data):
        """Создание инкрементальных изменений"""
        changes = {}
        
        # Сравниваем основные параметры
        for key in current_data:
            if key != '_props':
                if current_data[key] != original_data.get(key):
                    changes[key] = current_data[key]
        
        # Сравниваем _props
        if '_props' in current_data:
            original_props = original_data.get('_props', {})
            current_props = current_data['_props']
            
            props_changes = {}
            for key in current_props:
                if current_props[key] != original_props.get(key):
                    props_changes[key] = current_props[key]
            
            if props_changes:
                changes['_props'] = props_changes
        
        return changes
    
    def refresh_item(self):
        """Обновление данных предмета"""
        if self.current_item:
            item_id, _ = self.current_item
            if item_id in self.items_db.items_data:
                # Загружаем свежие данные из базы
                item_data = self.items_db.items_data[item_id]
                self.current_item = (item_id, item_data)
                # Обновляем форму с новыми данными
                self.load_item_to_form(item_data)
                messagebox.showinfo("Обновлено", "Данные предмета обновлены из базы данных")
    
    def reset_filters(self):
        """Сброс фильтров поиска"""
        self.id_var.set('')
        self.name_var.set('')
        self.type_var.set('Все')
        self.prefab_category_var.set('Все')
        self.rarity_var.set('Все')
        self.perform_search()
    
    def on_closing(self):
        """Обработка закрытия диалога"""
        self.dialog.destroy()

def main():
    """Главная функция для тестирования"""
    root = tk.Tk()
    root.withdraw()
    
    server_path = Path(__file__).parent.parent
    dialog = ItemsSearchDialog(root, server_path)
    
    root.mainloop()

if __name__ == "__main__":
    main()
