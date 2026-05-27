import mysql.connector

CFG = dict(host="localhost", user="root", password="root", database="salon")

def conn():
    return mysql.connector.connect(**CFG)

def fetch(sql, p=()):
    c = conn(); cur = c.cursor(dictionary=True)
    cur.execute(sql, p); r = cur.fetchall()
    c.close(); return r

def query(sql, p=()):
    c = conn(); cur = c.cursor()
    cur.execute(sql, p); c.commit()
    rid = cur.lastrowid; c.close(); return rid
