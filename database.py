"""database: file contains structure for data tables and db objects"""

import sqlite3

dbfile = "data/file.db"
max_rows = 250
seconds = 1.0

def drop():
    db = sqlite3.connect(dbfile)
    sql = "SELECT count(*) as total FROM sqlite_master WHERE type='table' AND name='items';"
    cursor = db.execute(sql)
    row = cursor.fetchone()    
    if not row or not row[0]: return False
    sql = "drop table items;"
    cursor = db.execute(sql)
    sql = "drop table children;"
    cursor = db.execute(sql)
    db.close()
    return True

def create():    
    db = sqlite3.connect(dbfile)
    sql = "SELECT count(*) as total FROM sqlite_master WHERE type='table' AND name='items';"
    cursor = db.execute(sql)
    row = cursor.fetchone()
    if row and row[0]: return False
    sql = """
        CREATE TABLE items (
            id INTEGER PRIMARY KEY,
            sku TEXT NOT NULL,
            nombre TEXT NOT NULL
        );"""
    cursor = db.execute(sql)
    sql = "CREATE UNIQUE INDEX item_sku ON items(sku);"
    cursor = db.execute(sql)

    sql = """
        CREATE TABLE children (
            id INTEGER PRIMARY KEY,
            sku TEXT NOT NULL,
            color TEXT NULL,
            talla TEXT NULL
        );"""
    cursor = db.execute(sql)
    sql = "CREATE UNIQUE INDEX child_sku ON children(sku);"
    cursor = db.execute(sql)
    db.close()
    return True

def get_row(sku='', table='items') :
    with sqlite3.connect(dbfile) as db:
        sql = f"SELECT * FROM {table} where sku=?;"
        cursor = db.execute(sql,(sku))
        row = cursor.fetchone()
        cursor.close()
        return row
