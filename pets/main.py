"""ООО «Товары для животных» — авторизация с captcha, роли, CRUD товаров."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import random, string, os, time as _time
import db

FONT = ("Arial", 11)
IMG_DIR = "images"; os.makedirs(IMG_DIR, exist_ok=True)
PLACEHOLDER = "picture.png"   # из ресурсов
USER = None
fail_count = 0       # неуспешные попытки входа
blocked_until = 0    # timestamp окончания блокировки
edit_win = None

# ---------- captcha ----------
def make_captcha():
    text = "".join(random.choices(string.ascii_uppercase+string.digits, k=4))
    img = Image.new("RGB", (160, 60), "white")
    d = ImageDraw.Draw(img)
    # шум — линии и точки
    for _ in range(80): d.point((random.randint(0,160), random.randint(0,60)), fill=(random.randint(0,200),)*3)
    for _ in range(6):
        d.line((random.randint(0,160), random.randint(0,60), random.randint(0,160), random.randint(0,60)),
               fill=(random.randint(0,180),)*3, width=1)
    try: f = ImageFont.truetype("arial.ttf", 32)
    except: f = ImageFont.load_default()
    # символы — со сдвигом по Y и поворотом (наложение)
    for i,ch in enumerate(text):
        ci = Image.new("RGBA", (40,50), (255,255,255,0))
        ImageDraw.Draw(ci).text((4,4), ch, font=f, fill=(random.randint(0,120),random.randint(0,120),random.randint(0,120)))
        ci = ci.rotate(random.randint(-25,25), expand=True)
        img.paste(ci, (10 + i*35 + random.randint(-3,3), random.randint(-2,8)), ci)
    # перечёркивание
    d.line((0, random.randint(20,40), 160, random.randint(20,40)), fill="black", width=2)
    return text, ImageTk.PhotoImage(img)

# ---------- окно входа ----------
def show_login():
    global fail_count
    for w in root.winfo_children(): w.destroy()
    root.configure(bg="white")
    f = tk.Frame(root, bg="white"); f.place(relx=0.5, rely=0.5, anchor="center")
    tk.Label(f, text="Вход в систему", font=("Arial",18,"bold"), bg="white").pack(pady=10)
    log_v = tk.StringVar(); pwd_v = tk.StringVar(); cap_v = tk.StringVar()
    tk.Label(f, text="Логин:", font=FONT, bg="white").pack(anchor="w")
    tk.Entry(f, textvariable=log_v, font=FONT, width=30).pack()
    tk.Label(f, text="Пароль:", font=FONT, bg="white").pack(anchor="w", pady=(6,0))
    tk.Entry(f, textvariable=pwd_v, show="*", font=FONT, width=30).pack()

    cap_text = [None]
    cap_lbl = tk.Label(f, bg="white"); cap_entry = tk.Entry(f, textvariable=cap_v, font=FONT, width=30)
    msg = tk.Label(f, text="", fg="red", bg="white", font=FONT)
    msg.pack(pady=4)

    def gen_captcha():
        t, ph = make_captcha(); cap_text[0] = t
        cap_lbl.config(image=ph); cap_lbl.img = ph

    def show_captcha():
        tk.Label(f, text="Введите код с картинки:", font=FONT, bg="white").pack(anchor="w", pady=(8,0))
        cap_lbl.pack(); cap_entry.pack(); gen_captcha()
        tk.Button(f, text="Обновить captcha", font=FONT, command=gen_captcha).pack()

    def do_login():
        global fail_count, blocked_until
        if _time.time() < blocked_until:
            return msg.config(text=f"Заблокировано, попробуйте через {int(blocked_until-_time.time())} сек.")
        # если captcha видна — проверяем
        if cap_text[0] is not None:
            if cap_v.get().strip().upper() != cap_text[0]:
                blocked_until = _time.time() + 10
                msg.config(text="Неверная captcha. Блокировка на 10 секунд.")
                gen_captcha(); cap_v.set(""); return
        r = db.fetch("""SELECT u.ID, u.FIO, r.Name AS Role FROM User u
                        JOIN Role r ON r.ID=u.RoleID
                        WHERE u.Login=%s AND u.Password=%s""",
                     (log_v.get(), pwd_v.get()))
        if not r:
            fail_count += 1
            msg.config(text="Неверный логин или пароль")
            if fail_count >= 1 and cap_text[0] is None: show_captcha()
            return
        global USER; USER = r[0]; fail_count = 0; show_main()

    tk.Button(f, text="Войти", font=FONT, bg="#00FA9A", command=do_login).pack(fill="x", pady=8)
    tk.Button(f, text="Войти как гость", font=FONT, command=lambda: (globals().__setitem__("USER", None), show_main())).pack(fill="x")

# ---------- главное окно ----------
def show_main():
    for w in root.winfo_children(): w.destroy()
    role = USER["Role"] if USER else "Гость"
    can_filter = role in ("Менеджер","Администратор")
    can_crud   = role == "Администратор"

    top = tk.Frame(root, bg="#7FFF00", pady=6); top.pack(fill="x")
    tk.Label(top, text="Товары для животных", font=("Arial",14,"bold"), bg="#7FFF00").pack(side="left", padx=10)
    tk.Label(top, text=f"{USER['FIO'] if USER else 'Гость'} ({role})", font=FONT, bg="#7FFF00").pack(side="right", padx=10)
    tk.Button(top, text="Выход", font=FONT, command=show_login).pack(side="right")

    pan = tk.Frame(root); pan.pack(fill="x", padx=10, pady=4)
    search_v = tk.StringVar(); manuf_v = tk.StringVar(value="Все производители"); sort_v = tk.StringVar(value="По возрастанию цены")
    counter = tk.Label(root, font=FONT, anchor="w"); counter.pack(fill="x", padx=10)

    if can_filter:
        tk.Label(pan, text="Поиск:", font=FONT).pack(side="left")
        tk.Entry(pan, textvariable=search_v, font=FONT, width=25).pack(side="left", padx=3)
        manufs = ["Все производители"] + [m["Name"] for m in db.fetch("SELECT Name FROM Manufacturer ORDER BY Name")]
        ttk.Combobox(pan, textvariable=manuf_v, values=manufs, state="readonly", width=22, font=FONT).pack(side="left", padx=3)
        ttk.Combobox(pan, textvariable=sort_v, values=["По возрастанию цены","По убыванию цены"], state="readonly", width=22, font=FONT).pack(side="left", padx=3)
    if can_crud:
        tk.Button(pan, text="+ Товар", font=FONT, bg="#00FA9A", command=lambda: open_edit(None)).pack(side="right")

    mid = tk.Frame(root); mid.pack(fill="both", expand=True, padx=10, pady=4)
    cv = tk.Canvas(mid, highlightthickness=0)
    sb = tk.Scrollbar(mid, command=cv.yview)
    inner = tk.Frame(cv)
    inner.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
    cv.create_window((0,0), window=inner, anchor="nw"); cv.configure(yscrollcommand=sb.set)
    cv.pack(side="left", fill="both", expand=True); sb.pack(side="right", fill="y")

    def thumb(path):
        p = path if path and os.path.exists(path) else PLACEHOLDER
        try:
            im = Image.open(p); im.thumbnail((120,120))
            return ImageTk.PhotoImage(im)
        except: return None

    def draw(rows):
        for w in inner.winfo_children(): w.destroy()
        for r in rows:
            bg = "#DDDDDD" if r["Stock"] == 0 else "white"
            card = tk.Frame(inner, bg=bg, bd=1, relief="solid", padx=6, pady=6); card.pack(fill="x", pady=3)
            ph = thumb(r["ImagePath"]); il = tk.Label(card, image=ph, bg=bg); il.img = ph; il.pack(side="left", padx=4)
            info = tk.Frame(card, bg=bg); info.pack(side="left", fill="both", expand=True)
            tk.Label(info, text=r["Name"], font=("Arial",12,"bold"), bg=bg).pack(anchor="w")
            tk.Label(info, text=r["Description"] or "", font=FONT, bg=bg, wraplength=550, justify="left").pack(anchor="w")
            tk.Label(info, text=f"Производитель: {r['Manufacturer'] or '-'}", font=FONT, bg=bg).pack(anchor="w")
            tk.Label(info, text=f"Цена: {float(r['Price']):.2f} ₽", font=FONT, bg=bg).pack(anchor="w")
            tk.Label(card, text=f"На складе: {r['Stock']}", font=FONT, bg=bg).pack(side="right", padx=10)
            if can_crud:
                btns = tk.Frame(card, bg=bg); btns.pack(side="right")
                tk.Button(btns, text="Изм.", font=FONT, command=lambda i=r["ID"]: open_edit(i)).pack(fill="x")
                tk.Button(btns, text="Удал.", font=FONT, command=lambda i=r["ID"]: delete_product(i)).pack(fill="x")

    def reload():
        rows = db.fetch("""SELECT p.*, m.Name AS Manufacturer, c.Name AS Category
                           FROM Product p
                           LEFT JOIN Manufacturer m ON m.ID=p.ManufacturerID
                           LEFT JOIN Category c    ON c.ID=p.CategoryID""")
        total = len(rows)
        if can_filter:
            q = search_v.get().lower()
            if q:
                rows = [r for r in rows if any(q in str(r[k] or "").lower()
                        for k in ("Article","Name","Description","Manufacturer","Category","Unit"))]
            if manuf_v.get() != "Все производители":
                rows = [r for r in rows if r["Manufacturer"] == manuf_v.get()]
            rev = sort_v.get().startswith("По убыванию")
            rows = sorted(rows, key=lambda r: float(r["Price"]), reverse=rev)
        draw(rows); counter.config(text=f"{len(rows)} из {total}")

    def delete_product(pid):
        # запрет если товар в заказе ИЛИ если в дополнительных и любой из них в заказе
        if db.fetch("SELECT 1 FROM OrderItem WHERE ProductID=%s LIMIT 1",(pid,)):
            return messagebox.showerror("Ошибка","Товар присутствует в заказе — удаление запрещено")
        attached = [r["AttachedProductID"] for r in db.fetch("SELECT AttachedProductID FROM AttachedProduct WHERE MainProductID=%s",(pid,))]
        for a in attached:
            if db.fetch("SELECT 1 FROM OrderItem WHERE ProductID=%s LIMIT 1",(a,)):
                return messagebox.showerror("Ошибка","Один из дополнительных товаров в заказе — удаление запрещено")
        if not messagebox.askyesno("?","Удалить товар (и его дополнительные)?"): return
        # удалить картинки
        for ap in attached + [pid]:
            r = db.fetch("SELECT ImagePath FROM Product WHERE ID=%s",(ap,))
            if r and r[0]["ImagePath"] and os.path.exists(r[0]["ImagePath"]):
                try: os.remove(r[0]["ImagePath"])
                except: pass
        db.query("DELETE FROM AttachedProduct WHERE MainProductID=%s OR AttachedProductID=%s",(pid,pid))
        for ap in attached: db.query("DELETE FROM Product WHERE ID=%s",(ap,))
        db.query("DELETE FROM Product WHERE ID=%s",(pid,))
        reload()

    if can_filter:
        for v in (search_v, manuf_v, sort_v): v.trace_add("write", lambda *_: reload())
    global _reload; _reload = reload
    reload()

# ---------- окно редактирования ----------
def open_edit(pid):
    global edit_win
    if edit_win and edit_win.winfo_exists(): return edit_win.lift()
    edit_win = tk.Toplevel(root); edit_win.title("Товар"); edit_win.configure(bg="white")
    cur = db.fetch("SELECT * FROM Product WHERE ID=%s",(pid,))[0] if pid else None
    f = tk.Frame(edit_win, bg="white", padx=10, pady=10); f.pack()

    row = [0]
    if pid:
        tk.Label(f, text=f"ID: {pid}", font=FONT, bg="white").grid(row=row[0], column=0, columnspan=2, sticky="w"); row[0]+=1

    art_v=tk.StringVar(value=(cur or {}).get("Article","")); name_v=tk.StringVar(value=(cur or {}).get("Name",""))
    unit_v=tk.StringVar(value=(cur or {}).get("Unit","шт.")); price_v=tk.StringVar(value=str((cur or {}).get("Price","0")))
    stock_v=tk.StringVar(value=str((cur or {}).get("Stock","0"))); img_v=tk.StringVar(value=(cur or {}).get("ImagePath","") or "")

    cats = db.fetch("SELECT * FROM Category ORDER BY Name")
    mans = db.fetch("SELECT * FROM Manufacturer ORDER BY Name")
    sups = db.fetch("SELECT * FROM Supplier ORDER BY Name")
    cat_map = {c["Name"]: c["ID"] for c in cats}; man_map = {m["Name"]: m["ID"] for m in mans}; sup_map = {s["Name"]: s["ID"] for s in sups}
    cat_v=tk.StringVar(value=next((c["Name"] for c in cats if c["ID"]==(cur or {}).get("CategoryID")), ""))
    man_v=tk.StringVar(value=next((m["Name"] for m in mans if m["ID"]==(cur or {}).get("ManufacturerID")), ""))
    sup_v=tk.StringVar(value=next((s["Name"] for s in sups if s["ID"]==(cur or {}).get("SupplierID")), ""))

    def add(lbl, var, widget="entry", values=None):
        tk.Label(f, text=lbl, font=FONT, bg="white").grid(row=row[0], column=0, sticky="w")
        if widget == "combo":
            ttk.Combobox(f, textvariable=var, values=values, font=FONT, width=38).grid(row=row[0], column=1, sticky="we")
        else:
            tk.Entry(f, textvariable=var, font=FONT, width=40).grid(row=row[0], column=1, sticky="we")
        row[0] += 1

    add("Артикул:", art_v); add("Наименование:", name_v)
    add("Категория:", cat_v, "combo", list(cat_map.keys()))
    add("Ед. изм.:", unit_v); add("Кол-во на складе:", stock_v)
    add("Поставщик:", sup_v, "combo", list(sup_map.keys()))
    add("Производитель:", man_v, "combo", list(man_map.keys()))
    add("Цена за ед.:", price_v)

    tk.Label(f, text="Описание:", font=FONT, bg="white").grid(row=row[0], column=0, sticky="nw")
    desc_t = tk.Text(f, width=40, height=4, font=FONT); desc_t.grid(row=row[0], column=1, sticky="we"); row[0]+=1
    if cur and cur["Description"]: desc_t.insert("1.0", cur["Description"])

    img_lbl = tk.Label(f, bg="white"); img_lbl.grid(row=row[0], column=1, sticky="w"); row[0]+=1
    def show_img():
        p = img_v.get() if img_v.get() and os.path.exists(img_v.get()) else PLACEHOLDER
        try:
            im = Image.open(p); im.thumbnail((300,200)); ph = ImageTk.PhotoImage(im)
            img_lbl.config(image=ph); img_lbl.img = ph
        except: pass
    show_img()
    def pick():
        p = filedialog.askopenfilename(filetypes=[("Images","*.png *.jpg *.jpeg")])
        if not p: return
        im = Image.open(p); im.thumbnail((300,200))
        dst = os.path.join(IMG_DIR, os.path.basename(p)); im.save(dst)
        if img_v.get() and os.path.exists(img_v.get()) and os.path.abspath(img_v.get())!=os.path.abspath(dst):
            try: os.remove(img_v.get())
            except: pass
        img_v.set(dst); show_img()
    tk.Button(f, text="Выбрать фото (300×200)", font=FONT, command=pick).grid(row=row[0], column=1, sticky="w"); row[0]+=1

    def get_or_create(table, name, mp):
        if not name: return None
        if name in mp: return mp[name]
        return db.query(f"INSERT INTO {table}(Name) VALUES (%s)", (name,))

    def save():
        if not art_v.get().strip() or not name_v.get().strip(): return messagebox.showerror("!","Артикул и наименование обязательны")
        try: price=float(price_v.get()); stock=int(stock_v.get())
        except: return messagebox.showerror("!","Проверьте числовые поля")
        if price < 0: return messagebox.showerror("!","Цена не может быть отрицательной")
        if stock < 0: return messagebox.showerror("!","Остаток не может быть отрицательным")
        dup = db.fetch("SELECT 1 FROM Product WHERE Article=%s" + (" AND ID<>%s" if pid else ""),
                       (art_v.get(), pid) if pid else (art_v.get(),))
        if dup: return messagebox.showerror("!","Артикул уже существует")
        cid = get_or_create("Category", cat_v.get(), cat_map)
        mid = get_or_create("Manufacturer", man_v.get(), man_map)
        sid = get_or_create("Supplier", sup_v.get(), sup_map)
        descr = desc_t.get("1.0","end").strip()
        if pid is None:
            db.query("""INSERT INTO Product(Article,Name,Unit,Price,SupplierID,ManufacturerID,CategoryID,Stock,Description,ImagePath)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                     (art_v.get(), name_v.get(), unit_v.get(), price, sid, mid, cid, stock, descr, img_v.get() or None))
        else:
            db.query("""UPDATE Product SET Article=%s,Name=%s,Unit=%s,Price=%s,SupplierID=%s,ManufacturerID=%s,CategoryID=%s,
                        Stock=%s,Description=%s,ImagePath=%s WHERE ID=%s""",
                     (art_v.get(), name_v.get(), unit_v.get(), price, sid, mid, cid, stock, descr, img_v.get() or None, pid))
        _reload(); edit_win.destroy()

    tk.Button(f, text="Сохранить", font=FONT, bg="#00FA9A", command=save).grid(row=row[0], column=1, sticky="we", pady=8)

# ---------- запуск ----------
root = tk.Tk(); root.title("Товары для животных"); root.geometry("1100x720")
show_login()
root.mainloop()
