#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dynamic UI - Модуль для динамического создания UI элементов
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path
from typing import Dict, Any, Optional, Callable

class DynamicUIBuilder:
    """Строитель динамического UI на основе конфигурации"""
    
    def __init__(self, parent_frame, config: Dict[str, Any], data: Dict[str, Any] = None):
        self.parent_frame = parent_frame
        self.config = config
        self.data = data or {}
        self.widgets = {}
        self.variables = {}
        
    def create_ui(self):
        """Создание UI на основе конфигурации"""
        # Очищаем существующие виджеты
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        self.widgets.clear()
        self.variables.clear()
        
        # Создаем виджеты для каждого параметра
        for param_name, param_config in self.config.items():
            if self.should_show_parameter(param_name, param_config):
                self.create_parameter_widget(param_name, param_config)
    
    def should_show_parameter(self, param_name: str, param_config: Dict[str, Any]) -> bool:
        """Определяет, нужно ли показывать параметр"""
        # Если параметр помечен как readonly и не существует в данных, не показываем
        if param_config.get('readonly', False) and param_name not in self.data:
            return False
        
        # Если параметр существует в данных, показываем
        if param_name in self.data:
            return True
        
        # Если параметр обязательный, показываем
        if param_config.get('required', False):
            return True
        
        # По умолчанию не показываем
        return False
    
    def create_parameter_widget(self, param_name: str, param_config: Dict[str, Any]):
        """Создание виджета для параметра"""
        param_type = param_config.get('type', 'string')
        label_text = param_config.get('label', param_name)
        description = param_config.get('description', '')
        readonly = param_config.get('readonly', False)
        
        # Создаем фрейм для параметра
        param_frame = ttk.Frame(self.parent_frame)
        param_frame.pack(fill=tk.X, pady=2)
        
        # Метка
        label = ttk.Label(param_frame, text=f"{label_text}:")
        label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Получаем значение
        value = self.data.get(param_name, self.get_default_value(param_config))
        
        # Создаем виджет в зависимости от типа
        if param_type == 'string':
            widget = self.create_string_widget(param_frame, param_name, value, readonly)
        elif param_type == 'text':
            widget = self.create_text_widget(param_frame, param_name, value, readonly)
        elif param_type == 'integer':
            widget = self.create_integer_widget(param_frame, param_name, value, param_config, readonly)
        elif param_type == 'float':
            widget = self.create_float_widget(param_frame, param_name, value, param_config, readonly)
        elif param_type == 'boolean':
            widget = self.create_boolean_widget(param_frame, param_name, value, readonly)
        elif param_type == 'enum':
            widget = self.create_enum_widget(param_frame, param_name, value, param_config, readonly)
        elif param_type == 'object':
            widget = self.create_object_widget(param_frame, param_name, value, readonly)
        elif param_type == 'array':
            widget = self.create_array_widget(param_frame, param_name, value, readonly)
        else:
            widget = self.create_string_widget(param_frame, param_name, value, readonly)
        
        # Сохраняем виджет
        self.widgets[param_name] = widget
        
        # Добавляем описание если есть
        if description:
            desc_label = ttk.Label(param_frame, text=f"({description})", font=('Arial', 8), foreground='gray')
            desc_label.pack(side=tk.LEFT, padx=(10, 0))
    
    def create_string_widget(self, parent, param_name: str, value: Any, readonly: bool) -> ttk.Entry:
        """Создание виджета для строки"""
        var = tk.StringVar(value=str(value) if value is not None else '')
        self.variables[param_name] = var
        
        widget = ttk.Entry(parent, textvariable=var, width=30)
        widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        if readonly:
            # Вместо readonly делаем поле неактивным, но редактируемым
            widget.config(state='disabled')
            # Добавляем обработчик для включения редактирования при клике
            widget.bind('<Button-1>', lambda e: widget.config(state='normal'))
            widget.bind('<FocusOut>', lambda e: widget.config(state='disabled') if readonly else None)
        
        return widget
    
    def create_text_widget(self, parent, param_name: str, value: Any, readonly: bool) -> tk.Text:
        """Создание виджета для текста"""
        widget = tk.Text(parent, height=3, width=50)
        widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        if value is not None:
            widget.insert(1.0, str(value))
        
        if readonly:
            # Вместо disabled делаем поле неактивным, но редактируемым
            widget.config(state='disabled')
            # Добавляем обработчик для включения редактирования при клике
            widget.bind('<Button-1>', lambda e: widget.config(state='normal'))
            widget.bind('<FocusOut>', lambda e: widget.config(state='disabled') if readonly else None)
        
        return widget
    
    def create_integer_widget(self, parent, param_name: str, value: Any, config: Dict[str, Any], readonly: bool) -> ttk.Spinbox:
        """Создание виджета для целого числа"""
        min_val = config.get('min', 0)
        max_val = config.get('max', 999999)
        
        var = tk.IntVar(value=int(value) if value is not None else min_val)
        self.variables[param_name] = var
        
        widget = ttk.Spinbox(parent, from_=min_val, to=max_val, textvariable=var, width=15)
        widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        if readonly:
            # Вместо readonly делаем поле неактивным, но редактируемым
            widget.config(state='disabled')
            # Добавляем обработчик для включения редактирования при клике
            widget.bind('<Button-1>', lambda e: widget.config(state='normal'))
            widget.bind('<FocusOut>', lambda e: widget.config(state='disabled') if readonly else None)
        
        return widget
    
    def create_float_widget(self, parent, param_name: str, value: Any, config: Dict[str, Any], readonly: bool) -> ttk.Entry:
        """Создание виджета для числа с плавающей точкой"""
        var = tk.DoubleVar(value=float(value) if value is not None else 0.0)
        self.variables[param_name] = var
        
        widget = ttk.Entry(parent, textvariable=var, width=15)
        widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        if readonly:
            # Вместо readonly делаем поле неактивным, но редактируемым
            widget.config(state='disabled')
            # Добавляем обработчик для включения редактирования при клике
            widget.bind('<Button-1>', lambda e: widget.config(state='normal'))
            widget.bind('<FocusOut>', lambda e: widget.config(state='disabled') if readonly else None)
        
        return widget
    
    def create_boolean_widget(self, parent, param_name: str, value: Any, readonly: bool) -> ttk.Checkbutton:
        """Создание виджета для булева значения"""
        var = tk.BooleanVar(value=bool(value) if value is not None else False)
        self.variables[param_name] = var
        
        widget = ttk.Checkbutton(parent, variable=var)
        widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        if readonly:
            # Вместо disabled делаем поле неактивным, но редактируемым
            widget.config(state='disabled')
            # Добавляем обработчик для включения редактирования при клике
            widget.bind('<Button-1>', lambda e: widget.config(state='normal'))
            widget.bind('<FocusOut>', lambda e: widget.config(state='disabled') if readonly else None)
        
        return widget
    
    def create_enum_widget(self, parent, param_name: str, value: Any, config: Dict[str, Any], readonly: bool) -> ttk.Combobox:
        """Создание виджета для перечисления"""
        options = config.get('options', [])
        
        var = tk.StringVar(value=str(value) if value is not None else '')
        self.variables[param_name] = var
        
        widget = ttk.Combobox(parent, textvariable=var, values=options, width=20)
        widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        if readonly:
            # Вместо readonly делаем поле неактивным, но редактируемым
            widget.config(state='disabled')
            # Добавляем обработчик для включения редактирования при клике
            widget.bind('<Button-1>', lambda e: widget.config(state='normal'))
            widget.bind('<FocusOut>', lambda e: widget.config(state='disabled') if readonly else None)
        
        return widget
    
    def create_object_widget(self, parent, param_name: str, value: Any, readonly: bool) -> ttk.Frame:
        """Создание виджета для объекта"""
        frame = ttk.Frame(parent)
        frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Кнопка для редактирования объекта
        button_text = "Редактировать объект"
        if value is None:
            button_text = "Создать объект"
        
        button = ttk.Button(frame, text=button_text, 
                          command=lambda: self.edit_object(param_name, value))
        button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Информация об объекте
        if value is not None:
            info_text = f"<{type(value).__name__}> ({len(value)} ключей)" if isinstance(value, dict) else str(value)
            info_label = ttk.Label(frame, text=info_text, foreground='gray')
            info_label.pack(side=tk.LEFT, padx=(5, 0))
        
        return frame
    
    def create_array_widget(self, parent, param_name: str, value: Any, readonly: bool) -> ttk.Frame:
        """Создание виджета для массива"""
        frame = ttk.Frame(parent)
        frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Кнопка для редактирования массива
        button_text = "Редактировать массив"
        if value is None:
            button_text = "Создать массив"
        
        button = ttk.Button(frame, text=button_text,
                          command=lambda: self.edit_array(param_name, value))
        button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Информация о массиве
        if value is not None:
            info_text = f"<{type(value).__name__}> ({len(value)} элементов)" if isinstance(value, list) else str(value)
            info_label = ttk.Label(frame, text=info_text, foreground='gray')
            info_label.pack(side=tk.LEFT, padx=(5, 0))
        
        return frame
    
    def edit_object(self, param_name: str, value: Any):
        """Редактирование объекта"""
        try:
            from modules.json_editor import JSONEditor
            
            def on_save(new_data):
                self.data[param_name] = new_data
                # Обновляем UI
                self.create_ui()
            
            editor = JSONEditor(self.parent_frame.winfo_toplevel(), 
                              f"Редактирование {param_name}", 
                              value, on_save)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при открытии редактора: {str(e)}")
    
    def edit_array(self, param_name: str, value: Any):
        """Редактирование массива"""
        try:
            from modules.json_editor import JSONEditor
            
            def on_save(new_data):
                self.data[param_name] = new_data
                # Обновляем UI
                self.create_ui()
            
            editor = JSONEditor(self.parent_frame.winfo_toplevel(), 
                              f"Редактирование {param_name}", 
                              value, on_save)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при открытии редактора: {str(e)}")
    
    def get_default_value(self, config: Dict[str, Any]) -> Any:
        """Получение значения по умолчанию"""
        param_type = config.get('type', 'string')
        
        if param_type == 'string':
            return ''
        elif param_type == 'text':
            return ''
        elif param_type == 'integer':
            return config.get('min', 0)
        elif param_type == 'float':
            return 0.0
        elif param_type == 'boolean':
            return False
        elif param_type == 'enum':
            options = config.get('options', [])
            return options[0] if options else ''
        elif param_type == 'object':
            return {}
        elif param_type == 'array':
            return []
        else:
            return ''
    
    def get_values(self) -> Dict[str, Any]:
        """Получение всех значений из виджетов"""
        values = {}
        
        for param_name, widget in self.widgets.items():
            if param_name in self.variables:
                # Простые типы с переменными
                values[param_name] = self.variables[param_name].get()
            elif isinstance(widget, tk.Text):
                # Текстовые поля
                values[param_name] = widget.get(1.0, tk.END).strip()
            elif isinstance(widget, ttk.Frame):
                # Объекты и массивы - берем из данных
                values[param_name] = self.data.get(param_name, {})
        
        return values
    
    def set_values(self, data: Dict[str, Any]):
        """Установка значений в виджеты"""
        self.data = data
        self.create_ui()

def load_parameters_config(config_path: Path) -> Dict[str, Any]:
    """Загрузка конфигурации параметров"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки конфигурации: {e}")
        return {}

def main():
    """Тестовая функция"""
    root = tk.Tk()
    root.title("Dynamic UI Test")
    root.geometry("600x400")
    
    # Загружаем конфигурацию
    config_path = Path(__file__).parent / "parameters_config.json"
    config = load_parameters_config(config_path)
    
    # Тестовые данные
    test_data = {
        "_id": "test_item_001",
        "_name": "Test Item",
        "_type": "Item",
        "Weight": 1.5,
        "Width": 2,
        "Height": 3,
        "QuestItem": True,
        "CanSellOnRagfair": False
    }
    
    # Создаем UI
    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    builder = DynamicUIBuilder(frame, config.get('basic_parameters', {}), test_data)
    builder.create_ui()
    
    # Кнопка для получения значений
    def get_values():
        values = builder.get_values()
        print("Values:", values)
        messagebox.showinfo("Values", str(values))
    
    ttk.Button(root, text="Get Values", command=get_values).pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    main()
