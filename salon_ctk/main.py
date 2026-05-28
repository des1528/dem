"""Салон красоты — CustomTkinter edition.
Те же требования, что в salon/, но с CustomTkinter и стилями М2:
  белый фон, шапка #7FFF00, целевые кнопки #00FA9A,
  карточка скидки > 15% — #2E8B57, шрифт Times New Roman.
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog, simpledialog
from PIL import Image
from datetime import datetime, timedelta, date
import shutil, os, re
import db

# --- константы стиля М2 ---
BG_MAIN     = "#FFFFFF"
BG_ACCENT   = "#7FFF00"
BG_ACTION   = "#00FA9A"
BG_ACTION_H = "#00C97A"        # hover
BG_DISCOUNT = "#2E8B57"
TXT_DARK    = "#1A1A1A"
TXT_LIGHT   = "#FFFFFF"

IMG_DIR     = "images"; os.makedirs(IMG_DIR, exist_ok=True)
ADMIN_CODE  = "0000"
IS_ADMIN    = False
edit_win    = None

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

root = ctk.CTk()
root.title("Салон красоты")
root.geometry("1200x780")
root.configure(fg_color=BG_MAIN)

F_TITLE  = ctk.CTkFont(family="Times New Roman", size=20, weight="bold")
F_HEAD   = ctk.CTkFont(family="Times New Roman", size=14, weight="bold")
F_NORMAL = ctk.CTkFont(family="Times New Roman", size=13)
F_SMALL  = ctk.CTkFont(family="Times New Roman", size=12)

# ---------- шапка ----------
top = ctk.CTkFrame(root, fg_color=BG_ACCENT, corner_radius=0, height=64)
top.pack(fill="x"); top.pack_propagate(False)
ctk.CTkLabel(top, text="✨  Салон красоты", font=F_TITLE, text_color=TXT_DARK).pack(side="left", padx=20)

admin_btn = ctk.CTkButton(top, text="Войти как админ", font=F_NORMAL,
                          fg_color=BG_ACTION, text_color=TXT_DARK, hover_color=BG_ACTION_H,
                          corner_radius=8, height=36)
admin_btn.pack(side="right", padx=10)
add_btn = ctk.CTkButton(top, text="+ Услуга", font=F_NORMAL,
                        fg_color=BG_ACTION, text_color=TXT_DARK, hover_color=BG_ACTION_H,
                        corner_radius=8, height=36)
up_btn  = ctk.CTkButton(top, text="Ближайшие записи", font=F_NORMAL,
                        fg_color=BG_ACTION, text_color=TXT_DARK, hover_color=BG_ACTION_H,
                        corner_radius=8, height=36)

# ---------- панель управления ----------
pan = ctk.CTkFrame(root, fg_color=BG_MAIN, corner_radius=0)
pan.pack(fill="x", padx=16, pady=10)

search_var = ctk.StringVar()
filter_var = ctk.StringVar(value="Все")
sort_var   = ctk.StringVar(value="По возрастанию цены")

ctk.CTkLabel(pan, text="Поиск:", font=F_NORMAL, text_color=TXT_DARK).pack(side="left")
ctk.CTkEntry(pan, textvariable=search_var, font=F_NORMAL, width=260, height=34,
             corner_radius=8, border_color=BG_ACCENT, border_width=2).pack(side="left", padx=8)
ctk.CTkLabel(pan, text="Скидка:", font=F_NORMAL, text_color=TXT_DARK).pack(side="left", padx=(8,2))
ctk.CTkOptionMenu(pan, variable=filter_var, width=110, height=34, corner_radius=8,
                  fg_color=BG_ACCENT, button_color=BG_ACCENT, button_hover_color=BG_ACTION_H,
                  text_color=TXT_DARK, font=F_NORMAL,
                  values=["Все","0-5","5-15","15-30","30-70","70-100"]).pack(side="left", padx=4)
ctk.CTkLabel(pan, text="Сортировка:", font=F_NORMAL, text_color=TXT_DARK).pack(side="left", padx=(8,2))
ctk.CTkOptionMenu(pan, variable=sort_var, width=210, height=34, corner_radius=8,
                  fg_color=BG_ACCENT, button_color=BG_ACCENT, button_hover_color=BG_ACTION_H,
                  text_color=TXT_DARK, font=F_NORMAL,
                  values=["По возрастанию цены","По убыванию цены"]).pack(side="left", padx=4)

# ---------- список карточек (скроллируемый) ----------
list_frame = ctk.CTkScrollableFrame(root, fg_color=BG_MAIN, corner_radius=0)
list_frame.pack(fill="both", expand=True, padx=16, pady=(0,6))

counter_label = ctk.CTkLabel(root, text="", font=F_SMALL, text_color=TXT_DARK, anchor="e")
counter_label.pack(fill="x", padx=20, pady=(0,8))

# ---------- утилиты ----------
def thumb(path, size=(120,120)):
    try:
        im = Image.open(path); im.thumbnail(size)
        return ctk.CTkImage(light_image=im, size=im.size)
    except: return None

def card_colors(disc):
    if disc * 100 > 15:
        return BG_DISCOUNT, TXT_LIGHT, "#256E47"
    return "#F7FFF7", TXT_DARK, "#D9F2E0"

def draw(rows):
    for w in list_frame.winfo_children(): w.destroy()
    for r in rows:
        disc = r["Discount"] or 0
        bg, fg, accent = card_colors(disc)
        card = ctk.CTkFrame(list_frame, fg_color=bg, corner_radius=14, border_width=1, border_color=accent)
        card.pack(fill="x", pady=6, padx=4)

        ph = thumb(r["MainImagePath"] or "")
        img_lbl = ctk.CTkLabel(card, image=ph, text="" if ph else "🖼", font=F_TITLE, width=130, height=130,
                               fg_color=accent, corner_radius=10, text_color=fg)
        img_lbl.pack(side="left", padx=12, pady=12)

        info = ctk.CTkFrame(card, fg_color="transparent"); info.pack(side="left", fill="both", expand=True, pady=12)
        ctk.CTkLabel(info, text=r["Title"], font=F_HEAD, text_color=fg, anchor="w").pack(anchor="w")
        ctk.CTkLabel(info, text=f"⏱  {(r['DurationInSeconds'] or 0)//60} мин", font=F_NORMAL, text_color=fg).pack(anchor="w", pady=(4,0))
        if disc > 0:
            ctk.CTkLabel(info, text=f"🎉 Скидка {int(disc*100)}%", font=F_NORMAL, text_color=fg).pack(anchor="w")
        descr = (r["Description"] or "")[:140]
        if descr:
            ctk.CTkLabel(info, text=descr, font=F_SMALL, text_color=fg, wraplength=560, justify="left").pack(anchor="w", pady=(4,0))

        price = ctk.CTkFrame(card, fg_color="transparent"); price.pack(side="right", padx=16)
        cost = float(r["Cost"])
        if disc > 0:
            ctk.CTkLabel(price, text=f"{cost:.0f} ₽", font=ctk.CTkFont(family="Times New Roman", size=12, overstrike=True),
                         text_color=fg).pack()
            ctk.CTkLabel(price, text=f"{cost*(1-disc):.0f} ₽",
                         font=ctk.CTkFont(family="Times New Roman", size=20, weight="bold"),
                         text_color=fg).pack()
        else:
            ctk.CTkLabel(price, text=f"{cost:.0f} ₽",
                         font=ctk.CTkFont(family="Times New Roman", size=20, weight="bold"),
                         text_color=fg).pack()

        if IS_ADMIN:
            btns = ctk.CTkFrame(card, fg_color="transparent"); btns.pack(side="right", padx=8)
            for txt, fn, action in (("Изм.", lambda i=r["ID"]: open_edit(i), False),
                                    ("Запис.", lambda i=r["ID"]: open_booking(i), True),
                                    ("Удал.", lambda i=r["ID"]: delete_service(i), False)):
                ctk.CTkButton(btns, text=txt, font=F_SMALL, width=70, height=30, corner_radius=8,
                              fg_color=BG_ACTION if action else "#E0E0E0",
                              text_color=TXT_DARK, hover_color=BG_ACTION_H if action else "#C8C8C8",
                              command=fn).pack(pady=2)

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
    rows = sorted(rows, key=lambda r: float(r["Cost"]),
                  reverse=sort_var.get().startswith("По убыванию"))
    draw(rows)
    counter_label.configure(text=f"Показано: {len(rows)} из {total}")

# ---------- действия ----------
def delete_service(sid):
    if db.fetch("SELECT 1 FROM ClientService WHERE ServiceID=%s LIMIT 1", (sid,)):
        return messagebox.showerror("Ошибка", "Есть записи клиентов — удаление запрещено")
    if not messagebox.askyesno("Подтверждение", "Удалить услугу?"): return
    db.query("DELETE FROM ServicePhoto WHERE ServiceID=%s", (sid,))
    db.query("DELETE FROM Service WHERE ID=%s", (sid,))
    reload()

def toggle_admin():
    global IS_ADMIN
    if IS_ADMIN:
        IS_ADMIN = False
    else:
        code = simpledialog.askstring("Админ", "Введите код:", show="*")
        if code is None: return
        if code != ADMIN_CODE: return messagebox.showerror("Ошибка", "Неверный код")
        IS_ADMIN = True
    refresh_admin_ui()
    reload()

def refresh_admin_ui():
    admin_btn.configure(text=("Выйти из админа" if IS_ADMIN else "Войти как админ"))
    if IS_ADMIN:
        up_btn.pack(side="right", padx=6); add_btn.pack(side="right", padx=6)
    else:
        up_btn.pack_forget(); add_btn.pack_forget()

admin_btn.configure(command=toggle_admin)
add_btn.configure(command=lambda: open_edit(None))
up_btn.configure(command=lambda: open_upcoming())

# ---------- окно добавления/редактирования ----------
def open_edit(sid):
    global edit_win
    if edit_win and edit_win.winfo_exists(): edit_win.lift(); return
    edit_win = ctk.CTkToplevel(root); edit_win.title("Услуга")
    edit_win.geometry("720x720"); edit_win.configure(fg_color=BG_MAIN)
    edit_win.transient(root); edit_win.lift(); edit_win.focus()

    cur = db.fetch("SELECT * FROM Service WHERE ID=%s",(sid,))[0] if sid else None
    form = ctk.CTkFrame(edit_win, fg_color=BG_MAIN); form.pack(fill="x", padx=20, pady=14)

    title_v = ctk.StringVar(value=cur["Title"] if cur else "")
    cost_v  = ctk.StringVar(value=str(cur["Cost"]) if cur else "")
    dur_v   = ctk.StringVar(value=str((cur["DurationInSeconds"] or 0)//60) if cur else "")
    disc_v  = ctk.StringVar(value=str(cur["Discount"] or 0) if cur else "0")
    img_v   = ctk.StringVar(value=(cur["MainImagePath"] if cur else "") or "")

    row = [0]
    def lbl(text):
        ctk.CTkLabel(form, text=text, font=F_NORMAL, text_color=TXT_DARK).grid(row=row[0], column=0, sticky="w", pady=4)
    def entry(var):
        e = ctk.CTkEntry(form, textvariable=var, font=F_NORMAL, width=420, height=34, corner_radius=8,
                         border_color=BG_ACCENT, border_width=2)
        e.grid(row=row[0], column=1, sticky="we", padx=8, pady=4); row[0]+=1

    if sid:
        lbl("ID:")
        ctk.CTkEntry(form, textvariable=ctk.StringVar(value=str(sid)), state="readonly",
                     font=F_NORMAL, width=420, height=34, corner_radius=8).grid(row=row[0], column=1, sticky="we", padx=8); row[0]+=1
    lbl("Название:"); entry(title_v)
    lbl("Стоимость, ₽:"); entry(cost_v)
    lbl("Длительность, мин:"); entry(dur_v)
    lbl("Скидка (0..1):"); entry(disc_v)
    lbl("Описание:")
    desc_t = ctk.CTkTextbox(form, width=420, height=110, font=F_NORMAL, corner_radius=8,
                            border_color=BG_ACCENT, border_width=2)
    desc_t.grid(row=row[0], column=1, sticky="we", padx=8, pady=4); row[0]+=1
    if cur and cur["Description"]: desc_t.insert("1.0", cur["Description"])

    lbl("Изображение:")
    img_box = ctk.CTkFrame(form, fg_color=BG_MAIN); img_box.grid(row=row[0], column=1, sticky="we", padx=8); row[0]+=1
    img_lbl = ctk.CTkLabel(img_box, text="нет фото", width=160, height=160,
                           fg_color="#F0F0F0", corner_radius=10, text_color=TXT_DARK, font=F_SMALL)
    img_lbl.pack(side="left")

    def show_main():
        if img_v.get() and os.path.exists(img_v.get()):
            ph = thumb(img_v.get(), (160,160))
            img_lbl.configure(image=ph, text=""); img_lbl.image = ph
    show_main()

    def pick_main():
        p = filedialog.askopenfilename(filetypes=[("Images","*.png *.jpg *.jpeg")])
        if not p: return
        dst = os.path.join(IMG_DIR, os.path.basename(p))
        if os.path.abspath(p) != os.path.abspath(dst): shutil.copy(p, dst)
        img_v.set(dst); show_main()

    ctk.CTkButton(img_box, text="Выбрать фото", font=F_NORMAL, fg_color=BG_ACTION,
                  text_color=TXT_DARK, hover_color=BG_ACTION_H, corner_radius=8,
                  command=pick_main).pack(side="left", padx=8)

    # доп. фото
    ctk.CTkLabel(edit_win, text="Дополнительные фото:", font=F_NORMAL, text_color=TXT_DARK).pack(anchor="w", padx=20)
    photos_frame = ctk.CTkFrame(edit_win, fg_color=BG_MAIN); photos_frame.pack(fill="x", padx=20, pady=4)

    def refresh_photos():
        for w in photos_frame.winfo_children(): w.destroy()
        if sid is None: return
        for ph_row in db.fetch("SELECT * FROM ServicePhoto WHERE ServiceID=%s",(sid,)):
            box = ctk.CTkFrame(photos_frame, fg_color="transparent"); box.pack(side="left", padx=6)
            ph = thumb(ph_row["PhotoPath"], (80,80))
            ctk.CTkLabel(box, image=ph, text="").pack(); box._img = ph
            ctk.CTkButton(box, text="✕", font=F_SMALL, width=24, height=20, corner_radius=6,
                          fg_color="#FF6B6B", hover_color="#E04545", text_color="white",
                          command=lambda i=ph_row["ID"]: (db.query("DELETE FROM ServicePhoto WHERE ID=%s",(i,)), refresh_photos())).pack()

    def add_photo():
        if sid is None: return messagebox.showinfo("Инфо", "Сначала сохраните услугу")
        p = filedialog.askopenfilename(filetypes=[("Images","*.png *.jpg *.jpeg")])
        if not p: return
        dst = os.path.join(IMG_DIR, os.path.basename(p))
        if os.path.abspath(p) != os.path.abspath(dst): shutil.copy(p, dst)
        db.query("INSERT INTO ServicePhoto(ServiceID,PhotoPath) VALUES (%s,%s)",(sid, dst))
        refresh_photos()

    ctk.CTkButton(edit_win, text="+ Добавить фото", font=F_NORMAL, fg_color=BG_ACCENT,
                  text_color=TXT_DARK, hover_color=BG_ACTION, corner_radius=8,
                  command=add_photo).pack(anchor="w", padx=20, pady=6)
    refresh_photos()

    def save():
        nonlocal sid
        title = title_v.get().strip()
        if not title: return messagebox.showerror("Ошибка","Введите название")
        try: cost=float(cost_v.get()); dur=int(dur_v.get()); disc=float(disc_v.get())
        except: return messagebox.showerror("Ошибка","Проверьте числовые поля")
        if cost <= 0: return messagebox.showerror("Ошибка","Цена должна быть положительной")
        if not (0 < dur <= 240): return messagebox.showerror("Ошибка","Длительность 1..240 минут")
        if not (0 <= disc <= 1): return messagebox.showerror("Ошибка","Скидка от 0 до 1")
        dup_sql = "SELECT 1 FROM Service WHERE Title=%s" + (" AND ID<>%s" if sid else "")
        if db.fetch(dup_sql, (title, sid) if sid else (title,)):
            return messagebox.showerror("Ошибка","Услуга с таким названием уже есть")
        descr = desc_t.get("1.0","end").strip()
        if sid is None:
            sid = db.query("INSERT INTO Service(Title,Cost,DurationInSeconds,Description,Discount,MainImagePath) VALUES (%s,%s,%s,%s,%s,%s)",
                           (title,cost,dur*60,descr,disc,img_v.get() or None))
        else:
            db.query("UPDATE Service SET Title=%s,Cost=%s,DurationInSeconds=%s,Description=%s,Discount=%s,MainImagePath=%s WHERE ID=%s",
                     (title,cost,dur*60,descr,disc,img_v.get() or None, sid))
        reload(); edit_win.destroy()

    ctk.CTkButton(edit_win, text="💾  Сохранить", font=F_HEAD, fg_color=BG_ACTION,
                  text_color=TXT_DARK, hover_color=BG_ACTION_H, corner_radius=10, height=44,
                  command=save).pack(pady=14, padx=20, fill="x")

# ---------- запись клиента ----------
def open_booking(sid):
    s = db.fetch("SELECT * FROM Service WHERE ID=%s",(sid,))[0]
    w = ctk.CTkToplevel(root); w.title("Запись на услугу")
    w.geometry("440x420"); w.configure(fg_color=BG_MAIN)
    w.transient(root); w.lift(); w.focus()

    ctk.CTkLabel(w, text=s["Title"], font=F_TITLE, text_color=TXT_DARK).pack(pady=(16,4))
    ctk.CTkLabel(w, text=f"Длительность: {s['DurationInSeconds']//60} мин",
                 font=F_NORMAL, text_color=TXT_DARK).pack()

    box = ctk.CTkFrame(w, fg_color=BG_MAIN); box.pack(fill="x", padx=20, pady=10)
    clients = db.fetch("SELECT ID, CONCAT_WS(' ',LastName,FirstName,IFNULL(Patronymic,'')) AS FIO FROM Client ORDER BY LastName")
    cli_map = {c["FIO"]: c["ID"] for c in clients}
    cli_var = ctk.StringVar(value=list(cli_map.keys())[0] if cli_map else "")

    ctk.CTkLabel(box, text="Клиент:", font=F_NORMAL, text_color=TXT_DARK, anchor="w").pack(fill="x")
    ctk.CTkOptionMenu(box, variable=cli_var, values=list(cli_map.keys()) or [""], font=F_NORMAL,
                      width=400, corner_radius=8, fg_color=BG_ACCENT, button_color=BG_ACCENT,
                      button_hover_color=BG_ACTION_H, text_color=TXT_DARK).pack(fill="x")

    ctk.CTkLabel(box, text="Дата (ГГГГ-ММ-ДД):", font=F_NORMAL, text_color=TXT_DARK, anchor="w").pack(fill="x", pady=(8,0))
    date_v = ctk.StringVar(value=date.today().isoformat())
    ctk.CTkEntry(box, textvariable=date_v, font=F_NORMAL, height=34, corner_radius=8,
                 border_color=BG_ACCENT, border_width=2).pack(fill="x")

    ctk.CTkLabel(box, text="Время (ЧЧ:ММ):", font=F_NORMAL, text_color=TXT_DARK, anchor="w").pack(fill="x", pady=(8,0))
    time_v = ctk.StringVar(value="10:00")
    ctk.CTkEntry(box, textvariable=time_v, font=F_NORMAL, height=34, corner_radius=8,
                 border_color=BG_ACCENT, border_width=2).pack(fill="x")

    end_lbl = ctk.CTkLabel(box, text="Окончание: —:—", font=F_NORMAL, text_color=TXT_DARK)
    end_lbl.pack(pady=(6,0))

    def upd_end(*_):
        try:
            t = datetime.strptime(time_v.get(), "%H:%M")
            end = t + timedelta(seconds=s["DurationInSeconds"])
            end_lbl.configure(text=f"Окончание: {end.strftime('%H:%M')}")
        except: end_lbl.configure(text="Окончание: —:—")
    time_v.trace_add("write", upd_end); upd_end()

    def save():
        if not cli_var.get(): return messagebox.showerror("Ошибка","Выберите клиента")
        if not re.match(r"^\d{1,2}:\d{2}$", time_v.get()):
            return messagebox.showerror("Ошибка","Время в формате ЧЧ:ММ")
        try: dt = datetime.strptime(f"{date_v.get()} {time_v.get()}", "%Y-%m-%d %H:%M")
        except: return messagebox.showerror("Ошибка","Некорректные дата/время")
        db.query("INSERT INTO ClientService(ClientID,ServiceID,StartTime) VALUES (%s,%s,%s)",
                 (cli_map[cli_var.get()], sid, dt))
        messagebox.showinfo("Готово","Запись добавлена"); w.destroy()

    ctk.CTkButton(w, text="💾  Сохранить", font=F_HEAD, fg_color=BG_ACTION, text_color=TXT_DARK,
                  hover_color=BG_ACTION_H, corner_radius=10, height=42,
                  command=save).pack(pady=10, padx=20, fill="x")

# ---------- ближайшие записи ----------
def open_upcoming():
    w = ctk.CTkToplevel(root); w.title("Ближайшие записи")
    w.geometry("960x640"); w.configure(fg_color=BG_MAIN)
    w.transient(root); w.lift()
    frame = ctk.CTkScrollableFrame(w, fg_color=BG_MAIN); frame.pack(fill="both", expand=True, padx=14, pady=14)

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
        if not rows:
            ctk.CTkLabel(frame, text="Записей на сегодня и завтра нет.",
                         font=F_NORMAL, text_color=TXT_DARK).pack(pady=20); return
        for r in rows:
            delta = r["StartTime"] - now
            mins = int(delta.total_seconds() // 60)
            if mins < 0:
                badge_text, badge_bg = "началась", "#9E9E9E"
            else:
                h, m = divmod(mins, 60)
                badge_text = f"{h} ч {m} мин"
                badge_bg = "#E64545" if mins < 60 else BG_DISCOUNT
            card = ctk.CTkFrame(frame, fg_color=BG_MAIN, border_color="#D9F2E0",
                                border_width=1, corner_radius=12)
            card.pack(fill="x", pady=5, padx=4)
            left = ctk.CTkFrame(card, fg_color="transparent"); left.pack(side="left", fill="both", expand=True, padx=14, pady=10)
            ctk.CTkLabel(left, text=r["Title"], font=F_HEAD, text_color=TXT_DARK, anchor="w").pack(anchor="w")
            fio = " ".join(filter(None,[r["LastName"], r["FirstName"], r["Patronymic"]]))
            ctk.CTkLabel(left, text=f"👤  {fio}", font=F_NORMAL, text_color=TXT_DARK).pack(anchor="w")
            ctk.CTkLabel(left, text=f"📞  {r['Phone']}    ✉  {r['Email'] or '—'}",
                         font=F_SMALL, text_color=TXT_DARK).pack(anchor="w")
            ctk.CTkLabel(left, text=f"🗓  {r['StartTime'].strftime('%Y-%m-%d %H:%M')}",
                         font=F_SMALL, text_color=TXT_DARK).pack(anchor="w")
            ctk.CTkLabel(card, text=badge_text, font=F_HEAD, text_color="white",
                         fg_color=badge_bg, corner_radius=10, width=120, height=36).pack(side="right", padx=14, pady=10)
        w.after(30_000, refresh)

    refresh()

# ---------- запуск ----------
search_var.trace_add("write", lambda *_: reload())
filter_var.trace_add("write", lambda *_: reload())
sort_var.trace_add("write",   lambda *_: reload())

refresh_admin_ui()
reload()
root.mainloop()
