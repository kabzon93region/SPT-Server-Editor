# 📦 Создание архива для релиза v0.4b

## 🎯 Подготовка архива

### 1. Создание архива через Git
```bash
# Создание архива с исходным кодом
git archive --format=zip --output=SPT_Server_Editor_v0.4b_source.zip HEAD

# Создание архива с документацией
git archive --format=zip --output=SPT_Server_Editor_v0.4b_docs.zip HEAD -- docs/ *.md

# Создание полного архива
git archive --format=zip --output=SPT_Server_Editor_v0.4b_full.zip HEAD
```

### 2. Создание архива вручную
Если Git архив не работает, создайте архив вручную:

#### Файлы для включения в архив:
```
SPT_Server_Editor_v0.4b/
├── main.py
├── stp_server_editor.py
├── requirements.txt
├── install.cmd
├── start.cmd
├── LICENSE
├── README.md
├── VERSION
├── CHANGELOG.md
├── RELEASE_NOTES.md
├── SECURITY.md
├── SUPPORT.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── .gitignore
├── modules/
│   ├── craft_manager.py
│   ├── scan_db.py
│   ├── items_cache.py
│   ├── items_manager.py
│   ├── bulk_parameters_dialog.py
│   ├── debug_logger.py
│   ├── item_parameters_analyzer.py
│   ├── logging_integration.py
│   └── ...
├── docs/
│   ├── TECHNICAL_DOCUMENTATION.md
│   ├── DEVELOPER_GUIDE.md
│   ├── DEPENDENCIES_ANALYSIS.md
│   ├── BULK_PARAMETERS_GUIDE.md
│   ├── DEBUG_LOGGING_GUIDE.md
│   ├── COMMENTS_DOCUMENTATION.md
│   └── ...
└── .github/
    ├── ISSUE_TEMPLATE/
    ├── workflows/
    └── ...
```

#### Файлы для исключения:
```
# Исключить из архива
cache/
logs/
__pycache__/
*.pyc
*.pyo
*.log
*.tmp
*.temp
*.bak
*.backup
*.json.bak
```

### 3. Создание архива через PowerShell
```powershell
# Создание архива
Compress-Archive -Path "main.py", "stp_server_editor.py", "requirements.txt", "modules", "docs", "*.md" -DestinationPath "SPT_Server_Editor_v0.4b_full.zip"

# Создание архива только с исходным кодом
Compress-Archive -Path "main.py", "stp_server_editor.py", "requirements.txt", "modules" -DestinationPath "SPT_Server_Editor_v0.4b_source.zip"

# Создание архива только с документацией
Compress-Archive -Path "*.md", "docs" -DestinationPath "SPT_Server_Editor_v0.4b_docs.zip"
```

### 4. Создание архива через 7-Zip
```bash
# Полный архив
7z a -tzip SPT_Server_Editor_v0.4b_full.zip main.py stp_server_editor.py requirements.txt modules docs *.md LICENSE README.md

# Архив с исходным кодом
7z a -tzip SPT_Server_Editor_v0.4b_source.zip main.py stp_server_editor.py requirements.txt modules

# Архив с документацией
7z a -tzip SPT_Server_Editor_v0.4b_docs.zip *.md docs
```

## 🔍 Проверка архива

### 1. Проверка содержимого
```bash
# Проверка архива
unzip -l SPT_Server_Editor_v0.4b_full.zip

# Проверка размера
ls -la SPT_Server_Editor_v0.4b_*.zip
```

### 2. Тестирование архива
```bash
# Распаковка и тестирование
unzip SPT_Server_Editor_v0.4b_full.zip -d test_extract
cd test_extract
python main.py --help
```

## 📋 Чек-лист архива

### Основные файлы
- [ ] `main.py` - Точка входа
- [ ] `stp_server_editor.py` - Основная программа
- [ ] `requirements.txt` - Зависимости
- [ ] `LICENSE` - Лицензия
- [ ] `README.md` - Документация

### Модули
- [ ] `modules/` - Все модули
- [ ] `modules/bulk_parameters_dialog.py` - Массовое редактирование
- [ ] `modules/debug_logger.py` - Система логирования
- [ ] `modules/item_parameters_analyzer.py` - Анализатор параметров

### Документация
- [ ] `TECHNICAL_DOCUMENTATION.md` - Техническая документация
- [ ] `DEVELOPER_GUIDE.md` - Руководство разработчика
- [ ] `CONTRIBUTING.md` - Руководство по участию
- [ ] `SECURITY.md` - Политика безопасности
- [ ] `SUPPORT.md` - Поддержка пользователей

### Конфигурация
- [ ] `.gitignore` - Игнорируемые файлы
- [ ] `VERSION` - Версия проекта
- [ ] `CHANGELOG.md` - Журнал изменений

### Исключения
- [ ] Нет файлов `cache/`
- [ ] Нет файлов `logs/`
- [ ] Нет файлов `__pycache__/`
- [ ] Нет временных файлов
- [ ] Нет резервных копий

## 🚀 Загрузка на GitHub

### 1. Подготовка к загрузке
- [ ] Архив создан
- [ ] Размер архива проверен
- [ ] Содержимое проверено
- [ ] Тестирование проведено

### 2. Загрузка
1. Перейдите к релизу на GitHub
2. Нажмите "Attach binaries"
3. Выберите файлы архива
4. Дождитесь загрузки
5. Проверьте, что файлы прикреплены

### 3. Проверка после загрузки
- [ ] Файлы загружены
- [ ] Размеры корректны
- [ ] Ссылки работают
- [ ] Скачивание возможно

## 📝 Примечания

### Размер архива
- Полный архив: ~2-5 MB
- Исходный код: ~1-2 MB
- Документация: ~500 KB

### Совместимость
- Архив должен работать на Windows
- Должен поддерживать длинные пути
- Должен сохранять права доступа

### Безопасность
- Не включайте конфиденциальные данные
- Проверьте содержимое перед публикацией
- Убедитесь, что нет личной информации

---

**Готово к публикации! 🚀**
