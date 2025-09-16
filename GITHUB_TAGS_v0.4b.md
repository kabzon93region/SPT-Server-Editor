# 🏷️ Теги для GitHub релиза v0.4b

## Основные теги

```
v0.4b
beta
release
```

## Функциональные теги

```
mass-editing
bulk-parameters
debug-logging
logging-system
documentation
```

## Технические теги

```
python
tkinter
spt-aki
tarkov
server-editor
json-editor
```

## Категории

```
feature
enhancement
beta
testing
```

## Полный список тегов для GitHub

```
v0.4b,beta,release,mass-editing,bulk-parameters,debug-logging,logging-system,documentation,python,tkinter,spt-aki,tarkov,server-editor,json-editor,feature,enhancement,testing
```

## Описание для GitHub Release

### Краткое описание
**SPT Server Editor v0.4b** - Бета-версия с массовым редактированием параметров предметов, системой логирования и расширенной документацией.

### Полное описание
```markdown
# 🚀 SPT Server Editor v0.4b - Beta Release

## ✨ Новые возможности

### ⚡ Массовое изменение параметров предметов
- Ввод списка ID предметов для массового редактирования
- Выбор параметров из базы данных
- Валидация входных данных
- Предварительный просмотр изменений
- Автоматическое резервное копирование (.json.bak)
- Подробное логирование операций

### 🔍 Система отладочного логирования
- Цветной консольный вывод
- Файловое логирование с ротацией
- ZIP архивация старых логов
- Многопоточное логирование
- Категоризация сообщений
- Детальная статистика

### 📚 Расширенная документация
- Техническая документация
- Руководство разработчика
- Руководство по участию
- Анализ зависимостей
- Руководства пользователя

## 🔧 Улучшения
- Модульная архитектура
- Потокобезопасность
- Улучшенная обработка ошибок
- Современный UI
- Оптимизация производительности

## 🐛 Исправления
- Исправлено расширение резервных копий
- Улучшена валидация параметров
- Исправлены проблемы с логированием
- Устранены проблемы с импортами

## 📦 Установка
1. Скачайте архив
2. Распакуйте в папку SPT-AKI
3. Запустите `install.cmd`
4. Запустите `start.cmd`

## 🧪 Тестирование
Это бета-версия. Создавайте резервные копии перед использованием.

## 📞 Поддержка
- GitHub: [kabzon93region/spt-server-editor](https://github.com/kabzon93region/spt-server-editor)
- Discord: [SPT-AKI Discord](https://discord.gg/sp-tarkov)
- SPT-AKI Hub: [hub.sp-tarkov.com](https://hub.sp-tarkov.com/)

## 📄 Лицензия
MIT License
```

## Файлы для релиза

### Основные файлы
- `main.py` - Точка входа
- `stp_server_editor.py` - Основная программа
- `requirements.txt` - Зависимости
- `LICENSE` - Лицензия MIT
- `README.md` - Документация

### Модули
- `modules/` - Все модули программы
- `modules/bulk_parameters_dialog.py` - Массовое редактирование
- `modules/debug_logger.py` - Система логирования
- `modules/item_parameters_analyzer.py` - Анализатор параметров

### Документация
- `TECHNICAL_DOCUMENTATION.md` - Техническая документация
- `DEVELOPER_GUIDE.md` - Руководство разработчика
- `CONTRIBUTING.md` - Руководство по участию
- `SECURITY.md` - Политика безопасности
- `SUPPORT.md` - Поддержка пользователей

### Конфигурация
- `.gitignore` - Игнорируемые файлы
- `VERSION` - Версия проекта
- `CHANGELOG.md` - Журнал изменений

## Инструкции по публикации

### 1. Подготовка
```bash
# Создание тега
git tag -a v0.4b -m "Release v0.4b - Beta with mass editing and logging"

# Отправка тега
git push origin v0.4b
```

### 2. Создание релиза на GitHub
1. Перейдите в раздел Releases
2. Нажмите "Create a new release"
3. Выберите тег `v0.4b`
4. Заголовок: `SPT Server Editor v0.4b - Beta Release`
5. Описание: Скопируйте из `RELEASE_v0.4b.md`
6. Приложите файлы архива
7. Отметьте как "Pre-release" (бета-версия)
8. Опубликуйте релиз

### 3. Файлы для архива
- `SPT_Server_Editor_v0.4b.zip` - Полный архив
- `SPT_Server_Editor_v0.4b_source.zip` - Исходный код
- `SPT_Server_Editor_v0.4b_docs.zip` - Документация

## Проверочный список

- [ ] Все файлы обновлены
- [ ] Версия изменена на 0.4b
- [ ] Теги созданы
- [ ] Документация обновлена
- [ ] Тестирование проведено
- [ ] Архивы созданы
- [ ] Релиз опубликован
- [ ] Уведомления отправлены
