#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON Editor - Редактор JSON с подсветкой синтаксиса
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import orjson
from pathlib import Path
from typing import Any, Optional, Callable

class JSONEditor:
    """Редактор JSON с подсветкой синтаксиса"""
    
    def __init__(self, parent, title: str = "JSON Editor", data: Any = None, 
                 on_save: Optional[Callable] = None, readonly: bool = False):
        self.parent = parent
        self.title = title
        self.data = data
        self.on_save = on_save
        self.readonly = readonly
        
        # Создание диалога
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("800x600")
        self.dialog.minsize(600, 400)
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Переменные
        self.original_data = data
        self.is_modified = False
        
        # Создание интерфейса
        self.create_widgets()
        
        # Загрузка данных
        if data is not None:
            self.load_data(data)
        
        # Обработка закрытия
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Создание интерфейса"""
        # Главный фрейм
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Панель инструментов
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # Кнопки
        ttk.Button(toolbar, text="💾 Сохранить", command=self.save_data).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="🔄 Обновить", command=self.refresh_data).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="🎨 Форматировать", command=self.format_json).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="🔍 Поиск", command=self.search_text).pack(side=tk.LEFT, padx=(0, 5))
        
        # Статус
        self.status_var = tk.StringVar(value="Готов")
        status_label = ttk.Label(toolbar, textvariable=self.status_var)
        status_label.pack(side=tk.RIGHT)
        
        # Текстовое поле с прокруткой (тема VS Code)
        self.text_widget = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.NONE,
            font=('Consolas', 10),
            bg='#ffffff',
            fg='#000000',
            insertbackground='#000000',
            selectbackground='#0078d4',
            selectforeground='#ffffff',
            undo=True,
            maxundo=50
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Привязка событий
        self.text_widget.bind('<KeyRelease>', self.on_text_change)
        self.text_widget.bind('<Control-s>', lambda e: self.save_data())
        self.text_widget.bind('<Control-f>', lambda e: self.search_text())
        self.text_widget.bind('<Control-z>', lambda e: self.text_widget.edit_undo())
        self.text_widget.bind('<Control-y>', lambda e: self.text_widget.edit_redo())
        
        # Настройка для readonly
        if self.readonly:
            self.text_widget.config(state=tk.DISABLED)
    
    def load_data(self, data: Any):
        """Загрузка данных в редактор"""
        try:
            # Конвертируем в JSON строку
            if isinstance(data, (dict, list)):
                json_str = orjson.dumps(data, option=orjson.OPT_INDENT_2).decode('utf-8')
            else:
                json_str = str(data)
            
            # Очищаем и вставляем текст
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(1.0, json_str)
            
            # Применяем подсветку синтаксиса
            self.apply_syntax_highlighting()
            
            self.is_modified = False
            self.update_status("Данные загружены")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке данных: {str(e)}")
    
    def apply_syntax_highlighting(self):
        """Применение подсветки синтаксиса JSON"""
        try:
            # Получаем весь текст
            content = self.text_widget.get(1.0, tk.END)
            
            # Очищаем все теги
            self.text_widget.tag_remove("json_key", 1.0, tk.END)
            self.text_widget.tag_remove("json_string", 1.0, tk.END)
            self.text_widget.tag_remove("json_number", 1.0, tk.END)
            self.text_widget.tag_remove("json_boolean", 1.0, tk.END)
            self.text_widget.tag_remove("json_null", 1.0, tk.END)
            self.text_widget.tag_remove("json_punctuation", 1.0, tk.END)
            
            # Настройка тегов (темная тема)
            self.text_widget.tag_configure("json_key", foreground="#0000ff", font=('Consolas', 10, 'bold'))
            self.text_widget.tag_configure("json_string", foreground="#008000", font=('Consolas', 10))
            self.text_widget.tag_configure("json_number", foreground="#ff6600", font=('Consolas', 10))
            self.text_widget.tag_configure("json_boolean", foreground="#800080", font=('Consolas', 10, 'bold'))
            self.text_widget.tag_configure("json_null", foreground="#808080", font=('Consolas', 10, 'italic'))
            self.text_widget.tag_configure("json_punctuation", foreground="#000000", font=('Consolas', 10, 'bold'))
            
            # Простая подсветка синтаксиса
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                self.highlight_line(line, line_num)
                
        except Exception as e:
            print(f"Ошибка подсветки синтаксиса: {e}")
    
    def highlight_line(self, line: str, line_num: int):
        """Подсветка одной строки"""
        try:
            # Находим ключи (строки в кавычках, за которыми следует двоеточие)
            import re
            
            # Ключи
            key_pattern = r'"([^"]+)"\s*:'
            for match in re.finditer(key_pattern, line):
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()}"
                self.text_widget.tag_add("json_key", start, end)
            
            # Строки
            string_pattern = r'"[^"]*"'
            for match in re.finditer(string_pattern, line):
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()}"
                # Проверяем, что это не ключ
                if not line[match.end():match.end()+1].strip().startswith(':'):
                    self.text_widget.tag_add("json_string", start, end)
            
            # Числа
            number_pattern = r'\b\d+\.?\d*\b'
            for match in re.finditer(number_pattern, line):
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()}"
                self.text_widget.tag_add("json_number", start, end)
            
            # Булевы значения
            boolean_pattern = r'\b(true|false)\b'
            for match in re.finditer(boolean_pattern, line, re.IGNORECASE):
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()}"
                self.text_widget.tag_add("json_boolean", start, end)
            
            # null
            null_pattern = r'\bnull\b'
            for match in re.finditer(null_pattern, line, re.IGNORECASE):
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()}"
                self.text_widget.tag_add("json_null", start, end)
            
            # Пунктуация
            punct_pattern = r'[{}[\](),:]'
            for match in re.finditer(punct_pattern, line):
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()}"
                self.text_widget.tag_add("json_punctuation", start, end)
                
        except Exception as e:
            print(f"Ошибка подсветки строки {line_num}: {e}")
    
    def on_text_change(self, event=None):
        """Обработка изменения текста"""
        self.is_modified = True
        self.update_status("Изменено")
        
        # Применяем подсветку синтаксиса
        self.dialog.after(100, self.apply_syntax_highlighting)
    
    def save_data(self):
        """Сохранение данных"""
        try:
            # Получаем текст
            content = self.text_widget.get(1.0, tk.END).strip()
            
            # Парсим JSON
            try:
                parsed_data = orjson.loads(content)
            except json.JSONDecodeError as e:
                messagebox.showerror("Ошибка JSON", f"Неверный формат JSON:\n{str(e)}")
                return
            
            # Вызываем callback для сохранения
            if self.on_save:
                self.on_save(parsed_data)
            
            self.is_modified = False
            self.update_status("Сохранено")
            messagebox.showinfo("Успех", "Данные сохранены успешно")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")
    
    def refresh_data(self):
        """Обновление данных"""
        if self.original_data is not None:
            self.load_data(self.original_data)
            self.update_status("Обновлено")
    
    def format_json(self):
        """Форматирование JSON"""
        try:
            # Получаем текст
            content = self.text_widget.get(1.0, tk.END).strip()
            
            # Парсим и форматируем
            parsed_data = orjson.loads(content)
            formatted = orjson.dumps(parsed_data, option=orjson.OPT_INDENT_2).decode('utf-8')
            
            # Заменяем текст
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(1.0, formatted)
            
            # Применяем подсветку
            self.apply_syntax_highlighting()
            
            self.update_status("Отформатировано")
            
        except json.JSONDecodeError as e:
            messagebox.showerror("Ошибка JSON", f"Неверный формат JSON:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при форматировании: {str(e)}")
    
    def search_text(self):
        """Поиск текста"""
        search_dialog = tk.simpledialog.askstring("Поиск", "Введите текст для поиска:")
        if search_dialog:
            # Очищаем предыдущие выделения
            self.text_widget.tag_remove("search", 1.0, tk.END)
            
            # Ищем текст
            start = 1.0
            while True:
                pos = self.text_widget.search(search_dialog, start, tk.END)
                if not pos:
                    break
                
                end = f"{pos}+{len(search_dialog)}c"
                self.text_widget.tag_add("search", pos, end)
                start = end
            
            # Настраиваем тег поиска
            self.text_widget.tag_configure("search", background="yellow", foreground="black")
            
            # Переходим к первому найденному
            first_match = self.text_widget.search(search_dialog, 1.0, tk.END)
            if first_match:
                self.text_widget.see(first_match)
                self.text_widget.mark_set(tk.INSERT, first_match)
    
    def update_status(self, message: str):
        """Обновление статуса"""
        self.status_var.set(message)
    
    def on_closing(self):
        """Обработка закрытия"""
        if self.is_modified:
            result = messagebox.askyesnocancel(
                "Несохраненные изменения",
                "У вас есть несохраненные изменения. Сохранить?"
            )
            if result is True:
                self.save_data()
            elif result is None:
                return  # Отмена закрытия
        
        self.dialog.destroy()

def main():
    """Тестовая функция"""
    root = tk.Tk()
    root.withdraw()
    
    # Тестовые данные
    test_data = {
        "name": "Test Item",
        "id": "test_item_001",
        "properties": {
            "weight": 1.5,
            "size": [2, 3],
            "enabled": True,
            "tags": ["weapon", "rifle"]
        },
        "stats": {
            "damage": 45,
            "accuracy": 0.85,
            "range": 300
        }
    }
    
    editor = JSONEditor(root, "Test JSON Editor", test_data)
    root.mainloop()

if __name__ == "__main__":
    main()
