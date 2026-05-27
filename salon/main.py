import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from PIL import Image, ImageTk
from datetime import datetime, timedelta, date
import shutil, os, re
import db

IS_ADMIN = False
ADMIN_CODE = "0000"
IMG_DIR = "images"
os.makedirs(IMG_DIR, exist_ok=True)
edit_win = None

root = tk.Tk()
root.title("Салон красоты")
root.geometry("1100x720")

# ---------- верхняя панель ----------
top = tk.Frame(root); top.pack(fill="x", padx=10, pady=8)
search_var = tk.StringVar()
filter_var = tk.StringVar(value="Все")
sort_var   = tk.StringVar(value="По возрастанию цены")

tk.Label(top, text="Поиск:").pack(side="left")
tk.Entry(top, textvariable=search_var, width=30).pack(side="left", padx=5)
tk.Label(top, text="Скидка:").pack(side="left")
ttk.Combobox(top, textvariable=filter_var, width=10, state="readonly",
             values=["Все","0-5","5-15","15-30","30-70","70-100"]).pack(side="left", padx=5)
tk.Label(top, text="Сортировка:").pack(side="left")
ttk.Combobox(top, textvariable=sort_var, width=22, state="readonly",
             values=["По возрастанию цены","По убыванию цены"]).pack(side="left", padx=5)

admin_btn = tk.Button(top, text="Войти как админ"); admin_btn.pack(side="right", padx=5)
add_btn   = tk.Button(top, text="+ Услуга")
up_btn    = tk.Button(top, text="Ближайшие записи")

# ---------- список услуг (скроллируемый) ----------
mid = tk.Frame(root); mid.pack(fill="both", expand=True, padx=10)
canvas = tk.Canvas(mid, highlightthickness=0)
sb = tk.Scrollbar(mid, command=canvas.yview)
services_frame = tk.Frame(canvas)
services_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0,0), window=services_frame, anchor="nw")
canvas.configure(yscrollcommand=sb.set)
canvas.pack(side="left", fill="both", expand=True)
sb.pack(side="right", fill="y")

counter_label = tk.Label(root, text="", anchor="e")
counter_label.pack(fill="x", padx=10, pady=4)

# ---------- основная логика ----------
def thumb(path, size=(110,110)):
    try:
        img = Image.open(path); img.thumbnail(size)
        return ImageTk.PhotoImage(img)
    except: return None

def draw(rows):
    for w in services_frame.winfo_children(): w.destroy()
    for r in rows:
        disc = r["Discount"] or 0
        bg = "#E8FFE8" if disc > 0 else "white"
        card = tk.Frame(services_frame, bg=bg, bd=1, relief="solid", padx=8, pady=8)
        card.pack(fill="x", pady=4)

        ph = thumb(r["MainImagePath"] or "")
        lbl_img = tk.Label(card, image=ph, bg=bg, width=110, height=110); lbl_img.img = ph
        lbl_img.pack(side="left", padx=6)

        info = tk.Frame(card, bg=bg); info.pack(side="left", fill="both", expand=True)
        tk.Label(info, text=r["Title"], font=("Arial",13,"bold"), bg=bg).pack(anchor="w")
        tk.Label(info, text=f"Длительность: {(r['DurationInSeconds'] or 0)//60} мин", bg=bg).pack(anchor="w")
        tk.Label(info, text=f"Скидка: {int(disc*100)}%", bg=bg).pack(anchor="w")

        price = tk.Frame(card, bg=bg); price.pack(side="right", padx=8)
        cost = float(r["Cost"])
        if disc > 0:
            tk.Label(price, text=f"{cost:.0f} ₽", fg="gray", font=("Arial",10,"overstrike"), bg=bg).pack()
            tk.Label(price, text=f"{cost*(1-disc):.0f} ₽", fg="red", font=("Arial",14,"bold"), bg=bg).pack()
        else:
            tk.Label(price, text=f"{cost:.0f} ₽", font=("Arial",14,"bold"), bg=bg).pack()

        if IS_ADMIN:
            btns = tk.Frame(card, bg=bg); btns.pack(side="right")
            tk.Button(btns, text="Изменить", command=lambda i=r["ID"]: open_edit(i)).pack(fill="x")
            tk.Button(btns, text="Удалить",  command=lambda i=r["ID"]: delete_service(i)).pack(fill="x")
            tk.Button(btns, text="Записать", command=lambda i=r["ID"]: open_booking(i)).pack(fill="x")

def reload():
    rows = db.fetch("SELECT * FROM Service")
    total = len(rows)
    q = search_var.get().lower()
    if q:
        rows = [r for r in rows if q in (r["Title"] or "").lower()
                                or q in (r["Description"] or "").lower()]
    f = filter_var.get()
    if f != "Все":
        lo, hi = map(int, f.split("-"))
        rows = [r for r in rows if lo <= (r["Discount"] or 0)*100 < hi]
    rev = sort_var.get().startswith("По убыванию")
    rows = sorted(rows, key=lambda r: float(r["Cost"]), reverse=rev)
    draw(rows)
    counter_label.config(text=f"{len(rows)} из {total}")

def delete_service(sid):
    if db.fetch("SELECT 1 FROM ClientService WHERE ServiceID=%s LIMIT 1", (sid,)):
        return messagebox.showerror("Ошибка", "Есть записи клиентов — удаление запрещено")
    if not messagebox.askyesno("Подтверждение", "Удалить услугу?"): return
    db.query("DELETE FROM ServicePhoto WHERE ServiceID=%s", (sid,))
    db.query("DELETE FROM Service WHERE ID=%s", (sid,))
    reload()

# ---------- режим админа ----------
def toggle_admin():
    global IS_ADMIN
    if IS_ADMIN:
        IS_ADMIN = False
    else:
        code = simpledialog.askstring("Админ", "Введите код:", show="*")
        if code is None: return
        if code != ADMIN_CODE: return messagebox.showerror("Ошибка","Неверный код")
        IS_ADMIN = True
    refresh_admin_ui()
    reload()

def refresh_admin_ui():
    admin_btn.config(text="Выйти из админа" if IS_ADMIN else "Войти как админ")
    if IS_ADMIN:
        add_btn.pack(side="right", padx=5)
        up_btn.pack(side="right", padx=5)
    else:
        add_btn.pack_forget(); up_btn.pack_forget()

admin_btn.config(command=toggle_admin)
add_btn.config(command=lambda: open_edit(None))
up_btn.config(command=lambda: open_upcoming())

# ---------- окно добавления/редактирования ----------
def open_edit(sid):
    global edit_win
    if edit_win and edit_win.winfo_exists():
        edit_win.lift(); return
    edit_win = tk.Toplevel(root)
    edit_win.title("Услуга"); edit_win.geometry("700x600")

    cur = None
    if sid is not None:
        cur = db.fetch("SELECT * FROM Service WHERE ID=%s",(sid,))[0]

    form = tk.Frame(edit_win); form.pack(fill="x", padx=10, pady=10)
    row = 0
    if sid is not None:
        tk.Label(form, text="ID:").grid(row=row,column=0,sticky="w")
        tk.Entry(form, state="readonly", textvariable=tk.StringVar(value=str(sid))).grid(row=row,column=1,sticky="we"); row+=1

    def add(label, var, w=40):
        nonlocal row
        tk.Label(form, text=label).grid(row=row, column=0, sticky="w")
        e = tk.Entry(form, textvariable=var, width=w); e.grid(row=row, column=1, sticky="we"); row+=1
        return e

    title_v = tk.StringVar(value=cur["Title"] if cur else "")
    cost_v  = tk.StringVar(value=str(cur["Cost"]) if cur else "")
    dur_v   = tk.StringVar(value=str((cur["DurationInSeconds"] or 0)//60) if cur else "")
    disc_v  = tk.StringVar(value=str(cur["Discount"] or 0) if cur else "0")
    img_v   = tk.StringVar(value=(cur["MainImagePath"] if cur else "") or "")

    add("Название:", title_v)
    add("Стоимость, ₽:", cost_v)
    add("Длительность, мин:", dur_v)
    add("Скидка (0..1):", disc_v)

    tk.Label(form, text="Описание:").grid(row=row,column=0,sticky="nw")
    desc_t = tk.Text(form, width=50, height=5); desc_t.grid(row=row,column=1,sticky="we"); row+=1
    if cur and cur["Description"]: desc_t.insert("1.0", cur["Description"])

    tk.Label(form, text="Гл. изображение:").grid(row=row,column=0,sticky="w")
    img_lbl = tk.Label(form); img_lbl.grid(row=row, column=1, sticky="w"); row+=1

    def show_main():
        if img_v.get():
            ph = thumb(img_v.get(),(120,120))
            img_lbl.config(image=ph); img_lbl.img = ph
    show_main()

    def pick_main():
        p = filedialog.askopenfilename(filetypes=[("Images","*.png *.jpg *.jpeg")])
        if not p: return
        dst = os.path.join(IMG_DIR, os.path.basename(p))
        if os.path.abspath(p) != os.path.abspath(dst): shutil.copy(p, dst)
        img_v.set(dst); show_main()

    tk.Button(form, text="Выбрать главное фото", command=pick_main).grid(row=row,column=1,sticky="w"); row+=1

    # доп. фото
    tk.Label(edit_win, text="Дополнительные фото:").pack(anchor="w", padx=10)
    photos_frame = tk.Frame(edit_win); photos_frame.pack(fill="x", padx=10)

    def refresh_photos():
        for w in photos_frame.winfo_children(): w.destroy()
        if sid is None: return
        for ph_row in db.fetch("SELECT * FROM ServicePhoto WHERE ServiceID=%s",(sid,)):
            box = tk.Frame(photos_frame); box.pack(side="left", padx=4)
            ph = thumb(ph_row["PhotoPath"],(70,70))
            l = tk.Label(box, image=ph); l.img = ph; l.pack()
            tk.Button(box, text="✕", command=lambda i=ph_row["ID"]: (db.query("DELETE FROM ServicePhoto WHERE ID=%s",(i,)), refresh_photos())).pack()

    def add_photo():
        if sid is None:
            return messagebox.showinfo("Инфо","Сначала сохраните услугу")
        p = filedialog.askopenfilename(filetypes=[("Images","*.png *.jpg *.jpeg")])
        if not p: return
        dst = os.path.join(IMG_DIR, os.path.basename(p))
        if os.path.abspath(p) != os.path.abspath(dst): shutil.copy(p, dst)
        db.query("INSERT INTO ServicePhoto(ServiceID,PhotoPath) VALUES (%s,%s)",(sid,dst))
        refresh_photos()

    tk.Button(edit_win, text="+ Добавить фото", command=add_photo).pack(anchor="w", padx=10, pady=4)
    refresh_photos()

    def save():
        nonlocal sid
        title = title_v.get().strip()
        if not title: return messagebox.showerror("Ошибка","Введите название")
        try:
            cost = float(cost_v.get()); dur = int(dur_v.get()); disc = float(disc_v.get())
        except: return messagebox.showerror("Ошибка","Проверьте числовые поля")
        if cost <= 0: return messagebox.showerror("Ошибка","Цена должна быть положительной")
        if not (0 < dur <= 240): return messagebox.showerror("Ошибка","Длительность 1..240 минут")
        if not (0 <= disc <= 1): return messagebox.showerror("Ошибка","Скидка от 0 до 1")
        dup_sql = "SELECT 1 FROM Service WHERE Title=%s" + (" AND ID<>%s" if sid else "")
        dup_p = (title, sid) if sid else (title,)
        if db.fetch(dup_sql, dup_p): return messagebox.showerror("Ошибка","Услуга с таким названием уже есть")
        descr = desc_t.get("1.0","end").strip()
        if sid is None:
            sid = db.query("INSERT INTO Service(Title,Cost,DurationInSeconds,Description,Discount,MainImagePath) VALUES (%s,%s,%s,%s,%s,%s)",
                           (title,cost,dur*60,descr,disc,img_v.get() or None))
        else:
            db.query("UPDATE Service SET Title=%s,Cost=%s,DurationInSeconds=%s,Description=%s,Discount=%s,MainImagePath=%s WHERE ID=%s",
                     (title,cost,dur*60,descr,disc,img_v.get() or None, sid))
        reload()
        edit_win.destroy()

    tk.Button(edit_win, text="Сохранить", command=save, bg="#4CAF50", fg="white").pack(pady=10)

# ---------- запись клиента ----------
def open_booking(sid):
    s = db.fetch("SELECT * FROM Service WHERE ID=%s",(sid,))[0]
    w = tk.Toplevel(root); w.title("Запись на услугу"); w.geometry("400x320")
    tk.Label(w, text=f"Услуга: {s['Title']}", font=("Arial",12,"bold")).pack(pady=5)
    tk.Label(w, text=f"Длительность: {s['DurationInSeconds']//60} мин").pack()

    clients = db.fetch("SELECT ID, CONCAT_WS(' ',LastName,FirstName,IFNULL(Patronymic,'')) AS FIO FROM Client ORDER BY LastName")
    cli_map = {c["FIO"]: c["ID"] for c in clients}
    cli_var = tk.StringVar()
    tk.Label(w, text="Клиент:").pack()
    ttk.Combobox(w, textvariable=cli_var, values=list(cli_map.keys()), width=40, state="readonly").pack()

    tk.Label(w, text="Дата (ГГГГ-ММ-ДД):").pack()
    date_v = tk.StringVar(value=date.today().isoformat())
    try:
        from tkcalendar import DateEntry
        DateEntry(w, textvariable=date_v, date_pattern="yyyy-mm-dd").pack()
    except:
        tk.Entry(w, textvariable=date_v).pack()

    tk.Label(w, text="Время начала (ЧЧ:ММ):").pack()
    time_v = tk.StringVar(value="10:00")
    end_lbl = tk.Label(w, text="Окончание: --:--")

    def upd_end(*_):
        try:
            t = datetime.strptime(time_v.get(), "%H:%M")
            end = t + timedelta(seconds=s["DurationInSeconds"])
            end_lbl.config(text=f"Окончание: {end.strftime('%H:%M')}")
        except: end_lbl.config(text="Окончание: --:--")

    e = tk.Entry(w, textvariable=time_v); e.pack()
    time_v.trace_add("write", upd_end); upd_end()
    end_lbl.pack()

    def save():
        if not cli_var.get(): return messagebox.showerror("Ошибка","Выберите клиента")
        if not re.match(r"^\d{1,2}:\d{2}$", time_v.get()): return messagebox.showerror("Ошибка","Время в формате ЧЧ:ММ")
        try: dt = datetime.strptime(f"{date_v.get()} {time_v.get()}","%Y-%m-%d %H:%M")
        except: return messagebox.showerror("Ошибка","Некорректные дата/время")
        db.query("INSERT INTO ClientService(ClientID,ServiceID,StartTime) VALUES (%s,%s,%s)",
                 (cli_map[cli_var.get()], sid, dt))
        messagebox.showinfo("Готово","Запись добавлена"); w.destroy()

    tk.Button(w, text="Сохранить", command=save, bg="#4CAF50", fg="white").pack(pady=10)

# ---------- ближайшие записи ----------
def open_upcoming():
    w = tk.Toplevel(root); w.title("Ближайшие записи"); w.geometry("900x600")
    frame = tk.Frame(w); frame.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh():
        for x in frame.winfo_children(): x.destroy()
        rows = db.fetch("""
            SELECT cs.StartTime, s.Title, s.DurationInSeconds,
                   c.LastName, c.FirstName, c.Patronymic, c.Email, c.Phone
            FROM ClientService cs
            JOIN Service s ON s.ID=cs.ServiceID
            JOIN Client  c ON c.ID=cs.ClientID
            WHERE DATE(cs.StartTime) IN (CURDATE(), CURDATE()+INTERVAL 1 DAY)
            ORDER BY cs.StartTime
        """)
        now = datetime.now()
        for r in rows:
            box = tk.Frame(frame, bd=1, relief="solid", padx=6, pady=4); box.pack(fill="x", pady=3)
            fio = " ".join(filter(None,[r["LastName"], r["FirstName"], r["Patronymic"]]))
            tk.Label(box, text=r["Title"], font=("Arial",11,"bold")).pack(anchor="w")
            tk.Label(box, text=f"Клиент: {fio} | {r['Email'] or ''} | {r['Phone']}").pack(anchor="w")
            tk.Label(box, text=f"Время: {r['StartTime'].strftime('%Y-%m-%d %H:%M')}").pack(anchor="w")
            delta = r["StartTime"] - now
            mins = int(delta.total_seconds() // 60)
            if mins < 0: text, color = "уже началась", "gray"
            else:
                h, m = divmod(mins, 60)
                text = f"осталось {h} ч {m} мин"
                color = "red" if mins < 60 else "black"
            tk.Label(box, text=text, fg=color, font=("Arial",10,"bold")).pack(anchor="w")
        w.after(30000, refresh)

    refresh()

# ---------- запуск ----------
search_var.trace_add("write", lambda *_: reload())
filter_var.trace_add("write", lambda *_: reload())
sort_var.trace_add("write",   lambda *_: reload())

refresh_admin_ui()
reload()
root.mainloop()
