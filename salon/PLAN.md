# План: Салон красоты — Сессия 1 (Python + Tkinter + MySQL)

## Контекст

Готовимся к ДЭ-2026 (предметная область «Салон красоты», Сессия 1). На экзамене ученик должен полностью самостоятельно с нуля написать приложение, реализующее ТЗ из `Сессия 1.pdf`. Поэтому код должен быть:

- **максимально коротким** (минимум абстракций, всё в одном файле, без классов где это не нужно),
- **легко запоминаемым** (повторяющиеся приёмы — `query()`, `fetch()`, общий шаблон окна),
- **полностью покрывающим ТЗ** (режим админа по коду `0000`, CRUD услуг, фото, запись на услугу, ближайшие записи).

Стек: **Python 3 + tkinter + mysql-connector-python + Pillow**.
СУБД: **MySQL** (Workbench), база поднимается из `my.sql`.

---

## Структура проекта

```
salon/
├── main.py            # одна точка входа, всё приложение
├── db.py              # подключение и helper-функции к MySQL
├── images/            # копии загруженных пользователем картинок
└── README.md
```

Всего ~400 строк кода. Цель — простота, а не модульность.

---

## Шаг 0a. Нормализация БД до 3НФ (теория + проверка схемы)

ТЗ требует, чтобы схема БД была в **третьей нормальной форме**. Проверяем каждую таблицу по трём правилам:

1. **1НФ** — все атрибуты атомарны, нет повторяющихся групп.
2. **2НФ** — выполнена 1НФ + все неключевые атрибуты полностью зависят от **всего** первичного ключа (актуально для составных ключей).
3. **3НФ** — выполнена 2НФ + нет транзитивных зависимостей (неключевой атрибут не зависит от другого неключевого).

### Анализ исходной схемы (`my.sql`)

| Таблица | Что проверяем | Вывод |
|---|---|---|
| `Service(ID, Title, Cost, DurationInSeconds, Description, Discount, MainImagePath)` | Все атрибуты атомарны, зависят только от `ID`. | ✅ 3НФ |
| `ServicePhoto(ID, ServiceID, PhotoPath)` | Вынесли «много фото на услугу» в отдельную таблицу — иначе нарушение 1НФ. | ✅ 3НФ |
| `Client(ID, FirstName, LastName, Patronymic, Birthday, Email, Phone, GenderCode, …)` | `GenderCode` — FK на `Gender(Code)`, не транзитивная зависимость, т.к. ссылается на ключ другой таблицы. | ✅ 3НФ |
| `Gender(Code, Name)` | Справочник пола вынесен отдельно — иначе у `Client` была бы повторяющаяся строка `Name="Мужской"`, и `Name` зависел бы от `GenderCode`, а не от `ID` (транзитивная зависимость, нарушение 3НФ). | ✅ 3НФ — это и есть пример вынесения справочника ради 3НФ. |
| `ClientService(ID, ClientID, ServiceID, StartTime, Comment)` | ID-шник суррогатный, неключевые атрибуты зависят только от него. | ✅ 3НФ |
| `Tag(ID, Title, Color)`, `TagOfClient(ClientID, TagID)` | Связь many-to-many через отдельную таблицу. | ✅ 3НФ |
| `Product`, `Manufacturer`, `ProductPhoto`, `ProductSale`, `AttachedProduct` | Аналогично — выделены справочники и связки. | ✅ 3НФ |

### Типичные нарушения, которые НУЖНО уметь распознать на экзамене

- В `Client` лежит поле `GenderName` рядом с `GenderCode` → транзитивная зависимость (`GenderName` зависит от `GenderCode`, а не от `Client.ID`) → **нарушение 3НФ**. Лечение — вынести в справочник `Gender`.
- В `Service` лежит поле `CategoryName` без таблицы категорий — то же самое. Лечение — `Category(ID, Name)` + `Service.CategoryID`.
- В `Client` поля `Tag1`, `Tag2`, `Tag3` — нарушение 1НФ (повторяющаяся группа). Лечение — `Tag` + `TagOfClient`.
- В одной таблице `Service` хранится несколько `PhotoPath` через запятую — нарушение 1НФ (атрибут неатомарен). Лечение — `ServicePhoto`.

**Вывод по нашей БД:** схема из `my.sql` уже находится в 3НФ, доводить ничего не нужно. На защите проекта эту таблицу нужно уметь привести как доказательство и объяснить принцип «справочник + FK» на примере `Gender`.

---

## Шаг 0. Подготовка БД (до старта Python)

1. Открыть MySQL Workbench, выполнить `my.sql` → создаются таблицы `Service`, `ServicePhoto`, `Client`, `ClientService`, `Gender` и др.
2. Импортировать данные из ресурсов (`service_b_import.csv`, `client_b_import.txt`, `serviceclient_b_import.xlsx`) — это делается **разово** скриптом-загрузчиком на pandas (см. шаг 7) или прямо через Workbench `Table Data Import Wizard`.
3. Заполнить `Gender` вручную двумя строками (`M`/`Мужской`, `Ж`/`Женский`) — этого хватит для FK.

---

## Шаг 1. `db.py` — подключение и хелперы

Один файл с тремя функциями. Все остальные модули используют их.

```python
import mysql.connector

CFG = dict(host="localhost", user="root", password="root", database="salon")

def conn():
    return mysql.connector.connect(**CFG)

def fetch(sql, params=()):
    with conn() as c:
        cur = c.cursor(dictionary=True)
        cur.execute(sql, params)
        return cur.fetchall()

def query(sql, params=()):
    with conn() as c:
        cur = c.cursor()
        cur.execute(sql, params)
        c.commit()
        return cur.lastrowid
```

**Запомнить:** `fetch` → SELECT, возвращает список словарей; `query` → INSERT/UPDATE/DELETE, возвращает `lastrowid`. Параметры всегда передаются как кортеж — никаких f-строк в SQL (защита от SQL-инъекций).

---

## Шаг 2. `main.py` — каркас приложения

Главное окно — список услуг. Состояние режима держим в одной глобальной переменной `IS_ADMIN`.

```python
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from datetime import datetime, date, timedelta
import shutil, os, re
import db

IS_ADMIN = False
ADMIN_CODE = "0000"
IMG_DIR = "images"
os.makedirs(IMG_DIR, exist_ok=True)

root = tk.Tk()
root.title("Салон красоты")
root.geometry("1000x700")
```

Далее идут глобальные виджеты: `search_var`, `filter_var`, `sort_var`, `services_frame` (Canvas+Frame для скролла), `counter_label`.

---

## Шаг 3. Список услуг (центральный экран)

### 3.1 Верхняя панель управления
- `Entry` для поиска (биндим на `<KeyRelease>` → `reload()`).
- `Combobox` для фильтра скидки: значения `["Все","0-5","5-15","15-30","30-70","70-100"]`, `<<ComboboxSelected>>` → `reload()`.
- `Combobox` для сортировки: `["По возрастанию цены","По убыванию цены"]`.
- Кнопка «Войти как админ» / «Выйти» — переключает `IS_ADMIN`, перерисовывает UI.
- Кнопки **Добавить** / **Ближайшие записи** — видимы только при `IS_ADMIN`.

### 3.2 Загрузка данных — функция `reload()`

```python
def reload():
    rows = db.fetch("SELECT * FROM Service")
    q = search_var.get().lower()
    rows = [r for r in rows if q in (r["Title"] or "").lower()
                            or q in (r["Description"] or "").lower()]
    f = filter_var.get()
    if f != "Все":
        lo, hi = map(int, f.split("-"))
        rows = [r for r in rows if lo <= (r["Discount"] or 0)*100 < hi]
    # своя сортировка — НЕ встроенная в TreeView
    rev = sort_var.get().startswith("По убыванию")
    rows = sorted(rows, key=lambda r: float(r["Cost"]), reverse=rev)
    draw(rows)
    counter_label.config(text=f"{len(rows)} из {db.fetch('SELECT COUNT(*) c FROM Service')[0]['c']}")
```

**Важно:** сортировка реализована вручную через `sorted(...)`, как требует ТЗ.

### 3.3 Отрисовка карточек — функция `draw(rows)`

Очищаем `services_frame`, для каждой строки делаем `tk.Frame` с:

- миниатюрой (`ImageTk.PhotoImage`, размер 100×100),
- лейблом названия,
- ценой: если `Discount > 0` — две метки: старая (`overstrike`) и новая (`Cost*(1-Discount)`),
- длительностью в минутах (`DurationInSeconds // 60`),
- размером скидки.

Фон карточки — `#E8FFE8` если скидка > 0, иначе белый.

Если `IS_ADMIN`: добавляем три кнопки — **Изменить**, **Удалить**, **Записать клиента**.

**Хитрость с картинкой:** `PhotoImage` нужно сохранять в атрибут виджета (`lbl.img = photo`), иначе GC её соберёт и картинки исчезнут.

### 3.4 Удаление услуги

```python
def delete_service(sid):
    if db.fetch("SELECT 1 FROM ClientService WHERE ServiceID=%s LIMIT 1", (sid,)):
        return messagebox.showerror("Ошибка","Есть записи клиентов — удаление запрещено")
    db.query("DELETE FROM ServicePhoto WHERE ServiceID=%s",(sid,))
    db.query("DELETE FROM Service WHERE ID=%s",(sid,))
    reload()
```

---

## Шаг 4. Окно добавления/редактирования (`open_edit(sid=None)`)

Используем `tk.Toplevel`. Глобальный флаг `edit_win` блокирует повторное открытие:

```python
edit_win = None
def open_edit(sid=None):
    global edit_win
    if edit_win and edit_win.winfo_exists():
        return edit_win.lift()
    edit_win = tk.Toplevel(root)
    ...
```

Поля: ID (только для чтения, скрыт при добавлении), Title (Entry), Cost (Entry), DurationInSeconds (Entry — пользователь вводит **минуты**, при сохранении × 60), Discount (Entry, 0..1), Description (Text), MainImage (Label-превью + кнопка «Выбрать»).

Если `sid` задан — `SELECT * FROM Service WHERE ID=%s`, заполнить поля.

### 4.1 Валидация перед сохранением
- Title не пуст.
- Если новая услуга или Title изменился — `SELECT 1 FROM Service WHERE Title=%s AND ID<>%s` должен вернуть пусто (уникальность).
- `0 < duration_min <= 240` (4 часа).
- Cost > 0, 0 ≤ Discount ≤ 1.

### 4.2 Сохранение

```python
if sid is None:
    new_id = db.query("INSERT INTO Service(Title,Cost,DurationInSeconds,Description,Discount,MainImagePath) VALUES (%s,%s,%s,%s,%s,%s)",
                      (title,cost,dur*60,descr,disc,img_path))
    sid = new_id
else:
    db.query("UPDATE Service SET Title=%s,Cost=%s,DurationInSeconds=%s,Description=%s,Discount=%s,MainImagePath=%s WHERE ID=%s",
             (title,cost,dur*60,descr,disc,img_path,sid))
```

В конце — `reload()` главного окна и `edit_win.destroy()`.

### 4.3 Выбор главного изображения

```python
def pick_main():
    p = filedialog.askopenfilename(filetypes=[("Images","*.png *.jpg *.jpeg")])
    if not p: return
    dst = os.path.join(IMG_DIR, os.path.basename(p))
    shutil.copy(p, dst)
    main_img_var.set(dst)
    show_preview(dst)
```

---

## Шаг 5. Дополнительные фото (внутри окна редактирования)

Слева — список путей из `ServicePhoto WHERE ServiceID=sid`, отрисованных миниатюрами 60×60 + крестик «удалить».

```python
def add_photo():
    p = filedialog.askopenfilename(filetypes=[("Images","*.png *.jpg *.jpeg")])
    if not p or sid is None:  # для новой услуги сначала сохранить, затем добавлять
        return
    dst = os.path.join(IMG_DIR, os.path.basename(p))
    shutil.copy(p, dst)
    db.query("INSERT INTO ServicePhoto(ServiceID,PhotoPath) VALUES (%s,%s)",(sid,dst))
    refresh_photos()

def del_photo(pid):
    db.query("DELETE FROM ServicePhoto WHERE ID=%s",(pid,))
    refresh_photos()
```

---

## Шаг 6. Запись клиента на услугу (`open_booking(sid)`)

Окно `Toplevel`:
- Лейблы: название услуги и длительность в минутах.
- `Combobox` клиентов: `SELECT ID, CONCAT_WS(' ',LastName,FirstName,Patronymic) AS FIO FROM Client`.
- Дата — `DateEntry` из пакета `tkcalendar` (если нельзя ставить — обычный `Entry` с маской).
- Время начала — `Entry`, валидация по regex `^\d{1,2}:\d{2}$`, плюс `datetime.strptime(value, "%H:%M")`.
- Автовычисляемое время окончания — `start + timedelta(seconds=DurationInSeconds)`, обновляется на каждое изменение поля времени.
- Кнопка «Сохранить»: `INSERT INTO ClientService(ClientID,ServiceID,StartTime) VALUES (...)`.

---

## Шаг 7. Окно «Ближайшие записи» (`open_upcoming()`)

`Toplevel` со списком на сегодня и завтра:

```sql
SELECT cs.ID, s.Title, s.DurationInSeconds, cs.StartTime,
       c.LastName, c.FirstName, c.Patronymic, c.Email, c.Phone
FROM ClientService cs
JOIN Service s ON s.ID=cs.ServiceID
JOIN Client  c ON c.ID=cs.ClientID
WHERE DATE(cs.StartTime) IN (CURDATE(), CURDATE()+INTERVAL 1 DAY)
ORDER BY cs.StartTime
```

Для каждой записи отрисовываем строку. Время до начала:

```python
delta = row["StartTime"] - datetime.now()
mins = int(delta.total_seconds() // 60)
h, m = divmod(mins, 60)
text = f"{h} часов {m} минут"
color = "red" if mins < 60 else "black"
```

Автообновление каждые 30 секунд: `win.after(30000, refresh)`.

---

## Шаг 8. Импорт исходных данных (одноразовый скрипт `import.py`)

Не часть основного приложения, но необходимо для подготовки. Использует `pandas`:

```python
import pandas as pd, db
# Услуги: CSV с табуляцией / точкой с запятой — проверить разделитель
df = pd.read_csv("service_b_import.csv", sep=";", encoding="utf-8")
for _, r in df.iterrows():
    db.query("INSERT INTO Service(Title,Cost,DurationInSeconds,Description,Discount) VALUES (%s,%s,%s,%s,%s)",
             (r["Title"], r["Cost"], int(r["DurationInSeconds"]),
              r.get("Description"), r.get("Discount") or 0))
```

Аналогично для `client_b_import.txt` (это вероятно TSV) и записей `serviceclient_b_import.xlsx` (`pd.read_excel`).

---

## Шаг 9. Режим администратора

В шапке окна — кнопка «Режим админа». По клику открывается маленький `Toplevel` с `Entry` на код. Если `entry.get() == "0000"` → `IS_ADMIN = True`, перерисовать главное окно (показать кнопки «Добавить», «Ближайшие записи», у карточек — «Изменить»/«Удалить»/«Записать»). Иначе — `messagebox.showerror`.

---

## Критические файлы

- `main.py` — весь UI и обработчики
- `db.py` — обёртка над MySQL
- `import.py` — однократная загрузка `*_b_import.*` в базу
- `my.sql` — исходный скрипт схемы (из ресурсов)

---

## Проверка (как тестировать готовое приложение)

1. `pip install mysql-connector-python pillow pandas openpyxl tkcalendar`
2. В MySQL Workbench запустить `my.sql`, добавить `Gender('М','Мужской'), ('Ж','Женский')`.
3. `python import.py` — наполнить БД из ресурсов.
4. `python main.py` — открывается список услуг (клиентский режим, кнопок CRUD не видно).
5. Проверить:
   - поиск по названию работает в реальном времени;
   - фильтр скидки даёт правильные диапазоны (скидка 30% → попадает в `30-70`);
   - сортировка по цене вверх и вниз;
   - счётчик «X из Y» обновляется;
   - услуга со скидкой имеет светло-зелёный фон и перечёркнутую цену.
6. Войти как админ кодом `0000` — появляются кнопки.
7. Добавить услугу с дубликатом названия → ошибка. С длительностью 300 мин → ошибка.
8. Открыть окно редактирования, попытаться открыть второе — не должно открываться.
9. Добавить/удалить дополнительные фото.
10. Создать запись клиента на услугу — открыть «Ближайшие записи», проверить таймер и красный цвет если < 1ч.
11. Попытаться удалить услугу, на которую есть запись → запрет.

---

## Подробное пошаговое объяснение (для подготовки к экзамену)

После того как план будет утверждён, на этапе реализации сгенерируется отдельный документ `GUIDE.md` с:
- порядком набора кода блок за блоком,
- мнемоническими подсказками (что и почему),
- шаблонами для запоминания (как структурируется любое `Toplevel`-окно, как делается реактивная фильтрация),
- типичными ошибками и как их избежать.

Этот документ — главная ценность для подготовки к экзамену.

В `GUIDE.md` отдельным разделом будет «3НФ простыми словами»:
- что такое функциональная и транзитивная зависимость,
- как «на лету» проверить таблицу по трём правилам,
- почему справочники (`Gender`, `Tag`) — главный приём приведения к 3НФ,
- два-три типичных вопроса экзаменатора с готовыми ответами.
