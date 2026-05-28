"""Салон красоты — CustomTkinter edition.
Сдержанная палитра в рамках требований М2:
  основной фон — белый,
  #7FFF00 — тонкий акцент-полоса в шапке (дополнительный фон),
  #00FA9A — целевые кнопки,
  #2E8B57 — фон карточки при скидке > 15% и брендовый цвет шапки/акцентов,
  шрифт — Times New Roman.
Декоративные эмодзи не используются.
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog, simpledialog
from PIL import Image
from datetime import datetime, timedelta, date
import shutil, os, re
import db

# --- палитра М2 (сдержанная) ---
BG_MAIN     = "#FFFFFF"
BG_PANEL    = "#F6F8F6"   # нейтральная подложка карточек / форм
BG_ACCENT   = "#7FFF00"   # дополнительный фон — тонкая полоса в шапке
BG_ACTION   = "#00FA9A"   # целевые кнопки
BG_ACTION_H = "#00C97A"   # hover
BG_BRAND    = "#2E8B57"   # текст в шапке, бордеры, фон карточки скидки > 15%
BG_BRAND_H  = "#256E47"
BORDER      = "#D9DDD9"   # тонкие рамки
TXT_DARK    = "#1F1F1F"
TXT_MUTED   = "#5A6660"
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

F_TITLE  = ctk.CTkFont(family="Times New Roman", size=22, weight="bold")
F_HEAD   = ctk.CTkFont(family="Times New Roman", size=15, weight="bold")
F_NORMAL = ctk.CTkFont(family="Times New Roman", size=13)
F_SMALL  = ctk.CTkFont(family="Times New Roman", size=12)
F_PRICE  = ctk.CTkFont(family="Times New Roman", size=20, weight="bold")

# ---------- шапка: белая, с тонкой #7FFF00-полосой снизу ----------
header_wrap = ctk.CTkFrame(root, fg_color=BG_MAIN, corner_radius=0)
header_wrap.pack(fill="x")

header = ctk.CTkFrame(header_wrap, fg_color=BG_MAIN, corner_radius=0, height=70)
header.pack(fill="x"); header.pack_propagate(False)

ctk.CTkLabel(header, text="Салон красоты", font=F_TITLE, text_color=BG_BRAND).pack(side="left", padx=24)

admin_btn = ctk.CTkButton(header, text="Войти как админ", font=F_NORMAL,
                          fg_color=BG_PANEL, text_color=BG_BRAND, hover_color="#E5EBE6",
                          border_color=BG_BRAND, border_width=1, corner_radius=8, height=36)
admin_btn.pack(side="right", padx=8)
add_btn = ctk.CTkButton(header, text="Добавить услугу", font=F_NORMAL,
                        fg_color=BG_ACTION, text_color=TXT_DARK, hover_color=BG_ACTION_H,
                        corner_radius=8, height=36)
up_btn  = ctk.CTkButton(header, text="Ближайшие записи", font=F_NORMAL,
                        fg_color=BG_BRAND, text_color=TXT_LIGHT, hover_color=BG_BRAND_H,
                        corner_radius=8, height=36)

# тонкая полоса дополнительного фона #7FFF00
ctk.CTkFrame(header_wrap, fg_color=BG_ACCENT, height=4, corner_radius=0).pack(fill="x")

# ---------- панель управления ----------
pan = ctk.CTkFrame(root, fg_color=BG_MAIN, corner_radius=0)
pan.pack(fill="x", padx=20, pady=(14,8))

search_var = ctk.StringVar()
filter_var = ctk.StringVar(value="Все")
sort_var   = ctk.StringVar(value="По возрастанию цены")

ctk.CTkLabel(pan, text="Поиск:", font=F_NORMAL, text_color=TXT_DARK).pack(side="left")
ctk.CTkEntry(pan, textvariable=search_var, font=F_NORMAL, width=260, height=34,
             corner_radius=8, border_color=BORDER, border_width=1,
             fg_color=BG_MAIN, text_color=TXT_DARK).pack(side="left", padx=(8,16))

ctk.CTkLabel(pan, text="Скидка:", font=F_NORMAL, text_color=TXT_DARK).pack(side="left", padx=(0,4))
ctk.CTkOptionMenu(pan, variable=filter_var, width=120, height=34, corner_radius=8,
                  fg_color=BG_PANEL, button_color=BG_PANEL, button_hover_color="#E5EBE6",
                  text_color=TXT_DARK, font=F_NORMAL, dropdown_font=F_NORMAL,
                  values=["Все","0-5","5-15","15-30","30-70","70-100"]).pack(side="left", padx=(0,16))

ctk.CTkLabel(pan, text="Сортировка:", font=F_NORMAL, text_color=TXT_DARK).pack(side="left", padx=(0,4))
ctk.CTkOptionMenu(pan, variable=sort_var, width=220, height=34, corner_radius=8,
                  fg_color=BG_PANEL, button_color=BG_PANEL, button_hover_color="#E5EBE6",
                  text_color=TXT_DARK, font=F_NORMAL, dropdown_font=F_NORMAL,
                  values=["По возрастанию цены","По убыванию цены"]).pack(side="left")

# ---------- список карточек ----------
list_frame = ctk.CTkScrollableFrame(root, fg_color=BG_MAIN, corner_radius=0,
                                    scrollbar_button_color=BORDER, scrollbar_button_hover_color=BG_BRAND)
list_frame.pack(fill="both", expand=True, padx=20, pady=(0,6))

counter_label = ctk.CTkLabel(root, text="", font=F_SMALL, text_color=TXT_MUTED, anchor="e")
counter_label.pack(fill="x", padx=24, pady=(0,10))

# ---------- утилиты ----------
def thumb(path, size=(120,120)):
    try:
        im = Image.open(path); im.thumbnail(size)
        return ctk.CTkImage(light_image=im, size=im.size)
    except: return None

def draw(rows):
    for w in list_frame.winfo_children(): w.destroy()
    for r in rows:
        disc = r["Discount"] or 0
        if disc * 100 > 15:
            bg, fg, sub, border = BG_BRAND, TXT_LIGHT, "#D6E9DE", BG_BRAND_H
        else:
            bg, fg, sub, border = BG_MAIN, TXT_DARK, TXT_MUTED, BORDER

        card = ctk.CTkFrame(list_frame, fg_color=bg, corner_radius=12,
                            border_width=1, border_color=border)
        card.pack(fill="x", pady=6, padx=2)

        ph = thumb(r["MainImagePath"] or "")
        img_holder = ctk.CTkFrame(card, fg_color=BG_PANEL if bg == BG_MAIN else BG_BRAND_H,
                                  corner_radius=10, width=134, height=134)
        img_holder.pack(side="left", padx=14, pady=14); img_holder.pack_propagate(False)
        ctk.CTkLabel(img_holder, image=ph, text="" if ph else "нет фото",
                     font=F_SMALL, text_color=sub).pack(expand=True)

        info = ctk.CTkFrame(card, fg_color="transparent"); info.pack(side="left", fill="both", expand=True, pady=14)
        ctk.CTkLabel(info, text=r["Title"], font=F_HEAD, text_color=fg, anchor="w").pack(anchor="w")
        ctk.CTkLabel(info, text=f"Длительность: {(r['DurationInSeconds'] or 0)//60} мин",
                     font=F_NORMAL, text_color=sub, anchor="w").pack(anchor="w", pady=(4,0))
        if disc > 0:
            ctk.CTkLabel(info, text=f"Скидка: {int(disc*100)} %",
                         font=F_NORMAL, text_color=sub, anchor="w").pack(anchor="w")
        descr = (r["Description"] or "").strip()
        if descr:
            ctk.CTkLabel(info, text=descr[:160], font=F_SMALL, text_color=sub,
                         wraplength=560, justify="left", anchor="w").pack(anchor="w", pady=(6,0))

        price_box = ctk.CTkFrame(card, fg_color="transparent"); price_box.pack(side="right", padx=18)
        cost = float(r["Cost"])
        if disc > 0:
            ctk.CTkLabel(price_box, text=f"{cost:.0f} ₽",
                         font=ctk.CTkFont(family="Times New Roman", size=12, overstrike=True),
                         text_color=sub).pack(anchor="e")
            ctk.CTkLabel(price_box, text=f"{cost*(1-disc):.0f} ₽",
                         font=F_PRICE, text_color=fg).pack(anchor="e")
        else:
            ctk.CTkLabel(price_box, text=f"{cost:.0f} ₽",
                         font=F_PRICE, text_color=fg).pack(anchor="e")

        if IS_ADMIN:
            btns = ctk.CTkFrame(card, fg_color="transparent"); btns.pack(side="right", padx=(0,12))
            for txt, fn, action in (("Изменить",  lambda i=r["ID"]: open_edit(i),     False),
                                    ("Записать",  lambda i=r["ID"]: open_booking(i),  True),
                                    ("Удалить",   lambda i=r["ID"]: delete_service(i), False)):
                if action:
                    fgc, txt_color, hvr = BG_ACTION, TXT_DARK, BG_ACTION_H
                else:
                    fgc = BG_PANEL if bg == BG_MAIN else BG_BRAND_H
                    txt_color = TXT_DARK if bg == BG_MAIN else TXT_LIGHT
                    hvr = "#E5EBE6" if bg == BG_MAIN else "#1E5A38"
                ctk.CTkButton(btns, text=txt, font=F_SMALL, width=92, height=30, corner_radius=8,
                              fg_color=fgc, text_color=txt_color, hover_color=hvr,
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
        code = simpledialog.askstring("Админ", "Введите код доступа:", show="*")
        if code is None: return
        if code != ADMIN_CODE: return messagebox.showerror("Ошибка", "Неверный код")
        IS_ADMIN = True
    refresh_admin_ui()
    reload()

def refresh_admin_ui():
    admin_btn.configure(text=("Выйти из режима администратора" if IS_ADMIN else "Войти как админ"))
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
    edit_win.geometry("760x760"); edit_win.configure(fg_color=BG_MAIN)
    edit_win.transient(root); edit_win.lift(); edit_win.focus()

    # шапка модалки
    hd = ctk.CTkFrame(edit_win, fg_color=BG_MAIN, height=56, corner_radius=0); hd.pack(fill="x"); hd.pack_propagate(False)
    ctk.CTkLabel(hd, text=("Редактирование услуги" if sid else "Новая услуга"),
                 font=F_HEAD, text_color=BG_BRAND).pack(side="left", padx=20)
    ctk.CTkFrame(edit_win, fg_color=BG_ACCENT, height=3, corner_radius=0).pack(fill="x")

    cur = db.fetch("SELECT * FROM Service WHERE ID=%s",(sid,))[0] if sid else None
    form = ctk.CTkFrame(edit_win, fg_color=BG_MAIN); form.pack(fill="x", padx=24, pady=14)

    title_v = ctk.StringVar(value=cur["Title"] if cur else "")
    cost_v  = ctk.StringVar(value=str(cur["Cost"]) if cur else "")
    dur_v   = ctk.StringVar(value=str((cur["DurationInSeconds"] or 0)//60) if cur else "")
    disc_v  = ctk.StringVar(value=str(cur["Discount"] or 0) if cur else "0")
    img_v   = ctk.StringVar(value=(cur["MainImagePath"] if cur else "") or "")

    row = [0]
    def lbl(text):
        ctk.CTkLabel(form, text=text, font=F_NORMAL, text_color=TXT_MUTED).grid(row=row[0], column=0, sticky="w", pady=5)
    def entry(var, readonly=False):
        e = ctk.CTkEntry(form, textvariable=var, font=F_NORMAL, width=440, height=34, corner_radius=8,
                         border_color=BORDER, border_width=1, fg_color=BG_MAIN, text_color=TXT_DARK)
        if readonly: e.configure(state="readonly")
        e.grid(row=row[0], column=1, sticky="we", padx=10, pady=5); row[0]+=1

    if sid:
        lbl("ID:"); entry(ctk.StringVar(value=str(sid)), readonly=True)
    lbl("Название:"); entry(title_v)
    lbl("Стоимость, ₽:"); entry(cost_v)
    lbl("Длительность, мин:"); entry(dur_v)
    lbl("Скидка (0..1):"); entry(disc_v)

    lbl("Описание:")
    desc_t = ctk.CTkTextbox(form, width=440, height=110, font=F_NORMAL, corner_radius=8,
                            border_color=BORDER, border_width=1, fg_color=BG_MAIN, text_color=TXT_DARK)
    desc_t.grid(row=row[0], column=1, sticky="we", padx=10, pady=5); row[0]+=1
    if cur and cur["Description"]: desc_t.insert("1.0", cur["Description"])

    lbl("Изображение:")
    img_box = ctk.CTkFrame(form, fg_color=BG_MAIN); img_box.grid(row=row[0], column=1, sticky="we", padx=10); row[0]+=1
    img_lbl = ctk.CTkLabel(img_box, text="нет фото", width=160, height=160,
                           fg_color=BG_PANEL, corner_radius=10, text_color=TXT_MUTED, font=F_SMALL)
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

    ctk.CTkButton(img_box, text="Выбрать файл", font=F_NORMAL, fg_color=BG_PANEL,
                  text_color=TXT_DARK, hover_color="#E5EBE6", border_color=BORDER, border_width=1,
                  corner_radius=8, command=pick_main).pack(side="left", padx=10)

    # доп. фото
    ctk.CTkLabel(edit_win, text="Дополнительные фотографии", font=F_NORMAL,
                 text_color=TXT_MUTED).pack(anchor="w", padx=24, pady=(8,0))
    photos_frame = ctk.CTkFrame(edit_win, fg_color=BG_MAIN); photos_frame.pack(fill="x", padx=24, pady=4)

    def refresh_photos():
        for w in photos_frame.winfo_children(): w.destroy()
        if sid is None: return
        for ph_row in db.fetch("SELECT * FROM ServicePhoto WHERE ServiceID=%s",(sid,)):
            box = ctk.CTkFrame(photos_frame, fg_color="transparent"); box.pack(side="left", padx=6)
            ph = thumb(ph_row["PhotoPath"], (80,80))
            holder = ctk.CTkFrame(box, fg_color=BG_PANEL, corner_radius=8, width=84, height=84)
            holder.pack(); holder.pack_propagate(False)
            ctk.CTkLabel(holder, image=ph, text="").pack(expand=True); holder._img = ph
            ctk.CTkButton(box, text="Удалить", font=F_SMALL, width=80, height=22, corner_radius=6,
                          fg_color=BG_PANEL, text_color=BG_BRAND, hover_color="#E5EBE6",
                          border_color=BG_BRAND, border_width=1,
                          command=lambda i=ph_row["ID"]: (db.query("DELETE FROM ServicePhoto WHERE ID=%s",(i,)), refresh_photos())).pack(pady=(4,0))

    def add_photo():
        if sid is None: return messagebox.showinfo("Информация", "Сначала сохраните услугу")
        p = filedialog.askopenfilename(filetypes=[("Images","*.png *.jpg *.jpeg")])
        if not p: return
        dst = os.path.join(IMG_DIR, os.path.basename(p))
        if os.path.abspath(p) != os.path.abspath(dst): shutil.copy(p, dst)
        db.query("INSERT INTO ServicePhoto(ServiceID,PhotoPath) VALUES (%s,%s)",(sid, dst))
        refresh_photos()

    ctk.CTkButton(edit_win, text="Добавить фотографию", font=F_NORMAL,
                  fg_color=BG_PANEL, text_color=BG_BRAND, hover_color="#E5EBE6",
                  border_color=BG_BRAND, border_width=1, corner_radius=8,
                  command=add_photo).pack(anchor="w", padx=24, pady=8)
    refresh_photos()

    def save():
        nonlocal sid
        title = title_v.get().strip()
        if not title: return messagebox.showerror("Ошибка","Введите название")
        try: cost=float(cost_v.get()); dur=int(dur_v.get()); disc=float(disc_v.get())
        except: return messagebox.showerror("Ошибка","Проверьте числовые поля")
        if cost <= 0: return messagebox.showerror("Ошибка","Цена должна быть положительной")
        if not (0 < dur <= 240): return messagebox.showerror("Ошибка","Длительность от 1 до 240 минут")
        if not (0 <= disc <= 1): return messagebox.showerror("Ошибка","Скидка от 0 до 1")
        dup_sql = "SELECT 1 FROM Service WHERE Title=%s" + (" AND ID<>%s" if sid else "")
        if db.fetch(dup_sql, (title, sid) if sid else (title,)):
            return messagebox.showerror("Ошибка","Услуга с таким названием уже существует")
        descr = desc_t.get("1.0","end").strip()
        if sid is None:
            sid = db.query("INSERT INTO Service(Title,Cost,DurationInSeconds,Description,Discount,MainImagePath) VALUES (%s,%s,%s,%s,%s,%s)",
                           (title,cost,dur*60,descr,disc,img_v.get() or None))
        else:
            db.query("UPDATE Service SET Title=%s,Cost=%s,DurationInSeconds=%s,Description=%s,Discount=%s,MainImagePath=%s WHERE ID=%s",
                     (title,cost,dur*60,descr,disc,img_v.get() or None, sid))
        reload(); edit_win.destroy()

    ctk.CTkButton(edit_win, text="Сохранить", font=F_HEAD, fg_color=BG_ACTION,
                  text_color=TXT_DARK, hover_color=BG_ACTION_H, corner_radius=10, height=44,
                  command=save).pack(pady=14, padx=24, fill="x")

# ---------- запись клиента ----------
def open_booking(sid):
    s = db.fetch("SELECT * FROM Service WHERE ID=%s",(sid,))[0]
    w = ctk.CTkToplevel(root); w.title("Запись на услугу")
    w.geometry("460x460"); w.configure(fg_color=BG_MAIN)
    w.transient(root); w.lift(); w.focus()

    hd = ctk.CTkFrame(w, fg_color=BG_MAIN, height=56, corner_radius=0); hd.pack(fill="x"); hd.pack_propagate(False)
    ctk.CTkLabel(hd, text="Запись на услугу", font=F_HEAD, text_color=BG_BRAND).pack(side="left", padx=20)
    ctk.CTkFrame(w, fg_color=BG_ACCENT, height=3, corner_radius=0).pack(fill="x")

    ctk.CTkLabel(w, text=s["Title"], font=F_TITLE, text_color=TXT_DARK).pack(pady=(14,2))
    ctk.CTkLabel(w, text=f"Длительность: {s['DurationInSeconds']//60} мин",
                 font=F_NORMAL, text_color=TXT_MUTED).pack()

    box = ctk.CTkFrame(w, fg_color=BG_MAIN); box.pack(fill="x", padx=24, pady=14)
    clients = db.fetch("SELECT ID, CONCAT_WS(' ',LastName,FirstName,IFNULL(Patronymic,'')) AS FIO FROM Client ORDER BY LastName")
    cli_map = {c["FIO"]: c["ID"] for c in clients}
    cli_var = ctk.StringVar(value=list(cli_map.keys())[0] if cli_map else "")

    ctk.CTkLabel(box, text="Клиент:", font=F_NORMAL, text_color=TXT_MUTED, anchor="w").pack(fill="x")
    ctk.CTkOptionMenu(box, variable=cli_var, values=list(cli_map.keys()) or [""], font=F_NORMAL,
                      width=400, corner_radius=8, fg_color=BG_PANEL, button_color=BG_PANEL,
                      button_hover_color="#E5EBE6", text_color=TXT_DARK,
                      dropdown_font=F_NORMAL).pack(fill="x")

    ctk.CTkLabel(box, text="Дата (ГГГГ-ММ-ДД):", font=F_NORMAL, text_color=TXT_MUTED, anchor="w").pack(fill="x", pady=(10,0))
    date_v = ctk.StringVar(value=date.today().isoformat())
    ctk.CTkEntry(box, textvariable=date_v, font=F_NORMAL, height=34, corner_radius=8,
                 border_color=BORDER, border_width=1, fg_color=BG_MAIN, text_color=TXT_DARK).pack(fill="x")

    ctk.CTkLabel(box, text="Время начала (ЧЧ:ММ):", font=F_NORMAL, text_color=TXT_MUTED, anchor="w").pack(fill="x", pady=(10,0))
    time_v = ctk.StringVar(value="10:00")
    ctk.CTkEntry(box, textvariable=time_v, font=F_NORMAL, height=34, corner_radius=8,
                 border_color=BORDER, border_width=1, fg_color=BG_MAIN, text_color=TXT_DARK).pack(fill="x")

    end_lbl = ctk.CTkLabel(box, text="Окончание: —:—", font=F_NORMAL, text_color=BG_BRAND)
    end_lbl.pack(pady=(8,0))

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
        except: return messagebox.showerror("Ошибка","Некорректные дата или время")
        db.query("INSERT INTO ClientService(ClientID,ServiceID,StartTime) VALUES (%s,%s,%s)",
                 (cli_map[cli_var.get()], sid, dt))
        messagebox.showinfo("Готово","Запись добавлена"); w.destroy()

    ctk.CTkButton(w, text="Сохранить", font=F_HEAD, fg_color=BG_ACTION, text_color=TXT_DARK,
                  hover_color=BG_ACTION_H, corner_radius=10, height=42,
                  command=save).pack(pady=14, padx=24, fill="x")

# ---------- ближайшие записи ----------
def open_upcoming():
    w = ctk.CTkToplevel(root); w.title("Ближайшие записи")
    w.geometry("980x640"); w.configure(fg_color=BG_MAIN)
    w.transient(root); w.lift()

    hd = ctk.CTkFrame(w, fg_color=BG_MAIN, height=56, corner_radius=0); hd.pack(fill="x"); hd.pack_propagate(False)
    ctk.CTkLabel(hd, text="Ближайшие записи (сегодня и завтра)",
                 font=F_HEAD, text_color=BG_BRAND).pack(side="left", padx=20)
    ctk.CTkFrame(w, fg_color=BG_ACCENT, height=3, corner_radius=0).pack(fill="x")

    frame = ctk.CTkScrollableFrame(w, fg_color=BG_MAIN,
                                   scrollbar_button_color=BORDER, scrollbar_button_hover_color=BG_BRAND)
    frame.pack(fill="both", expand=True, padx=16, pady=14)

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
                         font=F_NORMAL, text_color=TXT_MUTED).pack(pady=20); return
        for r in rows:
            delta = r["StartTime"] - now
            mins = int(delta.total_seconds() // 60)
            urgent = 0 <= mins < 60
            if mins < 0:
                badge_text, badge_bg, badge_fg = "уже началась", BG_PANEL, TXT_MUTED
            else:
                h, m = divmod(mins, 60)
                badge_text = f"осталось {h} ч {m} мин"
                badge_bg = "#B71C1C" if urgent else BG_BRAND
                badge_fg = TXT_LIGHT

            card = ctk.CTkFrame(frame, fg_color=BG_MAIN, border_color=BORDER,
                                border_width=1, corner_radius=10)
            card.pack(fill="x", pady=5, padx=2)
            left = ctk.CTkFrame(card, fg_color="transparent"); left.pack(side="left", fill="both", expand=True, padx=16, pady=12)
            ctk.CTkLabel(left, text=r["Title"], font=F_HEAD, text_color=TXT_DARK, anchor="w").pack(anchor="w")
            fio = " ".join(filter(None,[r["LastName"], r["FirstName"], r["Patronymic"]]))
            ctk.CTkLabel(left, text=f"Клиент: {fio}", font=F_NORMAL, text_color=TXT_DARK, anchor="w").pack(anchor="w", pady=(2,0))
            ctk.CTkLabel(left, text=f"Телефон: {r['Phone']}    Email: {r['Email'] or '—'}",
                         font=F_SMALL, text_color=TXT_MUTED, anchor="w").pack(anchor="w")
            ctk.CTkLabel(left, text=f"Время: {r['StartTime'].strftime('%Y-%m-%d %H:%M')}",
                         font=F_SMALL, text_color=TXT_MUTED, anchor="w").pack(anchor="w")
            ctk.CTkLabel(card, text=badge_text, font=F_HEAD, text_color=badge_fg,
                         fg_color=badge_bg, corner_radius=8, width=180, height=40).pack(side="right", padx=16, pady=12)
        w.after(30_000, refresh)

    refresh()

# ---------- запуск ----------
search_var.trace_add("write", lambda *_: reload())
filter_var.trace_add("write", lambda *_: reload())
sort_var.trace_add("write",   lambda *_: reload())

refresh_admin_ui()
reload()
root.mainloop()
