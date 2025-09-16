#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scav Recipes Dialog - Диалог для редактирования рецептов ящика диких
"""

import tkinter as tk
from tkinter import ttk, messagebox
import orjson as json
from pathlib import Path
from typing import Dict, List, Any, Optional
import random
import string

# Импорт модулей проекта
try:
    from items_cache import ItemsCache
    from context_menus import setup_context_menus_for_module
except ImportError:
    # Если модули не найдены, добавляем путь к модулям
    import sys
    modules_path = str(Path(__file__).parent)
    if modules_path not in sys.path:
        sys.path.insert(0, modules_path)
    
    from items_cache import ItemsCache
    from context_menus import setup_context_menus_for_module

class ScavRecipesDialog:
    """Диалог для редактирования рецептов ящика диких"""
    
    def __init__(self, parent, server_path: Path, items_cache: Optional[ItemsCache] = None):
        self.parent = parent
        self.server_path = server_path
        self.items_cache = items_cache
        self.production_file = server_path / "database" / "hideout" / "production.json"
        
        # Данные
        self.production_data = {}
        self.scav_recipes = []
        self.current_recipe_index = -1
        self.recipe_modified = False
        
        # Создание диалога
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Настройка ящика диких (Scav Recipes)")
        self.dialog.geometry("1200x900")
        self.dialog.minsize(1000, 800)
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрирование диалога
        self.center_dialog()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Загрузка данных
        self.load_data()
        
        # Настройка контекстных меню
        setup_context_menus_for_module(self)
        
        # Обработка закрытия
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_dialog(self):
        """Центрирование диалога"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (900 // 2)
        self.dialog.geometry(f"1200x900+{x}+{y}")
    
    def create_widgets(self):
        """Создание интерфейса диалога"""
        # Главный контейнер
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="🎒 Настройка ящика диких (Scav Recipes)", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Верхняя панель - список рецептов
        top_frame = ttk.LabelFrame(main_frame, text="Список рецептов ящика диких", padding="10")
        top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Дерево рецептов
        tree_frame = ttk.Frame(top_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'Время', 'Требования', 'Продукты')
        self.recipes_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12)
        
        # Настройка колонок
        self.recipes_tree.heading('ID', text='ID')
        self.recipes_tree.heading('Время', text='Время (сек)')
        self.recipes_tree.heading('Требования', text='Требования')
        self.recipes_tree.heading('Продукты', text='Продукты')
        
        self.recipes_tree.column('ID', width=200)
        self.recipes_tree.column('Время', width=80)
        self.recipes_tree.column('Требования', width=400)
        self.recipes_tree.column('Продукты', width=200)
        
        # Прокрутка для дерева
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.recipes_tree.yview)
        self.recipes_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.recipes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления
        buttons_frame = ttk.Frame(top_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Добавить рецепт", command=self.add_recipe).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Удалить рецепт", command=self.delete_recipe).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Дублировать", command=self.duplicate_recipe).pack(side=tk.LEFT)
        
        # Нижняя панель - редактирование рецепта
        bottom_frame = ttk.LabelFrame(main_frame, text="Редактирование рецепта", padding="10")
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        # Форма редактирования (без прокрутки)
        self.create_edit_form(bottom_frame)
        
        # Привязка событий
        self.recipes_tree.bind('<<TreeviewSelect>>', self.on_recipe_select)
        
        # Кнопки сохранения внизу диалога
        save_buttons_frame = ttk.Frame(main_frame)
        save_buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(save_buttons_frame, text="Сохранить все изменения", command=self.save_all_data).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(save_buttons_frame, text="Закрыть", command=self.on_closing).pack(side=tk.RIGHT)
    
    def create_edit_form(self, parent):
        """Создание формы редактирования рецепта"""
        # Верхняя строка - ID и время производства
        top_row = ttk.Frame(parent)
        top_row.pack(fill=tk.X, pady=(0, 10))
        
        # ID рецепта (левая половина)
        id_frame = ttk.Frame(top_row)
        id_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        ttk.Label(id_frame, text="ID рецепта:").pack(anchor=tk.W, pady=(0, 5))
        self.recipe_id_var = tk.StringVar()
        self.recipe_id_var.trace('w', self.on_field_change)
        ttk.Entry(id_frame, textvariable=self.recipe_id_var).pack(fill=tk.X)
        
        # Время производства (правая половина)
        time_frame = ttk.Frame(top_row)
        time_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        ttk.Label(time_frame, text="Время производства (сек):").pack(anchor=tk.W, pady=(0, 5))
        self.production_time_var = tk.IntVar()
        self.production_time_var.trace('w', self.on_field_change)
        ttk.Entry(time_frame, textvariable=self.production_time_var).pack(fill=tk.X)
        
        # Основной контент - требования и продукты в две колонки
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левая колонка - требования
        left_column = ttk.LabelFrame(content_frame, text="Требования", padding="5")
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Таблица требований
        req_frame = ttk.Frame(left_column)
        req_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        req_columns = ('ID', 'Тип', 'Предмет', 'Количество')
        self.requirements_tree = ttk.Treeview(req_frame, columns=req_columns, show='headings', height=8)
        
        self.requirements_tree.heading('ID', text='ID')
        self.requirements_tree.heading('Тип', text='Тип')
        self.requirements_tree.heading('Предмет', text='Предмет')
        self.requirements_tree.heading('Количество', text='Кол-во')
        
        self.requirements_tree.column('ID', width=200)
        self.requirements_tree.column('Тип', width=60)
        self.requirements_tree.column('Предмет', width=150)
        self.requirements_tree.column('Количество', width=60)
        
        # Прокрутка для требований
        req_scrollbar = ttk.Scrollbar(req_frame, orient=tk.VERTICAL, command=self.requirements_tree.yview)
        self.requirements_tree.configure(yscrollcommand=req_scrollbar.set)
        
        self.requirements_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        req_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Привязка событий для отслеживания изменений в требованиях
        self.requirements_tree.bind('<<TreeviewSelect>>', self.on_requirement_change)
        self.requirements_tree.bind('<Button-1>', self.on_requirement_change)
        self.requirements_tree.bind('<Key>', self.on_requirement_change)
        
        # Кнопки управления требованиями
        req_buttons_frame = ttk.Frame(left_column)
        req_buttons_frame.pack(fill=tk.X)
        
        ttk.Button(req_buttons_frame, text="Добавить", command=self.add_requirement).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(req_buttons_frame, text="Редактировать", command=self.edit_requirement).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(req_buttons_frame, text="Удалить", command=self.remove_requirement).pack(side=tk.LEFT)
        
        # Кнопка сохранения рецепта
        save_recipe_frame = ttk.Frame(left_column)
        save_recipe_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(save_recipe_frame, text="💾 Сохранить рецепт", command=self.save_recipe, 
                  style="Accent.TButton").pack(fill=tk.X)
        
        # Правая колонка - продукты по редкости
        right_column = ttk.LabelFrame(content_frame, text="Продукты по редкости", padding="5")
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Создание фреймов для каждой редкости
        rarities = ['Common', 'Rare', 'Superrare']
        self.rarity_vars = {}
        
        for i, rarity in enumerate(rarities):
            rarity_frame = ttk.Frame(right_column)
            rarity_frame.pack(fill=tk.X, pady=(0, 5))
            
            # Заголовок редкости
            ttk.Label(rarity_frame, text=rarity, font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
            
            # Строка с минимумом и максимумом
            minmax_frame = ttk.Frame(rarity_frame)
            minmax_frame.pack(fill=tk.X)
            
            # Минимум
            ttk.Label(minmax_frame, text="Мин:").pack(side=tk.LEFT, padx=(0, 5))
            min_var = tk.IntVar()
            min_var.trace('w', self.on_field_change)
            ttk.Entry(minmax_frame, textvariable=min_var, width=8).pack(side=tk.LEFT, padx=(0, 10))
            
            # Максимум
            ttk.Label(minmax_frame, text="Макс:").pack(side=tk.LEFT, padx=(0, 5))
            max_var = tk.IntVar()
            max_var.trace('w', self.on_field_change)
            ttk.Entry(minmax_frame, textvariable=max_var, width=8).pack(side=tk.LEFT)
            
            self.rarity_vars[rarity] = {'min': min_var, 'max': max_var}
        
        # Кнопки сохранения убраны - теперь они внизу диалога
    
    def on_field_change(self, *args):
        """Обработка изменений в полях формы"""
        if self.current_recipe_index >= 0:
            self.recipe_modified = True
            self.update_save_button()
    
    def on_requirement_change(self, *args):
        """Обработка изменений в требованиях"""
        if self.current_recipe_index >= 0:
            self.recipe_modified = True
            self.update_save_button()
    
    def update_save_button(self):
        """Обновление текста кнопки сохранения"""
        for widget in self.dialog.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Frame):
                        for button in child.winfo_children():
                            if isinstance(button, ttk.Button) and "Сохранить рецепт" in str(button.cget('text')):
                                if self.recipe_modified:
                                    button.configure(text="💾 Сохранить рецепт *")
                                else:
                                    button.configure(text="💾 Сохранить рецепт")
    
    def load_data(self):
        """Загрузка данных из файла"""
        try:
            if self.production_file.exists():
                with open(self.production_file, 'rb') as f:
                    self.production_data = json.loads(f.read())
                self.scav_recipes = self.production_data.get('scavRecipes', [])
            else:
                self.scav_recipes = []
            
            self.populate_recipes_tree()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки данных: {str(e)}")
            self.scav_recipes = []
    
    def populate_recipes_tree(self):
        """Заполнение дерева рецептов"""
        # Очистка дерева
        for item in self.recipes_tree.get_children():
            self.recipes_tree.delete(item)
        
        # Заполнение данными
        for i, recipe in enumerate(self.scav_recipes):
            recipe_id = recipe.get('_id', 'Неизвестно')
            production_time = recipe.get('productionTime', 0)
            
            # Требования с названиями предметов
            requirements = recipe.get('requirements', [])
            req_text = ""
            if requirements:
                req_items = []
                for req in requirements[:3]:  # Показываем только первые 3 предмета
                    template_id = req.get('templateId', '')
                    count = req.get('count', 0)
                    
                    # Получаем название предмета
                    item_name = "Неизвестно"
                    if self.items_cache and template_id:
                        item_name = self.items_cache.get_item_short_name(template_id)
                        # Обрезаем длинные названия
                        if len(item_name) > 20:
                            item_name = item_name[:17] + "..."
                    
                    req_items.append(f"{item_name} x{count}")
                
                req_text = ", ".join(req_items)
                if len(requirements) > 3:
                    req_text += f" (+{len(requirements) - 3} еще)"
            else:
                req_text = "Нет требований"
            
            # Продукты
            end_products = recipe.get('endProducts', {})
            products_text = ""
            for rarity, values in end_products.items():
                min_val = values.get('min', 0)
                max_val = values.get('max', 0)
                if min_val > 0 or max_val > 0:
                    products_text += f"{rarity}: {min_val}-{max_val}, "
            products_text = products_text.rstrip(", ")
            
            self.recipes_tree.insert('', 'end', values=(recipe_id, production_time, req_text, products_text))
    
    def on_recipe_select(self, event):
        """Обработка выбора рецепта"""
        selection = self.recipes_tree.selection()
        if not selection:
            return
        
        item = self.recipes_tree.item(selection[0])
        recipe_id = item['values'][0]
        
        # Находим рецепт по ID
        for i, recipe in enumerate(self.scav_recipes):
            if recipe.get('_id') == recipe_id:
                self.current_recipe_index = i
                self.load_recipe_to_form(recipe)
                break
    
    def load_recipe_to_form(self, recipe):
        """Загрузка рецепта в форму редактирования"""
        # Сбрасываем флаг изменений
        self.recipe_modified = False
        
        # ID рецепта
        self.recipe_id_var.set(recipe.get('_id', ''))
        
        # Время производства
        self.production_time_var.set(recipe.get('productionTime', 0))
        
        # Очистка требований
        for item in self.requirements_tree.get_children():
            self.requirements_tree.delete(item)
        
        # Загрузка требований
        requirements = recipe.get('requirements', [])
        for req in requirements:
            req_type = req.get('type', 'Item')
            template_id = req.get('templateId', '')
            count = req.get('count', 0)
            
            # Получаем название предмета и тип префаба
            item_name = "Неизвестно"
            prefab_type = ""
            if self.items_cache and template_id:
                item_name = self.items_cache.get_item_short_name(template_id)
                prefab_type = self.items_cache.get_item_prefab_type(template_id)
            
            # Формируем отображение как в основном менеджере крафта
            if prefab_type:
                item_display = f"{item_name} ({prefab_type})"
            else:
                item_display = f"{item_name} ({template_id})"
            
            self.requirements_tree.insert('', 'end', values=(template_id, req_type, item_display, count))
        
        # Загрузка продуктов по редкости
        end_products = recipe.get('endProducts', {})
        for rarity in ['Common', 'Rare', 'Superrare']:
            rarity_data = end_products.get(rarity, {})
            self.rarity_vars[rarity]['min'].set(rarity_data.get('min', 0))
            self.rarity_vars[rarity]['max'].set(rarity_data.get('max', 0))
    
    def add_recipe(self):
        """Добавление нового рецепта"""
        # Генерируем новый ID
        new_id = self._generate_recipe_id()
        
        # Создаем новый рецепт
        new_recipe = {
            "_id": new_id,
            "endProducts": {
                "Common": {"max": 0, "min": 0},
                "Rare": {"max": 0, "min": 0},
                "Superrare": {"max": 0, "min": 0}
            },
            "productionTime": 3600,
            "requirements": []
        }
        
        # Добавляем в список
        self.scav_recipes.append(new_recipe)
        
        # Обновляем дерево
        self.populate_recipes_tree()
        
        # Выбираем новый рецепт
        for item in self.recipes_tree.get_children():
            if self.recipes_tree.item(item)['values'][0] == new_id:
                self.recipes_tree.selection_set(item)
                self.recipes_tree.see(item)
                break
        
        # Загружаем в форму
        self.load_recipe_to_form(new_recipe)
    
    def delete_recipe(self):
        """Удаление выбранного рецепта"""
        selection = self.recipes_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите рецепт для удаления")
            return
        
        item = self.recipes_tree.item(selection[0])
        recipe_id = item['values'][0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить рецепт {recipe_id}?"):
            # Удаляем из списка
            self.scav_recipes = [r for r in self.scav_recipes if r.get('_id') != recipe_id]
            
            # Обновляем дерево
            self.populate_recipes_tree()
            
            # Очищаем форму
            self.clear_form()
    
    def duplicate_recipe(self):
        """Дублирование выбранного рецепта"""
        selection = self.recipes_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите рецепт для дублирования")
            return
        
        item = self.recipes_tree.item(selection[0])
        recipe_id = item['values'][0]
        
        # Находим рецепт
        original_recipe = None
        for recipe in self.scav_recipes:
            if recipe.get('_id') == recipe_id:
                original_recipe = recipe
                break
        
        if original_recipe:
            # Создаем копию с новым ID
            new_recipe = original_recipe.copy()
            new_recipe['_id'] = self._generate_recipe_id()
            
            # Добавляем в список
            self.scav_recipes.append(new_recipe)
            
            # Обновляем дерево
            self.populate_recipes_tree()
            
            # Выбираем новый рецепт
            for item in self.recipes_tree.get_children():
                if self.recipes_tree.item(item)['values'][0] == new_recipe['_id']:
                    self.recipes_tree.selection_set(item)
                    self.recipes_tree.see(item)
                    break
            
            # Загружаем в форму
            self.load_recipe_to_form(new_recipe)
    
    def add_requirement(self):
        """Добавление требования"""
        # Улучшенный диалог для добавления требования с поиском
        dialog = tk.Toplevel(self.dialog)
        dialog.title("Добавить требование")
        dialog.geometry("600x500")
        dialog.transient(self.dialog)
        dialog.grab_set()
        
        # Центрирование
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"600x500+{x}+{y}")
        
        # Главный контейнер
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Поиск предметов
        ttk.Label(main_frame, text="Поиск предмета:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        search_var = tk.StringVar()
        search_var.trace('w', lambda *args: self.search_items(search_var.get(), results_tree))
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=40)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(search_frame, text="Очистить", command=lambda: search_var.set("")).pack(side=tk.RIGHT)
        
        # Результаты поиска
        ttk.Label(main_frame, text="Результаты поиска:").pack(anchor=tk.W, pady=(10, 5))
        
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Таблица результатов
        results_columns = ('ID', 'Название', 'Тип префаба')
        results_tree = ttk.Treeview(results_frame, columns=results_columns, show='headings', height=8)
        
        results_tree.heading('ID', text='ID')
        results_tree.heading('Название', text='Название')
        results_tree.heading('Тип префаба', text='Тип префаба')
        
        results_tree.column('ID', width=200)
        results_tree.column('Название', width=200)
        results_tree.column('Тип префаба', width=150)
        
        # Прокрутка для результатов
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=results_tree.yview)
        results_tree.configure(yscrollcommand=results_scrollbar.set)
        
        results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Тип требования и количество
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Тип требования
        ttk.Label(options_frame, text="Тип:").pack(side=tk.LEFT, padx=(0, 5))
        type_var = tk.StringVar(value="Item")
        type_combo = ttk.Combobox(options_frame, textvariable=type_var, width=15, state="readonly")
        type_combo['values'] = ('Item', 'Area', 'Tool', 'Quest')
        type_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        # Количество
        ttk.Label(options_frame, text="Количество:").pack(side=tk.LEFT, padx=(0, 5))
        count_var = tk.IntVar(value=1)
        count_entry = ttk.Entry(options_frame, textvariable=count_var, width=10)
        count_entry.pack(side=tk.LEFT)
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def add_selected_item():
            selection = results_tree.selection()
            if not selection:
                messagebox.showwarning("Предупреждение", "Выберите предмет из списка")
                return
            
            item = results_tree.item(selection[0])
            template_id = item['values'][0]
            count = count_var.get()
            req_type = type_var.get()
            
            if count <= 0:
                messagebox.showerror("Ошибка", "Количество должно быть больше 0")
                return
            
            # Получаем название предмета и тип префаба
            item_name = "Неизвестно"
            prefab_type = ""
            if self.items_cache and template_id:
                item_name = self.items_cache.get_item_short_name(template_id)
                prefab_type = self.items_cache.get_item_prefab_type(template_id)
            
            # Формируем отображение как в основном менеджере крафта
            if prefab_type:
                item_display = f"{item_name} ({prefab_type})"
            else:
                item_display = f"{item_name} ({template_id})"
            
            # Добавляем в дерево требований
            self.requirements_tree.insert('', 'end', values=(template_id, req_type, item_display, count))
            
            # Отмечаем изменения
            self.on_requirement_change()
            
            dialog.destroy()
        
        ttk.Button(button_frame, text="Добавить выбранный", command=add_selected_item).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side=tk.RIGHT)
        
        # Загружаем все предметы при открытии
        self.search_items("", results_tree)
    
    def search_items(self, search_term, results_tree):
        """Поиск предметов по запросу"""
        # Очистка результатов
        for item in results_tree.get_children():
            results_tree.delete(item)
        
        if not self.items_cache:
            return
        
        search_term = search_term.lower()
        count = 0
        max_results = 100  # Ограничиваем количество результатов
        
        # Поиск по всем предметам в кэше
        for item_id, item_data in self.items_cache.full_cache.items():
            if count >= max_results:
                break
                
            # Получаем название и тип префаба
            item_name = self.items_cache.get_item_short_name(item_id)
            prefab_type = self.items_cache.get_item_prefab_type(item_id)
            
            # Проверяем соответствие поисковому запросу
            if (search_term in item_name.lower() or 
                search_term in item_id.lower() or 
                search_term in prefab_type.lower()):
                
                # Обрезаем длинные названия
                display_name = item_name
                if len(display_name) > 30:
                    display_name = display_name[:27] + "..."
                
                results_tree.insert('', 'end', values=(item_id, display_name, prefab_type))
                count += 1
    
    def edit_requirement(self):
        """Редактирование выбранного требования"""
        selection = self.requirements_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите требование для редактирования")
            return
        
        # Получаем данные выбранного требования
        item = selection[0]
        values = self.requirements_tree.item(item)['values']
        template_id = values[0]
        req_type = values[1]
        item_display = values[2]
        count = values[3]
        
        # Создаем диалог редактирования
        dialog = tk.Toplevel(self.dialog)
        dialog.title("Редактировать требование")
        dialog.geometry("500x300")
        dialog.transient(self.dialog)
        dialog.grab_set()
        
        # Центрирование
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"500x300+{x}+{y}")
        
        # Главный контейнер
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ID предмета
        ttk.Label(main_frame, text="ID предмета:").pack(anchor=tk.W, pady=(0, 5))
        id_var = tk.StringVar(value=template_id)
        ttk.Entry(main_frame, textvariable=id_var, width=50).pack(fill=tk.X, pady=(0, 10))
        
        # Тип требования
        ttk.Label(main_frame, text="Тип требования:").pack(anchor=tk.W, pady=(0, 5))
        type_var = tk.StringVar(value=req_type)
        type_combo = ttk.Combobox(main_frame, textvariable=type_var, width=47, state="readonly")
        type_combo['values'] = ('Item', 'Area', 'Tool', 'Quest')
        type_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Количество
        ttk.Label(main_frame, text="Количество:").pack(anchor=tk.W, pady=(0, 5))
        count_var = tk.IntVar(value=count)
        ttk.Entry(main_frame, textvariable=count_var, width=50).pack(fill=tk.X, pady=(0, 20))
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def save_changes():
            new_template_id = id_var.get().strip()
            new_type = type_var.get()
            new_count = count_var.get()
            
            if not new_template_id:
                messagebox.showerror("Ошибка", "Введите ID предмета")
                return
            
            if new_count <= 0:
                messagebox.showerror("Ошибка", "Количество должно быть больше 0")
                return
            
            # Получаем название предмета
            item_name = self.items_cache.get_item_name(new_template_id)
            if not item_name:
                item_name = new_template_id
            
            # Получаем тип префаба
            prefab_type = self.items_cache.get_item_prefab_type(new_template_id)
            
            # Формируем отображение
            if prefab_type:
                item_display = f"{item_name} ({prefab_type})"
            else:
                item_display = f"{item_name} ({new_template_id})"
            
            # Обновляем строку в таблице
            self.requirements_tree.item(item, values=(new_template_id, new_type, item_display, new_count))
            
            # Отмечаем изменения
            self.on_requirement_change()
            
            dialog.destroy()
        
        ttk.Button(button_frame, text="Сохранить", command=save_changes).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side=tk.RIGHT)
    
    def remove_requirement(self):
        """Удаление выбранного требования"""
        selection = self.requirements_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите требование для удаления")
            return
        
        self.requirements_tree.delete(selection[0])
        
        # Отмечаем изменения
        self.on_requirement_change()
    
    def save_recipe(self):
        """Сохранение рецепта"""
        if self.current_recipe_index < 0:
            messagebox.showwarning("Предупреждение", "Выберите рецепт для редактирования")
            return
        
        try:
            # Получаем данные из формы
            recipe_id = self.recipe_id_var.get().strip()
            production_time = self.production_time_var.get()
            
            if not recipe_id:
                messagebox.showerror("Ошибка", "Введите ID рецепта")
                return
            
            if production_time <= 0:
                messagebox.showerror("Ошибка", "Время производства должно быть больше 0")
                return
            
            # Собираем требования
            requirements = []
            for item in self.requirements_tree.get_children():
                values = self.requirements_tree.item(item)['values']
                template_id = values[0]  # ID теперь первый столбец
                req_type = values[1]     # Тип теперь второй столбец
                item_display = values[2] # Отображение предмета
                count = values[3]        # Количество теперь четвертый столбец
                
                requirements.append({
                    "count": count,
                    "isEncoded": False,
                    "isFunctional": False,
                    "isSpawnedInSession": False,
                    "templateId": template_id,
                    "type": req_type
                })
            
            # Собираем продукты по редкости
            end_products = {}
            for rarity in ['Common', 'Rare', 'Superrare']:
                min_val = self.rarity_vars[rarity]['min'].get()
                max_val = self.rarity_vars[rarity]['max'].get()
                end_products[rarity] = {"max": max_val, "min": min_val}
            
            # Обновляем рецепт
            self.scav_recipes[self.current_recipe_index] = {
                "_id": recipe_id,
                "endProducts": end_products,
                "productionTime": production_time,
                "requirements": requirements
            }
            
            # Обновляем дерево
            self.populate_recipes_tree()
            
            # Сбрасываем флаг изменений
            self.recipe_modified = False
            
            # Обновляем текст кнопки сохранения
            self.update_save_button()
            
            messagebox.showinfo("Успех", "Рецепт сохранен")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")
    
    def cancel_changes(self):
        """Отмена изменений"""
        if self.current_recipe_index >= 0 and self.current_recipe_index < len(self.scav_recipes):
            recipe = self.scav_recipes[self.current_recipe_index]
            self.load_recipe_to_form(recipe)
        else:
            self.clear_form()
    
    def clear_form(self):
        """Очистка формы"""
        self.recipe_id_var.set("")
        self.production_time_var.set(0)
        
        # Очистка требований
        for item in self.requirements_tree.get_children():
            self.requirements_tree.delete(item)
        
        # Очистка продуктов
        for rarity in ['Common', 'Rare', 'Superrare']:
            self.rarity_vars[rarity]['min'].set(0)
            self.rarity_vars[rarity]['max'].set(0)
        
        self.current_recipe_index = -1
    
    def _generate_recipe_id(self):
        """Генерация уникального ID рецепта"""
        while True:
            # Генерируем 24-символьный hex ID
            recipe_id = ''.join(random.choices(string.hexdigits.lower(), k=24))
            
            # Проверяем уникальность
            if not any(r.get('_id') == recipe_id for r in self.scav_recipes):
                return recipe_id
    
    def save_all_data(self):
        """Сохранение всех данных в файл"""
        try:
            # Обновляем данные
            self.production_data['scavRecipes'] = self.scav_recipes
            
            # Сохраняем в файл
            with open(self.production_file, 'wb') as f:
                f.write(json.dumps(self.production_data, option=json.OPT_INDENT_2))
            
            return True
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения файла: {str(e)}")
            return False
    
    def on_closing(self):
        """Обработка закрытия диалога"""
        if messagebox.askyesno("Подтверждение", "Сохранить изменения перед закрытием?"):
            if self.save_all_data():
                self.dialog.destroy()
        else:
            self.dialog.destroy()

def main():
    """Главная функция для тестирования модуля"""
    root = tk.Tk()
    root.withdraw()
    
    server_path = Path(__file__).parent.parent
    dialog = ScavRecipesDialog(root, server_path)
    
    root.mainloop()

if __name__ == "__main__":
    main()
