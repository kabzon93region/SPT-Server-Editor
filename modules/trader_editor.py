#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trader Editor - Модуль для редактирования торговцев
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

# Импорт модулей проекта
try:
    from modules.traders_database import TradersDatabase
    from modules.trader_dialogs import TraderConfigDialog, CreateTraderDialog
except ImportError:
    # Если модули не найдены, добавляем путь к модулям
    import sys
    modules_path = str(Path(__file__).parent)
    if modules_path not in sys.path:
        sys.path.insert(0, modules_path)
    
    from traders_database import TradersDatabase
    from trader_dialogs import TraderConfigDialog, CreateTraderDialog

class TraderEditor:
    """Главный класс модуля редактирования торговцев"""
    
    def __init__(self, parent_window, server_path: Path):
        self.parent_window = parent_window
        self.server_path = server_path
        
        # Инициализация базы данных торговцев
        self.traders_db = TradersDatabase(server_path)
        
        # Используем переданное окно напрямую
        self.window = parent_window
        self.window.title("Редактор торговцев")
        self.window.geometry("1000x700")
        self.window.minsize(800, 600)
        
        # Добавляем поддержку управления окном
        try:
            from modules.ui_utils import add_window_controls, create_window_control_buttons
            add_window_controls(self.window)
        except Exception as e:
            print(f"Ошибка добавления управления окном: {e}")
        
        # Переменные
        self.current_traders = []
        self.selected_trader = None
        
        # Создание интерфейса
        self.create_widgets()
        self.load_traders()
        
        # Обработка закрытия окна
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Создание интерфейса"""
        # Главный фрейм
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Верхняя панель с информацией
        self.create_info_panel(main_frame)
        
        # Панель с кнопками действий
        self.create_action_panel(main_frame)
        
        # Основная панель с торговцами
        self.create_traders_panel(main_frame)
        
        # Нижняя панель с детальной информацией
        self.create_details_panel(main_frame)
    
    def create_info_panel(self, parent):
        """Создание информационной панели"""
        info_frame = ttk.LabelFrame(parent, text="Общая информация", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Статистика
        stats = self.traders_db.get_trader_statistics()
        
        stats_text = f"Торговцев: {stats['total_traders']} | "
        stats_text += f"Ассортимент: {stats['total_assort_items']} | "
        stats_text += f"Квестовый: {stats['total_quest_assort_items']}"
        
        ttk.Label(info_frame, text=stats_text, font=("Arial", 10, "bold")).pack()
        
        # Конфигурация
        config_info = self.traders_db.get_trader_config_info()
        config_text = f"Обновление по умолчанию: {config_info['update_time_default']}с | "
        config_text += f"Множитель цен: {config_info['trader_price_multiplier']}x"
        
        ttk.Label(info_frame, text=config_text).pack()
    
    def create_action_panel(self, parent):
        """Создание панели действий"""
        action_frame = ttk.LabelFrame(parent, text="Действия", padding=10)
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Кнопки действий
        ttk.Button(action_frame, text="Обновить список", command=self.load_traders).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Создать торговца", command=self.create_trader).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Редактировать выбранного", command=self.edit_selected_trader).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Удалить выбранного", command=self.delete_selected_trader).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Настройки конфигурации", command=self.edit_config).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Экспорт данных", command=self.export_data).pack(side=tk.LEFT, padx=(0, 10))
    
    def create_traders_panel(self, parent):
        """Создание панели с торговцами"""
        traders_frame = ttk.LabelFrame(parent, text="Торговцы", padding=10)
        traders_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Создание Treeview с прокруткой
        columns = ("name", "currency", "balance", "discount", "assort", "quest_assort", "services")
        self.tree = ttk.Treeview(traders_frame, columns=columns, show="headings", height=12)
        
        # Настройка колонок
        self.tree.heading("name", text="Название", command=lambda: self.sort_by_column("name"))
        self.tree.heading("currency", text="Валюта", command=lambda: self.sort_by_column("currency"))
        self.tree.heading("balance", text="Баланс", command=lambda: self.sort_by_column("balance"))
        self.tree.heading("discount", text="Скидка", command=lambda: self.sort_by_column("discount"))
        self.tree.heading("assort", text="Ассортимент", command=lambda: self.sort_by_column("assort"))
        self.tree.heading("quest_assort", text="Квестовый", command=lambda: self.sort_by_column("quest_assort"))
        self.tree.heading("services", text="Услуги", command=lambda: self.sort_by_column("services"))
        
        # Настройка ширины колонок
        self.tree.column("name", width=120)
        self.tree.column("currency", width=80)
        self.tree.column("balance", width=100)
        self.tree.column("discount", width=80)
        self.tree.column("assort", width=100)
        self.tree.column("quest_assort", width=100)
        self.tree.column("services", width=200)
        
        # Прокрутка
        scrollbar_y = ttk.Scrollbar(traders_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(traders_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Размещение
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        traders_frame.grid_rowconfigure(0, weight=1)
        traders_frame.grid_columnconfigure(0, weight=1)
        
        # Обработка выбора
        self.tree.bind("<<TreeviewSelect>>", self.on_trader_select)
        self.tree.bind("<Double-1>", self.on_trader_double_click)
    
    def create_details_panel(self, parent):
        """Создание панели с детальной информацией"""
        details_frame = ttk.LabelFrame(parent, text="Детальная информация", padding=10)
        details_frame.pack(fill=tk.X)
        
        # Создание notebook для вкладок
        self.details_notebook = ttk.Notebook(details_frame)
        self.details_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка "Основная информация"
        self.create_basic_info_tab()
        
        # Вкладка "Страховка"
        self.create_insurance_tab()
        
        # Вкладка "Уровни лояльности"
        self.create_loyalty_tab()
        
        # Вкладка "Услуги"
        self.create_services_tab()
    
    def create_basic_info_tab(self):
        """Создание вкладки основной информации"""
        basic_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(basic_frame, text="Основная информация")
        
        # Создание текстового виджета для отображения информации
        self.basic_info_text = tk.Text(basic_frame, height=8, wrap=tk.WORD)
        self.basic_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Прокрутка для текстового виджета
        basic_scrollbar = ttk.Scrollbar(basic_frame, orient=tk.VERTICAL, command=self.basic_info_text.yview)
        self.basic_info_text.configure(yscrollcommand=basic_scrollbar.set)
        basic_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_insurance_tab(self):
        """Создание вкладки страховки"""
        insurance_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(insurance_frame, text="Страховка")
        
        self.insurance_info_text = tk.Text(insurance_frame, height=8, wrap=tk.WORD)
        self.insurance_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        insurance_scrollbar = ttk.Scrollbar(insurance_frame, orient=tk.VERTICAL, command=self.insurance_info_text.yview)
        self.insurance_info_text.configure(yscrollcommand=insurance_scrollbar.set)
        insurance_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_loyalty_tab(self):
        """Создание вкладки уровней лояльности"""
        loyalty_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(loyalty_frame, text="Уровни лояльности")
        
        self.loyalty_info_text = tk.Text(loyalty_frame, height=8, wrap=tk.WORD)
        self.loyalty_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        loyalty_scrollbar = ttk.Scrollbar(loyalty_frame, orient=tk.VERTICAL, command=self.loyalty_info_text.yview)
        self.loyalty_info_text.configure(yscrollcommand=loyalty_scrollbar.set)
        loyalty_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_services_tab(self):
        """Создание вкладки услуг"""
        services_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(services_frame, text="Услуги")
        
        self.services_info_text = tk.Text(services_frame, height=8, wrap=tk.WORD)
        self.services_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        services_scrollbar = ttk.Scrollbar(services_frame, orient=tk.VERTICAL, command=self.services_info_text.yview)
        self.services_info_text.configure(yscrollcommand=services_scrollbar.set)
        services_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def load_traders(self):
        """Загрузка торговцев в таблицу"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получение информации о торговцах
        self.current_traders = self.traders_db.get_all_traders_info()
        
        # Заполнение таблицы
        for trader in self.current_traders:
            # Форматирование баланса
            balance = self.traders_db.format_currency(
                trader.get('balance_rub', 0), 
                trader.get('currency', 'RUB')
            )
            
            # Форматирование скидки
            discount = f"{trader.get('discount', 0)}%"
            
            # Форматирование услуг
            services = ", ".join(trader.get('services', []))
            if not services:
                services = "Нет"
            
            self.tree.insert('', 'end', values=(
                trader['name'],
                trader.get('currency', 'RUB'),
                balance,
                discount,
                trader.get('assort_count', 0),
                trader.get('quest_assort_count', 0),
                services
            ))
    
    def sort_by_column(self, column):
        """Сортировка по колонке"""
        # TODO: Реализовать сортировку
        pass
    
    def on_trader_select(self, event):
        """Обработка выбора торговца"""
        selected_items = self.tree.selection()
        if selected_items:
            item = self.tree.item(selected_items[0])
            trader_name = item['values'][0]
            
            # Находим ID торговца по имени
            trader_id = self.traders_db.get_trader_id_by_name(trader_name)
            if trader_id:
                self.selected_trader = trader_id
                self.update_details_panel()
    
    def on_trader_double_click(self, event):
        """Обработка двойного клика по торговцу"""
        self.edit_selected_trader()
    
    def update_details_panel(self):
        """Обновление панели детальной информации"""
        if not self.selected_trader:
            return
        
        # Обновляем вкладку основной информации
        self.update_basic_info()
        
        # Обновляем вкладку страховки
        self.update_insurance_info()
        
        # Обновляем вкладку уровней лояльности
        self.update_loyalty_info()
        
        # Обновляем вкладку услуг
        self.update_services_info()
    
    def update_basic_info(self):
        """Обновление основной информации"""
        if not self.selected_trader:
            return
        
        basic_info = self.traders_db.get_trader_base_info(self.selected_trader)
        
        info_text = f"ID: {basic_info['id']}\n"
        info_text += f"Название: {basic_info['name']}\n"
        info_text += f"Валюта: {basic_info['currency']}\n"
        info_text += f"Баланс RUB: {basic_info['balance_rub']:,}\n"
        info_text += f"Баланс USD: {basic_info['balance_dol']:,}\n"
        info_text += f"Баланс EUR: {basic_info['balance_eur']:,}\n"
        info_text += f"Скидка: {basic_info['discount']}%\n"
        info_text += f"Доступен в рейде: {'Да' if basic_info['available_in_raid'] else 'Нет'}\n"
        info_text += f"Покупает предметы: {'Да' if basic_info['buyer_up'] else 'Нет'}\n"
        info_text += f"Продает кастомизацию: {'Да' if basic_info['customization_seller'] else 'Нет'}\n"
        info_text += f"Высота сетки: {basic_info['grid_height']}\n"
        
        self.basic_info_text.delete(1.0, tk.END)
        self.basic_info_text.insert(1.0, info_text)
    
    def update_insurance_info(self):
        """Обновление информации о страховке"""
        if not self.selected_trader:
            return
        
        insurance_info = self.traders_db.get_trader_insurance_info(self.selected_trader)
        
        info_text = f"Доступность: {'Да' if insurance_info['availability'] else 'Нет'}\n"
        info_text += f"Максимальное время возврата: {insurance_info['max_return_hour']} часов\n"
        info_text += f"Максимальное время хранения: {insurance_info['max_storage_time']} часов\n"
        info_text += f"Минимальная плата: {insurance_info['min_payment']}\n"
        info_text += f"Минимальное время возврата: {insurance_info['min_return_hour']} часов\n"
        info_text += f"Исключенные категории: {len(insurance_info['excluded_category'])} предметов\n"
        
        self.insurance_info_text.delete(1.0, tk.END)
        self.insurance_info_text.insert(1.0, info_text)
    
    def update_loyalty_info(self):
        """Обновление информации об уровнях лояльности"""
        if not self.selected_trader:
            return
        
        loyalty_levels = self.traders_db.get_trader_loyalty_levels(self.selected_trader)
        
        info_text = "Уровни лояльности:\n\n"
        
        for level, requirements in loyalty_levels.items():
            info_text += f"Уровень {level}:\n"
            info_text += f"  Минимальный уровень: {requirements.get('minLevel', 'N/A')}\n"
            info_text += f"  Минимальная сумма продаж: {requirements.get('minSalesSum', 'N/A')}\n"
            info_text += f"  Минимальная репутация: {requirements.get('minStanding', 'N/A')}\n"
            info_text += f"  Минимальный уровень опасности: {requirements.get('minDangerLevel', 'N/A')}\n\n"
        
        if not loyalty_levels:
            info_text = "Информация об уровнях лояльности недоступна"
        
        self.loyalty_info_text.delete(1.0, tk.END)
        self.loyalty_info_text.insert(1.0, info_text)
    
    def update_services_info(self):
        """Обновление информации об услугах"""
        if not self.selected_trader:
            return
        
        services = self.traders_db.get_trader_services(self.selected_trader)
        
        info_text = "Услуги торговца:\n\n"
        
        if services:
            for i, service in enumerate(services, 1):
                info_text += f"{i}. {service}\n"
        else:
            info_text = "Услуги не предоставляются"
        
        self.services_info_text.delete(1.0, tk.END)
        self.services_info_text.insert(1.0, info_text)
    
    def create_trader(self):
        """Создание нового торговца"""
        CreateTraderDialog(self.window, self.traders_db, self.load_traders)
    
    def edit_selected_trader(self):
        """Редактирование выбранного торговца"""
        if not self.selected_trader:
            messagebox.showwarning("Предупреждение", "Выберите торговца для редактирования")
            return
        
        # TODO: Реализовать диалог редактирования торговца
        messagebox.showinfo("Информация", f"Редактирование торговца {self.traders_db.get_trader_name(self.selected_trader)} будет реализовано")
    
    def delete_selected_trader(self):
        """Удаление выбранного торговца"""
        if not self.selected_trader:
            messagebox.showwarning("Предупреждение", "Выберите торговца для удаления")
            return
        
        trader_name = self.traders_db.get_trader_name(self.selected_trader)
        
        if messagebox.askyesno("Подтверждение", f"Удалить торговца '{trader_name}'?\n\nЭто действие нельзя отменить!"):
            try:
                # Удаляем папку торговца
                trader_dir = self.traders_db.traders_dir / self.selected_trader
                if trader_dir.exists():
                    import shutil
                    shutil.rmtree(trader_dir)
                
                # Удаляем из конфигурации времени обновления
                update_times = self.traders_db.trader_config.get('updateTime', [])
                self.traders_db.trader_config['updateTime'] = [
                    ut for ut in update_times if ut.get('traderId') != self.selected_trader
                ]
                
                # Сохраняем конфигурацию
                self.traders_db.save_trader_config()
                
                # Перезагружаем данные
                self.traders_db.load_all_traders()
                
                # Обновляем интерфейс
                self.load_traders()
                self.selected_trader = None
                self.update_details_panel()
                
                messagebox.showinfo("Успех", f"Торговец '{trader_name}' удален")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка удаления торговца: {str(e)}")
    
    def edit_config(self):
        """Редактирование конфигурации торговцев"""
        TraderConfigDialog(self.window, self.traders_db, self.load_traders)
    
    def export_data(self):
        """Экспорт данных торговцев"""
        # TODO: Реализовать экспорт данных
        messagebox.showinfo("Информация", "Экспорт данных торговцев будет реализован")
    
    def on_closing(self):
        """Обработка закрытия окна"""
        # Показываем главное окно (оно будет показано основной программой)
        pass

def main():
    """Главная функция для тестирования модуля"""
    root = tk.Tk()
    root.withdraw()  # Скрываем главное окно
    
    server_path = Path(__file__).parent.parent
    editor = TraderEditor(root, server_path)
    
    root.mainloop()

if __name__ == "__main__":
    main()
