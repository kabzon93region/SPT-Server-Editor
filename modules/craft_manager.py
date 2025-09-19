#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Craft Manager - Модуль для редактирования рецептов крафта в убежище
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import orjson as json  # Используем orjson для ускорения JSON операций
from pathlib import Path
from typing import Dict, List, Any, Optional
try:
    from items_cache import ItemsCache
    from hideout_areas import HideoutAreas
    from context_menus import setup_context_menus_for_module
except ImportError:
    # Попробуем импорт из текущей директории
    import sys
    from pathlib import Path
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    from items_cache import ItemsCache
    from hideout_areas import HideoutAreas
    from context_menus import setup_context_menus_for_module

class CraftManager:
    def __init__(self, parent, server_path: Path):
        try:
            self.parent = parent
            self.server_path = server_path
            self.production_file = server_path / "database" / "hideout" / "production.json"
            
            # Данные
            self.production_data = {}
            self.recipes = []
            self.current_recipe_index = -1
            
            # Кэш предметов
            try:
                self.items_cache = ItemsCache(server_path)
            except Exception as e:
                print(f"Ошибка инициализации кэша предметов: {e}")
                # Создаем пустой кэш в случае ошибки
                self.items_cache = None
            
            # Настройка окна
            self.parent.title("Менеджер крафта - SPT Server Editor")
            # Автоматический размер окна
            self.parent.update_idletasks()
            self.parent.geometry("")  # Сбрасываем фиксированный размер
            self.parent.minsize(1000, 600)
            
            # Добавляем поддержку управления окном
            try:
                from modules.ui_utils import add_module_window_controls, create_window_control_buttons
                add_module_window_controls(self.parent)
            except Exception as e:
                print(f"Ошибка добавления управления окном: {e}")
            
            # Стили
            self.setup_styles()
            
            # Создание интерфейса
            self.create_widgets()
            
            # Загрузка данных
            self.load_data()
            
            # Настройка контекстных меню
            setup_context_menus_for_module(self)
            
            # Обработчик закрытия окна
            self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)
            
        except Exception as e:
            print(f"Критическая ошибка инициализации CraftManager: {e}")
            import traceback
            traceback.print_exc()
            # Показываем ошибку пользователю
            import tkinter.messagebox as mb
            mb.showerror("Ошибка инициализации", f"Ошибка инициализации менеджера крафта:\n{str(e)}")
            raise
    
    def on_closing(self):
        """Обработчик закрытия окна"""
        try:
            # Закрываем окно модуля
            self.parent.destroy()
        except Exception as e:
            print(f"Ошибка при закрытии окна крафта: {e}")
    
    def setup_styles(self):
        """Настройка стилей"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Info.TLabel', font=('Arial', 10))
        style.configure('Recipe.Treeview', font=('Consolas', 9))
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Главный контейнер - используем content_container если он есть
        parent_container = getattr(self.parent, 'content_container', self.parent)
        
        # Если используем content_container, настраиваем grid
        if hasattr(self.parent, 'content_container'):
            parent_container.grid_rowconfigure(0, weight=1)
            parent_container.grid_columnconfigure(0, weight=1)
            main_frame = ttk.Frame(parent_container, padding="10")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        else:
            # Если content_container нет, используем pack
            main_frame = ttk.Frame(parent_container, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="🔨 Менеджер рецептов крафта", style='Header.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Левая панель - список рецептов
        left_frame = ttk.LabelFrame(main_frame, text="Список рецептов", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Поиск
        search_frame = ttk.Frame(left_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(search_frame, text="Поиск:").grid(row=0, column=0, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_recipes)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        search_frame.columnconfigure(1, weight=1)
        
        # Дерево рецептов
        tree_frame = ttk.Frame(left_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        columns = ('ID', 'Продукт', 'Время', 'Область')
        self.recipes_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', style='Recipe.Treeview')
        
        # Настройка колонок
        self.recipes_tree.heading('ID', text='ID', command=lambda: self.sort_recipes_by_column('ID'))
        self.recipes_tree.heading('Продукт', text='Продукт', command=lambda: self.sort_recipes_by_column('Продукт'))
        self.recipes_tree.heading('Время', text='Время (сек)', command=lambda: self.sort_recipes_by_column('Время'))
        self.recipes_tree.heading('Область', text='Область', command=lambda: self.sort_recipes_by_column('Область'))
        
        self.recipes_tree.column('ID', width=100)
        self.recipes_tree.column('Продукт', width=200)
        self.recipes_tree.column('Время', width=80)
        self.recipes_tree.column('Область', width=80)
        
        # Переменные для сортировки
        self.recipes_sort_column = None
        self.recipes_sort_reverse = False
        
        # Скроллбар для дерева
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.recipes_tree.yview)
        self.recipes_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.recipes_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Привязка событий
        self.recipes_tree.bind('<<TreeviewSelect>>', self.on_recipe_select)
        
        # Кнопки управления рецептами
        buttons_frame = ttk.Frame(left_frame)
        buttons_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Добавить рецепт", command=self.add_recipe).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(buttons_frame, text="Удалить рецепт", command=self.delete_recipe).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(buttons_frame, text="Дублировать", command=self.duplicate_recipe).grid(row=0, column=2)
        
        # Кнопка настройки ящика диких
        ttk.Button(buttons_frame, text="Настройка ящика диких", command=self.open_scav_recipes).grid(row=1, column=0, columnspan=3, pady=(5, 0), sticky=(tk.W, tk.E))
        
        # Правая панель - редактирование рецепта
        right_frame = ttk.LabelFrame(main_frame, text="Редактирование рецепта", padding="10")
        right_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Основные свойства
        props_frame = ttk.LabelFrame(right_frame, text="Основные свойства", padding="10")
        props_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # ID рецепта
        ttk.Label(props_frame, text="ID рецепта:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.recipe_id_var = tk.StringVar()
        ttk.Entry(props_frame, textvariable=self.recipe_id_var, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Продукт
        ttk.Label(props_frame, text="ID продукта:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.end_product_var = tk.StringVar()
        end_product_entry = ttk.Entry(props_frame, textvariable=self.end_product_var, width=30)
        end_product_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Отображение названия продукта
        self.end_product_display_var = tk.StringVar()
        self.end_product_display_label = ttk.Label(props_frame, textvariable=self.end_product_display_var, 
                                                  font=('Arial', 9), foreground='blue')
        self.end_product_display_label.grid(row=1, column=2, sticky=tk.W, pady=2, padx=(10, 0))
        
        # Привязываем обновление отображения к изменению ID
        self.end_product_var.trace('w', self.update_end_product_display)
        
        # Количество
        ttk.Label(props_frame, text="Количество:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.count_var = tk.StringVar()
        ttk.Entry(props_frame, textvariable=self.count_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        # Время производства
        ttk.Label(props_frame, text="Время (сек):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.production_time_var = tk.StringVar()
        ttk.Entry(props_frame, textvariable=self.production_time_var, width=10).grid(row=3, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        # Область
        ttk.Label(props_frame, text="Тип области:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.area_type_var = tk.StringVar()
        area_combo = ttk.Combobox(props_frame, textvariable=self.area_type_var, width=30, state="readonly")
        
        # Получаем список областей с названиями из hideout_areas.py
        area_list = HideoutAreas.get_area_list()
        area_combo['values'] = area_list
        area_combo.grid(row=4, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        # Добавляем отображение названия области рядом с полем выбора
        self.area_type_display_var = tk.StringVar()
        self.area_type_display_label = ttk.Label(props_frame, textvariable=self.area_type_display_var, 
                                                foreground="blue", font=("Arial", 9))
        self.area_type_display_label.grid(row=4, column=2, sticky=tk.W, pady=2, padx=(5, 0))
        
        # Привязываем обновление отображения к изменению выбора
        self.area_type_var.trace('w', self.update_area_type_display)
        
        # Флаги
        flags_frame = ttk.LabelFrame(props_frame, text="Флаги", padding="5")
        flags_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.continuous_var = tk.BooleanVar()
        ttk.Checkbutton(flags_frame, text="Непрерывное производство", variable=self.continuous_var).grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        self.locked_var = tk.BooleanVar()
        ttk.Checkbutton(flags_frame, text="Заблокирован", variable=self.locked_var).grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        self.need_fuel_var = tk.BooleanVar()
        ttk.Checkbutton(flags_frame, text="Нужно топливо", variable=self.need_fuel_var).grid(row=1, column=0, sticky=tk.W, padx=(0, 20))
        
        self.is_encoded_var = tk.BooleanVar()
        ttk.Checkbutton(flags_frame, text="Закодировано", variable=self.is_encoded_var).grid(row=1, column=1, sticky=tk.W, padx=(0, 20))
        
        props_frame.columnconfigure(1, weight=1)
        
        # Требования
        req_frame = ttk.LabelFrame(right_frame, text="Требования", padding="10")
        req_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Таблица требований
        req_list_frame = ttk.Frame(req_frame)
        req_list_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Создаем Treeview для требований
        req_columns = ('Тип', 'Предмет/Область', 'Количество/Уровень')
        self.requirements_tree = ttk.Treeview(req_list_frame, columns=req_columns, show='headings', height=8)
        
        # Настройка колонок требований
        self.requirements_tree.heading('Тип', text='Тип', command=lambda: self.sort_requirements_by_column('Тип'))
        self.requirements_tree.heading('Предмет/Область', text='Предмет/Область', command=lambda: self.sort_requirements_by_column('Предмет/Область'))
        self.requirements_tree.heading('Количество/Уровень', text='Количество/Уровень', command=lambda: self.sort_requirements_by_column('Количество/Уровень'))
        
        self.requirements_tree.column('Тип', width=80)
        self.requirements_tree.column('Предмет/Область', width=250)
        self.requirements_tree.column('Количество/Уровень', width=120)
        
        # Переменные для сортировки требований
        self.requirements_sort_column = None
        self.requirements_sort_reverse = False
        
        req_scrollbar = ttk.Scrollbar(req_list_frame, orient=tk.VERTICAL, command=self.requirements_tree.yview)
        self.requirements_tree.configure(yscrollcommand=req_scrollbar.set)
        
        self.requirements_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        req_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        req_list_frame.columnconfigure(0, weight=1)
        req_list_frame.rowconfigure(0, weight=1)
        
        # Кнопки управления требованиями
        req_buttons_frame = ttk.Frame(req_frame)
        req_buttons_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        ttk.Button(req_buttons_frame, text="Добавить предмет", command=lambda: self.add_requirement('Item')).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(req_buttons_frame, text="Добавить область", command=lambda: self.add_requirement('Area')).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(req_buttons_frame, text="Добавить инструмент", command=lambda: self.add_requirement('Tool')).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(req_buttons_frame, text="Добавить квест", command=lambda: self.add_requirement('QuestComplete')).grid(row=0, column=3, padx=(0, 5))
        ttk.Button(req_buttons_frame, text="Редактировать", command=self.edit_requirement).grid(row=0, column=4, padx=(5, 0))
        ttk.Button(req_buttons_frame, text="Удалить", command=self.remove_requirement).grid(row=0, column=5, padx=(5, 0))
        
        req_frame.columnconfigure(0, weight=1)
        req_frame.rowconfigure(0, weight=1)
        
        # Кнопки сохранения
        save_frame = ttk.Frame(right_frame)
        save_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(save_frame, text="Сохранить изменения", command=self.save_recipe).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(save_frame, text="Отменить изменения", command=self.cancel_changes).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(save_frame, text="Сохранить в файл", command=self.save_to_file).grid(row=0, column=2)
        
        # Настройка весов
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(1, weight=1)
        left_frame.rowconfigure(1, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Настройка горячих клавиш
        self.setup_hotkeys()
    
    def load_data(self):
        """Загрузка данных из файла"""
        try:
            if self.production_file.exists():
                with open(self.production_file, 'rb') as f:
                    self.production_data = json.loads(f.read())
                
                self.recipes = self.production_data.get('recipes', [])
                self.populate_recipes_tree()
            else:
                messagebox.showerror("Ошибка", f"Файл {self.production_file} не найден")
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Ошибка", f"Ошибка при загрузке данных: {str(e)}")
    
    def populate_recipes_tree(self):
        """Заполнение дерева рецептов"""
        try:
            # Очистка дерева
            for item in self.recipes_tree.get_children():
                self.recipes_tree.delete(item)
            
            # Добавление рецептов
            for i, recipe in enumerate(self.recipes):
                recipe_id = recipe.get('_id', 'N/A')
                end_product_id = recipe.get('endProduct', 'N/A')
                
                # Формируем отображение предмета с названием и типом префаба
                if self.items_cache and end_product_id != 'N/A':
                    end_product_name = self.items_cache.get_item_short_name(end_product_id)
                    prefab_type = self.items_cache.get_item_prefab_type(end_product_id)
                    end_product_display = f"{end_product_name} ({prefab_type})"
                else:
                    end_product_display = 'N/A'
                
                production_time = recipe.get('productionTime', 0)
                area_type_num = recipe.get('areaType', 'N/A')
                
                # Преобразуем номер области в название
                if area_type_num != 'N/A' and isinstance(area_type_num, int):
                    area_type = HideoutAreas.get_area_name(area_type_num)
                else:
                    area_type = str(area_type_num)
                
                self.recipes_tree.insert('', 'end', values=(recipe_id, end_product_display, production_time, area_type))
            
        except Exception as e:
            print(f"Ошибка при заполнении дерева рецептов: {e}")
            import traceback
            traceback.print_exc()
    
    def filter_recipes(self, *args):
        """Фильтрация рецептов по поисковому запросу"""
        search_term = self.search_var.get().lower()
        
        # Очистка дерева
        for item in self.recipes_tree.get_children():
            self.recipes_tree.delete(item)
        
        # Добавление отфильтрованных рецептов
        for i, recipe in enumerate(self.recipes):
            recipe_id = recipe.get('_id', '')
            end_product_id = recipe.get('endProduct', '')
            
            # Формируем отображение предмета с названием и типом префаба (как в обычном списке)
            if self.items_cache and end_product_id:
                end_product_name = self.items_cache.get_item_short_name(end_product_id)
                prefab_type = self.items_cache.get_item_prefab_type(end_product_id)
                end_product_display = f"{end_product_name} ({prefab_type})"
            else:
                end_product_display = 'N/A'
            
            # Получаем название области для поиска
            area_type_num = recipe.get('areaType', 'N/A')
            if area_type_num != 'N/A' and isinstance(area_type_num, int):
                area_type_name = HideoutAreas.get_area_name(area_type_num)
            else:
                area_type_name = str(area_type_num)
            
            if (search_term in recipe_id.lower() or 
                search_term in end_product_id.lower() or 
                search_term in end_product_name.lower() or
                search_term in prefab_type.lower() or
                search_term in area_type_name.lower()):
                production_time = recipe.get('productionTime', 0)
                
                self.recipes_tree.insert('', 'end', values=(recipe_id, end_product_display, production_time, area_type_name))
    
    def on_recipe_select(self, event):
        """Обработка выбора рецепта"""
        selection = self.recipes_tree.selection()
        if selection:
            item = self.recipes_tree.item(selection[0])
            recipe_id = item['values'][0]
            
            # Поиск полного рецепта
            for i, recipe in enumerate(self.recipes):
                if recipe['_id'] == recipe_id:
                    self.current_recipe_index = i
                    self.load_recipe_to_form(recipe)
                    break
    
    def load_recipe_to_form(self, recipe):
        """Загрузка данных рецепта в форму"""
        self.recipe_id_var.set(recipe.get('_id', ''))
        self.end_product_var.set(recipe.get('endProduct', ''))
        self.count_var.set(str(recipe.get('count', 1)))
        self.production_time_var.set(str(recipe.get('productionTime', 0)))
        # Преобразуем номер области в название для отображения
        area_type_num = recipe.get('areaType', '')
        if area_type_num != '' and isinstance(area_type_num, int):
            area_name = HideoutAreas.get_area_name(area_type_num)
            self.area_type_var.set(f"{area_type_num}: {area_name}")
        else:
            self.area_type_var.set("")
        
        # Обновляем отображение области
        self.update_area_type_display()
        
        # Флаги
        self.continuous_var.set(recipe.get('continuous', False))
        self.locked_var.set(recipe.get('locked', False))
        self.need_fuel_var.set(recipe.get('needFuelForAllProductionTime', False))
        self.is_encoded_var.set(recipe.get('isEncoded', False))
        
        # Требования
        self.load_requirements(recipe.get('requirements', []))
        
        # Обновляем отображение конечного продукта
        self.update_end_product_display()
    
    def update_end_product_display(self, *args):
        """Обновление отображения названия конечного продукта"""
        item_id = self.end_product_var.get().strip()
        if self.items_cache and item_id:
            item_name = self.items_cache.get_item_short_name(item_id)
            prefab_type = self.items_cache.get_item_prefab_type(item_id)
            display_text = f"{item_name} ({prefab_type})"
            self.end_product_display_var.set(display_text)
        else:
            self.end_product_display_var.set("")
    
    def update_area_type_display(self, *args):
        """Обновление отображения названия области"""
        area_selection = self.area_type_var.get().strip()
        if not area_selection:
            self.area_type_display_var.set("")
            return
        
        try:
            # Извлекаем номер области из строки вида "7: Медблок"
            if ':' in area_selection:
                area_number = int(area_selection.split(':')[0])
                area_name = HideoutAreas.get_area_name(area_number)
                self.area_type_display_var.set(f"→ {area_name}")
            else:
                # Если формат неожиданный, пытаемся извлечь номер
                area_number = int(area_selection)
                area_name = HideoutAreas.get_area_name(area_number)
                self.area_type_display_var.set(f"→ {area_name}")
        except (ValueError, IndexError):
            self.area_type_display_var.set("→ Неизвестная область")
    
    def sort_recipes_by_column(self, column):
        """Сортировка рецептов по колонке"""
        # Если кликнули на ту же колонку, меняем направление сортировки
        if self.recipes_sort_column == column:
            self.recipes_sort_reverse = not self.recipes_sort_reverse
        else:
            self.recipes_sort_column = column
            self.recipes_sort_reverse = False
        
        # Получаем все элементы дерева
        items = []
        for item in self.recipes_tree.get_children():
            values = self.recipes_tree.item(item)['values']
            items.append((item, values))
        
        # Определяем индекс колонки для сортировки
        column_index = {'ID': 0, 'Продукт': 1, 'Время': 2, 'Область': 3}[column]
        
        # Сортируем элементы
        def sort_key(item):
            value = item[1][column_index]
            if column == 'Время':
                # Для времени сортируем по числовому значению
                try:
                    return int(value) if value else 0
                except (ValueError, TypeError):
                    return 0
            else:
                # Для остальных колонок сортируем по строковому значению
                return str(value).lower()
        
        items.sort(key=sort_key, reverse=self.recipes_sort_reverse)
        
        # Перестраиваем дерево
        for item, values in items:
            self.recipes_tree.move(item, '', 'end')
        
        # Обновляем заголовки с индикатором сортировки
        for col in ['ID', 'Продукт', 'Время', 'Область']:
            if col == column:
                arrow = " ↓" if self.recipes_sort_reverse else " ↑"
                self.recipes_tree.heading(col, text=f"{col}{arrow}")
            else:
                self.recipes_tree.heading(col, text=col)
    
    def load_requirements(self, requirements):
        """Загрузка требований в таблицу"""
        # Очистка таблицы
        for item in self.requirements_tree.get_children():
            self.requirements_tree.delete(item)
        
        self.current_requirements = requirements.copy()
        
        for req in requirements:
            req_type = req.get('type', 'Unknown')
            if req_type == 'Item':
                count = req.get('count', 1)
                template_id = req.get('templateId', 'N/A')
                if self.items_cache and template_id != 'N/A':
                    item_name = self.items_cache.get_item_short_name(template_id)
                    prefab_type = self.items_cache.get_item_prefab_type(template_id)
                    item_display = f"{item_name} ({prefab_type})"
                else:
                    item_display = "Unknown" if template_id != 'N/A' else "N/A"
                self.requirements_tree.insert('', 'end', values=('Предмет', item_display, count))
            elif req_type == 'Area':
                area_type_num = req.get('areaType', 'N/A')
                level = req.get('requiredLevel', 1)
                if area_type_num != 'N/A' and isinstance(area_type_num, int):
                    area_type_name = HideoutAreas.get_area_name(area_type_num)
                else:
                    area_type_name = str(area_type_num)
                self.requirements_tree.insert('', 'end', values=('Область', area_type_name, f"Уровень {level}"))
            elif req_type == 'Tool':
                template_id = req.get('templateId', 'N/A')
                if self.items_cache and template_id != 'N/A':
                    tool_name = self.items_cache.get_item_short_name(template_id)
                    prefab_type = self.items_cache.get_item_prefab_type(template_id)
                    tool_display = f"{tool_name} ({prefab_type})"
                else:
                    tool_display = "Unknown" if template_id != 'N/A' else "N/A"
                self.requirements_tree.insert('', 'end', values=('Инструмент', tool_display, '-'))
            elif req_type == 'QuestComplete':
                quest_id = req.get('questId', 'N/A')
                self.requirements_tree.insert('', 'end', values=('Квест', quest_id, '-'))
    
    def sort_requirements_by_column(self, column):
        """Сортировка требований по колонке"""
        # Если кликнули на ту же колонку, меняем направление сортировки
        if self.requirements_sort_column == column:
            self.requirements_sort_reverse = not self.requirements_sort_reverse
        else:
            self.requirements_sort_column = column
            self.requirements_sort_reverse = False
        
        # Получаем все элементы дерева
        items = []
        for item in self.requirements_tree.get_children():
            values = self.requirements_tree.item(item)['values']
            items.append((item, values))
        
        # Определяем индекс колонки для сортировки
        column_index = {'Тип': 0, 'Предмет/Область': 1, 'Количество/Уровень': 2}[column]
        
        # Сортируем элементы
        def sort_key(item):
            value = item[1][column_index]
            if column == 'Количество/Уровень':
                # Для колонки количества/уровня сортируем по числовому значению
                try:
                    if value == '-':
                        return 0
                    elif value.startswith('Уровень '):
                        return int(value.replace('Уровень ', ''))
                    else:
                        return int(value)
                except (ValueError, TypeError):
                    return 0
            else:
                # Для остальных колонок сортируем по строковому значению
                return str(value).lower()
        
        items.sort(key=sort_key, reverse=self.requirements_sort_reverse)
        
        # Перестраиваем дерево
        for item, values in items:
            self.requirements_tree.move(item, '', 'end')
        
        # Обновляем заголовки с индикатором сортировки
        for col in ['Тип', 'Предмет/Область', 'Количество/Уровень']:
            if col == column:
                arrow = " ↓" if self.requirements_sort_reverse else " ↑"
                self.requirements_tree.heading(col, text=f"{col}{arrow}")
            else:
                self.requirements_tree.heading(col, text=col)
    
    def add_requirement(self, req_type):
        """Добавление нового требования"""
        if not hasattr(self, 'current_requirements'):
            self.current_requirements = []
        
        if req_type == 'Item':
            self.add_item_requirement()
        elif req_type == 'Area':
            self.add_area_requirement()
        elif req_type == 'Tool':
            self.add_tool_requirement()
        elif req_type == 'QuestComplete':
            self.add_quest_requirement()
    
    def add_item_requirement(self):
        """Добавление требования предмета"""
        if not self.items_cache:
            messagebox.showerror("Ошибка", "Справочник предметов не загружен")
            return
        
        def on_item_selected(item_id):
            # Создаем диалог для ввода количества
            count_dialog = tk.Toplevel(self.parent)
            count_dialog.title("Количество предмета")
            count_dialog.geometry("300x150")
            count_dialog.transient(self.parent)
            count_dialog.grab_set()
            
            # Центрирование окна
            x = self.parent.winfo_rootx() + 100
            y = self.parent.winfo_rooty() + 100
            count_dialog.geometry(f"+{x}+{y}")
            
            # Информация о предмете
            item_name = self.items_cache.get_item_short_name(item_id)
            prefab_type = self.items_cache.get_item_prefab_type(item_id)
            
            ttk.Label(count_dialog, text=f"Предмет: {item_name}").pack(pady=10)
            ttk.Label(count_dialog, text=f"Тип: {prefab_type}").pack(pady=5)
            
            # Поле количества
            count_frame = ttk.Frame(count_dialog)
            count_frame.pack(pady=10)
            
            ttk.Label(count_frame, text="Количество:").pack(side=tk.LEFT, padx=(0, 5))
            count_var = tk.StringVar(value="1")
            count_entry = ttk.Entry(count_frame, textvariable=count_var, width=10)
            count_entry.pack(side=tk.LEFT)
            count_entry.focus()
            
            def add_item():
                try:
                    count = int(count_var.get()) if count_var.get() else 1
                    if count <= 0:
                        raise ValueError("Количество должно быть положительным")
                except ValueError as e:
                    messagebox.showerror("Ошибка", f"Некорректное количество: {e}")
                    return
                
                requirement = {
                    "count": count,
                    "isEncoded": False,
                    "isFunctional": False,
                    "isSpawnedInSession": False,
                    "templateId": item_id,
                    "type": "Item"
                }
                
                if not hasattr(self, 'current_requirements'):
                    self.current_requirements = []
                
                self.current_requirements.append(requirement)
                self.load_requirements(self.current_requirements)
                count_dialog.destroy()
            
            # Кнопки
            buttons_frame = ttk.Frame(count_dialog)
            buttons_frame.pack(pady=10)
            
            ttk.Button(buttons_frame, text="Добавить", command=add_item).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(buttons_frame, text="Отмена", command=count_dialog.destroy).pack(side=tk.LEFT)
            
            # Привязка Enter
            count_entry.bind('<Return>', lambda e: add_item())
        
        # Открываем окно поиска
        ItemSearchDialog(self.parent, self.items_cache, on_item_selected)
    
    def add_area_requirement(self):
        """Добавление требования области"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Добавить область")
        dialog.geometry("500x250")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        dialog.geometry("+%d+%d" % (self.parent.winfo_rootx() + 50, self.parent.winfo_rooty() + 50))
        
        ttk.Label(dialog, text="Тип области:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        area_type_var = tk.StringVar()
        area_combo = ttk.Combobox(dialog, textvariable=area_type_var, width=40, state="readonly")
        
        # Получаем список областей с названиями
        area_list = HideoutAreas.get_area_list()
        area_combo['values'] = area_list
        area_combo.grid(row=0, column=1, padx=10, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(dialog, text="Требуемый уровень:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        level_var = tk.StringVar(value="1")
        ttk.Entry(dialog, textvariable=level_var, width=10).grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Настройка весов
        dialog.columnconfigure(1, weight=1)
        
        def save_area():
            area_selection = area_type_var.get().strip()
            level = level_var.get().strip()
            
            if not area_selection:
                messagebox.showerror("Ошибка", "Выберите тип области")
                return
            
            try:
                # Извлекаем номер области из строки вида "7: Медблок"
                area_type = int(area_selection.split(':')[0])
                level = int(level)
                if level <= 0:
                    raise ValueError
            except (ValueError, IndexError):
                messagebox.showerror("Ошибка", "Введите корректные значения")
                return
            
            requirement = {
                "areaType": area_type,
                "requiredLevel": level,
                "type": "Area"
            }
            
            if not hasattr(self, 'current_requirements'):
                self.current_requirements = []
            
            self.current_requirements.append(requirement)
            self.load_requirements(self.current_requirements)
            dialog.destroy()
        
        ttk.Button(dialog, text="Добавить", command=save_area).grid(row=2, column=0, padx=10, pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).grid(row=2, column=1, padx=10, pady=10)
    
    def add_tool_requirement(self):
        """Добавление требования инструмента"""
        if not self.items_cache:
            messagebox.showerror("Ошибка", "Справочник предметов не загружен")
            return
        
        def on_tool_selected(item_id):
            requirement = {
                "templateId": item_id,
                "type": "Tool"
            }
            
            if not hasattr(self, 'current_requirements'):
                self.current_requirements = []
            
            self.current_requirements.append(requirement)
            self.load_requirements(self.current_requirements)
        
        # Открываем окно поиска
        ItemSearchDialog(self.parent, self.items_cache, on_tool_selected)
    
    def add_quest_requirement(self):
        """Добавление требования квеста"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Добавить квест")
        dialog.geometry("400x150")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        dialog.geometry("+%d+%d" % (self.parent.winfo_rootx() + 50, self.parent.winfo_rooty() + 50))
        
        ttk.Label(dialog, text="ID квеста:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        quest_id_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=quest_id_var, width=30).grid(row=0, column=1, padx=10, pady=5)
        
        def save_quest():
            quest_id = quest_id_var.get().strip()
            
            if not quest_id:
                messagebox.showerror("Ошибка", "Введите ID квеста")
                return
            
            requirement = {
                "questId": quest_id,
                "type": "QuestComplete"
            }
            
            self.current_requirements.append(requirement)
            self.load_requirements(self.current_requirements)
            dialog.destroy()
        
        ttk.Button(dialog, text="Добавить", command=save_quest).grid(row=1, column=0, padx=10, pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).grid(row=1, column=1, padx=10, pady=10)
    
    def edit_requirement(self):
        """Редактирование выбранного требования"""
        selection = self.requirements_tree.selection()
        if not selection:
            messagebox.showinfo("Информация", "Выберите требование для редактирования")
            return
        
        # Получаем индекс выбранного элемента
        selected_item = selection[0]
        item_index = self.requirements_tree.index(selected_item)
        
        if item_index >= len(self.current_requirements):
            messagebox.showerror("Ошибка", "Неверный индекс требования")
            return
        
        # Получаем требование для редактирования
        requirement = self.current_requirements[item_index]
        req_type = requirement.get('type', 'Unknown')
        
        if req_type == 'Item':
            self.edit_item_requirement(item_index, requirement)
        elif req_type == 'Area':
            self.edit_area_requirement(item_index, requirement)
        elif req_type == 'Tool':
            self.edit_tool_requirement(item_index, requirement)
        elif req_type == 'QuestComplete':
            self.edit_quest_requirement(item_index, requirement)
        else:
            messagebox.showinfo("Информация", f"Редактирование типа '{req_type}' не поддерживается")
    
    def edit_item_requirement(self, index, requirement):
        """Редактирование требования предмета"""
        # Открываем диалог поиска предметов
        def on_item_selected(item_id):
            # Создаем диалог для ввода количества
            dialog = tk.Toplevel(self.parent)
            dialog.title("Количество предмета")
            dialog.geometry("300x150")
            dialog.transient(self.parent)
            dialog.grab_set()
            
            # Центрирование окна
            x = self.parent.winfo_rootx() + 100
            y = self.parent.winfo_rooty() + 100
            dialog.geometry(f"+{x}+{y}")
            
            ttk.Label(dialog, text="Количество:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
            count_var = tk.StringVar(value=str(requirement.get('count', 1)))
            ttk.Entry(dialog, textvariable=count_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
            
            def save_item():
                try:
                    count = int(count_var.get())
                    if count <= 0:
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Ошибка", "Введите корректное количество (целое число больше 0)")
                    return
                
                # Обновляем требование
                self.current_requirements[index] = {
                    "templateId": item_id,
                    "count": count,
                    "type": "Item"
                }
                
                # Перезагружаем таблицу
                self.load_requirements(self.current_requirements)
                dialog.destroy()
            
            ttk.Button(dialog, text="Сохранить", command=save_item).grid(row=1, column=0, padx=10, pady=10)
            ttk.Button(dialog, text="Отмена", command=dialog.destroy).grid(row=1, column=1, padx=10, pady=10)
        
        # Открываем диалог поиска предметов с предварительно выбранным предметом
        current_item_id = requirement.get('templateId', '')
        ItemSearchDialog(self.parent, self.items_cache, on_item_selected, current_item_id)
    
    def edit_area_requirement(self, index, requirement):
        """Редактирование требования области"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Редактирование области")
        dialog.geometry("400x200")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Центрирование окна
        x = self.parent.winfo_rootx() + 50
        y = self.parent.winfo_rooty() + 50
        dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(dialog, text="Тип области:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        area_type_var = tk.StringVar()
        area_combo = ttk.Combobox(dialog, textvariable=area_type_var, width=40, state="readonly")
        
        # Получаем список областей с названиями
        area_list = HideoutAreas.get_area_list()
        area_combo['values'] = area_list
        area_combo.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Устанавливаем текущее значение
        current_area = requirement.get('areaType', 0)
        current_level = requirement.get('requiredLevel', 1)
        area_name = HideoutAreas.get_area_name(current_area)
        area_type_var.set(f"{current_area}: {area_name}")
        
        ttk.Label(dialog, text="Уровень:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        level_var = tk.StringVar(value=str(current_level))
        ttk.Entry(dialog, textvariable=level_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        dialog.columnconfigure(1, weight=1)
        
        def save_area():
            area_selection = area_type_var.get().strip()
            level = level_var.get().strip()
            
            if not area_selection:
                messagebox.showerror("Ошибка", "Выберите тип области")
                return
            
            try:
                # Извлекаем номер области из строки вида "7: Медблок"
                area_type = int(area_selection.split(':')[0])
                level = int(level)
                if level <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректный уровень (целое число больше 0)")
                return
            
            # Обновляем требование
            self.current_requirements[index] = {
                "areaType": area_type,
                "requiredLevel": level,
                "type": "Area"
            }
            
            # Перезагружаем таблицу
            self.load_requirements(self.current_requirements)
            dialog.destroy()
        
        ttk.Button(dialog, text="Сохранить", command=save_area).grid(row=2, column=0, padx=10, pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).grid(row=2, column=1, padx=10, pady=10)
    
    def edit_tool_requirement(self, index, requirement):
        """Редактирование требования инструмента"""
        def on_tool_selected(tool_id):
            # Обновляем требование
            self.current_requirements[index] = {
                "templateId": tool_id,
                "type": "Tool"
            }
            
            # Перезагружаем таблицу
            self.load_requirements(self.current_requirements)
        
        # Открываем диалог поиска инструментов с предварительно выбранным инструментом
        current_tool_id = requirement.get('templateId', '')
        ItemSearchDialog(self.parent, self.items_cache, on_tool_selected, current_tool_id)
    
    def edit_quest_requirement(self, index, requirement):
        """Редактирование требования квеста"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Редактирование квеста")
        dialog.geometry("400x150")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Центрирование окна
        x = self.parent.winfo_rootx() + 50
        y = self.parent.winfo_rooty() + 50
        dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(dialog, text="ID квеста:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        quest_id_var = tk.StringVar(value=requirement.get('questId', ''))
        ttk.Entry(dialog, textvariable=quest_id_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        dialog.columnconfigure(1, weight=1)
        
        def save_quest():
            quest_id = quest_id_var.get().strip()
            if not quest_id:
                messagebox.showerror("Ошибка", "Введите ID квеста")
                return
            
            # Обновляем требование
            self.current_requirements[index] = {
                "questId": quest_id,
                "type": "QuestComplete"
            }
            
            # Перезагружаем таблицу
            self.load_requirements(self.current_requirements)
            dialog.destroy()
        
        ttk.Button(dialog, text="Сохранить", command=save_quest).grid(row=1, column=0, padx=10, pady=10)
        ttk.Button(dialog, text="Отмена", command=dialog.destroy).grid(row=1, column=1, padx=10, pady=10)
    
    def remove_requirement(self):
        """Удаление выбранного требования"""
        selection = self.requirements_tree.selection()
        if selection:
            # Получаем индекс выбранного элемента
            selected_item = selection[0]
            item_index = self.requirements_tree.index(selected_item)
            
            # Удаляем из списка требований
            del self.current_requirements[item_index]
            
            # Перезагружаем таблицу
            self.load_requirements(self.current_requirements)
        else:
            messagebox.showinfo("Информация", "Выберите требование для удаления")
    
    def save_recipe(self):
        """Сохранение изменений рецепта"""
        if self.current_recipe_index < 0:
            messagebox.showinfo("Информация", "Выберите рецепт для редактирования")
            return
        
        try:
            # Создание обновленного рецепта
            updated_recipe = {
                "_id": self.recipe_id_var.get().strip(),
                "areaType": self._extract_area_type_from_display(),
                "continuous": self.continuous_var.get(),
                "count": int(self.count_var.get()) if self.count_var.get() else 1,
                "endProduct": self.end_product_var.get().strip(),
                "isCodeProduction": False,
                "isEncoded": self.is_encoded_var.get(),
                "locked": self.locked_var.get(),
                "needFuelForAllProductionTime": self.need_fuel_var.get(),
                "productionLimitCount": 0,
                "productionTime": int(self.production_time_var.get()) if self.production_time_var.get() else 0,
                "requirements": self.current_requirements
            }
            
            # Обновление в списке
            self.recipes[self.current_recipe_index] = updated_recipe
            
            # Обновление дерева
            self.populate_recipes_tree()
            
            messagebox.showinfo("Успех", "Рецепт сохранен")
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные данные: {str(e)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")
    
    def cancel_changes(self):
        """Отмена изменений"""
        if self.current_recipe_index >= 0:
            recipe = self.recipes[self.current_recipe_index]
            self.load_recipe_to_form(recipe)
    
    def add_recipe(self):
        """Добавление нового рецепта"""
        # Генерация уникального ID в формате MongoDB ObjectId
        new_id = self._generate_next_recipe_id()
        
        # Дополнительная проверка уникальности (на всякий случай)
        existing_ids = {recipe.get('_id', '') for recipe in self.recipes}
        if new_id in existing_ids:
            print(f"ERROR: Сгенерированный ID {new_id} уже существует в списке рецептов!")
            messagebox.showerror("Ошибка", f"Сгенерированный ID уже существует: {new_id}")
            return
        
        print(f"INFO: Создаем новый рецепт с ID: {new_id}")
        
        new_recipe = {
            "_id": new_id,
            "areaType": 10,  # Верстак по умолчанию
            "continuous": False,
            "count": 1,
            "endProduct": "",
            "isCodeProduction": False,
            "isEncoded": False,
            "locked": False,
            "needFuelForAllProductionTime": False,
            "productionLimitCount": 0,
            "productionTime": 0,
            "requirements": []
        }
        
        self.recipes.append(new_recipe)
        self.current_recipe_index = len(self.recipes) - 1
        self.load_recipe_to_form(new_recipe)
        self.populate_recipes_tree()
        
        messagebox.showinfo("Успех", "Новый рецепт добавлен")
    
    def delete_recipe(self):
        """Удаление рецепта"""
        if self.current_recipe_index < 0:
            messagebox.showinfo("Информация", "Выберите рецепт для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранный рецепт?"):
            del self.recipes[self.current_recipe_index]
            self.current_recipe_index = -1
            self.populate_recipes_tree()
            
            # Очистка формы
            self.recipe_id_var.set("")
            self.end_product_var.set("")
            self.count_var.set("1")
            self.production_time_var.set("0")
            self.area_type_var.set("")
            self.continuous_var.set(False)
            self.locked_var.set(False)
            self.need_fuel_var.set(False)
            
            # Обновляем отображение области
            self.update_area_type_display()
            self.is_encoded_var.set(False)
            # Очистка таблицы требований
            for item in self.requirements_tree.get_children():
                self.requirements_tree.delete(item)
            self.current_requirements = []
            
            messagebox.showinfo("Успех", "Рецепт удален")
    
    def duplicate_recipe(self):
        """Дублирование рецепта"""
        if self.current_recipe_index < 0:
            messagebox.showinfo("Информация", "Выберите рецепт для дублирования")
            return
        
        original_recipe = self.recipes[self.current_recipe_index].copy()
        new_id = self._generate_next_recipe_id()
        
        # Дополнительная проверка уникальности
        existing_ids = {recipe.get('_id', '') for recipe in self.recipes}
        if new_id in existing_ids:
            messagebox.showerror("Ошибка", f"Сгенерированный ID уже существует: {new_id}")
            return
        
        # Создание копии с новым ID
        new_recipe = original_recipe.copy()
        new_recipe["_id"] = new_id
        
        # Глубокое копирование требований
        new_recipe["requirements"] = [req.copy() for req in original_recipe.get("requirements", [])]
        
        self.recipes.append(new_recipe)
        self.current_recipe_index = len(self.recipes) - 1
        self.load_recipe_to_form(new_recipe)
        self.populate_recipes_tree()
        
        messagebox.showinfo("Успех", "Рецепт дублирован")
    
    def save_to_file(self):
        """Сохранение в файл"""
        try:
            # Обновление данных
            self.production_data['recipes'] = self.recipes
            
            # Создание резервной копии
            backup_file = self.production_file.with_suffix('.json.backup')
            if self.production_file.exists():
                import shutil
                shutil.copy2(self.production_file, backup_file)
            
            # Сохранение с использованием orjson
            with open(self.production_file, 'wb') as f:
                f.write(json.dumps(self.production_data, option=json.OPT_INDENT_2))
            
            messagebox.showinfo("Успех", f"Данные сохранены в {self.production_file}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении файла: {str(e)}")
    
    def setup_hotkeys(self):
        """Настройка горячих клавиш независимо от раскладки"""
        # Привязываем горячие клавиши к окну
        self.parent.bind('<Control-c>', self.copy_text)
        self.parent.bind('<Control-v>', self.paste_text)
        self.parent.bind('<Control-x>', self.cut_text)
        self.parent.bind('<Control-a>', self.select_all_text)
        
        # Привязываем к таблице требований
        self.requirements_tree.bind('<Control-c>', self.copy_text)
        self.requirements_tree.bind('<Control-v>', self.paste_text)
        self.requirements_tree.bind('<Control-x>', self.cut_text)
        self.requirements_tree.bind('<Control-a>', self.select_all_text)
        
        # Привязываем к дереву рецептов
        self.recipes_tree.bind('<Control-c>', self.copy_text)
        self.recipes_tree.bind('<Control-v>', self.paste_text)
        self.recipes_tree.bind('<Control-x>', self.cut_text)
        self.recipes_tree.bind('<Control-a>', self.select_all_text)
        
        # Привязываем к полям ввода
        for widget in [self.end_product_var, self.production_time_var, self.area_type_var]:
            if hasattr(widget, 'widget'):
                widget.widget.bind('<Control-c>', self.copy_text)
                widget.widget.bind('<Control-v>', self.paste_text)
                widget.widget.bind('<Control-x>', self.cut_text)
                widget.widget.bind('<Control-a>', self.select_all_text)
    
    def copy_text(self, event=None):
        """Копирование выделенного текста"""
        try:
            widget = event.widget
            if hasattr(widget, 'get'):
                # Для Entry и Text виджетов
                if hasattr(widget, 'selection_get'):
                    selected_text = widget.selection_get()
                    self.parent.clipboard_clear()
                    self.parent.clipboard_append(selected_text)
                elif hasattr(widget, 'get'):
                    # Для Entry виджетов
                    if hasattr(widget, 'selection_range'):
                        start, end = widget.selection_range()
                        if start != end:
                            selected_text = widget.get()[start:end]
                            self.parent.clipboard_clear()
                            self.parent.clipboard_append(selected_text)
            elif hasattr(widget, 'selection'):
                # Для Listbox
                selection = widget.curselection()
                if selection:
                    selected_text = widget.get(selection[0])
                    self.parent.clipboard_clear()
                    self.parent.clipboard_append(selected_text)
            elif hasattr(widget, 'selection'):
                # Для Treeview
                selection = widget.selection()
                if selection:
                    item = widget.item(selection[0])
                    if 'values' in item:
                        selected_text = ' '.join(str(v) for v in item['values'])
                        self.parent.clipboard_clear()
                        self.parent.clipboard_append(selected_text)
        except Exception:
            pass  # Игнорируем ошибки
    
    def paste_text(self, event=None):
        """Вставка текста из буфера обмена"""
        try:
            widget = event.widget
            if hasattr(widget, 'insert'):
                # Для Entry и Text виджетов
                clipboard_text = self.parent.clipboard_get()
                if hasattr(widget, 'selection_range'):
                    # Для Entry виджетов
                    start, end = widget.selection_range()
                    widget.delete(start, end)
                    widget.insert(start, clipboard_text)
                else:
                    # Для Text виджетов
                    widget.insert(tk.INSERT, clipboard_text)
        except Exception:
            pass  # Игнорируем ошибки
    
    def cut_text(self, event=None):
        """Вырезание выделенного текста"""
        try:
            widget = event.widget
            if hasattr(widget, 'get') and hasattr(widget, 'selection_range'):
                # Для Entry виджетов
                start, end = widget.selection_range()
                if start != end:
                    selected_text = widget.get()[start:end]
                    self.parent.clipboard_clear()
                    self.parent.clipboard_append(selected_text)
                    widget.delete(start, end)
        except Exception:
            pass  # Игнорируем ошибки
    
    def select_all_text(self, event=None):
        """Выделение всего текста"""
        try:
            widget = event.widget
            if hasattr(widget, 'selection_range'):
                # Для Entry виджетов
                widget.selection_range(0, tk.END)
            elif hasattr(widget, 'tag_add'):
                # Для Text виджетов
                widget.tag_add(tk.SEL, "1.0", tk.END)
                widget.mark_set(tk.INSERT, "1.0")
                widget.see(tk.INSERT)
        except Exception:
            pass  # Игнорируем ошибки
    
    def _generate_next_recipe_id(self):
        """Генерация уникального ID рецепта в формате MongoDB ObjectId (24 символа hex)"""
        # Получаем все существующие ID
        existing_ids = set()
        for recipe in self.recipes:
            recipe_id = recipe.get('_id', '')
            if recipe_id and len(recipe_id) == 24:
                existing_ids.add(recipe_id)
        
        print(f"DEBUG: Найдено {len(existing_ids)} существующих ID рецептов")
        if len(existing_ids) <= 10:  # Показываем только если их немного
            print(f"DEBUG: Существующие ID: {sorted(existing_ids)}")
        
        # Если рецептов нет, возвращаем базовый ID
        if not existing_ids:
            return "600000000000000000000000"
        
        # Генерируем случайные ID до тех пор, пока не найдем уникальный
        import random
        max_attempts = 10000  # Увеличиваем количество попыток
        
        for attempt in range(max_attempts):
            # Генерируем случайное 24-символьное hex число, начинающееся с 6
            random_part = ''.join(random.choices('0123456789abcdef', k=23))
            new_id = f"6{random_part}"
            
            if new_id not in existing_ids:
                print(f"DEBUG: Сгенерирован уникальный ID: {new_id} (попытка {attempt + 1})")
                return new_id
        
        print(f"DEBUG: Не удалось найти уникальный ID за {max_attempts} попыток, используем timestamp")
        
        # Если все попытки исчерпаны, используем timestamp с дополнительной случайностью
        import time
        timestamp = int(time.time() * 1000000)
        random_offset = random.randint(1, 999999)
        timestamp_hex = f"{(timestamp + random_offset):024x}"
        
        # Если и timestamp не уникален, добавляем еще больше случайности
        counter = 0
        while timestamp_hex in existing_ids and counter < 1000:
            counter += 1
            timestamp_hex = f"{(timestamp + random_offset + counter):024x}"
        
        print(f"DEBUG: Финальный ID на основе timestamp: {timestamp_hex}")
        return timestamp_hex
    
    def _extract_area_type_from_display(self):
        """Извлечение номера области из отображения"""
        area_display = self.area_type_var.get().strip()
        if not area_display:
            return 0
        
        try:
            # Если это формат "7: Медблок", извлекаем номер
            if ':' in area_display:
                return int(area_display.split(':')[0])
            # Если это просто число
            else:
                return int(area_display)
        except (ValueError, IndexError):
            return 0

    def open_scav_recipes(self):
        """Открытие диалога настройки ящика диких"""
        try:
            from scav_recipes_dialog import ScavRecipesDialog
            dialog = ScavRecipesDialog(self.parent, self.server_path, self.items_cache)
        except ImportError:
            # Если модуль не найден, создаем простой диалог
            self._create_simple_scav_dialog()
    
    def _create_simple_scav_dialog(self):
        """Создание простого диалога для настройки ящика диких"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Настройка ящика диких")
        dialog.geometry("800x600")
        dialog.minsize(600, 400)
        dialog.resizable(True, True)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Центрирование диалога
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"800x600+{x}+{y}")
        
        # Заголовок
        title_label = ttk.Label(dialog, text="Настройка ящика диких (Scav Recipes)", font=("Arial", 14, "bold"))
        title_label.pack(pady=20)
        
        # Информация
        info_label = ttk.Label(dialog, text="Модуль настройки ящика диких находится в разработке.\nЗдесь будет интерфейс для редактирования scavRecipes.", 
                              font=("Arial", 10))
        info_label.pack(pady=20)
        
        # Кнопка закрытия
        ttk.Button(dialog, text="Закрыть", command=dialog.destroy).pack(pady=20)


class ItemSearchDialog:
    """Окно поиска предметов для добавления в рецепт"""
    
    def __init__(self, parent, items_cache, callback, preselected_item_id=None):
        self.parent = parent
        self.items_cache = items_cache
        self.callback = callback
        self.search_results = []
        self.preselected_item_id = preselected_item_id
        
        # Создание окна
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Поиск предмета")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрирование окна
        x = parent.winfo_rootx() + 50
        y = parent.winfo_rooty() + 50
        self.dialog.geometry(f"+{x}+{y}")
        
        self.create_widgets()
        self.setup_hotkeys()
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Поля поиска
        search_frame = ttk.LabelFrame(main_frame, text="Поиск", padding=10)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Поле ID предмета
        ttk.Label(search_frame, text="ID предмета:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.id_var = tk.StringVar()
        self.id_entry = ttk.Entry(search_frame, textvariable=self.id_var, width=30)
        self.id_entry.grid(row=0, column=1, padx=(0, 10), pady=5, sticky=(tk.W, tk.E))
        
        # Поле названия предмета
        ttk.Label(search_frame, text="Название предмета:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(search_frame, textvariable=self.name_var, width=30)
        self.name_entry.grid(row=1, column=1, padx=(0, 10), pady=5, sticky=(tk.W, tk.E))
        
        # Кнопка поиска
        search_btn = ttk.Button(search_frame, text="Поиск", command=self.search_items)
        search_btn.grid(row=0, column=2, rowspan=2, padx=(10, 0), pady=5)
        
        # Настройка весов для полей поиска
        search_frame.columnconfigure(1, weight=1)
        
        # Результаты поиска
        results_frame = ttk.LabelFrame(main_frame, text="Результаты поиска", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Создание Treeview для результатов
        columns = ('ID', 'Name', 'Prefab')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        # Настройка колонок с сортировкой
        self.results_tree.heading('ID', text='ID предмета', command=lambda: self.sort_results_by_column('ID'))
        self.results_tree.heading('Name', text='Название', command=lambda: self.sort_results_by_column('Name'))
        self.results_tree.heading('Prefab', text='Тип префаба', command=lambda: self.sort_results_by_column('Prefab'))
        
        # Переменные для сортировки результатов
        self.results_sort_column = None
        self.results_sort_reverse = False
        
        self.results_tree.column('ID', width=120, minwidth=100)
        self.results_tree.column('Name', width=300, minwidth=200)
        self.results_tree.column('Prefab', width=200, minwidth=150)
        
        # Скроллбары
        v_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Размещение Treeview и скроллбаров
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Настройка весов
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Кнопки управления
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="Добавить", command=self.add_selected_item).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT)
        
        # Привязка событий
        self.name_entry.bind('<Return>', lambda e: self.search_items())
        self.id_entry.bind('<Return>', lambda e: self.search_items())
        self.results_tree.bind('<Double-1>', lambda e: self.add_selected_item())
        
        # Предварительное заполнение полей, если указан предмет
        if self.preselected_item_id and self.items_cache:
            self.id_var.set(self.preselected_item_id)
            # Получаем название предмета для предварительного заполнения
            item_name = self.items_cache.get_item_short_name(self.preselected_item_id)
            if item_name and not item_name.startswith("Unknown"):
                self.name_var.set(item_name)
            # Автоматически выполняем поиск
            self.search_items()
        else:
            # Загружаем все предметы по умолчанию
            self.load_all_items()
    
    def setup_hotkeys(self):
        """Настройка горячих клавиш"""
        self.dialog.bind('<Control-f>', lambda e: self.search_items())
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
        self.results_tree.bind('<Control-a>', lambda e: self.select_all_results())
    
    def search_items(self):
        """Поиск предметов по критериям"""
        name_query = self.name_var.get().strip()
        id_query = self.id_var.get().strip()
        
        self.search_results = []
        
        if not self.items_cache:
            messagebox.showerror("Ошибка", "Справочник предметов не загружен")
            return
        
        # Поиск по названию (приоритет)
        if name_query:
            self.search_by_name(name_query)
        elif id_query:
            self.search_by_id(id_query)
        else:
            # Если оба поля пустые, показываем все предметы с названиями
            self.load_all_items()
    
    def search_by_name(self, query):
        """Поиск по названию предмета"""
        query_lower = query.lower()
        exact_matches = []
        partial_matches = []
        
        for item_id, item_data in self.items_cache.full_cache.items():
            if not item_data:
                continue
                
            # Получаем все возможные названия
            names = []
            if 'locale' in item_data and item_data['locale']:
                if item_data['locale'].get('Name'):
                    names.append(item_data['locale']['Name'].lower())
                if item_data['locale'].get('ShortName'):
                    names.append(item_data['locale']['ShortName'].lower())
            
            if 'props' in item_data:
                if item_data['props'].get('Name'):
                    names.append(item_data['props']['Name'].lower())
                if item_data['props'].get('ShortName'):
                    names.append(item_data['props']['ShortName'].lower())
            
            if 'name' in item_data:
                names.append(item_data['name'].lower())
            
            # Проверяем точное совпадение
            for name in names:
                if name == query_lower:
                    exact_matches.append((item_id, item_data))
                    break
                elif query_lower in name:
                    partial_matches.append((item_id, item_data))
                    break
        
        # Объединяем результаты (сначала точные совпадения)
        self.search_results = exact_matches + partial_matches
        self.display_results()
    
    def search_by_id(self, query):
        """Поиск по ID предмета"""
        query_lower = query.lower()
        
        for item_id, item_data in self.items_cache.full_cache.items():
            if not item_data:
                continue
                
            if query_lower in item_id.lower():
                self.search_results.append((item_id, item_data))
        
        self.display_results()
    
    def load_all_items(self):
        """Загрузка всех предметов с названиями"""
        self.search_results = []
        
        for item_id, item_data in self.items_cache.full_cache.items():
            if not item_data:
                continue
            
            # Проверяем, есть ли у предмета название
            has_name = False
            if 'locale' in item_data and item_data['locale']:
                if item_data['locale'].get('Name') or item_data['locale'].get('ShortName'):
                    has_name = True
            elif 'props' in item_data:
                if item_data['props'].get('Name') or item_data['props'].get('ShortName'):
                    has_name = True
            elif 'name' in item_data:
                has_name = True
            
            if has_name:
                self.search_results.append((item_id, item_data))
        
        self.display_results()
    
    def display_results(self):
        """Отображение результатов поиска"""
        # Очистка дерева
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Добавление результатов
        preselected_item = None
        for item_id, item_data in self.search_results:
            name = self.items_cache.get_item_short_name(item_id)
            prefab_type = self.items_cache.get_item_prefab_type(item_id)
            
            item = self.results_tree.insert('', 'end', values=(
                item_id,
                name,
                prefab_type
            ))
            
            # Запоминаем предварительно выбранный предмет
            if self.preselected_item_id and item_id == self.preselected_item_id:
                preselected_item = item
        
        # Выделяем предварительно выбранный предмет
        if preselected_item:
            self.results_tree.selection_set(preselected_item)
            self.results_tree.see(preselected_item)
    
    def add_selected_item(self):
        """Добавление выбранного предмета"""
        selection = self.results_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите предмет из списка")
            return
        
        # Получаем индекс выбранного элемента
        item_index = self.results_tree.index(selection[0])
        if 0 <= item_index < len(self.search_results):
            item_id, item_data = self.search_results[item_index]
            self.callback(item_id)
            self.dialog.destroy()
    
    def select_all_results(self):
        """Выделение всех результатов"""
        for item in self.results_tree.get_children():
            self.results_tree.selection_add(item)
    
    def sort_results_by_column(self, column):
        """Сортировка результатов поиска по колонке"""
        # Если кликнули на ту же колонку, меняем направление сортировки
        if self.results_sort_column == column:
            self.results_sort_reverse = not self.results_sort_reverse
        else:
            self.results_sort_column = column
            self.results_sort_reverse = False
        
        # Получаем все элементы дерева
        items = []
        for item in self.results_tree.get_children():
            values = self.results_tree.item(item)['values']
            items.append((item, values))
        
        # Определяем индекс колонки для сортировки
        column_index = {'ID': 0, 'Name': 1, 'Prefab': 2}[column]
        
        # Сортируем элементы
        def sort_key(item):
            value = item[1][column_index]
            return str(value).lower()
        
        items.sort(key=sort_key, reverse=self.results_sort_reverse)
        
        # Перестраиваем дерево
        for item, values in items:
            self.results_tree.move(item, '', 'end')
        
        # Обновляем заголовки с индикатором сортировки
        for col in ['ID', 'Name', 'Prefab']:
            if col == column:
                arrow = " ↓" if self.results_sort_reverse else " ↑"
                self.results_tree.heading(col, text=f"{col}{arrow}")
            else:
                self.results_tree.heading(col, text=col)

def main():
    """Главная функция для тестирования модуля"""
    root = tk.Tk()
    server_path = Path(__file__).parent.parent
    app = CraftManager(root, server_path)
    root.mainloop()

if __name__ == "__main__":
    main()
