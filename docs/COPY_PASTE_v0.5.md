# 📋 Готовый текст для копирования - v0.5

## Заголовок релиза
```
SPT Server Editor v0.5 - Stable Release
```

## Краткое описание
```
SPT Server Editor v0.5 - Стабильная версия с массовым редактированием параметров предметов, системой логирования и организованной документацией
```

## Теги
```
v0.5,stable,release,mass-editing,bulk-parameters,debug-logging,logging-system,documentation,ui-controls,python,tkinter,spt-aki,tarkov,server-editor,json-editor,null-bytes-fix,feature,enhancement,bugfix
```

## Полное описание (для GitHub)

```markdown
# 🚀 SPT Server Editor v0.5 - Stable Release

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

### 📚 Организованная документация
- Централизованная папка docs/
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
- Исправлена ошибка с null bytes в ui_utils.py
- Добавлена функция add_window_controls
- Исправлена ошибка с CraftManager.window
- Организована документация в папке docs/

## 📦 Установка
1. Скачайте архив
2. Распакуйте в папку SPT-AKI
3. Запустите `install.cmd`
4. Запустите `start.cmd`

## 🧪 Тестирование
Это стабильная версия. Все функции протестированы и работают корректно.

## 📞 Поддержка
- GitHub: [kabzon93region/spt-server-editor](https://github.com/kabzon93region/spt-server-editor)
- Discord: [SPT-AKI Discord](https://discord.gg/sp-tarkov)
- SPT-AKI Hub: [hub.sp-tarkov.com](https://hub.sp-tarkov.com/)

## 📄 Лицензия
MIT License
```

## Команды Git

```bash
# Создание тега
git tag -a v0.5 -m "Release v0.5 - Stable version with mass editing and logging"
git push origin v0.5

# Создание архивов
git archive --format=zip --output=SPT_Server_Editor_v0.5_full.zip HEAD
git archive --format=zip --output=SPT_Server_Editor_v0.5_source.zip HEAD
git archive --format=zip --output=SPT_Server_Editor_v0.5_docs.zip HEAD -- docs/
```

## Настройки релиза

- **Тег**: v0.5
- **Заголовок**: SPT Server Editor v0.5 - Stable Release
- **Pre-release**: НЕТ (стабильная версия)
- **Create discussion**: ДА
- **Files**: Прикрепить все архивы

---

**Готово для копирования! 📋**
