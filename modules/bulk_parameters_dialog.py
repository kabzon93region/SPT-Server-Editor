#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bulk Parameters Dialog - Диалог для массового изменения параметров предметов
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
import threading
import time
from datetime import datetime

# Импорт системы логирования loguru
try:
    from modules.loguru_logger import get_loguru_logger, LogCategory, debug, info, warning, error, critical, trace
    from modules.loguru_logger import log_function_calls, log_performance_decorator
except ImportError:
    # Заглушки для случая, если модуль логирования недоступен
    def get_loguru_logger():
        return None
    
    class LogCategory:
        SYSTEM = "SYSTEM"
        UI = "UI"
        DATABASE = "DATABASE"
        FILE_IO = "FILE_IO"
        ERROR = "ERROR"
        PERFORMANCE = "PERFORMANCE"
        VALIDATION = "VALIDATION"
        PROCESSING = "PROCESSING"
    
    def debug(msg, category=None, **kwargs): pass
    def info(msg, category=None, **kwargs): pass
    def warning(msg, category=None, **kwargs): pass
    def error(msg, category=None, **kwargs): pass
    def critical(msg, category=None, **kwargs): pass
    def trace(msg, category=None, **kwargs): pass
    
    def log_function_calls(category=None):
        def decorator(func):
            return func
        return decorator
    
    def log_performance_decorator(category=None):
        def decorator(func):
            return func
        return decorator

# Импорт модулей проекта
try:
    from modules.items_database import ItemsDatabase
    from modules.item_parameters_analyzer import ItemParametersAnalyzer
    from modules.ui_utils import center_window
except ImportError:
    # Если модули не найдены, добавляем путь к модулям
    import sys
    modules_path = str(Path(__file__).parent)
    if modules_path not in sys.path:
        sys.path.insert(0, modules_path)
    
    from items_database import ItemsDatabase
    from item_parameters_analyzer import ItemParametersAnalyzer
    from ui_utils import center_window

class BulkParametersDialog:
    """Диалог для массового изменения параметров предметов"""
    
    @log_function_calls(LogCategory.SYSTEM)
    def __init__(self, parent, server_path: Path, on_complete: Optional[Callable] = None):
        try:
            info("Инициализация BulkParametersDialog", LogCategory.SYSTEM)
            self.parent = parent
            self.server_path = server_path
            self.on_complete = on_complete
            
            debug(f"Путь к серверу: {server_path}", LogCategory.SYSTEM)
            
            # Инициализация модулей
            info("Инициализация модулей для массового изменения", LogCategory.DATABASE)
            try:
                self.items_db = ItemsDatabase(server_path)
                debug("ItemsDatabase инициализирован успешно", LogCategory.DATABASE)
            except Exception as e:
                error(f"Ошибка инициализации ItemsDatabase: {e}", LogCategory.ERROR, exception=e)
                raise
            
            try:
                self.analyzer = ItemParametersAnalyzer(server_path)
                debug("ItemParametersAnalyzer инициализирован успешно", LogCategory.DATABASE)
            except Exception as e:
                error(f"Ошибка инициализации ItemParametersAnalyzer: {e}", LogCategory.ERROR, exception=e)
                raise
            
            # Создание диалога
            info("Создание диалога массового изменения", LogCategory.UI)
            try:
                self.dialog = tk.Toplevel(parent)
                self.dialog.title("Массовое изменение параметров предметов")
                self.dialog.geometry("800x700")
                self.dialog.resizable(True, True)
                self.dialog.transient(parent)
                self.dialog.grab_set()
                debug("Диалог создан успешно", LogCategory.UI)
            except Exception as e:
                error(f"Ошибка создания диалога: {e}", LogCategory.ERROR, exception=e)
                raise
            
            # Центрирование
            try:
                center_window(self.dialog, 800, 700)
                debug("Диалог отцентрирован", LogCategory.UI)
            except Exception as e:
                warning(f"Ошибка центрирования диалога: {e}", LogCategory.UI)
            
            # Переменные
            self.item_ids_text = ""
            self.selected_parameter = ""
            self.parameter_value = ""
            self.is_processing = False
            self.processing_thread = None
            
            # Создание интерфейса
            info("Создание интерфейса диалога", LogCategory.UI)
            try:
                self.create_widgets()
                debug("Интерфейс создан успешно", LogCategory.UI)
            except Exception as e:
                error(f"Ошибка создания интерфейса: {e}", LogCategory.ERROR, exception=e)
                raise
            
            info("BulkParametersDialog инициализирован успешно", LogCategory.SYSTEM)
            
        except Exception as e:
            critical(f"Критическая ошибка инициализации BulkParametersDialog: {e}", LogCategory.ERROR, exception=e)
            # Показываем ошибку пользователю
            try:
                messagebox.showerror("Ошибка", f"Не удалось инициализировать диалог массового изменения:\n{e}")
            except:
                pass
            raise
        
        # Обработка закрытия
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        try:
            info("Начало создания интерфейса диалога", LogCategory.UI)
            
            # Главный фрейм
            try:
                main_frame = ttk.Frame(self.dialog, padding="10")
                main_frame.pack(fill=tk.BOTH, expand=True)
                debug("Главный фрейм создан", LogCategory.UI)
            except Exception as e:
                error(f"Ошибка создания главного фрейма: {e}", LogCategory.ERROR, exception=e)
                raise
            
            # Заголовок
            try:
                title_label = ttk.Label(main_frame, text="⚡ Массовое изменение параметров предметов", 
                                       font=("Arial", 14, "bold"))
                title_label.pack(pady=(0, 20))
                debug("Заголовок создан", LogCategory.UI)
            except Exception as e:
                error(f"Ошибка создания заголовка: {e}", LogCategory.ERROR, exception=e)
                raise
            
            # Создание notebook для вкладок
            try:
                self.notebook = ttk.Notebook(main_frame)
                self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
                debug("Notebook создан", LogCategory.UI)
            except Exception as e:
                error(f"Ошибка создания notebook: {e}", LogCategory.ERROR, exception=e)
                raise
            
            # Вкладка "Настройка"
            try:
                self.create_settings_tab()
                debug("Вкладка настроек создана", LogCategory.UI)
            except Exception as e:
                error(f"Ошибка создания вкладки настроек: {e}", LogCategory.ERROR, exception=e)
                raise
            
            # Вкладка "Предварительный просмотр"
            try:
                self.create_preview_tab()
                debug("Вкладка предварительного просмотра создана", LogCategory.UI)
            except Exception as e:
                error(f"Ошибка создания вкладки предварительного просмотра: {e}", LogCategory.ERROR, exception=e)
                raise
            
            # Вкладка "Лог"
            try:
                self.create_log_tab()
                debug("Вкладка лога создана", LogCategory.UI)
            except Exception as e:
                error(f"Ошибка создания вкладки лога: {e}", LogCategory.ERROR, exception=e)
                raise
            
            # Кнопки управления
            try:
                self.create_control_buttons(main_frame)
                debug("Кнопки управления созданы", LogCategory.UI)
            except Exception as e:
                error(f"Ошибка создания кнопок управления: {e}", LogCategory.ERROR, exception=e)
                raise
            
            info("Интерфейс диалога создан успешно", LogCategory.UI)
            
        except Exception as e:
            critical(f"Критическая ошибка создания интерфейса: {e}", LogCategory.ERROR, exception=e)
            raise
    
    def create_settings_tab(self):
        """Создание вкладки настроек"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Настройка")
        
        # Фрейм для списка ID предметов
        items_frame = ttk.LabelFrame(settings_frame, text="Список ID предметов", padding="10")
        items_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Инструкция
        instruction_label = ttk.Label(items_frame, 
                                    text="Введите ID предметов, каждый с новой строки:",
                                    font=("Arial", 10))
        instruction_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Текстовое поле для ID предметов
        self.item_ids_text_widget = scrolledtext.ScrolledText(items_frame, height=8, wrap=tk.WORD)
        self.item_ids_text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Кнопки для работы со списком
        list_buttons_frame = ttk.Frame(items_frame)
        list_buttons_frame.pack(fill=tk.X)
        
        ttk.Button(list_buttons_frame, text="Очистить", command=self.clear_item_ids).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(list_buttons_frame, text="Загрузить из файла", command=self.load_from_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(list_buttons_frame, text="Сохранить в файл", command=self.save_to_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(list_buttons_frame, text="Проверить ID", command=self.validate_item_ids).pack(side=tk.LEFT)
        
        # Фрейм для выбора параметра
        parameter_frame = ttk.LabelFrame(settings_frame, text="Параметр для изменения", padding="10")
        parameter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Выбор параметра
        param_select_frame = ttk.Frame(parameter_frame)
        param_select_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(param_select_frame, text="Параметр:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.parameter_var = tk.StringVar()
        self.parameter_combo = ttk.Combobox(param_select_frame, textvariable=self.parameter_var, 
                                          width=40, state="readonly")
        self.parameter_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Кнопка обновления списка параметров
        ttk.Button(param_select_frame, text="Обновить", command=self.update_parameters_list).pack(side=tk.LEFT)
        
        # Информация о параметре
        self.parameter_info_label = ttk.Label(parameter_frame, text="", font=("Arial", 9), foreground="blue")
        self.parameter_info_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Привязка события изменения параметра
        self.parameter_var.trace('w', self.on_parameter_changed)
        
        # Значение параметра
        value_frame = ttk.Frame(parameter_frame)
        value_frame.pack(fill=tk.X)
        
        ttk.Label(value_frame, text="Новое значение:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.value_var = tk.StringVar()
        self.value_entry = ttk.Entry(value_frame, textvariable=self.value_var, width=30)
        self.value_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Кнопка предложения значений
        ttk.Button(value_frame, text="Предложения", command=self.show_value_suggestions).pack(side=tk.LEFT)
        
        # Привязка события изменения значения
        self.value_var.trace('w', self.on_value_changed)
        
        # Информация о валидации
        self.validation_label = ttk.Label(parameter_frame, text="", font=("Arial", 9))
        self.validation_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Загрузка списка параметров
        self.update_parameters_list()
    
    def create_preview_tab(self):
        """Создание вкладки предварительного просмотра"""
        preview_frame = ttk.Frame(self.notebook)
        self.notebook.add(preview_frame, text="Предварительный просмотр")
        
        # Информация о предстоящих изменениях
        info_frame = ttk.LabelFrame(preview_frame, text="Информация о изменениях", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.preview_info_label = ttk.Label(info_frame, text="Заполните настройки для предварительного просмотра", 
                                          font=("Arial", 10))
        self.preview_info_label.pack(anchor=tk.W)
        
        # Таблица предварительного просмотра
        table_frame = ttk.LabelFrame(preview_frame, text="Предварительный просмотр изменений", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создание Treeview
        columns = ("item_id", "item_name", "current_value", "new_value", "status")
        self.preview_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Настройка колонок
        self.preview_tree.heading("item_id", text="ID предмета")
        self.preview_tree.heading("item_name", text="Название")
        self.preview_tree.heading("current_value", text="Текущее значение")
        self.preview_tree.heading("new_value", text="Новое значение")
        self.preview_tree.heading("status", text="Статус")
        
        self.preview_tree.column("item_id", width=120)
        self.preview_tree.column("item_name", width=200)
        self.preview_tree.column("current_value", width=150)
        self.preview_tree.column("new_value", width=150)
        self.preview_tree.column("status", width=100)
        
        # Скроллбары
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.preview_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.preview_tree.xview)
        self.preview_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Размещение
        self.preview_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Кнопка обновления предварительного просмотра
        ttk.Button(preview_frame, text="Обновить предварительный просмотр", 
                  command=self.update_preview).pack(pady=10)
    
    def create_log_tab(self):
        """Создание вкладки лога"""
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="Лог операций")
        
        # Текстовое поле для лога
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Кнопки для работы с логом
        log_buttons_frame = ttk.Frame(log_frame)
        log_buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(log_buttons_frame, text="Очистить лог", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(log_buttons_frame, text="Сохранить лог", command=self.save_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(log_buttons_frame, text="Экспорт в файл", command=self.export_log).pack(side=tk.LEFT)
    
    def create_control_buttons(self, parent):
        """Создание кнопок управления"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Кнопка запуска
        self.start_button = ttk.Button(buttons_frame, text="🚀 Запустить массовое изменение", 
                                     command=self.start_bulk_processing, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Кнопка отмены
        self.cancel_button = ttk.Button(buttons_frame, text="❌ Отмена", 
                                      command=self.on_closing, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Прогресс-бар
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(buttons_frame, variable=self.progress_var, 
                                          maximum=100, length=200)
        self.progress_bar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Статус
        self.status_var = tk.StringVar(value="Готов к работе")
        self.status_label = ttk.Label(buttons_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT)
    
    def update_parameters_list(self):
        """Обновление списка доступных параметров"""
        try:
            parameters = self.analyzer.get_available_parameters()
            self.parameter_combo['values'] = parameters
            
            # Показываем информацию о количестве параметров
            self.log_message(f"Загружено {len(parameters)} доступных параметров")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки параметров: {str(e)}")
    
    def on_parameter_changed(self, *args):
        """Обработка изменения выбранного параметра"""
        parameter = self.parameter_var.get()
        if not parameter:
            self.parameter_info_label.config(text="")
            return
        
        try:
            # Получаем информацию о параметре
            param_info = self.analyzer.get_parameter_info(parameter)
            
            info_text = f"Тип: {param_info['type']} | "
            info_text += f"Использований: {param_info['usage_count']} | "
            info_text += f"Часто используемый: {'Да' if param_info['is_common'] else 'Нет'}"
            
            self.parameter_info_label.config(text=info_text)
            
            # Обновляем предварительный просмотр
            self.update_preview()
            
        except Exception as e:
            self.parameter_info_label.config(text=f"Ошибка: {str(e)}")
    
    def on_value_changed(self, *args):
        """Обработка изменения значения параметра"""
        parameter = self.parameter_var.get()
        value = self.value_var.get()
        
        if not parameter or not value:
            self.validation_label.config(text="", foreground="black")
            return
        
        try:
            # Валидируем значение
            is_valid, message = self.analyzer.validate_parameter_value(parameter, value)
            
            if is_valid:
                self.validation_label.config(text=f"✓ {message}", foreground="green")
            else:
                self.validation_label.config(text=f"✗ {message}", foreground="red")
            
            # Обновляем предварительный просмотр
            self.update_preview()
            
        except Exception as e:
            self.validation_label.config(text=f"Ошибка валидации: {str(e)}", foreground="red")
    
    def show_value_suggestions(self):
        """Показ предложений значений для параметра"""
        parameter = self.parameter_var.get()
        if not parameter:
            messagebox.showwarning("Предупреждение", "Выберите параметр")
            return
        
        try:
            suggestions = self.analyzer.get_parameter_values(parameter, 20)
            
            if not suggestions:
                messagebox.showinfo("Информация", "Нет доступных значений для этого параметра")
                return
            
            # Создаем диалог с предложениями
            suggestion_dialog = tk.Toplevel(self.dialog)
            suggestion_dialog.title("Предложения значений")
            suggestion_dialog.geometry("400x300")
            suggestion_dialog.transient(self.dialog)
            suggestion_dialog.grab_set()
            
            center_window(suggestion_dialog, 400, 300)
            
            # Список предложений
            listbox = tk.Listbox(suggestion_dialog)
            listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            for suggestion in suggestions:
                listbox.insert(tk.END, suggestion)
            
            # Обработка выбора
            def on_select(event):
                selection = listbox.curselection()
                if selection:
                    selected_value = listbox.get(selection[0])
                    self.value_var.set(selected_value)
                    suggestion_dialog.destroy()
            
            listbox.bind('<Double-1>', on_select)
            
            # Кнопка отмены
            ttk.Button(suggestion_dialog, text="Отмена", command=suggestion_dialog.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка получения предложений: {str(e)}")
    
    def clear_item_ids(self):
        """Очистка списка ID предметов"""
        self.item_ids_text_widget.delete(1.0, tk.END)
        self.update_preview()
    
    def load_from_file(self):
        """Загрузка списка ID из файла"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Выберите файл с ID предметов",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.item_ids_text_widget.delete(1.0, tk.END)
                self.item_ids_text_widget.insert(1.0, content)
                self.update_preview()
                self.log_message(f"Загружен файл: {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки файла: {str(e)}")
    
    def save_to_file(self):
        """Сохранение списка ID в файл"""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            title="Сохранить список ID предметов",
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        
        if file_path:
            try:
                content = self.item_ids_text_widget.get(1.0, tk.END).strip()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log_message(f"Список сохранен в файл: {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка сохранения файла: {str(e)}")
    
    def validate_item_ids(self):
        """Проверка валидности ID предметов"""
        item_ids = self.get_item_ids_list()
        valid_ids = []
        invalid_ids = []
        
        for item_id in item_ids:
            if self.items_db.get_item(item_id):
                valid_ids.append(item_id)
            else:
                invalid_ids.append(item_id)
        
        if invalid_ids:
            message = f"Найдено {len(invalid_ids)} недействительных ID:\n\n"
            message += "\n".join(invalid_ids[:10])
            if len(invalid_ids) > 10:
                message += f"\n... и еще {len(invalid_ids) - 10}"
            messagebox.showwarning("Предупреждение", message)
        else:
            messagebox.showinfo("Информация", f"Все {len(valid_ids)} ID предметов действительны")
        
        self.log_message(f"Проверка ID: {len(valid_ids)} действительных, {len(invalid_ids)} недействительных")
    
    def get_item_ids_list(self) -> List[str]:
        """Получение списка ID предметов из текстового поля"""
        content = self.item_ids_text_widget.get(1.0, tk.END).strip()
        if not content:
            return []
        
        # Разбиваем по строкам и очищаем
        item_ids = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):  # Игнорируем пустые строки и комментарии
                item_ids.append(line)
        
        return item_ids
    
    def update_preview(self):
        """Обновление предварительного просмотра"""
        # Очищаем таблицу
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        
        # Получаем данные
        item_ids = self.get_item_ids_list()
        parameter = self.parameter_var.get()
        new_value = self.value_var.get()
        
        if not item_ids or not parameter or not new_value:
            self.preview_info_label.config(text="Заполните все поля для предварительного просмотра")
            return
        
        # Обновляем информацию
        self.preview_info_label.config(text=f"Будет изменено {len(item_ids)} предметов. Параметр: {parameter} = {new_value}")
        
        # Валидируем значение
        is_valid, message = self.analyzer.validate_parameter_value(parameter, new_value)
        if not is_valid:
            self.preview_info_label.config(text=f"Ошибка валидации: {message}")
            return
        
        # Заполняем таблицу предварительного просмотра
        valid_count = 0
        invalid_count = 0
        
        for item_id in item_ids[:50]:  # Показываем только первые 50 для производительности
            item = self.items_db.get_item(item_id)
            if not item:
                self.preview_tree.insert('', 'end', values=(
                    item_id, "Не найден", "N/A", new_value, "❌ Не найден"
                ))
                invalid_count += 1
                continue
            
            # Получаем текущее значение
            current_value = self.get_current_parameter_value(item, parameter)
            
            # Определяем статус
            if current_value is not None:
                status = "✅ Изменится"
                valid_count += 1
            else:
                status = "⚠️ Параметр отсутствует"
                invalid_count += 1
            
            # Получаем название предмета
            item_name = self.items_db.get_item_name(item_id)
            if len(item_name) > 30:
                item_name = item_name[:30] + "..."
            
            self.preview_tree.insert('', 'end', values=(
                item_id, item_name, str(current_value) if current_value is not None else "N/A", 
                new_value, status
            ))
        
        if len(item_ids) > 50:
            self.preview_tree.insert('', 'end', values=(
                "...", f"И еще {len(item_ids) - 50} предметов", "...", "...", "..."
            ))
        
        # Обновляем информацию
        self.preview_info_label.config(text=f"Предварительный просмотр: {valid_count} изменений, {invalid_count} проблем")
    
    def get_current_parameter_value(self, item: Dict[str, Any], parameter: str) -> Any:
        """Получение текущего значения параметра из предмета"""
        try:
            if parameter.startswith('_props.'):
                prop_name = parameter.replace('_props.', '')
                return item.get('_props', {}).get(prop_name)
            elif parameter.startswith('locale.'):
                locale_name = parameter.replace('locale.', '')
                return item.get('locale', {}).get(locale_name)
            else:
                return item.get(parameter)
        except:
            return None
    
    def start_bulk_processing(self):
        """Запуск массового изменения параметров"""
        # Валидация входных данных
        item_ids = self.get_item_ids_list()
        parameter = self.parameter_var.get()
        new_value = self.value_var.get()
        
        if not item_ids:
            messagebox.showwarning("Предупреждение", "Введите ID предметов")
            return
        
        if not parameter:
            messagebox.showwarning("Предупреждение", "Выберите параметр для изменения")
            return
        
        if not new_value:
            messagebox.showwarning("Предупреждение", "Введите новое значение параметра")
            return
        
        # Валидация значения
        is_valid, message = self.analyzer.validate_parameter_value(parameter, new_value)
        if not is_valid:
            messagebox.showerror("Ошибка", f"Неверное значение параметра: {message}")
            return
        
        # Подтверждение
        result = messagebox.askyesno(
            "Подтверждение", 
            f"Вы уверены, что хотите изменить параметр '{parameter}' на значение '{new_value}' для {len(item_ids)} предметов?\n\n"
            "Будет создана резервная копия базы данных."
        )
        
        if not result:
            return
        
        # Запуск обработки в отдельном потоке
        self.is_processing = True
        self.start_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        
        self.processing_thread = threading.Thread(
            target=self._bulk_processing_worker,
            args=(item_ids, parameter, new_value),
            daemon=True
        )
        self.processing_thread.start()
    
    def _bulk_processing_worker(self, item_ids: List[str], parameter: str, new_value: str):
        """Рабочий поток массового изменения"""
        try:
            self.dialog.after(0, lambda: self.status_var.set("Подготовка к изменению..."))
            self.dialog.after(0, lambda: self.progress_var.set(0))
            
            # Создание резервной копии
            self.dialog.after(0, lambda: self.status_var.set("Создание резервной копии..."))
            backup_success = self.create_backup()
            if not backup_success:
                self.dialog.after(0, lambda: self.status_var.set("Ошибка создания резервной копии"))
                return
            
            # Обработка предметов
            total_items = len(item_ids)
            processed = 0
            successful = 0
            failed = 0
            
            self.log_message(f"Начало массового изменения параметра '{parameter}' на значение '{new_value}'")
            self.log_message(f"Обрабатывается {total_items} предметов")
            
            for i, item_id in enumerate(item_ids):
                if not self.is_processing:  # Проверка на отмену
                    break
                
                try:
                    # Получаем предмет
                    item = self.items_db.get_item(item_id)
                    if not item:
                        self.log_message(f"❌ Предмет {item_id} не найден")
                        failed += 1
                        continue
                    
                    # Получаем текущее значение
                    current_value = self.get_current_parameter_value(item, parameter)
                    
                    # Логируем изменение
                    self.log_message(f"📝 {item_id}: {current_value} → {new_value}")
                    
                    # Применяем изменение
                    success = self.apply_parameter_change(item, parameter, new_value)
                    
                    if success:
                        # Сохраняем предмет
                        save_success = self.items_db.save_item_incremental(item_id, {parameter: new_value})
                        if save_success:
                            successful += 1
                            self.log_message(f"✅ {item_id} успешно изменен")
                        else:
                            failed += 1
                            self.log_message(f"❌ Ошибка сохранения {item_id}")
                    else:
                        failed += 1
                        self.log_message(f"❌ Ошибка изменения {item_id}")
                    
                    processed += 1
                    
                    # Обновляем прогресс
                    progress = (processed / total_items) * 100
                    self.dialog.after(0, lambda p=progress: self.progress_var.set(p))
                    self.dialog.after(0, lambda: self.status_var.set(f"Обработано: {processed}/{total_items}"))
                    
                except Exception as e:
                    failed += 1
                    self.log_message(f"❌ Ошибка обработки {item_id}: {str(e)}")
                    processed += 1
            
            # Завершение
            if self.is_processing:
                self.log_message(f"✅ Массовое изменение завершено!")
                self.log_message(f"📊 Результат: {successful} успешно, {failed} ошибок из {processed} обработано")
                
                self.dialog.after(0, lambda: self.status_var.set(f"Завершено: {successful} успешно, {failed} ошибок"))
                self.dialog.after(0, lambda: self.progress_var.set(100))
                
                # Показываем результат
                self.dialog.after(0, lambda: messagebox.showinfo(
                    "Завершено", 
                    f"Массовое изменение завершено!\n\n"
                    f"Успешно изменено: {successful}\n"
                    f"Ошибок: {failed}\n"
                    f"Всего обработано: {processed}"
                ))
            else:
                self.log_message("❌ Массовое изменение отменено пользователем")
                self.dialog.after(0, lambda: self.status_var.set("Отменено"))
            
        except Exception as e:
            self.log_message(f"❌ Критическая ошибка: {str(e)}")
            self.dialog.after(0, lambda: self.status_var.set(f"Ошибка: {str(e)}"))
        
        finally:
            self.is_processing = False
            self.dialog.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            self.dialog.after(0, lambda: self.cancel_button.config(state=tk.DISABLED))
    
    def apply_parameter_change(self, item: Dict[str, Any], parameter: str, new_value: str) -> bool:
        """Применение изменения параметра к предмету"""
        try:
            # Преобразуем значение в нужный тип
            param_type = self.analyzer.get_parameter_type(parameter)
            converted_value = self.convert_parameter_value(new_value, param_type)
            
            # Применяем изменение
            if parameter.startswith('_props.'):
                prop_name = parameter.replace('_props.', '')
                if '_props' not in item:
                    item['_props'] = {}
                item['_props'][prop_name] = converted_value
            elif parameter.startswith('locale.'):
                locale_name = parameter.replace('locale.', '')
                if 'locale' not in item:
                    item['locale'] = {}
                item['locale'][locale_name] = converted_value
            else:
                item[parameter] = converted_value
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ Ошибка применения изменения: {str(e)}")
            return False
    
    def convert_parameter_value(self, value: str, param_type: str) -> Any:
        """Преобразование строкового значения в нужный тип"""
        if param_type == 'int':
            return int(value)
        elif param_type == 'float':
            return float(value)
        elif param_type == 'bool':
            return value.lower() in ['true', '1', 'yes']
        elif param_type == 'str':
            return value
        else:
            # Для смешанных типов пробуем разные варианты
            try:
                return int(value)
            except ValueError:
                try:
                    return float(value)
                except ValueError:
                    if value.lower() in ['true', 'false', '1', '0', 'yes', 'no']:
                        return value.lower() in ['true', '1', 'yes']
                    return value
    
    def create_backup(self) -> bool:
        """Создание резервной копии базы данных"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.items_db.items_file.with_suffix(f'.backup_{timestamp}.json.bak')
            
            # Копируем файл
            import shutil
            shutil.copy2(self.items_db.items_file, backup_file)
            
            self.log_message(f"📁 Создана резервная копия: {backup_file.name}")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Ошибка создания резервной копии: {str(e)}")
            return False
    
    def log_message(self, message: str):
        """Добавление сообщения в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        def update_log():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        
        self.dialog.after(0, update_log)
    
    def clear_log(self):
        """Очистка лога"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def save_log(self):
        """Сохранение лога в файл"""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            title="Сохранить лог операций",
            defaultextension=".log",
            filetypes=[("Лог файлы", "*.log"), ("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        
        if file_path:
            try:
                content = self.log_text.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log_message(f"📄 Лог сохранен: {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка сохранения лога: {str(e)}")
    
    def export_log(self):
        """Экспорт лога в файл"""
        self.save_log()
    
    def on_closing(self):
        """Обработка закрытия диалога"""
        try:
            info("Начало закрытия диалога массового изменения", LogCategory.UI)
            
            if self.is_processing:
                debug("Диалог закрывается во время обработки", LogCategory.UI)
                result = messagebox.askyesno("Подтверждение", 
                                           "Идет обработка данных. Вы уверены, что хотите закрыть?")
                if result:
                    self.is_processing = False
                    if self.processing_thread and self.processing_thread.is_alive():
                        debug("Ожидание завершения потока обработки", LogCategory.UI)
                        self.processing_thread.join(timeout=1)
                    try:
                        self.dialog.destroy()
                        debug("Диалог уничтожен", LogCategory.UI)
                    except Exception as e:
                        error(f"Ошибка уничтожения диалога: {e}", LogCategory.ERROR, exception=e)
            else:
                try:
                    self.dialog.destroy()
                    debug("Диалог уничтожен", LogCategory.UI)
                except Exception as e:
                    error(f"Ошибка уничтожения диалога: {e}", LogCategory.ERROR, exception=e)
            
            if self.on_complete:
                try:
                    debug("Вызов callback функции", LogCategory.UI)
                    self.on_complete()
                except Exception as e:
                    error(f"Ошибка вызова callback функции: {e}", LogCategory.ERROR, exception=e)
            
            info("Диалог массового изменения закрыт успешно", LogCategory.UI)
            
        except Exception as e:
            critical(f"Критическая ошибка при закрытии диалога: {e}", LogCategory.ERROR, exception=e)
            # Принудительно уничтожаем диалог
            try:
                self.dialog.destroy()
            except:
                pass

def main():
    """Главная функция для тестирования модуля"""
    root = tk.Tk()
    root.withdraw()
    
    server_path = Path(__file__).parent.parent
    dialog = BulkParametersDialog(root, server_path)
    
    root.mainloop()

if __name__ == "__main__":
    main()
