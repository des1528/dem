"""Одноразовый импорт ресурсов в БД.
Перед запуском: выполнить my.sql, добавить пол:
  INSERT INTO Gender VALUES ('М','Мужской'),('Ж','Женский');
"""
import pandas as pd, db, os
from datetime import datetime

R = r"C:\demka\Подготовка к ДЭ-2026\Предметная область Салон красоты\Код 1.9 (2020) - Салон красоты\Сессия 1"

# --- Услуги ---
df = pd.read_csv(os.path.join(R, "service_b_import.csv"), sep=";", encoding="utf-8")
df.columns = [c.strip() for c in df.columns]
for _, r in df.iterrows():
    db.query("INSERT INTO Service(Title,Cost,DurationInSeconds,Description,Discount) VALUES (%s,%s,%s,%s,%s)",
             (str(r.get("Title") or r.iloc[0]),
              float(r.get("Cost") or 0),
              int(r.get("DurationInSeconds") or 0),
              (str(r.get("Description")) if r.get("Description") is not None else None),
              float(r.get("Discount") or 0)))

# --- Клиенты ---
df = pd.read_csv(os.path.join(R, "client_b_import.txt"), sep="\t", encoding="utf-8")
df.columns = [c.strip() for c in df.columns]
for _, r in df.iterrows():
    db.query("""INSERT INTO Client(FirstName,LastName,Patronymic,Birthday,RegistrationDate,Email,Phone,GenderCode)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
             (r["FirstName"], r["LastName"], r.get("Patronymic"),
              r.get("Birthday"), r.get("RegistrationDate") or datetime.now(),
              r.get("Email"), r["Phone"], r.get("GenderCode","М")))

# --- Записи на услуги ---
df = pd.read_excel(os.path.join(R, "serviceclient_b_import.xlsx"))
df.columns = [c.strip() for c in df.columns]
for _, r in df.iterrows():
    db.query("INSERT INTO ClientService(ClientID,ServiceID,StartTime) VALUES (%s,%s,%s)",
             (int(r["ClientID"]), int(r["ServiceID"]), r["StartTime"]))

print("Импорт завершён.")
