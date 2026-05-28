import os
import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
from datetime import date
from tkcalendar import DateEntry
import db

# paths
ROOT = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(ROOT, "resources")
PH = os.path.join(RES, "picture.png")
ICON = os.path.join(RES, "icon.ico")
LOGO = os.path.join(RES, "logo.png")

# style
BG_MAIN = "#FFFFFF"
BG_SOFT = "#F5DEB3"
BG_ACCENT = "#DEB887"
BG_DISCOUNT = "#FFDEAD"
BG_OUT = "#ADD8E6"
TXT_DARK = "#3B2A12"
TXT_RED = "#B71C1C"
FONT_NAME = "Arial"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# state
session = {"user": None, "role": None}
edit_win = None
order_edit_win = None


def font(sz, bold=False):
    return ctk.CTkFont(family=FONT_NAME, size=sz, weight="bold" if bold else "normal")


def ctk_image(path, w, h):
    try:
        img = Image.open(path)
    except Exception:
        img = Image.open(PH)
    return ctk.CTkImage(light_image=img, dark_image=img, size=(w, h))


def set_window_icon(win):
    try:
        win.iconbitmap(ICON)
    except Exception:
        pass


# header
def make_header(parent, title, on_back=None, on_logout=None):
    bar = ctk.CTkFrame(parent, fg_color=BG_SOFT, height=70, corner_radius=0)
    bar.pack(fill="x")
    bar.pack_propagate(False)
    try:
        logo_img = ctk_image(LOGO, 180, 50)
        ctk.CTkLabel(bar, image=logo_img, text="", fg_color=BG_SOFT).pack(side="left", padx=16)
    except Exception:
        pass
    ctk.CTkLabel(bar, text=title, font=font(20, True), text_color=TXT_DARK, fg_color=BG_SOFT).pack(side="left", padx=10)
    right = ctk.CTkFrame(bar, fg_color=BG_SOFT)
    right.pack(side="right", padx=14)
    if session["user"]:
        ctk.CTkLabel(right, text=session["user"]["fio"], font=font(13, True), text_color=TXT_DARK, fg_color=BG_SOFT).pack(side="right", padx=10)
        ctk.CTkLabel(right, text=session["role"], font=font(11), text_color=TXT_DARK, fg_color=BG_SOFT).pack(side="right", padx=10)
    if on_back:
        ctk.CTkButton(right, text="Назад", width=90, fg_color=BG_ACCENT, hover_color="#C9A26F", text_color=TXT_DARK, font=font(12, True), command=on_back).pack(side="right", padx=4)
    if on_logout:
        ctk.CTkButton(right, text="Выход", width=90, fg_color=BG_ACCENT, hover_color="#C9A26F", text_color=TXT_DARK, font=font(12, True), command=on_logout).pack(side="right", padx=4)


def clear(win):
    for w in win.winfo_children():
        w.destroy()


# login
def login_screen(root):
    clear(root)
    root.title("МирИгрушек — Вход")
    set_window_icon(root)
    root.configure(fg_color=BG_MAIN)

    outer = ctk.CTkFrame(root, fg_color=BG_MAIN)
    outer.pack(expand=True, fill="both")

    card = ctk.CTkFrame(outer, fg_color=BG_MAIN, border_color=BG_ACCENT, border_width=2, corner_radius=12)
    card.place(relx=0.5, rely=0.5, anchor="center")

    try:
        logo_img = ctk_image(LOGO, 260, 70)
        ctk.CTkLabel(card, image=logo_img, text="", fg_color=BG_MAIN).pack(pady=(28, 8), padx=40)
    except Exception:
        pass

    ctk.CTkLabel(card, text="Авторизация", font=font(22, True), text_color=TXT_DARK, fg_color=BG_MAIN).pack(pady=(4, 18), padx=40)

    ctk.CTkLabel(card, text="Логин", font=font(12), text_color=TXT_DARK, fg_color=BG_MAIN, anchor="w").pack(fill="x", padx=40)
    login_e = ctk.CTkEntry(card, width=320, font=font(13), fg_color=BG_MAIN, border_color=BG_ACCENT, text_color=TXT_DARK)
    login_e.pack(padx=40, pady=(2, 10))

    ctk.CTkLabel(card, text="Пароль", font=font(12), text_color=TXT_DARK, fg_color=BG_MAIN, anchor="w").pack(fill="x", padx=40)
    pass_e = ctk.CTkEntry(card, width=320, show="•", font=font(13), fg_color=BG_MAIN, border_color=BG_ACCENT, text_color=TXT_DARK)
    pass_e.pack(padx=40, pady=(2, 18))

    def do_login():
        l, p = login_e.get().strip(), pass_e.get().strip()
        if not l or not p:
            messagebox.showwarning("Внимание", "Введите логин и пароль для входа в систему.")
            return
        rows = db.fetch(
            "SELECT u.id, u.fio, u.login, r.name AS role FROM User u JOIN Role r ON r.id=u.role_id WHERE u.login=%s AND u.password=%s",
            (l, p),
        )
        if not rows:
            messagebox.showerror("Ошибка входа", "Неверный логин или пароль. Проверьте введённые данные и попробуйте снова.")
            return
        session["user"] = rows[0]
        session["role"] = rows[0]["role"]
        main_screen(root)

    def guest():
        session["user"] = None
        session["role"] = "Гость"
        main_screen(root)

    ctk.CTkButton(card, text="Войти", width=320, height=42, fg_color=BG_ACCENT, hover_color="#C9A26F", text_color=TXT_DARK, font=font(14, True), command=do_login).pack(padx=40, pady=4)
    ctk.CTkButton(card, text="Войти как гость", width=320, height=38, fg_color=BG_MAIN, hover_color=BG_SOFT, border_color=BG_ACCENT, border_width=2, text_color=TXT_DARK, font=font(13), command=guest).pack(padx=40, pady=(4, 28))


# logout
def logout(root):
    session["user"] = None
    session["role"] = None
    login_screen(root)


# main
def main_screen(root):
    clear(root)
    role = session["role"]
    root.title(f"МирИгрушек — Каталог ({role})")
    set_window_icon(root)
    root.configure(fg_color=BG_MAIN)

    make_header(root, "Каталог товаров", on_logout=lambda: logout(root))

    # toolbar
    can_filter = role in ("Менеджер", "Администратор")
    can_admin = role == "Администратор"
    can_orders = role in ("Менеджер", "Администратор")

    tools = ctk.CTkFrame(root, fg_color=BG_MAIN)
    tools.pack(fill="x", padx=16, pady=10)

    search_var = ctk.StringVar()
    sort_var = ctk.StringVar(value="Без сортировки")
    sup_var = ctk.StringVar(value="Все поставщики")

    if can_filter:
        ctk.CTkLabel(tools, text="Поиск:", font=font(12), text_color=TXT_DARK, fg_color=BG_MAIN).pack(side="left")
        ctk.CTkEntry(tools, width=240, textvariable=search_var, font=font(12), fg_color=BG_MAIN, border_color=BG_ACCENT, text_color=TXT_DARK).pack(side="left", padx=(6, 14))

        ctk.CTkLabel(tools, text="Сортировка:", font=font(12), text_color=TXT_DARK, fg_color=BG_MAIN).pack(side="left")
        ctk.CTkOptionMenu(
            tools,
            variable=sort_var,
            values=["Без сортировки", "Цена ↑", "Цена ↓", "Количество ↑", "Количество ↓"],
            fg_color=BG_ACCENT,
            button_color=BG_ACCENT,
            button_hover_color="#C9A26F",
            text_color=TXT_DARK,
            font=font(12),
        ).pack(side="left", padx=(6, 14))

        suppliers = ["Все поставщики"] + [r["name"] for r in db.fetch("SELECT name FROM Supplier ORDER BY name")]
        ctk.CTkLabel(tools, text="Поставщик:", font=font(12), text_color=TXT_DARK, fg_color=BG_MAIN).pack(side="left")
        ctk.CTkOptionMenu(
            tools,
            variable=sup_var,
            values=suppliers,
            fg_color=BG_ACCENT,
            button_color=BG_ACCENT,
            button_hover_color="#C9A26F",
            text_color=TXT_DARK,
            font=font(12),
        ).pack(side="left", padx=(6, 14))

    if can_admin:
        ctk.CTkButton(tools, text="Добавить товар", width=160, fg_color=BG_ACCENT, hover_color="#C9A26F", text_color=TXT_DARK, font=font(12, True), command=lambda: open_product_edit(root, None, reload_list)).pack(side="right", padx=4)
    if can_orders:
        ctk.CTkButton(tools, text="Заказы", width=120, fg_color=BG_ACCENT, hover_color="#C9A26F", text_color=TXT_DARK, font=font(12, True), command=lambda: orders_screen(root)).pack(side="right", padx=4)

    # list
    list_frame = ctk.CTkScrollableFrame(root, fg_color=BG_MAIN)
    list_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    def load():
        rows = db.fetch(
            """
            SELECT p.article, p.name, c.name AS category, p.description,
                   m.name AS manufacturer, s.name AS supplier,
                   p.price, u.name AS unit, p.stock, p.discount, p.photo
            FROM Product p
            JOIN Category c ON c.id=p.category_id
            JOIN Manufacturer m ON m.id=p.manufacturer_id
            JOIN Supplier s ON s.id=p.supplier_id
            JOIN Unit u ON u.id=p.unit_id
            """
        )
        q = search_var.get().strip().lower()
        if q:
            rows = [r for r in rows if any(q in str(r[k]).lower() for k in ("article", "name", "category", "description", "manufacturer", "supplier", "unit"))]
        sv = sup_var.get()
        if sv and sv != "Все поставщики":
            rows = [r for r in rows if r["supplier"] == sv]
        sk = sort_var.get()
        if sk == "Цена ↑":
            rows.sort(key=lambda r: float(r["price"]))
        elif sk == "Цена ↓":
            rows.sort(key=lambda r: float(r["price"]), reverse=True)
        elif sk == "Количество ↑":
            rows.sort(key=lambda r: int(r["stock"]))
        elif sk == "Количество ↓":
            rows.sort(key=lambda r: int(r["stock"]), reverse=True)
        return rows

    def reload_list(*_):
        for w in list_frame.winfo_children():
            w.destroy()
        rows = load()
        if not rows:
            ctk.CTkLabel(list_frame, text="Товары не найдены.", font=font(14), text_color=TXT_DARK, fg_color=BG_MAIN).pack(pady=40)
            return
        for r in rows:
            draw_card(list_frame, r)

    def draw_card(parent, r):
        out = int(r["stock"]) == 0
        disc = int(r["discount"])
        if out:
            bg = BG_OUT
        elif disc > 17:
            bg = BG_DISCOUNT
        else:
            bg = BG_MAIN
        card = ctk.CTkFrame(parent, fg_color=bg, border_color=BG_ACCENT, border_width=1, corner_radius=8)
        card.pack(fill="x", pady=6)

        photo_path = os.path.join(RES, r["photo"]) if r["photo"] else PH
        if not os.path.exists(photo_path):
            photo_path = PH
        img = ctk_image(photo_path, 150, 100)
        ctk.CTkLabel(card, image=img, text="", fg_color=bg).grid(row=0, column=0, rowspan=4, padx=14, pady=12)

        ctk.CTkLabel(card, text=r["name"], font=font(14, True), text_color=TXT_DARK, fg_color=bg, anchor="w", wraplength=520, justify="left").grid(row=0, column=1, sticky="w", padx=8, pady=(10, 0))
        ctk.CTkLabel(card, text=f"Артикул: {r['article']}    Категория: {r['category']}", font=font(11), text_color=TXT_DARK, fg_color=bg, anchor="w").grid(row=1, column=1, sticky="w", padx=8)
        ctk.CTkLabel(card, text=f"Производитель: {r['manufacturer']}    Поставщик: {r['supplier']}", font=font(11), text_color=TXT_DARK, fg_color=bg, anchor="w").grid(row=2, column=1, sticky="w", padx=8)
        desc = (r["description"] or "")[:200]
        ctk.CTkLabel(card, text=desc, font=font(10), text_color=TXT_DARK, fg_color=bg, anchor="w", wraplength=520, justify="left").grid(row=3, column=1, sticky="w", padx=8, pady=(0, 10))

        # price
        price_box = ctk.CTkFrame(card, fg_color=bg)
        price_box.grid(row=0, column=2, rowspan=4, padx=16, pady=10, sticky="e")
        if disc > 0:
            final = float(r["price"]) * (100 - disc) / 100
            strike = ctk.CTkFont(family=FONT_NAME, size=12, weight="bold", overstrike=True)
            ctk.CTkLabel(price_box, text=f"{float(r['price']):.2f} руб.", font=strike, text_color=TXT_RED, fg_color=bg).pack(anchor="e")
            ctk.CTkLabel(price_box, text=f"{final:.2f} руб.", font=font(16, True), text_color=TXT_DARK, fg_color=bg).pack(anchor="e")
            ctk.CTkLabel(price_box, text=f"скидка {disc}%", font=font(11), text_color=TXT_DARK, fg_color=bg).pack(anchor="e")
        else:
            ctk.CTkLabel(price_box, text=f"{float(r['price']):.2f} руб.", font=font(16, True), text_color=TXT_DARK, fg_color=bg).pack(anchor="e")
        ctk.CTkLabel(price_box, text=f"На складе: {r['stock']} {r['unit']}", font=font(11), text_color=TXT_DARK, fg_color=bg).pack(anchor="e")

        if can_admin:
            btns = ctk.CTkFrame(card, fg_color=bg)
            btns.grid(row=0, column=3, rowspan=4, padx=10, pady=10, sticky="e")
            ctk.CTkButton(btns, text="Редактировать", width=140, fg_color=BG_ACCENT, hover_color="#C9A26F", text_color=TXT_DARK, font=font(11, True), command=lambda a=r["article"]: open_product_edit(root, a, reload_list)).pack(pady=3)
            ctk.CTkButton(btns, text="Удалить", width=140, fg_color=BG_MAIN, hover_color=BG_SOFT, border_color=BG_ACCENT, border_width=2, text_color=TXT_DARK, font=font(11, True), command=lambda a=r["article"]: delete_product(a, reload_list)).pack(pady=3)

    if can_filter:
        search_var.trace_add("write", lambda *_: reload_list())
        sort_var.trace_add("write", lambda *_: reload_list())
        sup_var.trace_add("write", lambda *_: reload_list())

    reload_list()


# delete
def delete_product(article, reload_cb):
    used = db.fetch("SELECT id FROM `Order` WHERE article LIKE %s", (f"%{article}%",))
    if used:
        messagebox.showerror("Удаление невозможно", f"Товар «{article}» присутствует в заказах и не может быть удалён. Сначала удалите соответствующие заказы.")
        return
    if not messagebox.askyesno("Подтверждение удаления", f"Вы действительно хотите удалить товар «{article}»? Действие необратимо."):
        return
    row = db.fetch("SELECT photo FROM Product WHERE article=%s", (article,))
    db.query("DELETE FROM Product WHERE article=%s", (article,))
    if row and row[0]["photo"]:
        f = os.path.join(RES, row[0]["photo"])
        if os.path.exists(f) and row[0]["photo"] not in ("picture.png", "1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg", "6.jpg", "7.jpg", "8.jpg", "9.jpg", "10.jpg"):
            try:
                os.remove(f)
            except Exception:
                pass
    reload_cb()


# product
def open_product_edit(root, article, reload_cb):
    global edit_win
    if edit_win is not None and edit_win.winfo_exists():
        edit_win.lift()
        edit_win.focus()
        return

    w = ctk.CTkToplevel(root)
    w.title("Редактирование товара" if article else "Добавление товара")
    w.geometry("640x720")
    w.configure(fg_color=BG_MAIN)
    set_window_icon(w)
    w.transient(root)
    w.grab_set()

    edit_win = w

    bar = ctk.CTkFrame(w, fg_color=BG_SOFT, height=56, corner_radius=0)
    bar.pack(fill="x")
    bar.pack_propagate(False)
    ctk.CTkLabel(bar, text=("Редактирование товара" if article else "Добавление товара"), font=font(18, True), text_color=TXT_DARK, fg_color=BG_SOFT).pack(side="left", padx=20)

    body = ctk.CTkScrollableFrame(w, fg_color=BG_MAIN)
    body.pack(fill="both", expand=True, padx=20, pady=10)

    cats = db.fetch("SELECT id, name FROM Category ORDER BY name")
    sups = db.fetch("SELECT id, name FROM Supplier ORDER BY name")
    mans = db.fetch("SELECT id, name FROM Manufacturer ORDER BY name")
    units = db.fetch("SELECT id, name FROM Unit ORDER BY name")
    cur = None
    if article:
        rows = db.fetch("SELECT * FROM Product WHERE article=%s", (article,))
        if not rows:
            messagebox.showerror("Ошибка", "Товар не найден в базе данных.")
            w.destroy()
            return
        cur = rows[0]

    def field(label, val=""):
        ctk.CTkLabel(body, text=label, font=font(12), text_color=TXT_DARK, fg_color=BG_MAIN, anchor="w").pack(fill="x")
        e = ctk.CTkEntry(body, font=font(13), fg_color=BG_MAIN, border_color=BG_ACCENT, text_color=TXT_DARK)
        e.insert(0, val)
        e.pack(fill="x", pady=(2, 10))
        return e

    if article:
        ctk.CTkLabel(body, text="Артикул", font=font(12), text_color=TXT_DARK, fg_color=BG_MAIN, anchor="w").pack(fill="x")
        art_e = ctk.CTkEntry(body, font=font(13), fg_color=BG_SOFT, border_color=BG_ACCENT, text_color=TXT_DARK)
        art_e.insert(0, cur["article"])
        art_e.configure(state="disabled")
        art_e.pack(fill="x", pady=(2, 10))
    else:
        art_e = field("Артикул (например, ABCDEF)", "")

    name_e = field("Наименование", cur["name"] if cur else "")
    desc_e = field("Описание", cur["description"] if cur else "")
    price_e = field("Цена", str(cur["price"]) if cur else "")
    stock_e = field("Количество на складе", str(cur["stock"]) if cur else "")
    disc_e = field("Действующая скидка (%)", str(cur["discount"]) if cur else "0")

    def pick(items, key, fallback):
        if cur:
            for it in items:
                if it["id"] == cur[key]:
                    return it["name"]
        return fallback

    ctk.CTkLabel(body, text="Категория", font=font(12), text_color=TXT_DARK, fg_color=BG_MAIN, anchor="w").pack(fill="x")
    cat_var = ctk.StringVar(value=pick(cats, "category_id", cats[0]["name"] if cats else ""))
    ctk.CTkOptionMenu(body, variable=cat_var, values=[c["name"] for c in cats], fg_color=BG_ACCENT, button_color=BG_ACCENT, button_hover_color="#C9A26F", text_color=TXT_DARK, font=font(12)).pack(fill="x", pady=(2, 10))

    ctk.CTkLabel(body, text="Поставщик", font=font(12), text_color=TXT_DARK, fg_color=BG_MAIN, anchor="w").pack(fill="x")
    sup_var = ctk.StringVar(value=pick(sups, "supplier_id", sups[0]["name"] if sups else ""))
    ctk.CTkOptionMenu(body, variable=sup_var, values=[s["name"] for s in sups], fg_color=BG_ACCENT, button_color=BG_ACCENT, button_hover_color="#C9A26F", text_color=TXT_DARK, font=font(12)).pack(fill="x", pady=(2, 10))

    ctk.CTkLabel(body, text="Производитель", font=font(12), text_color=TXT_DARK, fg_color=BG_MAIN, anchor="w").pack(fill="x")
    man_var = ctk.StringVar(value=pick(mans, "manufacturer_id", mans[0]["name"] if mans else ""))
    ctk.CTkOptionMenu(body, variable=man_var, values=[m["name"] for m in mans], fg_color=BG_ACCENT, button_color=BG_ACCENT, button_hover_color="#C9A26F", text_color=TXT_DARK, font=font(12)).pack(fill="x", pady=(2, 10))

    ctk.CTkLabel(body, text="Единица измерения", font=font(12), text_color=TXT_DARK, fg_color=BG_MAIN, anchor="w").pack(fill="x")
    unit_var = ctk.StringVar(value=pick(units, "unit_id", units[0]["name"] if units else ""))
    ctk.CTkOptionMenu(body, variable=unit_var, values=[u["name"] for u in units], fg_color=BG_ACCENT, button_color=BG_ACCENT, button_hover_color="#C9A26F", text_color=TXT_DARK, font=font(12)).pack(fill="x", pady=(2, 10))

    # photo
    photo_state = {"file": cur["photo"] if cur else None, "tmp": None}
    ctk.CTkLabel(body, text="Фото товара", font=font(12), text_color=TXT_DARK, fg_color=BG_MAIN, anchor="w").pack(fill="x")
    photo_box = ctk.CTkFrame(body, fg_color=BG_MAIN)
    photo_box.pack(fill="x", pady=(2, 10))
    photo_lbl = ctk.CTkLabel(photo_box, text="", fg_color=BG_MAIN)
    photo_lbl.pack(side="left", padx=4)

    def refresh_photo():
        p = photo_state["tmp"] or (os.path.join(RES, photo_state["file"]) if photo_state["file"] else PH)
        if not os.path.exists(p):
            p = PH
        photo_lbl.configure(image=ctk_image(p, 150, 100))

    def pick():
        f = filedialog.askopenfilename(title="Выберите изображение", filetypes=[("Изображения", "*.jpg *.jpeg *.png *.bmp")])
        if f:
            photo_state["tmp"] = f
            refresh_photo()

    ctk.CTkButton(photo_box, text="Выбрать файл", width=160, fg_color=BG_ACCENT, hover_color="#C9A26F", text_color=TXT_DARK, font=font(12, True), command=pick).pack(side="left", padx=10)
    refresh_photo()

    def save():
        a = art_e.get().strip() if not article else cur["article"]
        nm = name_e.get().strip()
        ds = desc_e.get().strip()
        if not a or not nm:
            messagebox.showwarning("Ошибка ввода", "Заполните поля «Артикул» и «Наименование».")
            return
        try:
            pr = float(price_e.get().strip().replace(",", "."))
            if pr < 0:
                raise ValueError
        except Exception:
            messagebox.showwarning("Ошибка ввода", "Цена должна быть неотрицательным числом (допускаются сотые).")
            return
        try:
            st = int(stock_e.get().strip())
            if st < 0:
                raise ValueError
        except Exception:
            messagebox.showwarning("Ошибка ввода", "Количество на складе должно быть неотрицательным целым числом.")
            return
        try:
            dc = int(disc_e.get().strip() or "0")
            if dc < 0 or dc > 100:
                raise ValueError
        except Exception:
            messagebox.showwarning("Ошибка ввода", "Скидка — целое число от 0 до 100.")
            return
        cid = next(c["id"] for c in cats if c["name"] == cat_var.get())
        sid = next(s["id"] for s in sups if s["name"] == sup_var.get())
        mid = next(m["id"] for m in mans if m["name"] == man_var.get())
        uid = next(u["id"] for u in units if u["name"] == unit_var.get())

        # photo
        photo_name = photo_state["file"]
        if photo_state["tmp"]:
            try:
                img = Image.open(photo_state["tmp"])
                img.thumbnail((300, 200))
                ext = os.path.splitext(photo_state["tmp"])[1].lower() or ".jpg"
                photo_name = f"{a}{ext}"
                target = os.path.join(RES, photo_name)
                if photo_state["file"] and photo_state["file"] != photo_name:
                    old = os.path.join(RES, photo_state["file"])
                    if os.path.exists(old) and photo_state["file"] not in ("picture.png", "1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg", "6.jpg", "7.jpg", "8.jpg", "9.jpg", "10.jpg"):
                        try:
                            os.remove(old)
                        except Exception:
                            pass
                if img.mode != "RGB":
                    img = img.convert("RGB")
                img.save(target)
            except Exception as e:
                messagebox.showerror("Ошибка изображения", f"Не удалось обработать изображение: {e}")
                return

        try:
            if article:
                db.query(
                    "UPDATE Product SET name=%s, unit_id=%s, price=%s, supplier_id=%s, manufacturer_id=%s, category_id=%s, discount=%s, stock=%s, description=%s, photo=%s WHERE article=%s",
                    (nm, uid, pr, sid, mid, cid, dc, st, ds, photo_name, cur["article"]),
                )
            else:
                exists = db.fetch("SELECT article FROM Product WHERE article=%s", (a,))
                if exists:
                    messagebox.showwarning("Ошибка ввода", f"Товар с артикулом «{a}» уже существует.")
                    return
                db.query(
                    "INSERT INTO Product(article, name, unit_id, price, supplier_id, manufacturer_id, category_id, discount, stock, description, photo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (a, nm, uid, pr, sid, mid, cid, dc, st, ds, photo_name),
                )
        except Exception as e:
            messagebox.showerror("Ошибка БД", f"Не удалось сохранить товар:\n{e}")
            return
        messagebox.showinfo("Успех", "Данные товара сохранены.")
        w.destroy()
        reload_cb()

    actions = ctk.CTkFrame(w, fg_color=BG_MAIN, height=70)
    actions.pack(fill="x", side="bottom")
    ctk.CTkButton(actions, text="Сохранить", height=42, fg_color=BG_ACCENT, hover_color="#C9A26F", text_color=TXT_DARK, font=font(14, True), command=save).pack(side="right", padx=20, pady=14)
    ctk.CTkButton(actions, text="Отмена", height=42, fg_color=BG_MAIN, hover_color=BG_SOFT, border_color=BG_ACCENT, border_width=2, text_color=TXT_DARK, font=font(13), command=w.destroy).pack(side="right", padx=4, pady=14)

    def on_close():
        global edit_win
        edit_win = None
        w.destroy()

    w.protocol("WM_DELETE_WINDOW", on_close)


# orders
def orders_screen(root):
    clear(root)
    role = session["role"]
    can_admin = role == "Администратор"
    root.title("МирИгрушек — Заказы")
    set_window_icon(root)
    root.configure(fg_color=BG_MAIN)

    make_header(root, "Заказы", on_back=lambda: main_screen(root), on_logout=lambda: logout(root))

    tools = ctk.CTkFrame(root, fg_color=BG_MAIN)
    tools.pack(fill="x", padx=16, pady=10)
    if can_admin:
        ctk.CTkButton(tools, text="Добавить заказ", width=160, fg_color=BG_ACCENT, hover_color="#C9A26F", text_color=TXT_DARK, font=font(12, True), command=lambda: open_order_edit(root, None, reload_orders)).pack(side="right", padx=4)

    list_frame = ctk.CTkScrollableFrame(root, fg_color=BG_MAIN)
    list_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    def reload_orders(*_):
        for w in list_frame.winfo_children():
            w.destroy()
        rows = db.fetch(
            """
            SELECT o.id, o.article, s.name AS status, p.address AS pickup,
                   u.fio AS client, o.order_date, o.delivery_date, o.pickup_code
            FROM `Order` o
            JOIN OrderStatus s ON s.id=o.status_id
            JOIN PickupPoint p ON p.id=o.pickup_id
            LEFT JOIN User u ON u.id=o.client_id
            ORDER BY o.id
            """
        )
        if not rows:
            ctk.CTkLabel(list_frame, text="Заказов нет.", font=font(14), text_color=TXT_DARK, fg_color=BG_MAIN).pack(pady=40)
            return
        for r in rows:
            draw_order(list_frame, r)

    def draw_order(parent, r):
        card = ctk.CTkFrame(parent, fg_color=BG_MAIN, border_color=BG_ACCENT, border_width=1, corner_radius=8)
        card.pack(fill="x", pady=6)
        ctk.CTkLabel(card, text=f"Заказ № {r['id']}", font=font(15, True), text_color=TXT_DARK, fg_color=BG_MAIN, anchor="w").grid(row=0, column=0, sticky="w", padx=14, pady=(10, 0))
        ctk.CTkLabel(card, text=f"Статус: {r['status']}", font=font(12, True), text_color=TXT_DARK, fg_color=BG_SOFT, corner_radius=6).grid(row=0, column=1, sticky="e", padx=14, pady=(10, 0))
        ctk.CTkLabel(card, text=f"Артикул заказа: {r['article']}", font=font(12), text_color=TXT_DARK, fg_color=BG_MAIN, anchor="w", wraplength=600, justify="left").grid(row=1, column=0, columnspan=2, sticky="w", padx=14)
        ctk.CTkLabel(card, text=f"Клиент: {r['client'] or '—'}", font=font(11), text_color=TXT_DARK, fg_color=BG_MAIN, anchor="w").grid(row=2, column=0, sticky="w", padx=14)
        ctk.CTkLabel(card, text=f"Код получения: {r['pickup_code'] or '—'}", font=font(11), text_color=TXT_DARK, fg_color=BG_MAIN, anchor="e").grid(row=2, column=1, sticky="e", padx=14)
        ctk.CTkLabel(card, text=f"Пункт выдачи: {r['pickup']}", font=font(11), text_color=TXT_DARK, fg_color=BG_MAIN, anchor="w", wraplength=600, justify="left").grid(row=3, column=0, columnspan=2, sticky="w", padx=14)
        od = r["order_date"].strftime("%d.%m.%Y") if r["order_date"] else "—"
        dd = r["delivery_date"].strftime("%d.%m.%Y") if r["delivery_date"] else "—"
        ctk.CTkLabel(card, text=f"Дата заказа: {od}    Дата выдачи: {dd}", font=font(11), text_color=TXT_DARK, fg_color=BG_MAIN, anchor="w").grid(row=4, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 10))

        if can_admin:
            btns = ctk.CTkFrame(card, fg_color=BG_MAIN)
            btns.grid(row=0, column=2, rowspan=5, padx=10, pady=10, sticky="e")
            ctk.CTkButton(btns, text="Редактировать", width=140, fg_color=BG_ACCENT, hover_color="#C9A26F", text_color=TXT_DARK, font=font(11, True), command=lambda i=r["id"]: open_order_edit(root, i, reload_orders)).pack(pady=3)
            ctk.CTkButton(btns, text="Удалить", width=140, fg_color=BG_MAIN, hover_color=BG_SOFT, border_color=BG_ACCENT, border_width=2, text_color=TXT_DARK, font=font(11, True), command=lambda i=r["id"]: delete_order(i, reload_orders)).pack(pady=3)

        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)

    reload_orders()


# delete
def delete_order(oid, reload_cb):
    if not messagebox.askyesno("Подтверждение удаления", f"Удалить заказ № {oid}? Действие необратимо."):
        return
    try:
        db.query("DELETE FROM `Order` WHERE id=%s", (oid,))
    except Exception as e:
        messagebox.showerror("Ошибка БД", f"Не удалось удалить заказ:\n{e}")
        return
    reload_cb()


# order
def open_order_edit(root, oid, reload_cb):
    global order_edit_win
    if order_edit_win is not None and order_edit_win.winfo_exists():
        order_edit_win.lift()
        order_edit_win.focus()
        return

    w = ctk.CTkToplevel(root)
    w.title("Редактирование заказа" if oid else "Добавление заказа")
    w.geometry("560x560")
    w.configure(fg_color=BG_MAIN)
    set_window_icon(w)
    w.transient(root)
    w.grab_set()

    order_edit_win = w

    bar = ctk.CTkFrame(w, fg_color=BG_SOFT, height=56, corner_radius=0)
    bar.pack(fill="x")
    bar.pack_propagate(False)
    ctk.CTkLabel(bar, text=("Редактирование заказа" if oid else "Добавление заказа"), font=font(18, True), text_color=TXT_DARK, fg_color=BG_SOFT).pack(side="left", padx=20)

    body = ctk.CTkScrollableFrame(w, fg_color=BG_MAIN)
    body.pack(fill="both", expand=True, padx=20, pady=10)

    statuses = db.fetch("SELECT id, name FROM OrderStatus ORDER BY name")
    pickups = db.fetch("SELECT id, address FROM PickupPoint ORDER BY id")
    clients = db.fetch("SELECT u.id, u.fio FROM User u JOIN Role r ON r.id=u.role_id WHERE r.name='Авторизированный клиент' ORDER BY u.fio")

    cur = None
    if oid:
        rows = db.fetch("SELECT * FROM `Order` WHERE id=%s", (oid,))
        if not rows:
            messagebox.showerror("Ошибка", "Заказ не найден в базе данных.")
            w.destroy()
            return
        cur = rows[0]

    ctk.CTkLabel(body, text="Артикул заказа", font=font(12), text_color=TXT_DARK, fg_color=BG_MAIN, anchor="w").pack(fill="x")
    art_e = ctk.CTkEntry(body, font=font(13), fg_color=BG_MAIN, border_color=BG_ACCENT, text_color=TXT_DARK)
    art_e.insert(0, cur["article"] if cur else "")
    art_e.pack(fill="x", pady=(2, 10))

    ctk.CTkLabel(body, text="Статус заказа", font=font(12), text_color=TXT_DARK, fg_color=BG_MAIN, anchor="w").pack(fill="x")
    st_var = ctk.StringVar(value=([s["name"] for s in statuses if cur and s["id"] == cur["status_id"]] + [statuses[0]["name"]])[0])
    ctk.CTkOptionMenu(body, variable=st_var, values=[s["name"] for s in statuses], fg_color=BG_ACCENT, button_color=BG_ACCENT, button_hover_color="#C9A26F", text_color=TXT_DARK, font=font(12)).pack(fill="x", pady=(2, 10))

    ctk.CTkLabel(body, text="Адрес пункта выдачи", font=font(12), text_color=TXT_DARK, fg_color=BG_MAIN, anchor="w").pack(fill="x")
    addr_var = ctk.StringVar(value=([p["address"] for p in pickups if cur and p["id"] == cur["pickup_id"]] + [pickups[0]["address"]])[0])
    ctk.CTkOptionMenu(body, variable=addr_var, values=[p["address"] for p in pickups], fg_color=BG_ACCENT, button_color=BG_ACCENT, button_hover_color="#C9A26F", text_color=TXT_DARK, font=font(11), dynamic_resizing=True).pack(fill="x", pady=(2, 10))

    ctk.CTkLabel(body, text="Клиент", font=font(12), text_color=TXT_DARK, fg_color=BG_MAIN, anchor="w").pack(fill="x")
    cli_values = ["— не выбран —"] + [c["fio"] for c in clients]
    cli_var = ctk.StringVar(value=([c["fio"] for c in clients if cur and c["id"] == cur["client_id"]] + ["— не выбран —"])[0])
    ctk.CTkOptionMenu(body, variable=cli_var, values=cli_values, fg_color=BG_ACCENT, button_color=BG_ACCENT, button_hover_color="#C9A26F", text_color=TXT_DARK, font=font(12)).pack(fill="x", pady=(2, 10))

    ctk.CTkLabel(body, text="Код получения", font=font(12), text_color=TXT_DARK, fg_color=BG_MAIN, anchor="w").pack(fill="x")
    code_e = ctk.CTkEntry(body, font=font(13), fg_color=BG_MAIN, border_color=BG_ACCENT, text_color=TXT_DARK)
    code_e.insert(0, str(cur["pickup_code"]) if cur and cur["pickup_code"] is not None else "")
    code_e.pack(fill="x", pady=(2, 10))

    ctk.CTkLabel(body, text="Дата заказа", font=font(12), text_color=TXT_DARK, fg_color=BG_MAIN, anchor="w").pack(fill="x")
    od_def = cur["order_date"] if cur and cur["order_date"] else date.today()
    od_e = DateEntry(body, date_pattern="dd.mm.yyyy", year=od_def.year, month=od_def.month, day=od_def.day, background=BG_ACCENT, foreground=TXT_DARK)
    od_e.pack(fill="x", pady=(2, 10))

    ctk.CTkLabel(body, text="Дата выдачи", font=font(12), text_color=TXT_DARK, fg_color=BG_MAIN, anchor="w").pack(fill="x")
    dd_def = cur["delivery_date"] if cur and cur["delivery_date"] else date.today()
    dd_e = DateEntry(body, date_pattern="dd.mm.yyyy", year=dd_def.year, month=dd_def.month, day=dd_def.day, background=BG_ACCENT, foreground=TXT_DARK)
    dd_e.pack(fill="x", pady=(2, 10))

    def save():
        art = art_e.get().strip()
        if not art:
            messagebox.showwarning("Ошибка ввода", "Введите артикул заказа.")
            return
        code = code_e.get().strip()
        try:
            code_val = int(code) if code else None
        except Exception:
            messagebox.showwarning("Ошибка ввода", "Код получения должен быть целым числом.")
            return
        sid = next(s["id"] for s in statuses if s["name"] == st_var.get())
        pid = next(p["id"] for p in pickups if p["address"] == addr_var.get())
        cid = next((c["id"] for c in clients if c["fio"] == cli_var.get()), None)
        try:
            od = od_e.get_date()
            dd = dd_e.get_date()
        except Exception:
            messagebox.showwarning("Ошибка ввода", "Проверьте корректность дат.")
            return
        try:
            if oid:
                db.query(
                    "UPDATE `Order` SET article=%s, status_id=%s, pickup_id=%s, client_id=%s, order_date=%s, delivery_date=%s, pickup_code=%s WHERE id=%s",
                    (art, sid, pid, cid, od, dd, code_val, oid),
                )
            else:
                db.query(
                    "INSERT INTO `Order`(article, status_id, pickup_id, client_id, order_date, delivery_date, pickup_code) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (art, sid, pid, cid, od, dd, code_val),
                )
        except Exception as e:
            messagebox.showerror("Ошибка БД", f"Не удалось сохранить заказ:\n{e}")
            return
        messagebox.showinfo("Успех", "Данные заказа сохранены.")
        w.destroy()
        reload_cb()

    actions = ctk.CTkFrame(w, fg_color=BG_MAIN, height=70)
    actions.pack(fill="x", side="bottom")
    ctk.CTkButton(actions, text="Сохранить", height=42, fg_color=BG_ACCENT, hover_color="#C9A26F", text_color=TXT_DARK, font=font(14, True), command=save).pack(side="right", padx=20, pady=14)
    ctk.CTkButton(actions, text="Отмена", height=42, fg_color=BG_MAIN, hover_color=BG_SOFT, border_color=BG_ACCENT, border_width=2, text_color=TXT_DARK, font=font(13), command=w.destroy).pack(side="right", padx=4, pady=14)

    def on_close():
        global order_edit_win
        order_edit_win = None
        w.destroy()

    w.protocol("WM_DELETE_WINDOW", on_close)


def main():
    root = ctk.CTk()
    root.geometry("1280x780")
    set_window_icon(root)
    try:
        db.fetch("SELECT 1")
    except Exception as e:
        root.withdraw()
        messagebox.showerror("Ошибка БД", f"Не удалось подключиться к базе данных toysdb.\nПроверьте параметры в db.py.\n\n{e}")
        return
    login_screen(root)
    root.mainloop()


if __name__ == "__main__":
    main()
