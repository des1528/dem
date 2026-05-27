# Магазин обуви — ДЭ-2026 Модуль 1 (+ стили М2)

## Установка
```
pip install mysql-connector-python pillow openpyxl
```

## Подготовка БД
1. Workbench → выполнить `schema.sql` (создаёт БД `shoes` и таблицы, заполняет роли).
2. Параметры подключения — в [db.py](db.py).
3. Импорт ресурсов: `python import_data.py` (берёт файлы из `C:\demka\_extracted\m1\import`).

## Запуск
```
python main.py
```

Сначала появится окно входа. Логины/пароли — из `user_import.xlsx`. Кнопка «Войти как гость» пропускает авторизацию.

## Что где
- [schema.sql](schema.sql) — БД в 3НФ.
- [db.py](db.py) — `fetch`/`query`.
- [main.py](main.py) — UI: окно входа, главное, редактирование товара, заказы.
- [import_data.py](import_data.py) — однократная загрузка ресурсов.
- [PLAN.md](PLAN.md) — план реализации.
- [GUIDE.md](GUIDE.md) — пошаговое объяснение для экзамена.
