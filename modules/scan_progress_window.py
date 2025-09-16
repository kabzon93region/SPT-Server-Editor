#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scan Progress Window - Окно прогресса сканирования
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from pathlib import Path
from typing import Callable, Optional
from scan_db import DatabaseScanner

class ScanProgressWindow:
    def __init__(self, parent, server_path: Path, on_complete: Optional[Callable] = None):
        self.parent = parent
        self.server_path = server_path
        self.on_complete = on_complete
        
        # Создание модального окна
        self.window = tk.Toplevel(parent)
        self.window.title("Сканирование базы данных")
        self.window.geometry("500x300")
        self.window.resizable(False, False)
        
        # Делаем окно модальным
        self.window.transient(parent)
        self.window.grab_set()
        
        # Центрируем окно
        self.center_window()
        
        # Переменные
        self.scanner: Optional[DatabaseScanner] = None
        self.scan_thread: Optional[threading.Thread] = None
        self.is_scanning = False
        
        # Создание интерфейса
        self.create_widgets()
        
        # Запуск сканирования
        self.start_scanning()
    
    def center_window(self):
        """Центрирование окна на экране"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Главный фрейм
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="🔍 Сканирование базы данных", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Описание
        desc_label = ttk.Label(main_frame, 
                              text="Сбор данных о предметах с онлайн базы SPT-Tarkov.\n"
                                   "Это может занять несколько минут...",
                              font=('Arial', 10))
        desc_label.pack(pady=(0, 20))
        
        # Прогресс-бар
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.pack(pady=(0, 10))
        
        # Статус
        self.status_var = tk.StringVar(value="Инициализация...")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var,
                                     font=('Arial', 10))
        self.status_label.pack(pady=(0, 10))
        
        # Счетчик
        self.counter_var = tk.StringVar(value="0 / 0")
        self.counter_label = ttk.Label(main_frame, textvariable=self.counter_var,
                                      font=('Arial', 10, 'bold'))
        self.counter_label.pack(pady=(0, 20))
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(0, 10))
        
        self.pause_button = ttk.Button(button_frame, text="⏸️ Пауза", 
                                      command=self.toggle_pause, state='disabled')
        self.pause_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_button = ttk.Button(button_frame, text="❌ Отмена", 
                                       command=self.cancel_scanning)
        self.cancel_button.pack(side=tk.LEFT)
        
        # Информация о кэше
        info_frame = ttk.LabelFrame(main_frame, text="Информация", padding="10")
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.cache_info_var = tk.StringVar(value="Загрузка информации...")
        self.cache_info_label = ttk.Label(info_frame, textvariable=self.cache_info_var,
                                         font=('Arial', 9))
        self.cache_info_label.pack()
    
    def start_scanning(self):
        """Запуск сканирования в отдельном потоке"""
        self.is_scanning = True
        self.scan_thread = threading.Thread(target=self._scan_worker, daemon=True)
        self.scan_thread.start()
    
    def _scan_worker(self):
        """Рабочий поток сканирования"""
        try:
            # Создаем сканер
            self.scanner = DatabaseScanner(self.server_path)
            
            # Устанавливаем callbacks
            self.scanner.set_progress_callback(self.update_progress)
            self.scanner.set_status_callback(self.update_status)
            
            # Обновляем информацию о кэше
            self.update_cache_info()
            
            # Запускаем сканирование
            self.window.after(0, lambda: self.status_var.set("Сканирование предметов..."))
            self.window.after(0, lambda: self.pause_button.config(state='normal'))
            
            results = self.scanner.scan_all_items(delay_range=(0.3, 0.8))
            
            if self.scanner.is_cancelled:
                self.window.after(0, lambda: self.status_var.set("Сканирование отменено"))
                self.window.after(0, lambda: self.progress_var.set(0))
            else:
                self.window.after(0, lambda: self.status_var.set("Экспорт в читаемый формат..."))
                # Экспортируем в читаемый формат
                self.scanner.export_cache_to_readable()
                self.window.after(0, lambda: self.status_var.set("Сканирование завершено!"))
                self.window.after(0, lambda: self.progress_var.set(100))
            
            # Закрываем сканер
            self.scanner.close()
            
        except Exception as e:
            self.window.after(0, lambda: self.status_var.set(f"Ошибка: {str(e)}"))
            self.window.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка сканирования: {str(e)}"))
        
        finally:
            self.is_scanning = False
            self.window.after(0, self._on_scan_complete)
    
    def update_progress(self, current: int, total: int):
        """Обновление прогресса"""
        if total > 0:
            progress = (current / total) * 100
            self.window.after(0, lambda: self.progress_var.set(progress))
            self.window.after(0, lambda: self.counter_var.set(f"{current} / {total}"))
    
    def update_status(self, status: str):
        """Обновление статуса"""
        self.window.after(0, lambda: self.status_var.set(status))
    
    def update_cache_info(self):
        """Обновление информации о кэше"""
        if self.scanner:
            stats = self.scanner.get_cache_stats()
            info_text = f"Предметов в кэше: {stats['total_items']} | Размер: {stats['cache_file_size']} байт"
            self.window.after(0, lambda: self.cache_info_var.set(info_text))
    
    def toggle_pause(self):
        """Переключение паузы/продолжения"""
        if self.scanner:
            if self.scanner.is_paused:
                self.scanner.resume_scanning()
                self.pause_button.config(text="⏸️ Пауза")
                self.status_var.set("Сканирование продолжено...")
            else:
                self.scanner.pause_scanning()
                self.pause_button.config(text="▶️ Продолжить")
                self.status_var.set("Сканирование приостановлено...")
    
    def cancel_scanning(self):
        """Отмена сканирования"""
        if self.scanner and self.is_scanning:
            result = messagebox.askyesno("Отмена сканирования", 
                                       "Вы уверены, что хотите отменить сканирование?\n"
                                       "Прогресс будет сохранен.")
            if result:
                self.scanner.cancel_scanning()
                self.pause_button.config(state='disabled')
                self.cancel_button.config(state='disabled')
                self.status_var.set("Отмена сканирования...")
    
    def _on_scan_complete(self):
        """Обработка завершения сканирования"""
        self.pause_button.config(state='disabled')
        self.cancel_button.config(text="✅ Закрыть", command=self.close_window)
        
        if self.on_complete:
            self.on_complete()
    
    def close_window(self):
        """Закрытие окна"""
        if self.scanner:
            self.scanner.close()
        self.window.destroy()

def main():
    """Главная функция для тестирования модуля"""
    root = tk.Tk()
    root.withdraw()  # Скрываем главное окно
    
    def on_complete():
        print("Сканирование завершено!")
        root.quit()
    
    # Создаем окно прогресса
    progress_window = ScanProgressWindow(root, Path("."), on_complete)
    
    root.mainloop()

if __name__ == "__main__":
    main()
