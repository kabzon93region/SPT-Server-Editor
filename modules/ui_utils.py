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

def create_labeled_entry(parent: tk.Widget, label_text: str, 
                        textvariable: Optional[tk.StringVar] = None,
                        width: int = 20) -> tuple[ttk.Label, ttk.Entry]:
    """
    Создание поля ввода с подписью
    
    Args:
        parent: Родительский виджет
        label_text: Текст подписи
        textvariable: Переменная для хранения значения
        width: Ширина поля ввода
        
    Returns:
        Tuple[Label, Entry]: Подпись и поле ввода
    """
    label = ttk.Label(parent, text=label_text)
    entry = ttk.Entry(parent, textvariable=textvariable, width=width)
    
    return label, entry

def create_labeled_combobox(parent: tk.Widget, label_text: str,
                           values: List[str], textvariable: Optional[tk.StringVar] = None,
                           width: int = 20) -> tuple[ttk.Label, ttk.Combobox]:
    """
    Создание выпадающего списка с подписью
    
    Args:
        parent: Родительский виджет
        label_text: Текст подписи
        values: Список значений
        textvariable: Переменная для хранения значения
        width: Ширина списка
        
    Returns:
        Tuple[Label, Combobox]: Подпись и выпадающий список
    """
    label = ttk.Label(parent, text=label_text)
    combobox = ttk.Combobox(parent, textvariable=textvariable, 
                           values=values, width=width, state="readonly")
    
    return label, combobox

def create_button(parent: tk.Widget, text: str, command: Optional[Callable] = None,
                 width: int = 15) -> ttk.Button:
    """
    Создание кнопки
    
    Args:
        parent: Родительский виджет
        text: Текст кнопки
        command: Команда для выполнения при нажатии
        width: Ширина кнопки
        
    Returns:
        Button: Созданная кнопка
    """
    return ttk.Button(parent, text=text, command=command, width=width)

def create_treeview(parent: tk.Widget, columns: List[str], 
                   show_headings: bool = True) -> ttk.Treeview:
    """
    Создание таблицы (Treeview)
    
    Args:
        parent: Родительский виджет
        columns: Список колонок
        show_headings: Показывать заголовки
        
    Returns:
        Treeview: Созданная таблица
    """
    tree = ttk.Treeview(parent, columns=columns, show='headings' if show_headings else 'tree')
    
    # Настройка колонок
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, minwidth=50)
    
    return tree

def create_scrollable_treeview(parent: tk.Widget, columns: List[str],
                              show_headings: bool = True) -> tuple[tk.Frame, ttk.Treeview, ttk.Scrollbar]:
    """
    Создание прокручиваемой таблицы
    
    Args:
        parent: Родительский виджет
        columns: Список колонок
        show_headings: Показывать заголовки
        
    Returns:
        Tuple[Frame, Treeview, Scrollbar]: Контейнер, таблица и скроллбар
    """
    # Создаем фрейм для таблицы
    tree_frame = ttk.Frame(parent)
    
    # Создаем таблицу
    tree = ttk.Treeview(tree_frame, columns=columns, show='headings' if show_headings else 'tree')
    
    # Создаем скроллбары
    v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
    
    # Настройка таблицы
    tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    
    # Настройка колонок
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, minwidth=50)
    
    # Размещение элементов
    tree.grid(row=0, column=0, sticky="nsew")
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    h_scrollbar.grid(row=1, column=0, sticky="ew")
    
    # Настройка растягивания
    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)
    
    return tree_frame, tree, v_scrollbar

def apply_modern_style() -> None:
    """
    Применение светлого стиля к приложению
    """
    style = ttk.Style()
    
    # Настройка темы
    try:
        style.theme_use('clam')  # Современная тема
    except:
        pass  # Если тема недоступна, используем по умолчанию
    
    # Глобальная настройка светлой темы для всех tkinter виджетов
    setup_global_light_theme()
    
    # Цветовая схема светлой темы
    light_bg = '#ffffff'      # Белый фон
    light_fg = '#000000'      # Черный текст
    light_select = '#0078d4'  # Синий для выделения
    light_entry = '#ffffff'   # Белый для полей ввода
    light_button = '#0078d4'  # Синий для кнопок
    light_frame = '#f5f5f5'   # Светло-серый фон для фреймов
    light_hover = '#106ebe'   # Темно-синий при наведении
    light_disabled = '#cccccc' # Серый для отключенных элементов
    
    # Настройка цветов для всех элементов
    style.configure('TLabel', 
                   background=light_bg, 
                   foreground=light_fg, 
                   font=('Segoe UI', 9))
    
    style.configure('TButton', 
                   background=light_button, 
                   foreground='white',
                   font=('Segoe UI', 9),
                   borderwidth=1,
                   relief='solid')
    
    style.configure('TEntry', 
                   fieldbackground=light_entry, 
                   background=light_entry,
                   foreground=light_fg, 
                   font=('Segoe UI', 9),
                   borderwidth=1,
                   relief='solid',
                   bordercolor='#cccccc')
    
    style.configure('TCombobox', 
                   fieldbackground=light_entry, 
                   background=light_entry,
                   foreground=light_fg, 
                   font=('Segoe UI', 9),
                   borderwidth=1,
                   relief='solid',
                   bordercolor='#cccccc')
    
    style.configure('Treeview', 
                   background=light_bg, 
                   foreground=light_fg, 
                   font=('Consolas', 9),
                   fieldbackground=light_bg,
                   borderwidth=1,
                   relief='solid',
                   bordercolor='#cccccc')
    
    style.configure('TFrame', 
                   background=light_bg,
                   borderwidth=0)
    
    style.configure('TLabelFrame', 
                   background=light_frame, 
                   foreground=light_fg,
                   borderwidth=1,
                   relief='solid',
                   bordercolor='#cccccc')
    
    style.configure('TNotebook', 
                   background=light_bg,
                   borderwidth=0)
    
    style.configure('TNotebook.Tab', 
                   background=light_frame,
                   foreground=light_fg,
                   padding=[10, 5])
    
    style.configure('TCheckbutton', 
                   background=light_bg,
                   foreground=light_fg,
                   font=('Segoe UI', 9))
    
    style.configure('TRadiobutton', 
                   background=light_bg,
                   foreground=light_fg,
                   font=('Segoe UI', 9))
    
    style.configure('TScrollbar', 
                   background=light_frame,
                   troughcolor=light_frame,
                   borderwidth=0,
                   arrowcolor=light_fg,
                   darkcolor=light_frame,
                   lightcolor=light_frame)
    
    style.configure('Horizontal.TProgressbar', 
                   troughcolor='#e0e0e0',  # Светло-серый фон
                   background=light_select,  # Синий индикатор
                   borderwidth=0,
                   lightcolor=light_select,
                   darkcolor=light_select)
    
    # Настройка состояний кнопок
    style.map('TButton',
             background=[('active', light_hover),
                        ('pressed', '#005a9e')])
    
    # Настройка состояний полей ввода
    style.map('TEntry',
             fieldbackground=[('focus', light_entry),
                            ('!focus', light_entry)],
             bordercolor=[('focus', light_select),
                         ('!focus', '#cccccc')])
    
    # Настройка состояний выпадающих списков
    style.map('TCombobox',
             fieldbackground=[('focus', light_entry),
                            ('!focus', light_entry)],
             bordercolor=[('focus', light_select),
                         ('!focus', '#cccccc')])
    
    # Настройка состояний таблиц
    style.map('Treeview',
             background=[('selected', light_select)],
             foreground=[('selected', 'white')])

def setup_global_light_theme() -> None:
    """
    Глобальная настройка светлой темы для всех tkinter виджетов
    """
    # Цветовая схема светлой темы
    light_bg = '#ffffff'
    light_fg = '#000000'
    light_select = '#0078d4'
    light_entry = '#ffffff'
    light_button = '#0078d4'
    light_frame = '#f5f5f5'
    
    import tkinter
    root = tkinter._default_root
    if root is None:
        root = tkinter.Tk()
        root.withdraw()  # Скрываем окно
    
    root.option_add('*background', light_bg)
    root.option_add('*foreground', light_fg)
    root.option_add('*selectBackground', light_select)
    root.option_add('*selectForeground', 'white')
    root.option_add('*activeBackground', light_select)
    root.option_add('*activeForeground', 'white')
    root.option_add('*highlightBackground', light_bg)
    root.option_add('*highlightColor', light_select)
    root.option_add('*insertBackground', light_fg)
    root.option_add('*troughColor', light_frame)
    root.option_add('*borderWidth', 1)
    root.option_add('*relief', 'solid')
    root.option_add('*bordercolor', '#cccccc')
    
    # Настройки для конкретных виджетов
    root.option_add('*Entry.background', light_entry)
    root.option_add('*Entry.foreground', light_fg)
    root.option_add('*Entry.borderWidth', 1)
    root.option_add('*Entry.relief', 'solid')
    root.option_add('*Entry.bordercolor', '#cccccc')
    
    root.option_add('*Text.background', light_entry)
    root.option_add('*Text.foreground', light_fg)
    root.option_add('*Text.insertBackground', light_fg)
    root.option_add('*Text.selectBackground', light_select)
    root.option_add('*Text.selectForeground', 'white')
    
    root.option_add('*Listbox.background', light_entry)
    root.option_add('*Listbox.foreground', light_fg)
    root.option_add('*Listbox.selectBackground', light_select)
    root.option_add('*Listbox.selectForeground', 'white')
    
    root.option_add('*Canvas.background', light_bg)
    root.option_add('*Canvas.foreground', light_fg)
    
    root.option_add('*Frame.background', light_bg)
    root.option_add('*Label.background', light_bg)
    root.option_add('*Label.foreground', light_fg)
    
    root.option_add('*Button.background', light_button)
    root.option_add('*Button.foreground', 'white')
    root.option_add('*Button.activeBackground', light_select)
    root.option_add('*Button.activeForeground', 'white')
    
    root.option_add('*Checkbutton.background', light_bg)
    root.option_add('*Checkbutton.foreground', light_fg)
    root.option_add('*Checkbutton.activeBackground', light_bg)
    root.option_add('*Checkbutton.activeForeground', light_fg)
    
    root.option_add('*Radiobutton.background', light_bg)
    root.option_add('*Radiobutton.foreground', light_fg)
    root.option_add('*Radiobutton.activeBackground', light_bg)
    root.option_add('*Radiobutton.activeForeground', light_fg)
    
    root.option_add('*Scale.background', light_bg)
    root.option_add('*Scale.foreground', light_fg)
    root.option_add('*Scale.troughColor', light_frame)
    root.option_add('*Scale.activeBackground', light_select)
    
    root.option_add('*Scrollbar.background', light_frame)
    root.option_add('*Scrollbar.troughColor', light_frame)
    root.option_add('*Scrollbar.activeBackground', light_select)
    
    root.option_add('*Menu.background', light_bg)
    root.option_add('*Menu.foreground', light_fg)
    root.option_add('*Menu.activeBackground', light_select)
    root.option_add('*Menu.activeForeground', 'white')
    
    root.option_add('*Menubutton.background', light_button)
    root.option_add('*Menubutton.foreground', 'white')
    root.option_add('*Menubutton.activeBackground', light_select)
    root.option_add('*Menubutton.activeForeground', 'white')

def show_info(title: str, message: str) -> None:
    """
    Показать информационное сообщение
    
    Args:
        title: Заголовок окна
        message: Текст сообщения
    """
    messagebox.showinfo(title, message)

def show_warning(title: str, message: str) -> None:
    """
    Показать предупреждение
    
    Args:
        title: Заголовок окна
        message: Текст сообщения
    """
    messagebox.showwarning(title, message)

def show_error(title: str, message: str) -> None:
    """
    Показать сообщение об ошибке
    
    Args:
        title: Заголовок окна
        message: Текст сообщения
    """
    messagebox.showerror(title, message)

def ask_yes_no(title: str, message: str) -> bool:
    """
    Задать вопрос да/нет
    
    Args:
        title: Заголовок окна
        message: Текст вопроса
        
    Returns:
        bool: True если пользователь выбрал "Да"
    """
    return messagebox.askyesno(title, message)

def ask_ok_cancel(title: str, message: str) -> bool:
    """
    Задать вопрос ОК/Отмена
    
    Args:
        title: Заголовок окна
        message: Текст вопроса
        
    Returns:
        bool: True если пользователь выбрал "ОК"
    """
    return messagebox.askokcancel(title, message)

def create_tooltip(widget: tk.Widget, text: str) -> None:
    """
    Создание всплывающей подсказки для виджета
    
    Args:
        widget: Виджет для подсказки
        text: Текст подсказки
    """
    def on_enter(event):
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        
        label = tk.Label(tooltip, text=text, background="#ffffe0", 
                        relief="solid", borderwidth=1, font=('Segoe UI', 8))
        label.pack()
        
        widget.tooltip = tooltip
    
    def on_leave(event):
        if hasattr(widget, 'tooltip'):
            widget.tooltip.destroy()
            del widget.tooltip
    
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

def load_json_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Загрузка JSON файла
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        Optional[Dict]: Данные из файла или None при ошибке
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки файла {file_path}: {e}")
        return None

def save_json_file(file_path: Path, data: Dict[str, Any]) -> bool:
    """
    Сохранение JSON файла
    
    Args:
        file_path: Путь к файлу
        data: Данные для сохранения
        
    Returns:
        bool: True если сохранение успешно
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка сохранения файла {file_path}: {e}")
        return False

def create_progress_dialog(parent: tk.Widget, title: str, message: str) -> tuple[tk.Toplevel, ttk.Progressbar, ttk.Label]:
    """
    Создание диалога с прогресс-баром
    
    Args:
        parent: Родительское окно
        title: Заголовок диалога
        message: Сообщение
        
    Returns:
        Tuple[Toplevel, Progressbar, Label]: Диалог, прогресс-бар и метка
    """
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.resizable(False, False)
    dialog.grab_set()
    
    # Центрирование
    center_window(dialog, 400, 120)
    
    # Создание элементов
    label = ttk.Label(dialog, text=message)
    label.pack(pady=10)
    
    progress = ttk.Progressbar(dialog, mode='indeterminate')
    progress.pack(pady=10, padx=20, fill='x')
    progress.start()
    
    return dialog, progress, label

def update_progress_dialog(progress: ttk.Progressbar, label: ttk.Label, 
                          value: int, maximum: int, message: str = None) -> None:
    """
    Обновление диалога прогресса
    
    Args:
        progress: Прогресс-бар
        label: Метка
        value: Текущее значение
        maximum: Максимальное значение
        message: Новое сообщение
    """
    if message:
        label.config(text=message)
    
    progress.config(mode='determinate', maximum=maximum, value=value)
    progress.update()

def close_progress_dialog(dialog: tk.Toplevel) -> None:
    """
    Закрытие диалога прогресса
    
    Args:
        dialog: Диалог для закрытия
    """
    dialog.destroy()

def create_tree(parent: tk.Widget, columns: List[str], 
               show_headings: bool = True) -> ttk.Treeview:
    """
    Создание таблицы (Treeview) с прокруткой
    
    Args:
        parent: Родительский виджет
        columns: Список колонок
        show_headings: Показывать заголовки
        
    Returns:
        Treeview: Созданная таблица
    """
    # Создаем фрейм для таблицы
    tree_frame = ttk.Frame(parent)
    tree_frame.pack(fill=tk.BOTH, expand=True)
    
    # Создаем таблицу
    tree = ttk.Treeview(tree_frame, columns=columns, show='headings' if show_headings else 'tree')
    
    # Создаем скроллбары
    v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
    
    # Настройка таблицы
    tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    
    # Настройка колонок
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, minwidth=50)
    
    # Размещение элементов
    tree.grid(row=0, column=0, sticky="nsew")
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    h_scrollbar.grid(row=1, column=0, sticky="ew")
    
    # Настройка растягивания
    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)
    
    return tree