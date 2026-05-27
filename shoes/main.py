"""Магазин обуви ООО «Обувь» — М1 + стили М2.
Авторизация → роли: Гость / Клиент / Менеджер / Администратор.
Стили М2: белый фон, Times New Roman, #7FFF00 — доп. фон, #00FA9A — кнопки действий,
#2E8B57 — фон карточки при скидке > 15%.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os, shutil
import db

# ---------- стили М2 ----------
FONT = ("Times New Roman", 11)
BG_MAIN = "white"
BG_ACCENT = "#7FFF00"     # доп. фон (шапка)
BG_ACTION = "#00FA9A"     # целевая кнопка
BG_DISCOUNT = "#2E8B57"   # фон карточки если скидка > 15
IMG_DIR = "images"; os.makedirs(IMG_DIR, exist_ok=True)

USER = None     # {"ID","FIO","Role"} либо None (гость)
edit_win = None

# ---------- окно входа ----------
def show_login():
    for w in root.winfo_children(): w.destroy()
    root.configure(bg=BG_MAIN)
    f = tk.Frame(root, bg=BG_MAIN); f.place(relx=0.5, rely=0.5, anchor="center")
    tk.Label(f, text="Вход в систему", font=("Times New Roman",18,"bold"), bg=BG_MAIN).pack(pady=10)
    tk.Label(f, text="Логин:", font=FONT, bg=BG_MAIN).pack(anchor="w")
    log_v = tk.StringVar(); tk.Entry(f, textvariable=log_v, font=FONT, width=30).pack()
    tk.Label(f, text="Пароль:", font=FONT, bg=BG_MAIN).pack(anchor="w", pady=(8,0))
    pwd_v = tk.StringVar(); tk.Entry(f, textvariable=pwd_v, show="*", font=FONT, width=30).pack()

    def do_login():
        r = db.fetch("""SELECT u.ID, u.FIO, r.Name AS Role FROM User u
                        JOIN Role r ON r.ID=u.RoleID
                        WHERE u.Login=%s AND u.Password=%s""", (log_v.get(), pwd_v.get()))
        if not r: return messagebox.showerror("Ошибка","Неверный логин или пароль")
        global USER; USER = r[0]; show_main()
    def as_guest():
        global USER; USER = None; show_main()

    tk.Button(f, text="Войти", font=FONT, bg=BG_ACTION, command=do_login).pack(fill="x", pady=10)
    tk.Button(f, text="Войти как гость", font=FONT, command=as_guest).pack(fill="x")

# ---------- главное окно ----------
def show_main():
    for w in root.winfo_children(): w.destroy()
    role = USER["Role"] if USER else "Гость"
    can_filter = role in ("Менеджер","Администратор")
    can_crud   = role == "Администратор"
    can_orders = role in ("Менеджер","Администратор")

    # шапка
    top = tk.Frame(root, bg=BG_ACCENT, pady=6); top.pack(fill="x")
    tk.Label(top, text="ООО «Обувь»", font=("Times New Roman",16,"bold"), bg=BG_ACCENT).pack(side="left", padx=10)
    tk.Label(top, text=f"Пользователь: {USER['FIO'] if USER else 'Гость'} ({role})",
             font=FONT, bg=BG_ACCENT).pack(side="right", padx=10)
    tk.Button(top, text="Выход", font=FONT, command=show_login).pack(side="right")

    # панель управления
    pan = tk.Frame(root, bg=BG_MAIN); pan.pack(fill="x", padx=10, pady=6)
    search_v = tk.StringVar(); manuf_v = tk.StringVar(value="Все производители")
    sort_v = tk.StringVar(value="По возрастанию цены")

    if can_filter:
        tk.Label(pan, text="Поиск:", font=FONT, bg=BG_MAIN).pack(side="left")
        tk.Entry(pan, textvariable=search_v, font=FONT, width=25).pack(side="left", padx=4)

        manufs = ["Все производители"] + [m["Name"] for m in db.fetch("SELECT Name FROM Manufacturer ORDER BY Name")]
        ttk.Combobox(pan, textvariable=manuf_v, values=manufs, state="readonly", width=22, font=FONT).pack(side="left", padx=4)
        ttk.Combobox(pan, textvariable=sort_v, state="readonly", width=22, font=FONT,
                     values=["По возрастанию цены","По убыванию цены"]).pack(side="left", padx=4)

    if can_crud:
        tk.Button(pan, text="+ Товар", font=FONT, bg=BG_ACTION,
                  command=lambda: open_edit(None)).pack(side="right", padx=4)
    if can_orders:
        tk.Button(pan, text="Заказы", font=FONT,
                  command=open_orders).pack(side="right", padx=4)

    counter = tk.Label(root, text="", font=FONT, bg=BG_MAIN, anchor="e"); counter.pack(fill="x", padx=10)

    # скроллируемый список
    mid = tk.Frame(root, bg=BG_MAIN); mid.pack(fill="both", expand=True, padx=10, pady=4)
    cv = tk.Canvas(mid, bg=BG_MAIN, highlightthickness=0)
    sb = tk.Scrollbar(mid, command=cv.yview)
    inner = tk.Frame(cv, bg=BG_MAIN)
    inner.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
    cv.create_window((0,0), window=inner, anchor="nw"); cv.configure(yscrollcommand=sb.set)
    cv.pack(side="left", fill="both", expand=True); sb.pack(side="right", fill="y")

    def thumb(path):
        try:
            im = Image.open(path); im.thumbnail((110,110))
            return ImageTk.PhotoImage(im)
        except: return None

    def draw(rows):
        for w in inner.winfo_children(): w.destroy()
        for r in rows:
            disc = r["Discount"] or 0
            bg = BG_DISCOUNT if disc > 15 else (BG_MAIN if r["Stock"] > 0 else "#DDDDDD")
            fg = "white" if bg == BG_DISCOUNT else "black"
            card = tk.Frame(inner, bg=bg, bd=1, relief="solid", padx=6, pady=6); card.pack(fill="x", pady=3)
            img = thumb(r["ImagePath"] or "")
            ilbl = tk.Label(card, image=img, bg=bg, width=110, height=110); ilbl.img = img
            ilbl.pack(side="left", padx=4)
            info = tk.Frame(card, bg=bg); info.pack(side="left", fill="both", expand=True)
            tk.Label(info, text=f"{r['Article']} — {r['Name']}", font=("Times New Roman",12,"bold"), bg=bg, fg=fg).pack(anchor="w")
            tk.Label(info, text=f"Производитель: {r['Manufacturer'] or '-'}", font=FONT, bg=bg, fg=fg).pack(anchor="w")
            tk.Label(info, text=f"Категория: {r['Category'] or '-'} | {r['Unit']}", font=FONT, bg=bg, fg=fg).pack(anchor="w")
            tk.Label(info, text=(r["Description"] or "")[:120], font=FONT, bg=bg, fg=fg, wraplength=600, justify="left").pack(anchor="w")
            price = float(r["Price"])
            ptxt = f"{price:.2f} ₽"
            if disc > 0: ptxt += f" (-{disc}%) → {price*(1-disc/100):.2f} ₽"
            tk.Label(info, text=ptxt, font=("Times New Roman",12,"bold"), bg=bg, fg=fg).pack(anchor="w")
            tk.Label(card, text=f"На складе: {r['Stock']}", font=FONT, bg=bg, fg=fg).pack(side="right", padx=8)
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
        draw(rows)
        counter.config(text=f"{len(rows)} из {total}")

    def delete_product(pid):
        if db.fetch("SELECT 1 FROM OrderItem WHERE ProductID=%s LIMIT 1",(pid,)):
            return messagebox.showerror("Ошибка","Товар присутствует в заказе — удаление запрещено")
        if not messagebox.askyesno("?","Удалить товар?"): return
        path = (db.fetch("SELECT ImagePath FROM Product WHERE ID=%s",(pid,)) or [{}])[0].get("ImagePath")
        db.query("DELETE FROM Product WHERE ID=%s",(pid,))
        if path and os.path.exists(path):
            try: os.remove(path)
            except: pass
        reload()

    if can_filter:
        search_v.trace_add("write", lambda *_: reload())
        manuf_v.trace_add("write", lambda *_: reload())
        sort_v.trace_add("write", lambda *_: reload())

    # сохранить функции в глобальные имена, чтобы Toplevel'ы могли позвать
    global _reload, _delete; _reload = reload; _delete = delete_product
    reload()

# ---------- окно добавления/редактирования товара ----------
def open_edit(pid):
    global edit_win
    if edit_win and edit_win.winfo_exists(): return edit_win.lift()
    edit_win = tk.Toplevel(root); edit_win.title("Товар"); edit_win.configure(bg=BG_MAIN)

    cur = db.fetch("SELECT * FROM Product WHERE ID=%s",(pid,))[0] if pid else None
    f = tk.Frame(edit_win, bg=BG_MAIN, padx=10, pady=10); f.pack()

    row = [0]
    def add(label, var):
        tk.Label(f, text=label, font=FONT, bg=BG_MAIN).grid(row=row[0], column=0, sticky="w")
        e = tk.Entry(f, textvariable=var, font=FONT, width=40); e.grid(row=row[0], column=1, sticky="we"); row[0]+=1
        return e

    if pid:
        tk.Label(f, text="ID:", font=FONT, bg=BG_MAIN).grid(row=row[0], column=0, sticky="w")
        tk.Entry(f, textvariable=tk.StringVar(value=str(pid)), state="readonly", font=FONT).grid(row=row[0], column=1, sticky="we"); row[0]+=1

    art_v   = tk.StringVar(value=(cur or {}).get("Article",""))
    name_v  = tk.StringVar(value=(cur or {}).get("Name",""))
    unit_v  = tk.StringVar(value=(cur or {}).get("Unit","шт."))
    price_v = tk.StringVar(value=str((cur or {}).get("Price","0")))
    disc_v  = tk.StringVar(value=str((cur or {}).get("Discount","0")))
    stock_v = tk.StringVar(value=str((cur or {}).get("Stock","0")))
    img_v   = tk.StringVar(value=(cur or {}).get("ImagePath","") or "")

    cats = db.fetch("SELECT * FROM Category ORDER BY Name")
    mans = db.fetch("SELECT * FROM Manufacturer ORDER BY Name")
    sups = db.fetch("SELECT * FROM Supplier ORDER BY Name")
    cat_map = {c["Name"]: c["ID"] for c in cats}
    man_map = {m["Name"]: m["ID"] for m in mans}
    sup_map = {s["Name"]: s["ID"] for s in sups}

    cat_v = tk.StringVar(value=next((c["Name"] for c in cats if c["ID"]==(cur or {}).get("CategoryID")), ""))
    man_v = tk.StringVar(value=next((m["Name"] for m in mans if m["ID"]==(cur or {}).get("ManufacturerID")), ""))
    sup_v = tk.StringVar(value=next((s["Name"] for s in sups if s["ID"]==(cur or {}).get("SupplierID")), ""))

    add("Артикул:", art_v); add("Наименование:", name_v); add("Ед. изм.:", unit_v)
    add("Цена:", price_v);  add("Скидка, %:", disc_v); add("Остаток:", stock_v)

    def addcb(label, var, values):
        tk.Label(f, text=label, font=FONT, bg=BG_MAIN).grid(row=row[0], column=0, sticky="w")
        ttk.Combobox(f, textvariable=var, values=values, font=FONT, width=37).grid(row=row[0], column=1, sticky="we"); row[0]+=1
    addcb("Категория:", cat_v, list(cat_map.keys()))
    addcb("Производитель:", man_v, list(man_map.keys()))
    addcb("Поставщик:", sup_v, list(sup_map.keys()))

    tk.Label(f, text="Описание:", font=FONT, bg=BG_MAIN).grid(row=row[0], column=0, sticky="nw")
    desc_t = tk.Text(f, width=40, height=4, font=FONT); desc_t.grid(row=row[0], column=1, sticky="we"); row[0]+=1
    if cur and cur["Description"]: desc_t.insert("1.0", cur["Description"])

    img_lbl = tk.Label(f, bg=BG_MAIN)
    img_lbl.grid(row=row[0], column=1, sticky="w")
    def show_img():
        if img_v.get() and os.path.exists(img_v.get()):
            im = Image.open(img_v.get()); im.thumbnail((300,200))
            ph = ImageTk.PhotoImage(im); img_lbl.config(image=ph); img_lbl.img = ph
    show_img(); row[0]+=1
    def pick():
        p = filedialog.askopenfilename(filetypes=[("Images","*.png *.jpg *.jpeg")])
        if not p: return
        im = Image.open(p); im.thumbnail((300,200))
        dst = os.path.join(IMG_DIR, os.path.basename(p))
        im.save(dst)
        # удалить старое
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
        if not art_v.get().strip(): return messagebox.showerror("!","Артикул обязателен")
        if not name_v.get().strip(): return messagebox.showerror("!","Наименование обязательно")
        try: price=float(price_v.get()); disc=int(disc_v.get()); stock=int(stock_v.get())
        except: return messagebox.showerror("!","Проверьте числовые поля")
        if price < 0: return messagebox.showerror("!","Цена не может быть отрицательной")
        if stock < 0: return messagebox.showerror("!","Остаток не может быть отрицательным")
        # уникальность артикула
        dup = db.fetch("SELECT 1 FROM Product WHERE Article=%s" + (" AND ID<>%s" if pid else ""),
                       (art_v.get(), pid) if pid else (art_v.get(),))
        if dup: return messagebox.showerror("!","Артикул уже существует")
        cid = get_or_create("Category", cat_v.get(), cat_map)
        mid = get_or_create("Manufacturer", man_v.get(), man_map)
        sid = get_or_create("Supplier", sup_v.get(), sup_map)
        descr = desc_t.get("1.0","end").strip()
        if pid is None:
            db.query("""INSERT INTO Product(Article,Name,Unit,Price,SupplierID,ManufacturerID,CategoryID,Discount,Stock,Description,ImagePath)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                     (art_v.get(),name_v.get(),unit_v.get(),price,sid,mid,cid,disc,stock,descr,img_v.get() or None))
        else:
            db.query("""UPDATE Product SET Article=%s,Name=%s,Unit=%s,Price=%s,SupplierID=%s,ManufacturerID=%s,
                        CategoryID=%s,Discount=%s,Stock=%s,Description=%s,ImagePath=%s WHERE ID=%s""",
                     (art_v.get(),name_v.get(),unit_v.get(),price,sid,mid,cid,disc,stock,descr,img_v.get() or None, pid))
        _reload(); edit_win.destroy()

    tk.Button(f, text="Сохранить", font=FONT, bg=BG_ACTION, command=save).grid(row=row[0], column=1, sticky="we", pady=8)

# ---------- окно заказов ----------
def open_orders():
    w = tk.Toplevel(root); w.title("Заказы"); w.geometry("900x600"); w.configure(bg=BG_MAIN)
    can_crud = USER and USER["Role"] == "Администратор"

    top = tk.Frame(w, bg=BG_ACCENT); top.pack(fill="x")
    tk.Label(top, text="Заказы", font=("Times New Roman",14,"bold"), bg=BG_ACCENT).pack(side="left", padx=10, pady=4)
    if can_crud:
        tk.Button(top, text="+ Заказ", font=FONT, bg=BG_ACTION, command=lambda: edit_order(None)).pack(side="right", padx=8)

    tree = ttk.Treeview(w, columns=("date","deliv","pickup","client","code","status"), show="headings")
    for col,t in zip(("date","deliv","pickup","client","code","status"),
                     ("Дата","Доставка","Пункт","Клиент","Код","Статус")):
        tree.heading(col, text=t)
    tree.pack(fill="both", expand=True, padx=10, pady=6)

    def reload():
        tree.delete(*tree.get_children())
        for o in db.fetch("""SELECT o.*, p.Address FROM `Order` o
                             JOIN PickupPoint p ON p.ID=o.PickupPointID ORDER BY o.OrderDate DESC"""):
            tree.insert("", "end", iid=o["ID"], values=(o["OrderDate"],o["DeliveryDate"],
                        o["Address"],o["ClientFIO"],o["Code"],o["Status"]))

    def edit_order(oid):
        ow = tk.Toplevel(w); ow.title("Заказ"); ow.configure(bg=BG_MAIN)
        cur = db.fetch("SELECT * FROM `Order` WHERE ID=%s",(oid,))[0] if oid else None
        pp = db.fetch("SELECT * FROM PickupPoint ORDER BY Address"); pp_map = {p["Address"]:p["ID"] for p in pp}
        v_date = tk.StringVar(value=str((cur or {}).get("OrderDate","")))
        v_deliv= tk.StringVar(value=str((cur or {}).get("DeliveryDate","") or ""))
        v_addr = tk.StringVar(value=next((p["Address"] for p in pp if p["ID"]==(cur or {}).get("PickupPointID")), ""))
        v_fio  = tk.StringVar(value=(cur or {}).get("ClientFIO",""))
        v_code = tk.StringVar(value=str((cur or {}).get("Code","100")))
        v_stat = tk.StringVar(value=(cur or {}).get("Status","Новый"))
        rr=[0]
        for lbl,var,values in [("Дата заказа (ГГГГ-ММ-ДД):",v_date,None),
                               ("Дата доставки:",v_deliv,None),
                               ("Пункт выдачи:",v_addr,list(pp_map.keys())),
                               ("ФИО клиента:",v_fio,None),
                               ("Код получения:",v_code,None),
                               ("Статус:",v_stat,["Новый","В пути","Готов","Завершен","Отменен"])]:
            tk.Label(ow,text=lbl,font=FONT,bg=BG_MAIN).grid(row=rr[0],column=0,sticky="w")
            if values: ttk.Combobox(ow,textvariable=var,values=values,font=FONT,width=30).grid(row=rr[0],column=1,sticky="we")
            else: tk.Entry(ow,textvariable=var,font=FONT,width=32).grid(row=rr[0],column=1,sticky="we")
            rr[0]+=1
        def save():
            try: ppid = pp_map.get(v_addr.get()) or db.query("INSERT INTO PickupPoint(Address) VALUES (%s)",(v_addr.get(),))
            except: return messagebox.showerror("!","Укажите пункт выдачи")
            if not v_date.get(): return messagebox.showerror("!","Дата обязательна")
            if oid is None:
                db.query("""INSERT INTO `Order`(OrderDate,DeliveryDate,PickupPointID,ClientFIO,Code,Status)
                            VALUES (%s,%s,%s,%s,%s,%s)""",(v_date.get(), v_deliv.get() or None, ppid, v_fio.get(), int(v_code.get()), v_stat.get()))
            else:
                db.query("""UPDATE `Order` SET OrderDate=%s,DeliveryDate=%s,PickupPointID=%s,ClientFIO=%s,Code=%s,Status=%s WHERE ID=%s""",
                         (v_date.get(), v_deliv.get() or None, ppid, v_fio.get(), int(v_code.get()), v_stat.get(), oid))
            reload(); ow.destroy()
        tk.Button(ow,text="Сохранить",font=FONT,bg=BG_ACTION,command=save).grid(row=rr[0],column=1,sticky="we",pady=6)

    def del_sel():
        sel = tree.selection()
        if not sel: return
        if not messagebox.askyesno("?","Удалить заказ?"): return
        oid = int(sel[0])
        db.query("DELETE FROM OrderItem WHERE OrderID=%s",(oid,))
        db.query("DELETE FROM `Order` WHERE ID=%s",(oid,))
        reload()

    if can_crud:
        bar = tk.Frame(w, bg=BG_MAIN); bar.pack(fill="x", padx=10, pady=4)
        tk.Button(bar,text="Редактировать",font=FONT,command=lambda: tree.selection() and edit_order(int(tree.selection()[0]))).pack(side="left",padx=4)
        tk.Button(bar,text="Удалить",font=FONT,command=del_sel).pack(side="left",padx=4)
    reload()

# ---------- запуск ----------
root = tk.Tk(); root.title("ООО Обувь"); root.geometry("1100x720")
try: root.iconbitmap("Icon.ico")
except: pass
show_login()
root.mainloop()
