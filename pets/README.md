# Товары для животных — полная версия ДЭ-2026

## Установка
```
pip install mysql-connector-python pillow openpyxl
```

## Подготовка
1. В Workbench: `schema.sql`.
2. Положи `picture.png` (заглушка) в папку `pets/` (есть в ресурсах).
3. `python import_data.py`.

## Запуск
```
python main.py                       # приложение
python -m unittest test_lib -v       # 10 тестов
```

## Что где
- [schema.sql](schema.sql) — БД.
- [db.py](db.py) — обёртка над MySQL.
- [main.py](main.py) — UI: окно входа с captcha, главное, редактирование.
- [SF2022User01Lib.py](SF2022User01Lib.py) — библиотека расчёта свободных окон.
- [test_lib.py](test_lib.py) — 10 unit-тестов.
- [PLAN.md](PLAN.md), [GUIDE.md](GUIDE.md) — план + пошаговый гайд.
