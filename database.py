"""database: file contains structure for data tables and db objects"""

import sqlite3
from model import Model, Producto, Variacion
import datetime
import json

dbfile = "data/file.db"
logfile = "data/errors.log"
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
    sql = "drop table markets;"
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
            talla TEXT NULL,
            product_id INTEGER
        );"""
    cursor = db.execute(sql)
    sql = "CREATE UNIQUE INDEX child_sku ON children(sku);"
    cursor = db.execute(sql)

    sql="""CREATE TABLE markets (
    id int(11) NOT NULL PRIMARY KEY,
    market varchar(100) NOT NULL
    );"""
    cursor = db.execute(sql)

    db.close()
    return True

def get_all(table=''):
    with sqlite3.connect(dbfile) as db:
        sql = f"SELECT * FROM {table};"
        db.row_factory = sqlite3.Row
        cursor = db.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        return rows

def get_row(sku='', table='items') :
    with sqlite3.connect(dbfile) as db:
        sql = f"SELECT * FROM {table} where sku=?;"
        db.row_factory = sqlite3.Row
        cursor = db.execute(sql, (sku,))
        row = cursor.fetchone()
        cursor.close()
        return row

def add_item(data):
    if not data: return
    if type(data[0])==list: data=data[0]
    db = sqlite3.connect(dbfile)
    sql = "insert or replace into items (id, sku, nombre) values (?, ?, ?);"
    for x in data:
        db.execute(sql, (x['id'], x['sku'], x['nombre']))
    db.commit()    
    db.close()

def add_children(data):
    if not data: return
    if type(data[0])==list: data=data[0]
    db = sqlite3.connect(dbfile)
    sql = "insert or replace into children (id, sku, product_id, color, talla) values (?, ?, ?, ?, ?);"
    for x in data:
        db.execute(sql, (x['id'], x['sku'], x['product_id'], x['color'], x['talla']))
    db.commit()    
    db.close()

def log_error(error):
    with open(logfile,"a") as f:
        f.write(str(datetime.datetime.now())+"\n")
        f.write(str(error)+"\n")