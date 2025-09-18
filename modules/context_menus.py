#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Context Menus - Универсальные контекстные меню для полей ввода
"""

import tkinter as tk
from tkinter import ttk

class ContextMenuManager:
    """Менеджер контекстных меню для полей ввода"""
    
    @staticmethod
    def bind_context_menu(widget):
        """Привязывает контекстное меню к виджету"""
        if isinstance(widget, (tk.Entry, tk.Text, ttk.Entry)):
            widget.bind("<Button-3>", lambda e: ContextMenuManager.show_context_menu(e, widget))
            widget.bind("<Control-a>", lambda e: ContextMenuManager.select_all(widget))
            widget.bind("<Control-c>", lambda e: ContextMenuManager.copy_text(widget))
            widget.bind("<Control-v>", lambda e: ContextMenuManager.paste_text(widget))
            widget.bind("<Control-x>", lambda e: ContextMenuManager.cut_text(widget))
            # Поддержка русской раскладки
            widget.bind("<Control-KeyPress>", lambda e: ContextMenuManager.on_control_key(e, widget))
    
    @staticmethod
    def on_control_key(event, widget):
        """Обработка Ctrl+клавиша для поддержки русской раскладки"""
        try:
            # Проверяем keycode для определения клавиши
            if event.keycode == 65:  # A или ф
                ContextMenuManager.select_all(widget)
            elif event.keycode == 67:  # C или с
                ContextMenuManager.copy_text(widget)
            elif event.keycode == 86:  # V или м
                ContextMenuManager.paste_text(widget)
            elif event.keycode == 88:  # X или ч
                ContextMenuManager.cut_text(widget)
        except Exception as e:
            print(f"Ошибка обработки клавиши: {e}")
        return "break"
    
    @staticmethod
    def show_context_menu(event, widget):
        """Показывает контекстное меню"""
        try:
            # Создаем контекстное меню
            context_menu = tk.Menu(widget, tearoff=0)
            
            # Добавляем пункты меню
            context_menu.add_command(label="Вырезать (Ctrl+X)", 
                                   command=lambda: ContextMenuManager.cut_text(widget))
            context_menu.add_command(label="Копировать (Ctrl+C)", 
                                   command=lambda: ContextMenuManager.copy_text(widget))
            context_menu.add_command(label="Вставить (Ctrl+V)", 
                                   command=lambda: ContextMenuManager.paste_text(widget))
            context_menu.add_separator()
            context_menu.add_command(label="Выделить все (Ctrl+A)", 
                                   command=lambda: ContextMenuManager.select_all(widget))
            context_menu.add_command(label="Очистить", 
                                   command=lambda: ContextMenuManager.clear_text(widget))
            
            # Показываем меню
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        except Exception as e:
            print(f"Ошибка создания контекстного меню: {e}")
    
    @staticmethod
    def cut_text(widget):
        """Вырезает выделенный текст"""
        try:
            if isinstance(widget, tk.Text):
                widget.event_generate("<<Cut>>")
            else:
                # Для Entry виджетов
                if widget.selection_present():
                    selected_text = widget.selection_get()
                    widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                    widget.clipboard_clear()
                    widget.clipboard_append(selected_text)
        except Exception as e:
            print(f"Ошибка вырезания текста: {e}")
    
    @staticmethod
    def copy_text(widget):
        """Копирует выделенный текст"""
        try:
            if isinstance(widget, tk.Text):
                widget.event_generate("<<Copy>>")
            else:
                # Для Entry виджетов
                if widget.selection_present():
                    selected_text = widget.selection_get()
                    widget.clipboard_clear()
                    widget.clipboard_append(selected_text)
        except Exception as e:
            print(f"Ошибка копирования текста: {e}")
    
    @staticmethod
    def paste_text(widget):
        """Вставляет текст из буфера обмена"""
        try:
            if isinstance(widget, tk.Text):
                widget.event_generate("<<Paste>>")
            else:
                # Для Entry виджетов
                clipboard_text = widget.clipboard_get()
                if widget.selection_present():
                    widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                widget.insert(tk.INSERT, clipboard_text)
        except Exception as e:
            print(f"Ошибка вставки текста: {e}")
    
    @staticmethod
    def select_all(widget):
        """Выделяет весь текст"""
        try:
            if isinstance(widget, tk.Text):
                widget.tag_add(tk.SEL, "1.0", tk.END)
                widget.mark_set(tk.INSERT, "1.0")
                widget.see(tk.INSERT)
            else:
                # Для Entry виджетов
                widget.select_range(0, tk.END)
                widget.icursor(tk.END)
        except Exception as e:
            print(f"Ошибка выделения текста: {e}")
    
    @staticmethod
    def clear_text(widget):
        """Очищает текст в виджете"""
        try:
            if isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
            else:
                widget.delete(0, tk.END)
        except Exception as e:
            print(f"Ошибка очистки текста: {e}")

def bind_context_menus_to_widget(parent_widget):
    """Рекурсивно привязывает контекстные меню ко всем полям ввода в виджете"""
    try:
        # Привязываем к самому виджету, если это поле ввода
        ContextMenuManager.bind_context_menu(parent_widget)
        
        # Рекурсивно обрабатываем дочерние виджеты
        for child in parent_widget.winfo_children():
            bind_context_menus_to_widget(child)
    except Exception as e:
        print(f"Ошибка привязки контекстного меню: {e}")

def setup_context_menus_for_module(module_instance):
    """Настраивает контекстные меню для всего модуля"""
    try:
        # Определяем главное окно модуля
        main_window = None
        if hasattr(module_instance, 'window'):
            main_window = module_instance.window
        elif hasattr(module_instance, 'parent'):
            main_window = module_instance.parent
        elif hasattr(module_instance, 'root'):
            main_window = module_instance.root
        
        if main_window:
            # Привязываем контекстные меню ко всем полям ввода в окне модуля
            bind_context_menus_to_widget(main_window)
        else:
            print("Не удалось найти главное окно модуля для настройки контекстных меню")
    except Exception as e:
        print(f"Ошибка настройки контекстных меню: {e}")
