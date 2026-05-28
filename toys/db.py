import mysql.connector

CFG = dict(host="localhost", user="root", password="root", database="toysdb", charset="utf8mb4")


def conn():
    return mysql.connector.connect(**CFG)


def fetch(sql, args=()):
    with conn() as c:
        cur = c.cursor(dictionary=True)
        cur.execute(sql, args)
        return cur.fetchall()


def query(sql, args=()):
    with conn() as c:
        cur = c.cursor()
        cur.execute(sql, args)
        c.commit()
        return cur.lastrowid
