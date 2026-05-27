# План: Магазин обуви (М1) + стили (М2)

## Контекст
Готовимся к ДЭ-2026, Модуль 1 «ООО Обувь». Нужно desktop-приложение на Python (Tkinter + MySQL), реализующее:
- авторизацию из таблицы `User`,
- 4 роли: Гость, Клиент, Менеджер, Администратор,
- список товаров с поиском/сортировкой/фильтром (для М/А),
- CRUD товаров (только Администратор),
- список заказов (для М/А) и их CRUD (только А).

Стили М2 применяем «поверх» (белый фон, Times New Roman, #7FFF00 шапка, #00FA9A целевые кнопки, #2E8B57 — фон карточки при скидке > 15%).

## Структура
```
shoes/
├── schema.sql         # БД в 3НФ (справочники вынесены)
├── db.py              # fetch/query (как в salon)
├── main.py            # окно входа + главное окно + редактирование + заказы
├── import_data.py     # импорт Tovar.xlsx, user_import.xlsx, Заказ_import.xlsx, Пункты выдачи
├── images/
├── PLAN.md, GUIDE.md, README.md
```

## Схема БД (3НФ)
- `Role(ID, Name)`, `User(ID, RoleID→Role, FIO, Login, Password)` — справочник ролей выделен.
- `Category`, `Manufacturer`, `Supplier`, `PickupPoint` — все справочники отдельными таблицами.
- `Product(ID, Article, Name, Unit, Price, SupplierID, ManufacturerID, CategoryID, Discount, Stock, Description, ImagePath)`.
- `Order(ID, OrderDate, DeliveryDate, PickupPointID, ClientFIO, Code, Status)` + `OrderItem(OrderID, ProductID, Qty)` — связка многие-ко-многим.

## Ключевые приёмы
- Глобальная переменная `USER` (None для гостя или dict с ролью).
- `show_login()` / `show_main()` — две функции на полную перерисовку, через `for w in root.winfo_children(): w.destroy()`.
- Реактивные `trace_add("write", ...)` на поиск/фильтр/сортировку.
- Запрет на дубль артикула: `SELECT 1 FROM Product WHERE Article=%s AND ID<>%s`.
- Запрет удаления, если есть `OrderItem`.
- При смене картинки: сжимаем до 300×200 через PIL `thumbnail`, копируем в `images/`, удаляем старую.
- `get_or_create("Category", name)` — единая функция для справочников при сохранении.

## Стили М2 (как применяю)
- Шрифт `("Times New Roman", 11)` назначен константой `FONT`, всем виджетам передаётся явно.
- `BG_MAIN = "white"`, `BG_ACCENT = "#7FFF00"` (шапка), `BG_ACTION = "#00FA9A"` (кнопки «Войти», «Сохранить», «+ Товар»), `BG_DISCOUNT = "#2E8B57"` (фон карточки если `Discount > 15`).
- Логотип/иконка: `root.iconbitmap("Icon.ico")` если файл есть.

## Проверка
1. `pip install mysql-connector-python pillow openpyxl`
2. В Workbench: выполнить `schema.sql`.
3. `python import_data.py` — наполнить из ресурсов `Прил_2_ОЗ_КОД 09.02.07-2-2026-М1.rar`.
4. `python main.py` — окно входа.
5. Войти под каждой ролью:
   - Гость: видит товары без поиска/фильтра.
   - Клиент: то же.
   - Менеджер: поиск + фильтр + сортировка + заказы.
   - Администратор: всё + CRUD товаров и заказов.
6. Попытаться удалить товар, который в заказе — ошибка.
7. Скидка > 15% → карточка тёмно-зелёная.
8. Остаток 0 → карточка серая.
