# SETUP — пошаговый запуск всех проектов

Гайд для Windows 10/11. Все команды — PowerShell. Время полной установки с нуля ~15 минут.

---

## 0. Что мы устанавливаем

| Компонент | Зачем | Откуда |
|---|---|---|
| Python 3.10+ | язык приложений | [python.org/downloads](https://www.python.org/downloads/) |
| MySQL Server 8.x + Workbench | СУБД | [dev.mysql.com/downloads/installer](https://dev.mysql.com/downloads/installer/) |
| Git | склонировать репо | [git-scm.com](https://git-scm.com/) |

> Если что-то из этого уже стоит — пропускай шаг.

---

## 1. Установка Python

1. Скачать **Python 3.12** (или новее) с [python.org](https://www.python.org/downloads/).
2. В установщике **обязательно** поставить галочку **«Add python.exe to PATH»**.
3. Проверить:
   ```powershell
   python --version
   pip --version
   ```
   Должны выводить версии.

---

## 2. Установка MySQL

1. Скачать **MySQL Installer for Windows** с [dev.mysql.com/downloads/installer](https://dev.mysql.com/downloads/installer/).
2. Выбрать тип установки **Developer Default** → ставит MySQL Server + Workbench + Connector.
3. На шаге настройки сервера:
   - Authentication Method → **Use Legacy Authentication** (проще, не требует SHA256).
   - Root password — придумай и **запомни**. В наших скриптах по умолчанию `root` / `root`; если поставишь другой — поправь в `db.py` каждого проекта.
4. Запустить MySQL Workbench → подключиться к `Local instance MySQL` под `root`.
5. Проверка:
   ```powershell
   mysql --version
   ```

---

## 3. Клонирование репозитория

```powershell
cd C:\
git clone https://github.com/des1528/dem.git demka
cd demka
```

---

## 4. Виртуальное окружение Python

**Зачем:** изолировать зависимости проекта от системы. Без venv `pip install` ставит пакеты глобально — это может ломать другие проекты.

```powershell
# Создать venv в корне demka
python -m venv .venv

# Активировать
.\.venv\Scripts\Activate.ps1
```

> **Ошибка «выполнение сценариев отключено»?**
> Открой PowerShell **от администратора** и один раз выполни:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```
> Потом перезапусти обычный PowerShell.

После активации в начале строки появится `(.venv)`. Все `pip` и `python` внутри `.venv` идут только в эту папку.

**Деактивировать** (когда закончил):
```powershell
deactivate
```

---

## 5. Установка зависимостей

В активированном venv:

```powershell
pip install --upgrade pip
pip install mysql-connector-python pillow openpyxl pandas python-docx tkcalendar
```

Что для чего:

| Пакет | Используется в | Зачем |
|---|---|---|
| `mysql-connector-python` | salon/shoes/pets | подключение к MySQL |
| `pillow` (PIL) | salon/shoes/pets | работа с изображениями, captcha |
| `openpyxl` | shoes/pets import_data | чтение `.xlsx` ресурсов |
| `pandas` | salon import_data | чтение `.csv/.xlsx` |
| `python-docx` | variativ | генерация Word-руководства |
| `tkcalendar` | salon | виджет выбора даты |

Проверка (всё должно импортироваться без ошибок):
```powershell
python -c "import mysql.connector, PIL, openpyxl, pandas, docx, tkcalendar; print('OK')"
```

---

## 6. Создание баз данных

Для каждого проекта есть `init_demo.sql` — он создаёт БД и сразу наполняет её тестовыми данными.

### Через MySQL Workbench (рекомендую)
1. Workbench → подключиться к `Local instance MySQL`.
2. `File` → `Open SQL Script` → выбрать файл (например `C:\demka\salon\init_demo.sql`).
3. Нажать молнию ⚡ (Execute, или `Ctrl+Shift+Enter`) — выполнить весь скрипт.
4. Внизу должна появиться таблица «Услуг: 12, Клиентов: 7, ...» — значит данные залились.
5. Повторить для `shoes\init_demo.sql` и `pets\init_demo.sql`.

### Или через CLI
```powershell
mysql -u root -p < C:\demka\salon\init_demo.sql
mysql -u root -p < C:\demka\shoes\init_demo.sql
mysql -u root -p < C:\demka\pets\init_demo.sql
```

> **Пароль root отличается от `root`?**
> Открой `C:\demka\salon\db.py` (и аналогично `shoes\db.py`, `pets\db.py`) и поправь:
> ```python
> CFG = dict(host="localhost", user="root", password="ТВОЙ_ПАРОЛЬ", database="salon")
> ```

---

## 7. Запуск проектов

### 7.1 Салон красоты (salon/)

```powershell
cd C:\demka\salon
python main.py
```

Что увидеть:
- Список 12 услуг с миниатюрами (заглушки, если фото не подгрузил).
- В шапке: поиск, фильтр скидки, сортировка.
- Снизу: счётчик `12 из 12`.
- Кнопка «Войти как админ» → ввод кода **`0000`** → появляются кнопки «+ Услуга», «Ближайшие записи», «Изменить» / «Удалить» в карточках.
- «Ближайшие записи» → должны показаться 4 записи (сегодня и завтра), у некоторых таймер красный (< 1 часа).

### 7.2 Магазин обуви (shoes/)

```powershell
cd C:\demka\shoes
python main.py
```

Окно входа. Логины:
- Администратор: `admin@shop.ru` / `admin123`
- Менеджер: `manager@shop.ru` / `manager123`
- Клиент: `client@shop.ru` / `client123`
- Гость: кнопка «Войти как гость»

Под админом доступны: «+ Товар», «Заказы», «Изм.» / «Удал.» в карточках. Карточка товара `A234T5` (скидка 50%) — тёмно-зелёная, товар `S010N1` (остаток 0) — серая.

### 7.3 Товары для животных (pets/)

```powershell
cd C:\demka\pets
python main.py
```

Логины те же, но с доменом `@pets.ru`. Особенности:
- После **первой** неудачи логина появляется **captcha** (4 символа, шум, перечёркивание).
- Неудача с captcha → блокировка на **10 секунд**.
- Попробовать удалить товар `A001` (поводок, остаток 0) — он не в заказе, удалится. Товары 1, 2, 4, 7, 8 — в заказах, удаление запрещено.

### 7.4 Тесты библиотеки

```powershell
cd C:\demka\pets
python -m unittest test_lib -v
```

Должно быть `Ran 10 tests in 0.001s — OK`.

### 7.5 Генерация руководства пользователя (variativ/)

```powershell
cd C:\demka\variativ
python build_userguide.py
```

Появится `РУКОВОДСТВО_ПОЛЬЗОВАТЕЛЯ.docx`. Открыть в Word → F9 на оглавлении (для обновления) → вставить три скриншота на места «(Рисунок N — ...)» → сохранить.

### 7.6 WPF-эталон (Demo2026/)

Это **C#-проект**, не Python. Если хочешь его запустить:
1. Установить **Visual Studio 2022 Community** ([visualstudio.microsoft.com](https://visualstudio.microsoft.com/)) с компонентом «.NET desktop development».
2. Установить **SQL Server Express** (через тот же MySQL Installer не получится — это другая СУБД от Microsoft).
3. Восстановить базу из `Demo2026\ALLDATABASE.sql` через SSMS.
4. Открыть `Demo2026\GenaBukinShop2026\GenaBukinShop2026.sln` в Visual Studio → F5.
5. В `DbManager.cs` поправить строку подключения под своё имя сервера.

Если SQL Server и VS ставить лень — этот проект просто как референс «как делается на C#».

---

## 8. Типичные проблемы

| Симптом | Что проверить |
|---|---|
| `mysql.connector.errors.InterfaceError: 2003: Can't connect to MySQL server on 'localhost'` | MySQL Server не запущен. Win+R → `services.msc` → найти `MySQL80` (или похожее) → Start. |
| `Access denied for user 'root'@'localhost'` | Пароль в `db.py` не совпадает с тем, что задали при установке MySQL. |
| `ModuleNotFoundError: No module named 'mysql'` | venv не активирован, либо ставили пакеты не в venv. |
| `Unknown database 'salon'` | Не запустили `init_demo.sql` в Workbench. |
| `ImportError: cannot import name 'ImageTk' from 'PIL'` | Поставлен `PIL` вместо `pillow`. Удалить и переставить: `pip uninstall PIL; pip install pillow`. |
| `_tkinter.TclError: couldn't recognize data` | Картинка битая. Положи в проект `picture.png` (есть в `_extracted/pets/...`) — он используется как заглушка. |
| Не работает `Activate.ps1` | См. раздел 4 про `Set-ExecutionPolicy`. |
| Кириллица в консоли превращается в `???` | В PowerShell выполни `chcp 65001` перед запуском Python. |

---

## 9. Быстрая шпаргалка «с нуля до работающего salon/»

```powershell
# 1. Один раз — установить Python и MySQL (см. шаги 1-2)

# 2. Клонировать
cd C:\
git clone https://github.com/des1528/dem.git demka
cd demka

# 3. Создать и активировать venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 4. Поставить зависимости
pip install mysql-connector-python pillow openpyxl pandas python-docx tkcalendar

# 5. Создать БД (в Workbench: открыть init_demo.sql → ⚡)
#    или из CLI:
mysql -u root -proot < salon\init_demo.sql

# 6. Запустить
cd salon
python main.py
```

Готово.
