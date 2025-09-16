#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trader Dialogs - Диалоги для работы с торговцами
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Dict, List, Optional, Any, Callable
import random
import string
from pathlib import Path
import orjson as json

# Импорт модулей проекта
try:
    from modules.traders_database import TradersDatabase
except ImportError:
    # Если модули не найдены, добавляем путь к модулям
    import sys
    modules_path = str(Path(__file__).parent)
    if modules_path not in sys.path:
        sys.path.insert(0, modules_path)
    
    from traders_database import TradersDatabase

class TraderConfigDialog:
    """Диалог редактирования конфигурации торговцев"""
    
    def __init__(self, parent, traders_db, callback):
        self.parent = parent
        self.traders_db = traders_db
        self.callback = callback
        
        # Создание диалога
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Настройки конфигурации торговцев")
        self.dialog.geometry("800x600")
        self.dialog.minsize(600, 400)
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрирование диалога
        self.center_dialog()
        
        # Загрузка текущей конфигурации
        self.config = self.traders_db.trader_config.copy()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обработка закрытия
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)
    
    def center_dialog(self):
        """Центрирование диалога"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"800x600+{x}+{y}")
    
    def create_widgets(self):
        """Создание интерфейса диалога"""
        # Создание главного контейнера с прокруткой
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Размещение элементов
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        main_frame = ttk.Frame(scrollable_frame, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Настройки конфигурации торговцев", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Создание notebook для вкладок
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Вкладка "Общие настройки"
        self.create_general_tab(notebook)
        
        # Вкладка "Время обновления"
        self.create_update_time_tab(notebook)
        
        # Вкладка "Настройки Забора"
        self.create_fence_tab(notebook)
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Сохранить", command=self.on_save).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Отмена", command=self.on_cancel).pack(side=tk.RIGHT)
        
        # Привязка прокрутки колесиком мыши
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        self.dialog.bind("<Destroy>", _unbind_mousewheel)
    
    def create_general_tab(self, notebook):
        """Создание вкладки общих настроек"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Общие настройки")
        
        # Время обновления по умолчанию
        ttk.Label(frame, text="Время обновления по умолчанию (секунды):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.update_time_default_var = tk.IntVar(value=self.config.get('updateTimeDefault', 3600))
        ttk.Entry(frame, textvariable=self.update_time_default_var, width=20).grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Сброс торговцев при запуске сервера
        self.reset_from_start_var = tk.BooleanVar(value=self.config.get('tradersResetFromServerStart', True))
        ttk.Checkbutton(frame, text="Сброс торговцев при запуске сервера", variable=self.reset_from_start_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Покупки считаются найденными в рейде
        self.purchases_found_in_raid_var = tk.BooleanVar(value=self.config.get('purchasesAreFoundInRaid', False))
        ttk.Checkbutton(frame, text="Покупки считаются найденными в рейде", variable=self.purchases_found_in_raid_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Множитель цен торговцев
        ttk.Label(frame, text="Множитель цен торговцев:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.price_multiplier_var = tk.DoubleVar(value=self.config.get('traderPriceMultipler', 1.0))
        ttk.Entry(frame, textvariable=self.price_multiplier_var, width=20).grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Настройка растягивания колонок
        frame.columnconfigure(1, weight=1)
    
    def create_update_time_tab(self, notebook):
        """Создание вкладки времени обновления"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Время обновления")
        
        # Создание Treeview для времени обновления
        columns = ("name", "trader_id", "min_time", "max_time")
        self.update_time_tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        
        self.update_time_tree.heading("name", text="Название")
        self.update_time_tree.heading("trader_id", text="ID торговца")
        self.update_time_tree.heading("min_time", text="Мин. время (сек)")
        self.update_time_tree.heading("max_time", text="Макс. время (сек)")
        
        self.update_time_tree.column("name", width=120)
        self.update_time_tree.column("trader_id", width=200)
        self.update_time_tree.column("min_time", width=100)
        self.update_time_tree.column("max_time", width=100)
        
        # Прокрутка
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.update_time_tree.yview)
        self.update_time_tree.configure(yscrollcommand=scrollbar.set)
        
        self.update_time_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Кнопки для редактирования времени обновления
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        ttk.Button(button_frame, text="Редактировать", command=self.edit_update_time).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Добавить", command=self.add_update_time).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Удалить", command=self.remove_update_time).pack(side=tk.LEFT)
        
        # Заполнение таблицы
        self.populate_update_time_table()
    
    def create_fence_tab(self, notebook):
        """Создание вкладки настроек Забора"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Настройки Забора")
        
        fence_config = self.config.get('fence', {})
        discount_options = fence_config.get('discountOptions', {})
        
        # Размер ассортимента
        ttk.Label(frame, text="Размер ассортимента:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.assort_size_var = tk.IntVar(value=discount_options.get('assortSize', 45))
        ttk.Entry(frame, textvariable=self.assort_size_var, width=20).grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Множитель цены предметов
        ttk.Label(frame, text="Множитель цены предметов:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.item_price_mult_var = tk.DoubleVar(value=discount_options.get('itemPriceMult', 0.8))
        ttk.Entry(frame, textvariable=self.item_price_mult_var, width=20).grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Множитель цены пресетов
        ttk.Label(frame, text="Множитель цены пресетов:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.preset_price_mult_var = tk.DoubleVar(value=discount_options.get('presetPriceMult', 1.15))
        ttk.Entry(frame, textvariable=self.preset_price_mult_var, width=20).grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Настройка растягивания колонок
        frame.columnconfigure(1, weight=1)
    
    def populate_update_time_table(self):
        """Заполнение таблицы времени обновления"""
        for item in self.update_time_tree.get_children():
            self.update_time_tree.delete(item)
        
        update_times = self.config.get('updateTime', [])
        for update_time in update_times:
            name = update_time.get('_name', 'Неизвестно')
            trader_id = update_time.get('traderId', '')
            seconds = update_time.get('seconds', {})
            min_time = seconds.get('min', 0)
            max_time = seconds.get('max', 0)
            
            self.update_time_tree.insert('', 'end', values=(name, trader_id, min_time, max_time))
    
    def edit_update_time(self):
        """Редактирование времени обновления"""
        selected_items = self.update_time_tree.selection()
        if not selected_items:
            messagebox.showwarning("Предупреждение", "Выберите торговца для редактирования")
            return
        
        item = self.update_time_tree.item(selected_items[0])
        trader_id = item['values'][1]
        
        # Находим торговца в конфигурации
        update_times = self.config.get('updateTime', [])
        for i, update_time in enumerate(update_times):
            if update_time.get('traderId') == trader_id:
                # Диалог редактирования времени
                dialog = UpdateTimeDialog(self.dialog, update_time, self.update_time_callback, i)
                break
    
    def add_update_time(self):
        """Добавление времени обновления"""
        dialog = UpdateTimeDialog(self.dialog, None, self.add_update_time_callback, None)
    
    def remove_update_time(self):
        """Удаление времени обновления"""
        selected_items = self.update_time_tree.selection()
        if not selected_items:
            messagebox.showwarning("Предупреждение", "Выберите торговца для удаления")
            return
        
        item = self.update_time_tree.item(selected_items[0])
        trader_id = item['values'][1]
        
        if messagebox.askyesno("Подтверждение", f"Удалить время обновления для торговца {item['values'][0]}?"):
            update_times = self.config.get('updateTime', [])
            self.config['updateTime'] = [ut for ut in update_times if ut.get('traderId') != trader_id]
            self.populate_update_time_table()
    
    def update_time_callback(self, index, update_time_data):
        """Обратный вызов для обновления времени обновления"""
        update_times = self.config.get('updateTime', [])
        if 0 <= index < len(update_times):
            update_times[index] = update_time_data
            self.populate_update_time_table()
    
    def add_update_time_callback(self, index, update_time_data):
        """Обратный вызов для добавления времени обновления"""
        update_times = self.config.get('updateTime', [])
        update_times.append(update_time_data)
        self.populate_update_time_table()
    
    def on_save(self):
        """Сохранение конфигурации"""
        try:
            # Обновляем конфигурацию
            self.config['updateTimeDefault'] = self.update_time_default_var.get()
            self.config['tradersResetFromServerStart'] = self.reset_from_start_var.get()
            self.config['purchasesAreFoundInRaid'] = self.purchases_found_in_raid_var.get()
            self.config['traderPriceMultipler'] = self.price_multiplier_var.get()
            
            # Обновляем настройки Забора
            fence_config = self.config.get('fence', {})
            discount_options = fence_config.get('discountOptions', {})
            discount_options['assortSize'] = self.assort_size_var.get()
            discount_options['itemPriceMult'] = self.item_price_mult_var.get()
            discount_options['presetPriceMult'] = self.preset_price_mult_var.get()
            fence_config['discountOptions'] = discount_options
            self.config['fence'] = fence_config
            
            # Сохраняем в базе данных
            self.traders_db.trader_config = self.config
            if self.traders_db.save_trader_config():
                messagebox.showinfo("Успех", "Конфигурация торговцев сохранена")
                self.dialog.destroy()
                if self.callback:
                    self.callback()
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить конфигурацию")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")
    
    def on_cancel(self):
        """Отмена редактирования"""
        self.dialog.destroy()

class UpdateTimeDialog:
    """Диалог редактирования времени обновления"""
    
    def __init__(self, parent, update_time_data, callback, index):
        self.parent = parent
        self.update_time_data = update_time_data or {}
        self.callback = callback
        self.index = index
        
        # Создание диалога
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Редактирование времени обновления")
        self.dialog.geometry("500x400")
        self.dialog.minsize(400, 300)
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрирование диалога
        self.center_dialog()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обработка закрытия
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)
    
    def center_dialog(self):
        """Центрирование диалога"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
    
    def create_widgets(self):
        """Создание интерфейса диалога"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title = "Редактирование времени обновления" if self.update_time_data else "Добавление времени обновления"
        title_label = ttk.Label(main_frame, text=title, font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Название торговца
        ttk.Label(main_frame, text="Название торговца:").pack(anchor=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar(value=self.update_time_data.get('_name', ''))
        ttk.Entry(main_frame, textvariable=self.name_var, width=40).pack(fill=tk.X, pady=(0, 10))
        
        # ID торговца
        ttk.Label(main_frame, text="ID торговца:").pack(anchor=tk.W, pady=(0, 5))
        self.trader_id_var = tk.StringVar(value=self.update_time_data.get('traderId', ''))
        ttk.Entry(main_frame, textvariable=self.trader_id_var, width=40).pack(fill=tk.X, pady=(0, 10))
        
        # Минимальное время
        ttk.Label(main_frame, text="Минимальное время (секунды):").pack(anchor=tk.W, pady=(0, 5))
        seconds = self.update_time_data.get('seconds', {})
        self.min_time_var = tk.IntVar(value=seconds.get('min', 3600))
        ttk.Entry(main_frame, textvariable=self.min_time_var, width=40).pack(fill=tk.X, pady=(0, 10))
        
        # Максимальное время
        ttk.Label(main_frame, text="Максимальное время (секунды):").pack(anchor=tk.W, pady=(0, 5))
        self.max_time_var = tk.IntVar(value=seconds.get('max', 3600))
        ttk.Entry(main_frame, textvariable=self.max_time_var, width=40).pack(fill=tk.X, pady=(0, 20))
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Сохранить", command=self.on_save).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Отмена", command=self.on_cancel).pack(side=tk.RIGHT)
    
    def on_save(self):
        """Сохранение времени обновления"""
        try:
            update_time_data = {
                '_name': self.name_var.get(),
                'traderId': self.trader_id_var.get(),
                'seconds': {
                    'min': self.min_time_var.get(),
                    'max': self.max_time_var.get()
                }
            }
            
            self.callback(self.index, update_time_data)
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")
    
    def on_cancel(self):
        """Отмена редактирования"""
        self.dialog.destroy()

class CreateTraderDialog:
    """Диалог создания нового торговца"""
    
    def __init__(self, parent, traders_db, callback):
        self.parent = parent
        self.traders_db = traders_db
        self.callback = callback
        
        # Создание диалога
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Создание нового торговца")
        self.dialog.geometry("600x500")
        self.dialog.minsize(500, 400)
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрирование диалога
        self.center_dialog()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обработка закрытия
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)
    
    def center_dialog(self):
        """Центрирование диалога"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
    
    def create_widgets(self):
        """Создание интерфейса диалога"""
        # Создание главного контейнера с прокруткой
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Размещение элементов
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        main_frame = ttk.Frame(scrollable_frame, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Создание нового торговца", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Название торговца
        ttk.Label(main_frame, text="Название торговца:").pack(anchor=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=50).pack(fill=tk.X, pady=(0, 10))
        
        # ID торговца
        ttk.Label(main_frame, text="ID торговца (оставьте пустым для автогенерации):").pack(anchor=tk.W, pady=(0, 5))
        self.trader_id_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.trader_id_var, width=50).pack(fill=tk.X, pady=(0, 10))
        
        # Шаблон для копирования
        ttk.Label(main_frame, text="Шаблон для копирования:").pack(anchor=tk.W, pady=(0, 5))
        self.template_var = tk.StringVar()
        template_combo = ttk.Combobox(main_frame, textvariable=self.template_var, width=47)
        template_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Заполнение списка шаблонов
        template_names = []
        for trader_id in self.traders_db.traders_data.keys():
            name = self.traders_db.get_trader_name(trader_id)
            template_names.append(f"{name} ({trader_id})")
        
        template_combo['values'] = template_names
        if template_names:
            template_combo.set(template_names[0])
        
        # Валюта
        ttk.Label(main_frame, text="Валюта:").pack(anchor=tk.W, pady=(0, 5))
        self.currency_var = tk.StringVar(value="RUB")
        currency_combo = ttk.Combobox(main_frame, textvariable=self.currency_var, width=47)
        currency_combo.pack(fill=tk.X, pady=(0, 10))
        currency_combo['values'] = ["RUB", "USD", "EUR"]
        
        # Баланс
        ttk.Label(main_frame, text="Начальный баланс:").pack(anchor=tk.W, pady=(0, 5))
        self.balance_var = tk.IntVar(value=7000000)
        ttk.Entry(main_frame, textvariable=self.balance_var, width=50).pack(fill=tk.X, pady=(0, 20))
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Создать", command=self.on_create).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Отмена", command=self.on_cancel).pack(side=tk.RIGHT)
        
        # Привязка прокрутки колесиком мыши
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        self.dialog.bind("<Destroy>", _unbind_mousewheel)
    
    def generate_trader_id(self):
        """Генерация уникального ID торговца"""
        while True:
            # Генерируем 24-символьный hex ID
            trader_id = ''.join(random.choices(string.hexdigits.lower(), k=24))
            
            # Проверяем уникальность
            if trader_id not in self.traders_db.traders_data:
                return trader_id
    
    def on_create(self):
        """Создание торговца"""
        try:
            # Валидация
            if not self.name_var.get().strip():
                messagebox.showerror("Ошибка", "Введите название торговца")
                return
            
            # Генерируем ID если не указан
            trader_id = self.trader_id_var.get().strip()
            if not trader_id:
                trader_id = self.generate_trader_id()
            
            # Проверяем уникальность ID
            if trader_id in self.traders_db.traders_data:
                messagebox.showerror("Ошибка", "Торговец с таким ID уже существует")
                return
            
            # Получаем шаблон
            template_text = self.template_var.get()
            if not template_text:
                messagebox.showerror("Ошибка", "Выберите шаблон для копирования")
                return
            
            # Извлекаем ID шаблона
            template_id = template_text.split('(')[-1].rstrip(')')
            
            if template_id not in self.traders_db.traders_data:
                messagebox.showerror("Ошибка", "Шаблон не найден")
                return
            
            # Копируем данные шаблона
            template_data = self.traders_db.traders_data[template_id].copy()
            
            # Обновляем базовые данные
            if 'base' in template_data:
                base = template_data['base'].copy()
                base['_id'] = trader_id
                base['currency'] = self.currency_var.get()
                base['balance_rub'] = self.balance_var.get()
                base['balance_dol'] = 0
                base['balance_eur'] = 0
                template_data['base'] = base
            
            # Создаем папку торговца
            trader_dir = self.traders_db.traders_dir / trader_id
            trader_dir.mkdir(exist_ok=True)
            
            # Сохраняем файлы торговца
            for file_name, data in template_data.items():
                if data:  # Только если данные не пустые
                    file_path = trader_dir / f"{file_name}.json"
                    with open(file_path, 'wb') as f:
                        f.write(json.dumps(data, option=json.OPT_INDENT_2))
            
            # Добавляем в конфигурацию времени обновления
            update_times = self.traders_db.trader_config.get('updateTime', [])
            update_times.append({
                '_name': self.name_var.get().lower().replace(' ', '_'),
                'traderId': trader_id,
                'seconds': {
                    'min': 3600,
                    'max': 7200
                }
            })
            self.traders_db.trader_config['updateTime'] = update_times
            
            # Сохраняем конфигурацию
            self.traders_db.save_trader_config()
            
            # Перезагружаем данные
            self.traders_db.load_all_traders()
            
            messagebox.showinfo("Успех", f"Торговец {self.name_var.get()} создан успешно")
            self.dialog.destroy()
            if self.callback:
                self.callback()
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка создания торговца: {str(e)}")
    
    def on_cancel(self):
        """Отмена создания"""
        self.dialog.destroy()

def main():
    """Главная функция для тестирования модуля"""
    root = tk.Tk()
    root.withdraw()
    
    server_path = Path(__file__).parent.parent
    from traders_database import TradersDatabase
    traders_db = TradersDatabase(server_path)
    
    # Тест диалога конфигурации
    TraderConfigDialog(root, traders_db, None)
    
    root.mainloop()

if __name__ == "__main__":
    main()
