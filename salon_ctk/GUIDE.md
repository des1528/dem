# GUIDE — Салон красоты на CustomTkinter

Этот гайд продолжает [salon/GUIDE.md](../salon/GUIDE.md): бизнес-логика и БД у нас те же. Разбираем **только** то, что меняется при переезде на CustomTkinter, и палитру М2.

---

## 1. Что такое CustomTkinter и зачем он нужен

`tkinter` — стандартный GUI Python, но виджеты выглядят как из 90-х. **CustomTkinter** (далее CTk) — это надстройка над tkinter с современным дизайном: закруглённые углы, hover-эффекты, нормальные тёмные/светлые темы. Все имена виджетов знакомые: `CTk`, `CTkFrame`, `CTkLabel`, `CTkButton`, `CTkEntry`, `CTkOptionMenu`, `CTkTextbox`, `CTkScrollableFrame`, `CTkToplevel`, `CTkImage`, `CTkFont`.

Установка:
```powershell
pip install customtkinter
```

В CTk **не нужно** знать `pack/grid/place` иначе — менеджеры геометрии те же, что в tkinter. Меняется только класс виджета.

---

## 2. Главные отличия от tkinter

| tkinter | CustomTkinter |
|---|---|
| `tk.Tk()` | `ctk.CTk()` |
| `tk.Frame(parent, bg="white")` | `ctk.CTkFrame(parent, fg_color="white")` |
| `tk.Label(...)`, параметр `bg=` | `ctk.CTkLabel(...)`, параметр `fg_color=` |
| `tk.Button(... bg=, fg=, activebackground=)` | `ctk.CTkButton(... fg_color=, text_color=, hover_color=, corner_radius=, height=)` |
| `ttk.Combobox(state="readonly")` | `ctk.CTkOptionMenu(values=[...])` |
| `tk.Text` | `ctk.CTkTextbox` |
| `Canvas + Frame + Scrollbar` ручная сборка | `ctk.CTkScrollableFrame` — одной строкой |
| `ImageTk.PhotoImage(img)` | `ctk.CTkImage(light_image=img, size=(w,h))` |
| Шрифт через кортеж `("Arial",12)` | `ctk.CTkFont(family="Times New Roman", size=13, weight="bold")` |
| `widget.config(...)` | `widget.configure(...)` |

**Главное правило:** `bg_color` это «прозрачный родительский фон», `fg_color` это «непрозрачный фон самого виджета». Запомни: `fg_color` ≠ цвет текста; цвет текста — `text_color`.

---

## 3. Палитра М2 — сдержанный вариант

Требования М2 жёсткие: должны присутствовать **все четыре** цвета. Но никто не заставляет красить ими всё подряд. Принцип:

> Один цвет — одна роль. Не больше 10–15 % площади экрана яркого цвета.

| Цвет | Где применить (сдержанно) |
|---|---|
| `#FFFFFF` | основной фон окна и большинства виджетов |
| `#7FFF00` (дополнительный фон) | декоративная полоса 3–4 px под шапкой |
| `#00FA9A` (целевое действие) | только кнопки «Сохранить», «Записать», «Добавить» |
| `#2E8B57` (брендовый, для скидки > 15 %) | заголовок, активные второстепенные кнопки, бордеры выделения, фон карточек со скидкой > 15 % |

Дополнительные «вспомогательные» цвета, **не противоречащие** М2:
- `#F6F8F6` — нейтральная подложка (выпадающие, плейсхолдер фото)
- `#D9DDD9` — рамки полей
- `#5A6660` — приглушённый текст (подписи, второстепенная информация)
- `#1F1F1F` — основной текст
- `#B71C1C` — индикатор срочности (бейдж «осталось < 1 ч»)

### 3.1 Почему `#7FFF00` — это лишь полоса, а не вся шапка

`#7FFF00` (chartreuse) — экстремально яркий цвет. Если им закрасить шапку 70 px высотой — глаза болят через минуту. Достаточно полосы 3–4 px:

```python
ctk.CTkFrame(parent, fg_color="#7FFF00", height=4, corner_radius=0).pack(fill="x")
```

Требование М2 «дополнительный фон» выполнено: цвет используется как фон, просто на узкой области.

---

## 4. Шрифт Times New Roman

CTk не наследует tkinter-кортежи. Создаём объекты `CTkFont`:

```python
F_TITLE  = ctk.CTkFont(family="Times New Roman", size=22, weight="bold")
F_HEAD   = ctk.CTkFont(family="Times New Roman", size=15, weight="bold")
F_NORMAL = ctk.CTkFont(family="Times New Roman", size=13)
F_SMALL  = ctk.CTkFont(family="Times New Roman", size=12)
```

И всем виджетам передаём `font=F_NORMAL` и т.д. Также есть модификаторы:
- `overstrike=True` — для перечёркивания старой цены,
- `underline=True` — для подчёркивания ссылок,
- `slant="italic"` — курсив.

---

## 5. Скроллируемый список — одна строка вместо пятнадцати

В обычном `tkinter` для скролла набора виджетов нужно:
```python
canvas = tk.Canvas(parent); sb = tk.Scrollbar(parent, command=canvas.yview)
inner = tk.Frame(canvas)
inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0,0), window=inner, anchor="nw")
canvas.configure(yscrollcommand=sb.set)
canvas.pack(side="left", fill="both", expand=True); sb.pack(side="right", fill="y")
```

В CTk то же самое — одна строка:
```python
list_frame = ctk.CTkScrollableFrame(parent, fg_color="white")
list_frame.pack(fill="both", expand=True)
```

И добавляешь карточки прямо в `list_frame.pack()`. Скроллбар появляется автоматически, как только содержимое не помещается.

---

## 6. Изображения без размытия

`ImageTk.PhotoImage` рисует попиксельно — на high-DPI экранах размывается. `CTkImage` хранит и светлую, и тёмную версии и масштабируется средствами CTk:

```python
from PIL import Image
img = Image.open(path); img.thumbnail((120, 120))
photo = ctk.CTkImage(light_image=img, size=img.size)
ctk.CTkLabel(parent, image=photo, text="").pack()
```

**Важно:** так же, как в tkinter, не теряй ссылку — `widget.image = photo` (или храни в любой переменной за пределами функции).

---

## 7. Карточка услуги — пошагово

Структура — три блока в одном `CTkFrame`:

```python
card = ctk.CTkFrame(list_frame, fg_color=bg, corner_radius=12,
                    border_width=1, border_color=border)
card.pack(fill="x", pady=6, padx=2)

# 1. Левая колонка: миниатюра в квадратной подложке
img_holder = ctk.CTkFrame(card, fg_color=BG_PANEL, corner_radius=10, width=134, height=134)
img_holder.pack(side="left", padx=14, pady=14); img_holder.pack_propagate(False)
ctk.CTkLabel(img_holder, image=ph, text="").pack(expand=True)

# 2. Средняя колонка: название, длительность, скидка, описание
info = ctk.CTkFrame(card, fg_color="transparent"); info.pack(side="left", fill="both", expand=True)
ctk.CTkLabel(info, text=r["Title"], font=F_HEAD, text_color=fg).pack(anchor="w")
# ... остальные строки

# 3. Правая колонка: цена и (опционально) перечёркнутая старая цена
price_box = ctk.CTkFrame(card, fg_color="transparent"); price_box.pack(side="right", padx=18)
```

**Ключевые приёмы:**

- `corner_radius=12` — мягкие закруглённые углы.
- `border_width=1, border_color=...` — тонкая рамка вместо тяжёлой 2-3 px.
- `fg_color="transparent"` — у внутренних фреймов, чтобы они «прозрачно» накладывались на родительскую карточку.
- `pack_propagate(False)` для квадрата под фото — иначе он схлопнется до размера содержимого.

---

## 8. Логика скидки > 15 %

В одном месте принимаем решение о цветах:

```python
disc = r["Discount"] or 0
if disc * 100 > 15:
    bg, fg, sub, border = BG_BRAND, TXT_LIGHT, "#D6E9DE", BG_BRAND_H
else:
    bg, fg, sub, border = BG_MAIN, TXT_DARK, TXT_MUTED, BORDER
```

Дальше все элементы карточки берут цвет из этих переменных. Преимущество: правка одного `if` меняет всю карточку.

> ТЗ М2: «Если размер скидки превышает 15%, в качестве фона необходимо применить цвет #2E8B57». В БД скидка — дробь от 0 до 1, поэтому сравниваем `disc * 100 > 15` (а не `disc > 0.15`, чтобы не путаться в дальнейшем).

---

## 9. Кнопки трёх классов

Чтобы интерфейс не выглядел как новогодняя ёлка, у нас три типа кнопок:

```python
# 1. Целевое действие (Сохранить, Записать, Добавить услугу)
ctk.CTkButton(... fg_color=BG_ACTION, text_color=TXT_DARK,
              hover_color=BG_ACTION_H, corner_radius=10, height=44)

# 2. Брендовая вторичная (Ближайшие записи)
ctk.CTkButton(... fg_color=BG_BRAND, text_color=TXT_LIGHT,
              hover_color=BG_BRAND_H, corner_radius=8, height=36)

# 3. Outline / нейтральная (Войти как админ, Выбрать файл, Изменить, Удалить)
ctk.CTkButton(... fg_color=BG_PANEL, text_color=BG_BRAND,
              hover_color="#E5EBE6", border_color=BG_BRAND, border_width=1,
              corner_radius=8, height=36)
```

На экране одновременно должна быть **только одна** яркая зелёная кнопка (целевое действие). Если их две — пользователь не понимает, на что нажимать. Это «закон одного главного действия» Material Design.

---

## 10. Toplevel-окна — единый шаблон

Все три модалки (редактирование, запись, ближайшие) построены по одной схеме:

```python
w = ctk.CTkToplevel(root); w.title("...")
w.geometry("..."); w.configure(fg_color=BG_MAIN)
w.transient(root); w.lift(); w.focus()

# 1. Заголовок модалки (брендовый цвет на белом)
hd = ctk.CTkFrame(w, fg_color=BG_MAIN, height=56, corner_radius=0)
hd.pack(fill="x"); hd.pack_propagate(False)
ctk.CTkLabel(hd, text="...", font=F_HEAD, text_color=BG_BRAND).pack(side="left", padx=20)

# 2. Полоска #7FFF00 — единственный обязательный элемент палитры
ctk.CTkFrame(w, fg_color=BG_ACCENT, height=3, corner_radius=0).pack(fill="x")

# 3. Содержимое
# 4. Кнопка «Сохранить» в #00FA9A снизу
```

`w.transient(root)` — модалка не появляется отдельной кнопкой в Windows-таскбаре.
`w.lift()` + `w.focus()` — окно выходит наверх и получает фокус сразу.

---

## 11. Запрет на второе окно редактирования

Идентично оригинальному `salon/`:
```python
edit_win = None  # глобально

def open_edit(sid):
    global edit_win
    if edit_win and edit_win.winfo_exists():
        edit_win.lift(); return
    edit_win = ctk.CTkToplevel(root)
    ...
```

`winfo_exists()` — корректно работает и с `CTkToplevel`.

---

## 12. Автообновление «Ближайших записей»

```python
def refresh():
    # ... перерисовать карточки
    w.after(30_000, refresh)
refresh()
```

`.after()` — метод стандартного tkinter, в CTk наследуется без изменений. `30_000` мс = 30 секунд (требование ТЗ).

---

## 13. Чек-лист перед сдачей

- [ ] Установлен `customtkinter` (`pip show customtkinter`).
- [ ] Запущен `init_demo.sql` — БД `salon` есть, заполнена тестовыми данными.
- [ ] При запуске видишь шапку с надписью «Салон красоты» в `#2E8B57` и тонкой `#7FFF00`-полосой под ней.
- [ ] Карточка услуги «Spa-уход за лицом» (скидка 50%) — целиком `#2E8B57` с белым текстом.
- [ ] Карточки без скидки — белые с тонкой серой рамкой.
- [ ] Поиск, фильтр, сортировка работают в реальном времени.
- [ ] Под админом (`0000`) появляются кнопки «Добавить услугу» (целевая зелёная), «Ближайшие записи» (брендовая), «Изменить»/«Удалить» (outline) в карточках.
- [ ] В «Ближайших записях» бейдж становится красным, когда осталось < 1 часа.
- [ ] При нажатии «Записать» открывается модалка с шапкой «Запись на услугу» в `#2E8B57` и `#7FFF00`-полосой.
- [ ] Времена «Окончание» пересчитываются по мере ввода времени начала.
- [ ] Все надписи на русском, без эмодзи и без жаргонизмов.
- [ ] Шрифт Times New Roman везде.

---

## 14. Что повторить за день до экзамена

1. **Шаблон модалки** (заголовок + полоса + содержимое + Сохранить).
2. **Три класса кнопок** — на одном экране только одна целевая.
3. **`CTkScrollableFrame`** — простая замена ручному Canvas.
4. **`CTkImage`** + хранение ссылки.
5. **Палитра М2 + сдержанные вспомогательные** — список ровно из 8 цветов.
6. Решение «скидка > 15 %» одним `if`, а потом все цвета берутся из переменных.
7. `w.after(30000, refresh)` — для автообновления.

Удачи на экзамене.
