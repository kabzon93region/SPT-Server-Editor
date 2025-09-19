"""
Утилиты для работы с пользовательским интерфейсом
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Any, Callable
import json
from pathlib import Path

def center_window(window: tk.Tk, width: int, height: int) -> None:
    """
    Центрирование окна на экране
    
    Args:
        window: Окно для центрирования
        width: Ширина окна
        height: Высота окна
    """
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    window.geometry(f"{width}x{height}+{x}+{y}")

def create_scrollable_frame(parent: tk.Widget) -> tuple[tk.Frame, tk.Scrollbar]:
    """
    Создание прокручиваемого фрейма
    
    Args:
        parent: Родительский виджет
        
    Returns:
        Tuple[Frame, Scrollbar]: Фрейм и скроллбар
    """
    # Создаем Canvas для прокрутки
    canvas = tk.Canvas(parent, highlightthickness=0)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    # Настройка прокрутки
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    return scrollable_frame, scrollbar

def setup_resizable_window(window: tk.Tk, min_width: int = 800, min_height: int = 600) -> None:
    """
    Настройка окна с возможностью изменения размера
    
    Args:
        window: Окно для настройки
        min_width: Минимальная ширина
        min_height: Минимальная высота
    """
    window.minsize(min_width, min_height)
    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)

def apply_modern_style() -> None:
    """
    Применение современного стиля к приложению
    """
    style = ttk.Style()
    
    # Настройка темы
    style.theme_use('clam')
    
    # Стили для кнопок
    style.configure('TButton', padding=6)
    style.configure('Accent.TButton', padding=8, font=('Arial', 9, 'bold'))
    
    # Стили для фреймов
    style.configure('Card.TFrame', relief='raised', borderwidth=1)
    style.configure('Info.TFrame', relief='sunken', borderwidth=1)
    
    # Стили для лейблов
    style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
    style.configure('Subtitle.TLabel', font=('Arial', 10, 'bold'))
    style.configure('Info.TLabel', font=('Arial', 9))
    
    # Стили для полей ввода
    style.configure('TEntry', padding=4)
    style.configure('Search.TEntry', padding=6)
    
    # Стили для Treeview
    style.configure('Treeview', rowheight=25)
    style.configure('Treeview.Heading', font=('Arial', 9, 'bold'))

def setup_auto_scaling(window: tk.Tk, base_width: int = 1920, base_height: int = 1080) -> None:
    """
    Настройка автоматического масштабирования для разных разрешений экрана
    
    Args:
        window: Окно для настройки
        base_width: Базовое разрешение по ширине
        base_height: Базовое разрешение по высоте
    """
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Вычисляем коэффициент масштабирования
    scale_x = screen_width / base_width
    scale_y = screen_height / base_height
    scale = min(scale_x, scale_y, 1.0)  # Не увеличиваем больше 100%
    
    # Применяем масштабирование
    if scale < 1.0:
        window.tk.call('tk', 'scaling', scale)

def create_info_frame(parent: tk.Widget, title: str, info_text: str) -> ttk.Frame:
    """
    Создание информационного фрейма
    
    Args:
        parent: Родительский виджет
        title: Заголовок
        info_text: Информационный текст
        
    Returns:
        ttk.Frame: Информационный фрейм
    """
    info_frame = ttk.LabelFrame(parent, text=title, style='Info.TFrame')
    
    # Заголовок
    title_label = ttk.Label(info_frame, text=title, style='Title.TLabel')
    title_label.pack(pady=(5, 10))
    
    # Информационный текст
    info_label = ttk.Label(info_frame, text=info_text, style='Info.TLabel', wraplength=400)
    info_label.pack(pady=(0, 10))
    
    return info_frame

def create_button_frame(parent: tk.Widget, buttons: List[Dict[str, Any]]) -> ttk.Frame:
    """
    Создание фрейма с кнопками
    
    Args:
        parent: Родительский виджет
        buttons: Список кнопок с параметрами
        
    Returns:
        ttk.Frame: Фрейм с кнопками
    """
    button_frame = ttk.Frame(parent)
    
    for i, button_config in enumerate(buttons):
        button = ttk.Button(button_frame, **button_config)
        button.pack(side=tk.LEFT, padx=5, pady=5)
    
    return button_frame

def create_progress_bar(parent: tk.Widget, text: str = "Выполняется...") -> tuple[ttk.Progressbar, ttk.Label]:
    """
    Создание прогресс-бара с текстом
    
    Args:
        parent: Родительский виджет
        text: Текст для отображения
        
    Returns:
        Tuple[Progressbar, Label]: Прогресс-бар и лейбл
    """
    progress_frame = ttk.Frame(parent)
    
    # Лейбл с текстом
    progress_label = ttk.Label(progress_frame, text=text, style='Info.TLabel')
    progress_label.pack(pady=(0, 5))
    
    # Прогресс-бар
    progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
    progress_bar.pack(fill=tk.X, pady=(0, 5))
    
    return progress_bar, progress_label

def show_error_dialog(parent: tk.Widget, title: str, message: str) -> None:
    """
    Показ диалога с ошибкой
    
    Args:
        parent: Родительский виджет
        title: Заголовок диалога
        message: Сообщение об ошибке
    """
    messagebox.showerror(title, message)

def show_info_dialog(parent: tk.Widget, title: str, message: str) -> None:
    """
    Показ информационного диалога
    
    Args:
        parent: Родительский виджет
        title: Заголовок диалога
        message: Информационное сообщение
    """
    messagebox.showinfo(title, message)

def show_warning_dialog(parent: tk.Widget, title: str, message: str) -> None:
    """
    Показ диалога с предупреждением
    
    Args:
        parent: Родительский виджет
        title: Заголовок диалога
        message: Сообщение с предупреждением
    """
    messagebox.showwarning(title, message)

def ask_yes_no(parent: tk.Widget, title: str, message: str) -> bool:
    """
    Диалог с вопросом Да/Нет
    
    Args:
        parent: Родительский виджет
        title: Заголовок диалога
        message: Вопрос
        
    Returns:
        bool: True если пользователь выбрал "Да"
    """
    return messagebox.askyesno(title, message)

def ask_ok_cancel(parent: tk.Widget, title: str, message: str) -> bool:
    """
    Диалог с кнопками OK/Отмена
    
    Args:
        parent: Родительский виджет
        title: Заголовок диалога
        message: Сообщение
        
    Returns:
        bool: True если пользователь выбрал "OK"
    """
    return messagebox.askokcancel(title, message)

def create_search_entry(parent: tk.Widget, placeholder: str = "Поиск...") -> ttk.Entry:
    """
    Создание поля поиска с плейсхолдером
    
    Args:
        parent: Родительский виджет
        placeholder: Текст плейсхолдера
        
    Returns:
        ttk.Entry: Поле поиска
    """
    search_entry = ttk.Entry(parent, style='Search.TEntry')
    
    # Добавляем плейсхолдер
    search_entry.insert(0, placeholder)
    search_entry.configure(foreground='gray')
    
    def on_focus_in(event):
        if search_entry.get() == placeholder:
            search_entry.delete(0, tk.END)
            search_entry.configure(foreground='black')
    
    def on_focus_out(event):
        if not search_entry.get():
            search_entry.insert(0, placeholder)
            search_entry.configure(foreground='gray')
    
    search_entry.bind('<FocusIn>', on_focus_in)
    search_entry.bind('<FocusOut>', on_focus_out)
    
    return search_entry

def create_treeview(parent: tk.Widget, columns: List[str], show_headers: bool = True) -> ttk.Treeview:
    """
    Создание Treeview с настройками
    
    Args:
        parent: Родительский виджет
        columns: Список колонок
        show_headers: Показывать заголовки
        
    Returns:
        ttk.Treeview: Настроенный Treeview
    """
    tree = ttk.Treeview(parent, columns=columns, show='headings' if show_headers else 'tree')
    
    # Настройка колонок
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, minwidth=50)
    
    # Настройка растягивания
    tree.grid_rowconfigure(0, weight=1)
    tree.grid_columnconfigure(0, weight=1)
    
    return tree

def create_window_control_buttons(parent: tk.Widget) -> tk.Frame:
    """
    Создает кнопки управления окном (свернуть, развернуть, закрыть)
    
    Args:
        parent: Родительский виджет, к которому будут привязаны кнопки.
        
    Returns:
        tk.Frame: Фрейм с кнопками управления.
    """
    control_frame = ttk.Frame(parent)
    
    # Кнопка "Свернуть"
    minimize_button = ttk.Button(control_frame, text="—", command=lambda: parent.iconify())
    minimize_button.pack(side=tk.LEFT, padx=1, pady=1)
    
    # Кнопка "Развернуть/Восстановить"
    # Для простоты пока только развернуть, можно добавить логику переключения
    maximize_button = ttk.Button(control_frame, text="⬜", command=lambda: parent.state('zoomed'))
    maximize_button.pack(side=tk.LEFT, padx=1, pady=1)
    
    # Кнопка "Закрыть"
    close_button = ttk.Button(control_frame, text="✕", command=parent.destroy)
    close_button.pack(side=tk.LEFT, padx=1, pady=1)
    
    return control_frame

def add_window_controls(window: tk.Tk) -> None:
    """
    Добавляет кастомные элементы управления окном (свернуть, развернуть, закрыть)
    и скрывает стандартную строку заголовка.
    
    Args:
        window: Главное окно Tkinter.
    """
    # Скрываем стандартную строку заголовка
    window.overrideredirect(True)
    
    # Создаем фрейм для кастомной строки заголовка
    title_bar = ttk.Frame(window, relief="raised", bd=2)
    title_bar.pack(side=tk.TOP, fill=tk.X, expand=False)
    
    # Добавляем заголовок окна
    title_label = ttk.Label(title_bar, text=window.title(), anchor=tk.W)
    title_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    
    # Добавляем кнопки управления окном
    control_buttons = create_window_control_buttons(window)
    control_buttons.pack(side=tk.RIGHT)
    
    # Функции для перетаскивания окна
    def start_move(event):
        window.x = event.x
        window.y = event.y

    def stop_move(event):
        window.x = None
        window.y = None

    def on_motion(event):
        deltax = event.x - window.x
        deltay = event.y - window.y
        x = window.winfo_x() + deltax
        y = window.winfo_y() + deltay
        window.geometry(f"+{x}+{y}")

    title_bar.bind("<ButtonPress-1>", start_move)
    title_bar.bind("<ButtonRelease-1>", stop_move)
    title_bar.bind("<B1-Motion>", on_motion)